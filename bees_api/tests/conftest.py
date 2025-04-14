import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.db import get_db
from app.models import Base, User

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Override the DATABASE_URL from settings for tests
settings.DATABASE_URL = TEST_DATABASE_URL

# Create test async engine
test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# Create a fixture for the FastAPI app with test dependencies
@pytest.fixture
def app() -> FastAPI:
    from app.main import app as application
    return application


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Create all tables in the test database
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create a new session for testing
    async with TestingSessionLocal() as session:
        yield session

    # Drop all tables after tests are done
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Override the get_db dependency for tests
@pytest.fixture
def override_get_db(db_session: AsyncSession) -> Generator:
    async def _override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    return _override_get_db


@pytest.fixture
def app_with_test_db(app: FastAPI, override_get_db) -> FastAPI:
    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    # Create a test user
    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        is_active=True,
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user


@pytest_asyncio.fixture
async def auth_headers(test_user: User, app: FastAPI, async_client: AsyncClient) -> dict:
    # Get auth token
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            mutation {
                login(username: "testuser", password: "password") {
                    accessToken
                    tokenType
                }
            }
            """
        },
    )
    json_response = response.json()
    token = json_response["data"]["login"]["accessToken"]
    return {"Authorization": f"Bearer {token}"}
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register(app_with_test_db: dict, async_client: AsyncClient):
    # Test user registration
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            mutation {
                register(
                    username: "newuser",
                    email: "newuser@example.com",
                    password: "password123"
                ) {
                    id
                    username
                    email
                    isActive
                }
            }
            """
        },
    )
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Parse the response JSON
    json_response = response.json()
    assert "errors" not in json_response
    assert "data" in json_response
    assert "register" in json_response["data"]
    
    # Check the returned user data
    user_data = json_response["data"]["register"]
    assert user_data["username"] == "newuser"
    assert user_data["email"] == "newuser@example.com"
    assert user_data["isActive"] is True


async def test_login_success(test_user, app_with_test_db: dict, async_client: AsyncClient):
    # Test successful login
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
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Parse the response JSON
    json_response = response.json()
    assert "errors" not in json_response
    assert "data" in json_response
    assert "login" in json_response["data"]
    
    # Check the returned token data
    token_data = json_response["data"]["login"]
    assert token_data["accessToken"] is not None
    assert token_data["tokenType"] == "bearer"


async def test_login_failure(app_with_test_db: dict, async_client: AsyncClient):
    # Test login with incorrect credentials
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            mutation {
                login(username: "testuser", password: "wrongpassword") {
                    accessToken
                    tokenType
                }
            }
            """
        },
    )
    
    # Check if the response contains errors
    assert response.status_code == 200  # GraphQL always returns 200, but with errors
    json_response = response.json()
    assert "errors" in json_response
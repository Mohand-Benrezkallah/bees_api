import os
from datetime import date, datetime
from typing import List, Optional

import strawberry
from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.file_uploads import Upload
from strawberry.types import Info

from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.crud import (authenticate_user, create_bee, create_user, delete_bee,
                      get_bee, get_bees, get_user_by_email,
                      get_user_by_username)
from app.db import get_db
from app.models import Bee, User


# Context dependency
async def get_context(
    db: AsyncSession = Depends(get_db),
):
    return {
        "db": db,
    }


# GraphQL Types
@strawberry.type
class BeeType:
    id: int
    name: str
    origin: str
    image_path: Optional[str]
    species: str
    captured_date: date


@strawberry.type
class UserType:
    id: int
    username: str
    email: str
    is_active: bool


@strawberry.type
class TokenType:
    access_token: str
    token_type: str


# Queries
@strawberry.type
class Query:
    @strawberry.field
    async def bees(self, info: Info) -> List[BeeType]:
        # Verify authentication
        user = await get_current_user(info.context["request"].headers.get("Authorization", "").replace("Bearer ", ""), info.context["db"])
        
        # Get bees
        db_bees = await get_bees(info.context["db"])
        return [
            BeeType(
                id=bee.id,
                name=bee.name,
                origin=bee.origin,
                image_path=bee.image_path,
                species=bee.species,
                captured_date=bee.captured_date,
            )
            for bee in db_bees
        ]

    @strawberry.field
    async def bee(self, info: Info, id: int) -> Optional[BeeType]:
        # Verify authentication
        user = await get_current_user(info.context["request"].headers.get("Authorization", "").replace("Bearer ", ""), info.context["db"])
        
        # Get bee
        db_bee = await get_bee(info.context["db"], id)
        if not db_bee:
            return None
        
        return BeeType(
            id=db_bee.id,
            name=db_bee.name,
            origin=db_bee.origin,
            image_path=db_bee.image_path,
            species=db_bee.species,
            captured_date=db_bee.captured_date,
        )

    @strawberry.field
    async def me(self, info: Info) -> UserType:
        # Verify authentication
        user = await get_current_user(info.context["request"].headers.get("Authorization", "").replace("Bearer ", ""), info.context["db"])
        
        return UserType(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
        )


# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register(
        self, info: Info, username: str, email: str, password: str
    ) -> UserType:
        db = info.context["db"]
        
        # Check if user already exists
        existing_user = await get_user_by_username(db, username)
        if existing_user:
            raise ValueError("Username already registered")
        
        existing_email = await get_user_by_email(db, email)
        if existing_email:
            raise ValueError("Email already registered")
        
        # Create new user
        db_user = await create_user(db, username, email, password)
        
        return UserType(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            is_active=db_user.is_active,
        )

    @strawberry.mutation
    async def login(self, info: Info, username: str, password: str) -> TokenType:
        db = info.context["db"]
        
        # Authenticate user
        user = await authenticate_user(db, username, password)
        if not user:
            raise ValueError("Incorrect username or password")
        
        # Create access token
        access_token = create_access_token(data={"sub": user.username})
        
        return TokenType(
            access_token=access_token,
            token_type="bearer",
        )

    @strawberry.mutation
    async def add_bee(
        self,
        info: Info,
        name: str,
        origin: str,
        species: str,
        captured_date: date,
        image: Optional[Upload] = None,
    ) -> BeeType:
        # Verify authentication
        user = await get_current_user(info.context["request"].headers.get("Authorization", "").replace("Bearer ", ""), info.context["db"])
        
        # Handle image upload if provided
        image_path = None
        if image:
            # Create upload directory if it doesn't exist
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            
            # Save the uploaded file
            upload_file: UploadFile = await image.get_upload_file()
            
            # Create a unique filename using timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{upload_file.filename}"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            
            # Write the file
            with open(file_path, "wb") as buffer:
                content = await upload_file.read()
                buffer.write(content)
            
            # Store the relative path
            image_path = f"images/{filename}"
        
        # Create bee
        db_bee = await create_bee(
            info.context["db"],
            name=name,
            origin=origin,
            species=species,
            captured_date=captured_date,
            image_path=image_path,
        )
        
        return BeeType(
            id=db_bee.id,
            name=db_bee.name,
            origin=db_bee.origin,
            image_path=db_bee.image_path,
            species=db_bee.species,
            captured_date=db_bee.captured_date,
        )

    @strawberry.mutation
    async def delete_bee(self, info: Info, id: int) -> bool:
        # Verify authentication
        user = await get_current_user(info.context["request"].headers.get("Authorization", "").replace("Bearer ", ""), info.context["db"])
        
        # Delete bee
        success = await delete_bee(info.context["db"], id)
        return success


# Create the schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
import os
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import Bee, User


# User operations
async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, username: str, email: str, password: str) -> User:
    hashed_password = get_password_hash(password)
    db_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# Bee operations
async def get_bees(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Bee]:
    result = await db.execute(select(Bee).offset(skip).limit(limit))
    return result.scalars().all()

async def get_bee(db: AsyncSession, bee_id: int) -> Optional[Bee]:
    result = await db.execute(select(Bee).where(Bee.id == bee_id))
    return result.scalars().first()

async def create_bee(
    db: AsyncSession, 
    name: str, 
    origin: str, 
    species: str, 
    captured_date: date,
    image_path: Optional[str] = None
) -> Bee:
    db_bee = Bee(
        name=name,
        origin=origin,
        species=species,
        captured_date=captured_date,
        image_path=image_path
    )
    db.add(db_bee)
    await db.commit()
    await db.refresh(db_bee)
    return db_bee

async def delete_bee(db: AsyncSession, bee_id: int) -> bool:
    db_bee = await get_bee(db, bee_id)
    if not db_bee:
        return False
        
    # Delete image file if it exists
    if db_bee.image_path:
        image_full_path = os.path.join(os.getcwd(), db_bee.image_path)
        if os.path.exists(image_full_path):
            os.remove(image_full_path)
            
    await db.delete(db_bee)
    await db.commit()
    return True
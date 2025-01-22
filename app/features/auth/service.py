from typing import Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import UserRegister, UserCreate

logger = logging.getLogger(__name__)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    try:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}")
        raise

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        raise

async def create_user(db: AsyncSession, user_data: Union[UserCreate, UserRegister]) -> User:
    try:
        logger.info(f"Creating user with email: {user_data.email}")
        db_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash=get_password_hash(user_data.password),
            is_active=True,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logger.info(f"Successfully created user with ID: {db_user.id}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        await db.rollback()
        raise

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    try:
        user = await get_user_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        raise 
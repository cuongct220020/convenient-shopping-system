# app/repositories/user_repository.py
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from shopping_shared.databases.base_repository import BaseRepository

from app.models.user import User
from app.schemas import (
    UserCreateSchema,
    UserInfoUpdateSchema
)


class UserRepository(BaseRepository[User, UserCreateSchema, UserInfoUpdateSchema]):
    """
    Repository for User model-specific database operations.
    Inherits all common CRUD, pagination, and soft-delete logic from BaseRepository.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Fetches user by username."""
        return await self.get_by_field_case_insensitive("username", username)

    async def get_by_email(self, email: EmailStr) -> Optional[User]:
        """Fetch user record by email."""
        return await self.get_by_field_case_insensitive("email", email)

    async def activate_user(self, user_id: UUID) -> Optional[User]:
        """Activates a user account by setting is_active to True."""
        return await self.update_field(user_id, "is_active", True)

    async def update_password(self, user_id: UUID, hashed_password: str) -> Optional[User]:
        """Updates the user's password with the hashed value."""
        return await self.update_field(user_id, "password_hash", hashed_password)



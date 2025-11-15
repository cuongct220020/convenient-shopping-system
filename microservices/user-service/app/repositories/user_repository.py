# app/repositories/user_repository.py
from datetime import datetime, UTC
from typing import Optional, Any, Dict

from pydantic import EmailStr
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models.user import User
from app.models.address import Address
from shopping_shared.databases.base_repository import BaseRepository
from app.schemas import (
    UserCreateSchema,
    UserUpdateSchema,
    UserIdentityProfileUpdateSchema,
    UserHealthProfileUpdateSchema,
)


class UserRepository(BaseRepository[User, UserCreateSchema, UserUpdateSchema]):
    """
    Repository for User model-specific database operations.
    Inherits all common CRUD, pagination, and soft-delete logic from BaseRepository.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)


    async def _get_by_field(
        self,
        field_name: str,
        subject: str,
        include_deleted: bool = False
    ) -> Optional[User]:
        """Fetches a user by its field name."""
        if not subject:
            return None

        field = getattr(self.model, field_name)
        stmt = select(self.model).where(func.lower(field) == func.lower(subject))
        stmt = self._apply_filters_and_sort(stmt, filters=None, sort_by=None, include_deleted=include_deleted)

        result = await self.session.execute(stmt.limit(1))
        return result.scalars().first()


    async def get_by_username(self, username: str) -> Optional[User]:
        """Fetches user by username."""
        return await self._get_by_field("username", username)

    async def get_by_email(self, email: EmailStr) -> Optional[User]:
        """Fetch user record by email."""
        return await self._get_by_field("email", email)

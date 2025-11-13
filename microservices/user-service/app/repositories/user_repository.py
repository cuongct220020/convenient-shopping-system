# app/repositories/user_repository.py
from datetime import datetime, UTC
from typing import Optional, Any, Dict

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

    async def get_by_username(self, username: str, include_deleted: bool = False) -> Optional[User]:
        """
        Fetch a user record by email (case-insensitive), respecting soft-delete.
        Returns None if no user is found.
        """
        if not username:
            return None

        # Build the initial statement with the email filter
        stmt = select(self.model).where(func.lower(self.model.email) == func.lower(username))

        # Use the base class's helper to apply standard filters (like soft-delete)
        stmt = self._apply_filters_and_sort(stmt, include_deleted=include_deleted)

        result = await self.session.execute(stmt.limit(1))
        return result.scalars().first()

    async def activate_user(self, user_id: Any) -> bool:
        """
        Activates a user account by setting is_active to True.
        Returns True if the user was found and activated, False otherwise.
        """
        stmt = (
            update(self.model)
            .where(self.model.id == user_id)
            .where(self.model.is_active == False)
            .values(is_active=True)
        )
        result = await self.session.execute(stmt)
        if result.rowcount > 0:
            await self.session.flush()
            return True
        return False

    async def update_user_identity_profile(self, user_id: Any, profile_data: UserIdentityProfileUpdateSchema) -> Optional[User]:
        """
        Updates a user's identity profile and their associated address.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Update user's direct fields from the identity profile
        update_values = profile_data.model_dump(exclude_unset=True, exclude={'address'})
        if update_values:
            q = update(User).where(User.id == user_id).values(**update_values, updated_at=func.now())
            await self.session.execute(q)

        # Handle address update
        if profile_data.address:
            address_data = profile_data.address.model_dump(exclude_unset=True)
            if address_data:
                # Check if user already has an address
                if user.address_id:
                    # Update existing address
                    q = update(Address).where(Address.id == user.address_id).values(**address_data, updated_at=func.now())
                    await self.session.execute(q)
                else:
                    # Create new address and link to user
                    insert_stmt = insert(Address).values(**address_data).returning(Address.id)
                    result = await self.session.execute(insert_stmt)
                    new_address_id = result.scalar_one()
                    await self.session.execute(update(User).where(User.id == user_id).values(address_id=new_address_id, updated_at=func.now()))

        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_user_health_profile(self, user_id: Any, profile_data: UserHealthProfileUpdateSchema) -> Optional[User]:
        """
        Updates a user's health profile.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None

        update_values = profile_data.model_dump(exclude_unset=True)
        if update_values:
            q = update(User).where(User.id == user_id).values(**update_values, updated_at=func.now())
            await self.session.execute(q)
            await self.session.flush()
            await self.session.refresh(user)

        return user
        
    async def create_with_role(self, user_data: Dict[str, Any]) -> User:
        """Creates a new user with a specific role."""
        # This method assumes user_data is a dict from UserAdminCreateSchema
        new_user = self.model(**user_data)
        self.session.add(new_user)
        await self.session.flush()
        await self.session.refresh(new_user)
        return new_user
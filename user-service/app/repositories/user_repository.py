# user-service/app/repositories/user_repository.py
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.user import User
from app.schemas.user_schema import UserCreateSchema, UserInfoUpdateSchema
from shopping_shared.databases.base_repository import BaseRepository



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

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user record by email."""
        return await self.get_by_field_case_insensitive("email", email)

    async def activate_user(self, user_id: UUID) -> Optional[User]:
        """Activates a user account by setting is_active to True."""
        return await self.update_field(user_id, "is_active", True)

    async def update_password(self, user_id: UUID, hashed_password: str) -> Optional[User]:
        """Updates the user's password with the hashed value."""
        return await self.update_field(user_id, "password_hash", hashed_password)


    async def create_user(self, user_data: dict) -> User:
        """
        Creates a new user from a dictionary.
        Useful when the service has pre-processed data (e.g. hashed password).
        """
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user


    async def update(self, user_id: UUID, data: UserInfoUpdateSchema) -> Optional[User]:
        """
        Updates an existing user record, handling unique constraints properly.
        Specifically handles phone number updates to avoid self-referencing unique constraint violations.
        """
        instance = await self.get_by_id(user_id)
        if instance:
            # Use exclude_unset to only update fields that were provided in the request
            update_data = data.model_dump(exclude_unset=True)

            # Handle phone number update carefully to avoid unique constraint issues
            if 'phone_num' in update_data:
                new_phone = update_data['phone_num']
                # If the new phone number is the same as the current one, skip the update
                if new_phone == instance.phone_num:
                    del update_data['phone_num']

            for key, value in update_data.items():
                setattr(instance, key, value)
            self.session.add(instance)
            await self.session.flush()
            await self.session.refresh(instance)
        return instance

    async def get_user_with_profiles(self, user_id: UUID) -> Optional[User]:
        """
        Gets user with eager-loaded identity and health profiles.
        Useful for /users/me endpoint to return complete user data.
        """
        from sqlalchemy.orm import selectinload

        load_options = [
            selectinload(User.identity_profile),
            selectinload(User.health_profile)
        ]
        return await self.get_by_id(user_id, load_options=load_options)


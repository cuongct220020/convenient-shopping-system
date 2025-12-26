# user-service/app/repositories/user_repository.py
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.user import User
from app.schemas import UserCreateSchema, UserInfoUpdateSchema
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

    async def update_email(self, user_id: UUID, new_email: str) -> Optional[User]:
        """
        Updates the user's email address. Should be called after OTP verification.
        """
        return await self.update_fields(user_id, {
            "email": new_email,
            # "updated_at": time(UTC)
        })


    async def verify_email(self, user_id: UUID) -> Optional[User]:
        """Marks user's email as verified."""
        return await self.update_field(user_id, "email_verified", True)


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


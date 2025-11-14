# app/services/user_service.py
from typing import Any
from app.decorators.cache import cache
from shared.shopping_shared import NotFound, Conflict, Unauthorized
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas import (
    ChangePasswordRequestSchema,
    UserDetailedProfileSchema,
    UserUpdateSchema,
    UserIdentityProfileUpdateSchema,
    UserHealthProfileUpdateSchema,
    UserAdminCreateSchema,
    UserAdminUpdateSchema,
)
from app.utils.password_utils import hash_password, verify_password
from app.services.auth_service import AuthService


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    @cache(schema=UserDetailedProfileSchema, ttl=300, prefix="user_profile")
    async def get_user_by_id(self, user_id: int) -> User:
        """Fetches a user by their ID. Raises NotFound if the user does not exist."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFound(f"User with id {user_id} not found")
        return user

    @classmethod
    async def change_password(
            cls,
            user_id: Any,
            data: ChangePasswordRequestSchema,
            user_repo: UserRepository
    ):
        """Changes a user's password and invalidates all their tokens."""
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise NotFound("Authenticated user not found.")

        if not verify_password(data.current_password.get_secret_value(), user.password):
            raise Unauthorized("Invalid old password.")

        hashed_new_password = hash_password(data.new_password.get_secret_value())
        user.password = hashed_new_password

        # Invalidate all sessions for the user
        await AuthService.revoke_all_tokens_for_user(user.id, user_repo)

    async def update_user_identity_profile(self, user_id: Any, profile_data: UserIdentityProfileUpdateSchema) -> User:
        """Updates a user's identity profile information."""
        updated_user = await self.user_repo.update_user_identity_profile(user_id, profile_data)
        if not updated_user:
            raise NotFound(f"User with id {user_id} not found.")
        return updated_user

    async def update_user_health_profile(self, user_id: Any, profile_data: UserHealthProfileUpdateSchema) -> User:
        """Updates a user's health profile information."""
        updated_user = await self.user_repo.update_user_health_profile(user_id, profile_data)
        if not updated_user:
            raise NotFound(f"User with id {user_id} not found.")
        return updated_user

    # --- Admin Management Methods ---

    async def list_all_users(self, page: int, page_size: int):
        """Lists all users with pagination for admin purposes."""
        return await self.user_repo.get_paginated(page=page, page_size=page_size)

    async def create_user_by_admin(self, user_data: UserAdminCreateSchema) -> User:
        """Creates a new user by an admin."""
        existing_user = await self.user_repo.get_by_username(user_data.email)
        if existing_user:
            raise Conflict(f"User with email {user_data.email} already exists.")

        hashed_password = hash_password(user_data.password)

        new_user_data = user_data.model_dump()
        new_user_data['password'] = hashed_password
        
        new_user = await self.user_repo.create_with_role(new_user_data)
        return new_user

    async def get_user_details_by_admin(self, user_id: int) -> User:
        """Fetches detailed user information for admin."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFound(f"User with id {user_id} not found.")
        return user

    async def update_user_by_admin(self, user_id: int, update_data: UserAdminUpdateSchema) -> User:
        """Updates a user's information by an admin."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFound(f"User with id {user_id} not found.")

        # The UserAdminUpdateSchema can be passed down if the repo method expects it
        # or converted to a simpler UserUpdateSchema if needed.
        # For now, let's assume the repo's `update` can handle the broader schema.
        updated_user = await self.user_repo.update(user_id, update_data)
        return updated_user

    async def delete_user_by_admin(self, user_id: int) -> None:
        """
        Deletes a user (soft delete by setting is_active=False) and revokes all their tokens.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFound(f"User with id {user_id} not found.")

        await self.user_repo.update(user_id, UserUpdateSchema(is_active=False))

        await AuthService.revoke_all_tokens_for_user(user_id, self.user_repo)

# microservices/user-service/app/services/user_service.py
from typing import List
from uuid import UUID

from shopping_shared.exceptions import NotFound, Conflict, Unauthorized
from shopping_shared.utils.logger_utils import get_logger

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas import (
    UserCreateSchema,
    UserInfoUpdateSchema,
    UserAdminCreateSchema,
    UserAdminUpdateSchema,
)
from app.schemas.auth_schema import ChangePasswordRequestSchema
from app.utils.password_utils import hash_password, verify_password

logger = get_logger("UserService")


class UserService:
    """
    Service for handling User core logic.
    Uses BaseRepository directly for all CRUD operations.
    """
    def __init__(self, user_repo: UserRepository):
        self.repository = user_repo

    # --- Standard CRUD operations (delegating to repository) ---

    async def get(self, user_id: UUID) -> User:
        """Fetch a single user by ID."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFound(f"User with id {user_id} not found")
        return user

    async def get_all(self, page: int = 1, page_size: int = 100) -> List[User]:
        """Fetch a paginated list of users."""
        result = await self.repository.get_paginated(page=page, page_size=page_size)
        return result.items

    async def create(self, user_data: UserCreateSchema) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.repository.get_by_email(user_data.email)
        if existing_user:
            raise Conflict(f"User with email {user_data.email} already exists.")

        return await self.repository.create(user_data)

    async def update(self, user_id: UUID, update_data: UserInfoUpdateSchema) -> User:
        """Update an existing user."""
        user = await self.repository.update(user_id, update_data)
        if not user:
            raise NotFound(f"User with id {user_id} not found")
        return user

    async def delete(self, user_id: UUID) -> None:
        """Delete a user (soft delete if supported)."""
        success = await self.repository.soft_delete(user_id)
        if not success:
            raise NotFound(f"User with id {user_id} not found")

    # --- Business logic methods ---

    async def change_password(
        self,
        user_id: UUID,
        data: ChangePasswordRequestSchema
    ) -> None:
        """Changes a user's password and invalidates all their tokens."""
        # Local import to avoid circular dependency
        from app.services.redis_service import RedisService

        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFound("Authenticated user not found.")

        if not verify_password(data.current_password.get_secret_value(), user.password_hash):
            raise Unauthorized("Invalid old password.")

        hashed_new_password = hash_password(data.new_password.get_secret_value())
        
        # Update password via repository
        await self.repository.update_password(user.id, hashed_new_password)

        # Invalidate all sessions for the user
        await RedisService.remove_session_from_allowlist(str(user.id))
        await RedisService.revoke_all_tokens_for_user(str(user.id))

        logger.info(f"Password changed for user {user_id}, all tokens revoked")
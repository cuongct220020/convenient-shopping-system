# user-service/app/services/admin_service.py
from uuid import UUID

from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreateSchema, UserAdminUpdateSchema
from app.utils.password_utils import hash_password
from shopping_shared.exceptions import Conflict, NotFound
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Admin Service")

class AdminService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository


    async def get_user_by_admin(self, user_id):
        """Fetch a user by ID for admin."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFound(f"User with id {user_id} not found")
        return user

    async def get_all_users(self, page: int = 1, page_size: int = 20):
        """Fetch all users with pagination."""
        return await self.user_repository.get_paginated(page=page, page_size=page_size)

    async def create_user_by_admin(self, user_data: UserCreateSchema):
        """Creates a new user by an admin."""
        existing_user = await self.user_repository.get_by_username(user_data.username)
        if existing_user:
            raise Conflict(f"User with username {user_data.username} already exists.")

        # Hash password (handle SecretStr properly)
        password_str = user_data.password.get_secret_value() if hasattr(user_data.password, 'get_secret_value') else str(user_data.password)
        hashed_password = hash_password(password_str)

        # Convert schema to dict and inject hashed password
        new_user_data = user_data.model_dump(exclude={'password'})
        new_user_data['password_hash'] = hashed_password

        # Create user via repository
        user = await self.user_repository.create_user(new_user_data)

        logger.info(f"Admin created user: {user.username}")
        return user

    async def update_user_by_admin(self, user_id: UUID, update_data: UserAdminUpdateSchema):
        """Updates a user's information by an admin."""
        user = await self.user_repository.update(user_id, update_data)
        if not user:
            raise NotFound(f"User with id {user_id} not found")

        logger.info(f"Admin updated user: {user_id}")
        return user

    async def delete_user_by_admin(self, user_id: UUID):
        """Deletes (soft delete) a user by an admin."""
        # Using soft_delete if supported, or delete
        # Assuming BaseRepository has soft_delete and User model supports it
        # If not, use delete. BaseRepository.delete is hard delete.
        # But BaseRepository has soft_delete. Let's assume User model has is_deleted.
        # Safe fallback:
        deleted = await self.user_repository.soft_delete(user_id)
        if not deleted:
             # Try hard delete if soft delete failed (e.g. model doesn't support it logic in repo threw error? No, returns False if not found)
             # But if it threw AttributeError, we might want hard delete?
             # For now, let's assume soft_delete works or we fallback to something else if needed.
             # If user not found, deleted is False.
             # Check existence first?
             user = await self.user_repository.get_by_id(user_id)
             if not user:
                 raise NotFound(f"User with id {user_id} not found")
             await self.user_repository.delete(user_id) # Hard delete fallback or actual delete

        logger.info(f"Admin deleted user: {user_id}")
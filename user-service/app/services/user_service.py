# user-service/app/services/user_service.py
from uuid import UUID

from app.models import User
from app.schemas.user_admin_schema import UserAdminUpdateSchema
from shopping_shared.exceptions import NotFound, Unauthorized
from shopping_shared.utils.logger_utils import get_logger

from app.repositories.user_repository import UserRepository
from app.services.redis_service import redis_service
from shopping_shared.caching.redis_keys import RedisKeys

from app.schemas.auth_schema import ChangePasswordRequestSchema
from app.utils.password_utils import hash_password, verify_password

logger = get_logger("User Service")


class UserService:
    """
    Service for handling User core logic.
    Uses BaseRepository directly for all CRUD operations.
    """
    def __init__(self, user_repo: UserRepository):
        self.repository = user_repo


    async def get_user_core_info(self, user_id: UUID) -> User:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFound(f"User {user_id} not found")
        return user


    async def update_user_core_info(self, user_id: UUID, update_data: UserAdminUpdateSchema) -> User:
        user = await self.repository.update(user_id, update_data)
        if not user:
            raise NotFound(f"User with id {user_id} not found")
        
        # Invalidate cache
        await redis_service.delete_key(RedisKeys.user_core_key(str(user_id)))
        await redis_service.delete_key(RedisKeys.admin_user_detail_key(str(user_id)))
        
        return user


    async def change_password(
        self,
        user_id: UUID,
        data: ChangePasswordRequestSchema
    ) -> None:
        """Changes a user's password and invalidates all their tokens."""

        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFound("Authenticated user not found.")

        if not verify_password(data.current_password, user.password_hash):
            raise Unauthorized("Invalid old password.")

        hashed_new_password = hash_password(data.new_password.get_secret_value())
        
        # Update password via repository
        await self.repository.update_password(user.id, hashed_new_password)

        # Invalidate all sessions for the user
        await redis_service.remove_session_from_allowlist(str(user.id))
        await redis_service.revoke_all_tokens_for_user(str(user.id))

        logger.info(f"Password changed for user {user_id}, all tokens revoked")
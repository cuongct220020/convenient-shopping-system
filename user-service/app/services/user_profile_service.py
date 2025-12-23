# user-service/app/services/user_profile_service.py
from uuid import UUID

from app.models import UserIdentityProfile, UserHealthProfile
from app.schemas import (
    UserIdentityProfileUpdateSchema,
    UserHealthProfileUpdateSchema
)
from app.repositories.user_profile_repository import (
    UserIdentityProfileRepository,
    UserHealthProfileRepository
)

from shopping_shared.exceptions import NotFound
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("User Profile Service")


class UserIdentityProfileService:
    def __init__(self, repo: UserIdentityProfileRepository):
        self.repository = repo

    async def get(self, user_id: UUID) -> UserIdentityProfile:
        """
        Get identity profile by user_id. Always returns a profile (creates default if not exists).
        Use case: GET /users/me/profile/identity
        """
        return await self.repository.get_or_create_for_user(user_id)

    async def update(self, user_id: UUID, update_data: UserIdentityProfileUpdateSchema) -> UserIdentityProfile:
        """
        Update identity profile. Creates default profile first if doesn't exist, then updates.
        Use case: PATCH /users/me/profile/identity
        """
        # Ensure profile exists
        await self.repository.get_or_create_for_user(user_id)

        # Update with provided data
        profile = await self.repository.update(user_id, update_data)
        if not profile:
            raise NotFound(f"Identity profile for user {user_id} not found")

        logger.info(f"Updated identity profile for user {user_id}")
        return profile


class UserHealthProfileService:
    def __init__(self, repo: UserHealthProfileRepository):
        self.repository = repo

    async def get(self, user_id: UUID) -> UserHealthProfile:
        """
        Get health profile by user_id. Always returns a profile (creates default if not exists).
        Use case: GET /users/me/profile/health
        """
        return await self.repository.get_or_create_for_user(user_id)

    async def update(self, user_id: UUID, update_data: UserHealthProfileUpdateSchema) -> UserHealthProfile:
        """
        Update health profile. Creates default profile first if doesn't exist, then updates.
        Use case: PATCH /users/me/profile/health
        """
        # Ensure profile exists
        await self.repository.get_or_create_for_user(user_id)

        # Update with provided data
        profile = await self.repository.update(user_id, update_data)
        if not profile:
            raise NotFound(f"Health profile for user {user_id} not found")

        logger.info(f"Updated health profile for user {user_id}")
        return profile




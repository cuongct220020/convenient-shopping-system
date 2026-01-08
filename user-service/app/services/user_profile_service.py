# user-service/app/services/user_profile_service.py
from uuid import UUID

from app.models import UserIdentityProfile, UserHealthProfile
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.schemas.user_profile_schema import (
    UserIdentityProfileUpdateSchema,
    UserHealthProfileUpdateSchema
)
from app.repositories.user_profile_repository import (
    UserIdentityProfileRepository,
    UserHealthProfileRepository
)

from shopping_shared.exceptions import NotFound
from shopping_shared.utils.logger_utils import get_logger
from app.services.redis_service import redis_service
from shopping_shared.caching.redis_keys import RedisKeys

logger = get_logger("User Profile Service")


class UserIdentityProfileService:
    def __init__(self, repo: UserIdentityProfileRepository, group_membership_repository: GroupMembershipRepository):
        self.repository = repo
        self.group_membership_repo = group_membership_repository

    async def get_identity_profile(self, user_id: UUID) -> UserIdentityProfile:
        """
        Get identity profile by user_id. Always returns a profile (creates default if not exists).
        Use case: GET /users/me/profile/identity
        """
        return await self.repository.get_or_create_for_user(user_id)


    async def update_identity_profile(self, user_id: UUID, update_data: UserIdentityProfileUpdateSchema) -> UserIdentityProfile | None:
        """
        Update identity profile. Creates default profile first if doesn't exist, then updates.
        Use case: PATCH /users/me/profile/identity
        """

        # Ensure profile exists and get it to find the PK
        existing_profile = await self.repository.get_or_create_for_user(user_id)

        # Handle nested Address update manually
        # Extract address data if present
        address_data = None
        if update_data.address is not None:
            address_data = update_data.address.model_dump(exclude_unset=True)
            # Remove address from main update data to prevent "dict" assignment error
            # We create a new copy of data to avoid modifying the input schema state if needed
            # But here we modify what we pass to repository
            # Pydantic model .copy() or manually exclude?
            # repository.update accepts schema.
            # We can pass dict to repository.update? No, it expects Schema.
            # But repository.update calls data.model_dump().
            
            # Problem: BaseRepository.update takes Schema.
            # We need to customize the update logic.
            
            # Let's perform update manually here since it's complex
            pass

        # We need to use the repository but handle the address specifically.
        # Since BaseRepository.update is generic, we can't easily intercept.
        # Better: Update the object fields manually here and save.
        
        from app.models import Address
        
        # 1. Update simple fields
        fields = update_data.model_dump(exclude_unset=True, exclude={'address'})
        for key, value in fields.items():
            setattr(existing_profile, key, value)
            
        # 2. Update Address
        if address_data is not None:
            if existing_profile.address:
                # Update existing address
                for k, v in address_data.items():
                    setattr(existing_profile.address, k, v)
            else:
                # Create new address
                new_address = Address(**address_data)
                existing_profile.address = new_address
        
        self.repository.session.add(existing_profile)
        await self.repository.session.flush()
        await self.repository.session.refresh(existing_profile)

        # Invalidate group cache keys
        user_groups = await self.group_membership_repo.get_user_groups(user_id)

        for membership, _ in user_groups:
            group_id_str = str(membership.group_id)

            group_members_list_key = RedisKeys.group_members_list_key(group_id_str)
            await redis_service.delete_key(group_members_list_key)
            logger.info(f"Delete group membership key: {group_members_list_key}")

            group_detail_key = RedisKeys.group_detail_key(group_id_str)
            await redis_service.delete_key(group_detail_key)
            logger.info(f"Delete group detail key: {group_detail_key}")

        # Invalidate personal cache keys
        user_id_str = str(user_id)
        await redis_service.delete_key(RedisKeys.user_profile_identity_key(user_id_str))
        await redis_service.delete_key(RedisKeys.admin_user_detail_key(user_id_str))

        # Reload with relationships (e.g. address) to avoid MissingGreenlet
        return await self.repository.get_or_create_for_user(user_id)


class UserHealthProfileService:
    def __init__(self, repo: UserHealthProfileRepository, group_membership_repository: GroupMembershipRepository):
        self.repository = repo
        self.group_membership_repo = group_membership_repository


    async def get_health_profile(self, user_id: UUID) -> UserHealthProfile:
        """
        Get health profile by user_id. Always returns a profile (creates default if not exists).
        Use case: GET /users/me/profile/health
        """
        return await self.repository.get_or_create_for_user(user_id)


    async def update_health_profile(self, user_id: UUID, update_data: UserHealthProfileUpdateSchema) -> UserHealthProfile:
        """
        Update health profile. Creates default profile first if doesn't exist, then updates.
        Use case: PATCH /users/me/profile/health
        """
        # Ensure profile exists and get it to find the PK
        existing_profile = await self.repository.get_or_create_for_user(user_id)

        # Update with provided data using the real PK (id), NOT user_id
        profile = await self.repository.update(existing_profile.id, update_data)
        if not profile:
            raise NotFound(f"Health profile for user {user_id} not found")

        # Invalidate group cache keys
        user_groups = await self.group_membership_repo.get_user_groups(user_id)

        for membership, _ in user_groups:
            group_id_str = str(membership.group_id)

            group_members_list_key = RedisKeys.group_members_list_key(group_id_str)
            await redis_service.delete_key(group_members_list_key)
            logger.info(f"Delete group membership key: {group_members_list_key}")

            group_detail_key = RedisKeys.group_detail_key(group_id_str)
            await redis_service.delete_key(group_detail_key)
            logger.info(f"Delete group detail key: {group_detail_key}")

        # Invalidate caches
        user_id_str = str(user_id)
        await redis_service.delete_key(RedisKeys.user_profile_health_key(user_id_str))
        await redis_service.delete_key(RedisKeys.admin_user_detail_key(user_id_str))

        # Reload to ensure consistency (and if any relationships are added later)
        return await self.repository.get_or_create_for_user(user_id)
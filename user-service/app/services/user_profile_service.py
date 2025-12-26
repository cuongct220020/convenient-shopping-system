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

        # Reload with relationships (e.g. address) to avoid MissingGreenlet
        return await self.repository.get_or_create_for_user(user_id)


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
        # Ensure profile exists and get it to find the PK
        existing_profile = await self.repository.get_or_create_for_user(user_id)

        # Update with provided data using the real PK (id), NOT user_id
        profile = await self.repository.update(existing_profile.id, update_data)
        if not profile:
            raise NotFound(f"Health profile for user {user_id} not found")

        # Reload to ensure consistency (and if any relationships are added later)
        return await self.repository.get_or_create_for_user(user_id)




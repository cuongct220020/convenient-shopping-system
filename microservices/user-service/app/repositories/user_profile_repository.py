from app.models import UserIdentityProfile, UserHealthProfile
from app.schemas import UserIdentityProfileSchema, UserIdentityProfileUpdateSchema, UserHealthProfileUpdateSchema
from shopping_shared.databases.base_repository import BaseRepository


class UserIdentityProfileRepository(BaseRepository[UserIdentityProfile, UserIdentityProfileUpdateSchema, ...]):
    """
    Repository for UserIdentityProfile model.
    Uses UpdateSchema for both Create and Update since profiles are typically updated/created together with user data
    """

    async def upsert_profile(self, user_id: str, profile_data: UserIdentityProfileUpdateSchema):
        """Upsert user identity profile - create if doesn't exist, update if exists"""
        return await self.upsert_by_field("user_id", user_id, profile_data)

    async def get_by_user_id(self, user_id: str) -> UserIdentityProfile:
        """Get user identity profile by user ID"""
        return await self.get_by_field("user_id", user_id)


class UserHealthProfileRepository(BaseRepository[UserHealthProfile, UserHealthProfileUpdateSchema, ...]):

    async def upsert_profile(self, user_id: str, profile_data: UserHealthProfileUpdateSchema):
        """Upsert user identity profile - create if doesn't exist, update if exists"""
        return await self.upsert_by_field("user_id", user_id, profile_data)

    async def get_by_user_id(self, user_id: str) -> UserHealthProfile:
        return await self.get_by_field("user_id", user_id)

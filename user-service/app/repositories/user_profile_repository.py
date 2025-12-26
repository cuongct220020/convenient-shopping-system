# user-service/app/repositories/user_profile_repository.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from shopping_shared.databases.base_repository import BaseRepository
from app.models import UserIdentityProfile, UserHealthProfile
from app.schemas import (
    UserIdentityProfileCreateSchema,
    UserIdentityProfileUpdateSchema,
    UserHealthProfileCreateSchema,
    UserHealthProfileUpdateSchema
)


class UserIdentityProfileRepository(
    BaseRepository[
        UserIdentityProfile,
        UserIdentityProfileCreateSchema,
        UserIdentityProfileUpdateSchema
    ]
):
    def __init__(self, session: AsyncSession):
        super().__init__(UserIdentityProfile, session)

    async def get_or_create_for_user(self, user_id: UUID) -> UserIdentityProfile:
        """
        Gets existing identity profile or creates a new default one.
        This ensures every user always has an identity profile.

        Use case: GET /users/me/profile/identity.
        """
        # Fix: Query by user_id (FK), not PK
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        stmt = select(UserIdentityProfile).where(UserIdentityProfile.user_id == user_id).options(
            selectinload(UserIdentityProfile.address)
        )
        result = await self.session.execute(stmt)
        profile = result.scalars().first()

        if not profile:
            # Create default profile with defaults
            from app.enums.user import UserGender

            default_user = UserIdentityProfileCreateSchema(
                user_id=user_id,
                gender=UserGender.OTHER,
                date_of_birth=None,
                occupation=None,
                address=None,
            )
            # IMPORTANT: We need to use dictionary for creation to handle relationships correctly if needed
            # but here address is None so it's fine.
            profile = UserIdentityProfile(**default_user.model_dump())
            self.session.add(profile)
            await self.session.flush()
            await self.session.refresh(profile)

        return profile


class UserHealthProfileRepository(
    BaseRepository[
        UserHealthProfile,
        UserHealthProfileCreateSchema,
        UserHealthProfileUpdateSchema
    ]
):
    def __init__(self, session: AsyncSession):
        super().__init__(UserHealthProfile, session)

    async def get_or_create_for_user(self, user_id: UUID) -> UserHealthProfile:
        """
        Gets existing health profile or creates a new default one.
        This ensures every user always has a health profile.

        Use case: GET /users/me/profile/health
        """
        # Fix: Query by user_id (FK), not PK
        from sqlalchemy import select
        stmt = select(UserHealthProfile).where(UserHealthProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        profile = result.scalars().first()

        if not profile:
            # Create default profile with defaults
            from app.enums import ActivityLevel, HealthCondition, HealthGoal

            default_data = UserHealthProfileCreateSchema(
                user_id=user_id,
                height_cm=None,
                weight_kg=None,
                activity_level=ActivityLevel.MODERATE,
                curr_condition=HealthCondition.NORMAL,
                health_goal=HealthGoal.MAINTAIN
            )
            profile = UserHealthProfile(**default_data.model_dump())
            self.session.add(profile)
            await self.session.flush()
            await self.session.refresh(profile)
        return profile


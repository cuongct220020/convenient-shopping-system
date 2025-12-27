# user-service/app/repositories/family_group_repository.py
from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import FamilyGroup, GroupMembership, User
from app.enums import GroupRole
from app.schemas.family_group_schema import (
    FamilyGroupCreateSchema, 
    FamilyGroupUpdateSchema,
    GroupMembershipCreateSchema,
    GroupMembershipUpdateSchema
)
from shopping_shared.databases.base_repository import BaseRepository


class FamilyGroupRepository(
    BaseRepository[
        FamilyGroup,
        FamilyGroupCreateSchema,
        FamilyGroupUpdateSchema
    ]
):
    def __init__(self, session: AsyncSession):
        super().__init__(FamilyGroup, session)

    async def get_with_details(self, group_id: UUID) -> Optional[FamilyGroup]:
        """
        Get group with eager loaded members and creator.
        Useful for detailed views where we need to show member lists and the creator.
        """
        stmt = (
            select(FamilyGroup)
            .where(FamilyGroup.id == group_id)
            .options(
                selectinload(FamilyGroup.creator),
                selectinload(FamilyGroup.group_memberships).selectinload(GroupMembership.user)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_groups(self, user_id: UUID) -> Sequence[GroupMembership]:
        """
        Get all groups that a user is a member of with Group info eagerly loaded.
        """
        stmt = (
            select(GroupMembership)
            .where(GroupMembership.user_id == user_id)
            .options(selectinload(GroupMembership.group))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_group(self, data: dict) -> FamilyGroup:
        """
        Creates a new family group from a dictionary.
        Bypasses schema validation for internal fields like created_by_user_id.
        """
        group = FamilyGroup(**data)
        self.session.add(group)
        await self.session.flush()
        await self.session.refresh(group)
        return group
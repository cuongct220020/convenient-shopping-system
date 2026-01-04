# user-service/app/repositories/family_group_repository.py
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import FamilyGroup, GroupMembership
from app.schemas.family_group_schema import (
    FamilyGroupCreateSchema,
    FamilyGroupUpdateSchema,
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

        return await self.get_by_id(
            group_id,
            load_options=[
                selectinload(FamilyGroup.creator),
                selectinload(FamilyGroup.group_memberships).selectinload(GroupMembership.user)
            ]
        )

    async def get_group_with_members_and_info(self, group_id: UUID) -> Optional[Tuple[FamilyGroup, int, list]]:
        """
        Get group with its member count and member IDs in a single optimized query.
        Returns: (group, member_count, list_of_member_user_ids)
        """
        # Get member count in a query
        member_count_stmt = select(func.count(GroupMembership.user_id)).where(GroupMembership.group_id == group_id)
        member_count_result = await self.session.execute(member_count_stmt)
        member_count = member_count_result.scalar()

        # Get member IDs in a separate query
        members_stmt = select(GroupMembership.user_id).where(GroupMembership.group_id == group_id)
        members_result = await self.session.execute(members_stmt)
        member_ids = [row[0] for row in members_result.all()]

        # Get group with creator
        stmt = (
            select(FamilyGroup)
            .where(FamilyGroup.id == group_id)
            .options(selectinload(FamilyGroup.creator))
        )

        result = await self.session.execute(stmt)
        group = result.scalars().first()
        if not group:
            return None

        return group, member_count, member_ids
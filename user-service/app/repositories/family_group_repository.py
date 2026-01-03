# user-service/app/repositories/family_group_repository.py
from typing import Optional
from uuid import UUID
from sqlalchemy import select
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
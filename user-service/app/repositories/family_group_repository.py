# user-service/repositories/family_group_repository.py
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FamilyGroup, GroupMembership
from app.enums import GroupRole
from app.schemas import (
    FamilyGroupCreateSchema, 
    FamilyGroupUpdateSchema,
    # Assuming these are exported from app.schemas.family_group_schema
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


class GroupMembershipRepository(
    BaseRepository[
        GroupMembership,
        GroupMembershipCreateSchema,
        GroupMembershipUpdateSchema
    ]
):
    def __init__(self, session: AsyncSession):
        super().__init__(GroupMembership, session)

    async def get_membership(self, user_id: UUID, group_id: UUID) -> Optional[GroupMembership]:
        """Fetch membership by composite key (user_id, group_id)."""
        return await self.session.get(GroupMembership, (user_id, group_id))

    async def add_membership(self, user_id: UUID, group_id: UUID, role: GroupRole) -> GroupMembership:
        """Adds a user to a group with a specific role."""
        membership = GroupMembership(user_id=user_id, group_id=group_id, role=role)
        self.session.add(membership)
        await self.session.flush()
        return membership

    async def remove_membership(self, user_id: UUID, group_id: UUID) -> None:
        """Removes a user from a group."""
        membership = await self.get_membership(user_id, group_id)
        if membership:
            await self.session.delete(membership)
            await self.session.flush()

    async def update_role(self, user_id: UUID, group_id: UUID, new_role: GroupRole) -> Optional[GroupMembership]:
        """Updates the role of a user in a group."""
        membership = await self.get_membership(user_id, group_id)
        if membership:
            membership.role = new_role
            await self.session.flush()
        return membership
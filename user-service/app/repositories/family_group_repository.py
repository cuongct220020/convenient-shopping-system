# user-service/app/repositories/family_group_repository.py
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import FamilyGroup, GroupMembership
from app.enums import GroupRole
from app.schemas import (
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
        return await self.get_by_id(
            group_id, 
            load_options=[
                selectinload(FamilyGroup.members),
                selectinload(FamilyGroup.creator)
            ]
        )


class GroupMembershipRepository(
    BaseRepository[
        GroupMembership,
        GroupMembershipCreateSchema,
        GroupMembershipUpdateSchema
    ]
):
    """
    Repository for GroupMembership.
    
    Note on Schemas:
    GroupMembershipCreateSchema and GroupMembershipUpdateSchema are required
    for the BaseRepository generic typing and can be used if we switch to 
    using the standard .create() or .update() methods. 
    However, due to the composite primary key nature of this table, 
    custom methods like add_membership and get_membership are often more practical.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(GroupMembership, session)

    async def get_membership(self, user_id: UUID, group_id: UUID) -> Optional[GroupMembership]:
        """Fetch membership by composite key (user_id, group_id)."""
        return await self.session.get(GroupMembership, (user_id, group_id))

    async def add_membership(self, user_id: UUID, group_id: UUID, role: GroupRole) -> GroupMembership:
        """Adds a user to a group with a specific role."""
        # We could use self.create(GroupMembershipCreateSchema(...)) here,
        # but direct model instantiation is also fine and slightly more performant for simple join tables.
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

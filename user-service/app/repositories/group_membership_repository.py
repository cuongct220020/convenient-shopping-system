# user-service/app/repositories/group_membership_repository.py
from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import GroupMembership, User
from app.enums import GroupRole
from app.schemas import (
    GroupMembershipCreateSchema,
    GroupMembershipUpdateSchema
)
from shopping_shared.databases.base_repository import BaseRepository



class GroupMembershipRepository(
    BaseRepository[
        GroupMembership,
        GroupMembershipCreateSchema,
        GroupMembershipUpdateSchema
    ]
):
    """
    Repository for GroupMembership.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(GroupMembership, session)

    async def get_membership(self, user_id: UUID, group_id: UUID) -> Optional[GroupMembership]:
        """Fetch membership by composite key (user_id, group_id)."""
        return await self.session.get(GroupMembership, (user_id, group_id))

    async def get_all_members(self, group_id: UUID) -> Sequence[GroupMembership]:
        """
        Fetch all members of a group with User info eagerly loaded.
        Optimized for List View.
        """
        stmt = (
            select(GroupMembership)
            .where(GroupMembership.group_id == group_id)
            .options(selectinload(GroupMembership.user))  # Load User info to avoid N+1
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_member_detailed(self, group_id: UUID, user_id: UUID) -> Optional[GroupMembership]:
        """
        Fetch a specific member with User info AND Profiles eagerly loaded.
        Optimized for Detail View (Single query for everything).
        """
        stmt = (
            select(GroupMembership)
            .where(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == user_id
            )
            .options(
                selectinload(GroupMembership.user).options(
                    selectinload(User.identity_profile),
                    selectinload(User.health_profile)
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

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

    async def get_members_by_role(self, group_id: UUID, role: GroupRole) -> Sequence[GroupMembership]:
        """Fetch all members of a group with a specific role."""
        stmt = (
            select(GroupMembership)
            .where(
                GroupMembership.group_id == group_id,
                GroupMembership.role == role
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
# user-service/app/repositories/group_membership_repository.py
from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import GroupMembership, User, FamilyGroup
from app.enums import GroupRole
from app.schemas.family_group_schema import GroupMembershipCreateSchema, GroupMembershipUpdateSchema

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


    async def get_user_groups(self, user_id: UUID) -> Sequence[tuple[GroupMembership, int]]:
        """
        Get all groups that a user is a member of.
        Returns a list of tuples: (membership, member_count).
        Optimized to avoid N+1 queries by counting members in the database.
        """
        from sqlalchemy import func

        # Subquery to count members per group
        member_count_subquery = (
            select(func.count(GroupMembership.user_id))
            .where(GroupMembership.group_id == FamilyGroup.id)
            .correlate(FamilyGroup)
            .scalar_subquery()
        )

        stmt = (
            select(GroupMembership, member_count_subquery.label("member_count"))
            .join(GroupMembership.group)
            .where(GroupMembership.user_id == user_id)
            .options(
                selectinload(GroupMembership.group)
                .selectinload(FamilyGroup.creator)
            )
        )
        result = await self.session.execute(stmt)
        # Convert Row objects to explicit tuples to fix type warnings
        return [(row[0], row[1]) for row in result.all()]


    async def get_membership(
        self,
        user_id: UUID,
        group_id: UUID
    ) -> Optional[GroupMembership]:
        """Fetch membership by composite key (user_id, group_id)."""
        return await self.session.get(GroupMembership, (user_id, group_id))

    async def get_all_members(self, group_id: UUID) -> Sequence[GroupMembership]:
        """
        Fetch all members of a group with User info eagerly loaded.
        Optimized for List View.
        """
        return await self.get_many(
            filters={"group_id": group_id},
            load_options=[selectinload(GroupMembership.user)]
        )


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


    async def add_membership(
        self,
        user_id: UUID,
        group_id: UUID,
        role: GroupRole,
        added_by_user_id: Optional[UUID] = None,
        user: Optional[User] = None
    ) -> GroupMembership:
        """Adds a user to a group. Optimized to avoid redundant SELECT if user object is provided."""
        membership = GroupMembership(
            user_id=user_id,
            group_id=group_id,
            role=role,
            added_by_user_id=added_by_user_id
        )
        
        if user:
            # Optimization: Assign the already fetched user object to the relationship
            # This prevents SQLAlchemy from needing to fetch it again later.
            membership.user = user
            
        self.session.add(membership)
        await self.session.flush()

        # If user wasn't provided, we fetch with relation to avoid lazy-load issues later
        if not user:
            stmt = (
                select(GroupMembership)
                .where(
                    GroupMembership.user_id == user_id,
                    GroupMembership.group_id == group_id
                )
                .options(selectinload(GroupMembership.user))
            )
            result = await self.session.execute(stmt)
            return result.scalars().first()
            
        return membership


    async def remove_membership(
            self,
            user_id: UUID,
            group_id: UUID
    ) -> None:
        """Removes a user from a group."""
        membership = await self.get_membership(user_id, group_id)
        if membership:
            await self.session.delete(membership)
            await self.session.flush()


    async def update_role(
        self,
        user_id: UUID,
        group_id: UUID,
        new_role: GroupRole
    ) -> Optional[GroupMembership]:
        """Updates the role of a user in a group."""
        stmt = (
            select(GroupMembership)
            .where(
                GroupMembership.user_id == user_id,
                GroupMembership.group_id == group_id
            )
            .options(selectinload(GroupMembership.user))
        )
        result = await self.session.execute(stmt)
        membership = result.scalars().first()

        if membership:
            membership.role = new_role
            await self.session.flush()
        return membership
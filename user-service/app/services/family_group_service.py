# user-service/app/services/family_group_service.py
from uuid import UUID
from typing import Sequence

from pydantic import EmailStr

from app.models import FamilyGroup, GroupMembership
from app.enums import GroupRole
from app.schemas import (
    FamilyGroupCreateSchema,
    FamilyGroupUpdateSchema
)
from app.repositories.family_group_repository import FamilyGroupRepository, GroupMembershipRepository
from app.repositories.user_repository import UserRepository

from shopping_shared.exceptions import Forbidden, NotFound, Conflict
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("Family Group Service")


class FamilyGroupService:
    def __init__(
        self,
        repo: FamilyGroupRepository,
        member_repo: GroupMembershipRepository,
        user_repo: UserRepository
    ):
        self.repository = repo
        self.member_repo = member_repo
        self.user_repo = user_repo

    # --- Standard CRUD operations ---

    async def get(self, group_id: UUID) -> FamilyGroup:
        """Get a family group by ID."""
        group = await self.repository.get_by_id(group_id)
        if not group:
            raise NotFound(f"Family group with id {group_id} not found")
        return group

    async def get_all(self, page: int = 1, page_size: int = 100):
        """Get paginated list of family groups."""
        return await self.repository.get_paginated(page=page, page_size=page_size)

    async def get_group_members(self, group_id: UUID) -> Sequence[GroupMembership]:
        """
        Get all members of a group with basic User info.
        Used for the 'List View'.
        """
        # Ensure group exists
        await self.get(group_id)
        return await self.member_repo.get_all_members(group_id)

    async def get_group_member_detailed(self, group_id: UUID, user_id: UUID) -> GroupMembership:
        """
        Get a specific member with FULL details (User + Identity + Health).
        Used for the 'Detail View'.
        """
        # Ensure group exists
        await self.get(group_id)
        
        member = await self.member_repo.get_member_detailed(group_id, user_id)
        if not member:
            raise NotFound("Member not found in this group.")
        
        return member

    async def update(self, group_id: UUID, update_data: FamilyGroupUpdateSchema) -> FamilyGroup:
        """Update a family group."""
        group = await self.repository.update(group_id, update_data)
        if not group:
            raise NotFound(f"Family group with id {group_id} not found")
        logger.info(f"Updated family group {group_id}")
        return group

    async def delete(self, group_id: UUID) -> None:
        """Deletes a group (Admin/Internal use)."""
        await self.repository.delete(group_id)

    # --- Business logic methods ---
    async def create_group(self, user_id: UUID, group_data: FamilyGroupCreateSchema) -> FamilyGroup:
        """Creates a new family group, assigns creator, and adds creator as HEAD_CHEF."""
        # 1. Create Group
        data = group_data.model_dump()
        data['created_by_user_id'] = user_id
        group = await self.repository.create(FamilyGroupCreateSchema(**data))

        # 2. Add Creator as HEAD_CHEF member
        await self.member_repo.add_membership(user_id, group.id, GroupRole.HEAD_CHEF)
        
        logger.info(f"Created family group {group.id} with HEAD_CHEF {user_id}")
        return group


    async def delete_group_by_creator(self, user_id: UUID, group_id: UUID) -> None:
        """Deletes a group. Only the creator (Head Chef) can delete."""
        group = await self.get(group_id)
        if str(group.created_by_user_id) != str(user_id):
            raise Forbidden("Only the group creator can delete this group.")

        await self.repository.delete(group_id)
        logger.info(f"Deleted family group {group_id} by user {user_id}")


    async def add_member_by_email(self, requester_id: UUID, group_id: UUID, email: EmailStr) -> GroupMembership:
        """Adds a user to the group by email."""
        # 1. Check permission (Only HEAD_CHEF can add)
        if not await self._is_head_chef(requester_id, group_id):
            raise Forbidden("Only Head Chef can add members.")

        # 2. Find User
        user_to_add = await self.user_repo.get_by_email(str(email))
        if not user_to_add:
            raise NotFound(f"User with email {email} not found.")

        # 3. Check existing membership
        existing = await self.member_repo.get_membership(user_to_add.id, group_id)
        if existing:
            raise Conflict("User is already a member of this group.")

        # 4. Add Member
        membership = await self.member_repo.add_membership(user_to_add.id, group_id, GroupRole.MEMBER)

        logger.info(f"Added user {user_to_add.id} to group {group_id}")
        return membership


    async def remove_member(self, requester_id: UUID, group_id: UUID, target_user_id: UUID) -> None:
        """Removes a member from the group."""
        # Logic:
        # - User can remove themselves.
        # - Head Chef can remove anyone.
        is_self = str(requester_id) == str(target_user_id)
        is_head_chef = await self._is_head_chef(requester_id, group_id)

        if not is_self and not is_head_chef:
            raise Forbidden("You do not have permission to remove this member.")

        existing = await self.member_repo.get_membership(target_user_id, group_id)
        if not existing:
             raise NotFound("Membership not found.")

        await self.member_repo.remove_membership(target_user_id, group_id)
        logger.info(f"Removed user {target_user_id} from group {group_id}")

    async def update_member_role(self, requester_id: UUID, group_id: UUID, target_user_id: UUID, new_role: GroupRole) -> GroupMembership:
        """Updates a member's role."""
        if not await self._is_head_chef(requester_id, group_id):
            raise Forbidden("Only Head Chef can update roles.")

        membership = await self.member_repo.update_role(target_user_id, group_id, new_role)
        if not membership:
            raise NotFound("Membership not found.")

        logger.info(f"Updated role for user {target_user_id} in group {group_id} to {new_role}")
        return membership

    async def _is_head_chef(self, user_id: UUID, group_id: UUID) -> bool:
        """Helper to check if user is HEAD_CHEF of the group."""
        membership = await self.member_repo.get_membership(user_id, group_id)
        return membership and membership.role == GroupRole.HEAD_CHEF
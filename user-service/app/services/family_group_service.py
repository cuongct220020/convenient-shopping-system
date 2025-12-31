# user-service/app/services/family_group_service.py
from uuid import UUID
from typing import Sequence

from app.models import FamilyGroup, GroupMembership, User
from app.enums import GroupRole
from app.schemas.family_group_schema import (
    FamilyGroupCreateSchema,
    FamilyGroupUpdateSchema
)
from app.repositories.family_group_repository import FamilyGroupRepository
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.repositories.user_repository import UserRepository
from app.services.kafka_service import kafka_service

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


    async def get_group_with_members(self, group_id: UUID) -> FamilyGroup:
        """
        Get a group with its members and creator info loaded.
        """
        group = await self.repository.get_with_details(group_id)
        if not group:
            raise NotFound(f"Family group with id {group_id} not found")
        return group


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
        updated = await self.repository.update(group_id, update_data)
        if not updated:
            raise NotFound(f"Family group with id {group_id} not found")
        
        # Fetch fresh data with relationships loaded
        group = await self.repository.get_with_details(group_id)
        
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
        # Use repository.create_group which accepts dict and bypasses schema validation
        group = await self.repository.create_group(data)

        # 2. Add Creator as HEAD_CHEF member (creator adds themselves)
        await self.member_repo.add_membership(user_id, group.id, GroupRole.HEAD_CHEF, user_id)
        
        # 3. Fetch full group details for response
        full_group = await self.repository.get_with_details(group.id)
        
        logger.info(f"Created family group {group.id} with HEAD_CHEF {user_id}")
        return full_group


    async def delete_group_by_creator(self, user_id: UUID, group_id: UUID) -> None:
        """Deletes a group. Only the creator (Head Chef) can delete."""
        group = await self.get(group_id)
        if str(group.created_by_user_id) != str(user_id):
            raise Forbidden("Only the group creator can delete this group.")

        await self.repository.delete(group_id)
        logger.info(f"Deleted family group {group_id} by user {user_id}")


    async def add_member_by_identifier(
        self,
        requester_id: UUID,
        requester_username: str,
        group_id: UUID,
        user_to_add: User
    ) -> GroupMembership:
        """Adds a user to the group by email or username"""

        # 1. Check permission (Only HEAD_CHEF can add)
        if not await self._is_head_chef(requester_id, group_id): # Add 'await' here
            raise Forbidden("Only Head Chef can add members.")

        # 2. Check existing membership
        existing = await self.member_repo.get_membership(user_to_add.id, group_id)
        if existing:
            raise Conflict("User is already a member of this group.")

        # 3. Get group name and group membership ids *before* adding the member
        group = await self.get(group_id) # Fetch group to get its name
        group_members = await self.member_repo.get_all_members(group_id) # Fetch members before adding
        group_name = group.group_name
        group_members_ids = [member.user_id for member in group_members]
        user_to_add_identifier = user_to_add.email if user_to_add.email else user_to_add.username

        # 4. Publish message to kafka topics
        await kafka_service.publish_add_user_group_message(
            requester_id=requester_id,
            requester_username=requester_username,
            group_id=group_id,
            group_name=group_name,
            user_to_add_id=user_to_add.id,
            user_to_add_identifier=user_to_add_identifier,
            group_members_ids=group_members_ids
        )

        # 5. Add Member (requester adds target user)
        logger.info(f"Added user {user_to_add.id} to group {group_id}")
        membership = await self.member_repo.add_membership(user_to_add.id, group_id, GroupRole.MEMBER, requester_id)

        return membership


    async def remove_member(
        self,
        requester_id: UUID,
        requester_username: str,
        group_id: UUID,
        target_user_id: UUID
    ):
        """Removes a member from the group."""
        # Logic:
        # - User can remove themselves.
        # - Head Chef can remove anyone.
        is_self = str(requester_id) == str(target_user_id)

        if not is_self and not await self._is_head_chef(requester_id, group_id):
            raise Forbidden("You do not have permission to remove this member.")

        # Fetch the existing member details to get their identifier
        existing_member = await self.get_group_member_detailed(group_id, target_user_id)
        # Access the user's email/username from the fetched member object
        target_user_identifier = existing_member.user.email if existing_member.user.email else existing_member.user.username

        if not existing_member:
             raise NotFound("Membership not found.")

        # Fetch group name BEFORE removing the member to ensure group still exists
        group = await self.get(group_id)
        group_name = group.group_name

        await self.member_repo.remove_membership(target_user_id, group_id)
        logger.info(f"Removed user {target_user_id} from group {group_id}")

        await kafka_service.publish_remove_user_group_message(
            requester_id=str(requester_id),
            requester_username=str(requester_username),
            group_id=str(group_id),
            group_name=str(group_name),
            user_to_remove_id=str(target_user_id),
            user_to_remove_identifier = str(target_user_identifier)
        )


    async def update_member_role(
        self,
        requester_id: UUID,
        requester_username: str,
        requester_email: str,
        group_id: UUID,
        target_user_id: UUID,
        new_role: GroupRole
    ) -> GroupMembership:
        """Updates a member's role."""
        if not await self._is_head_chef(requester_id, group_id):
            raise Forbidden("Only Head Chef can update roles.")

        group = await self.get(group_id)
        group_name = group.group_name

        # Check if the target user is actually a member of the group
        existing_membership = await self.get_group_member_detailed(group_id, target_user_id)
        if not existing_membership:
            raise NotFound("Membership not found.")

        membership = await self.member_repo.update_role(target_user_id, group_id, new_role)
        if not membership:
            raise NotFound("Failed to update membership role.")

        logger.info(f"Updated role for user {target_user_id} in group {group_id} to {new_role}")


        if new_role == GroupRole.HEAD_CHEF:
            # Access the user's email/username from the fetched membership object
            target_user_identifier = existing_membership.user.username if existing_membership.user.username else existing_membership.user.email

            await kafka_service.publish_update_headchef_group_message(
                requester_id=str(requester_id),
                requester_username=str(requester_username),
                group_id=str(group_id),
                group_name=str(group_name),
                old_head_chef_id=str(requester_id),
                old_head_chef_identifier=str(requester_username) if requester_username else requester_email,
                new_head_chef_id=str(target_user_id),
                new_head_chef_identifier=target_user_identifier
            )

        return membership


    async def get_user_groups(self, user_id: UUID) -> Sequence[GroupMembership]:
        """
        Get all groups that a user is a member of.
        """
        return await self.member_repo.get_user_groups(user_id)


    async def leave_group(
        self,
        user_id: UUID,
        user_name: str,
        user_email: str,
        group_id: UUID
    ):
        """Allow a member to leave a group."""
        membership = await self.member_repo.get_membership(user_id=user_id, group_id=group_id)

        if not membership:
            raise NotFound("You are not a member of this group")

        # Get all members in the group to check if this is the last member
        all_members = await self.member_repo.get_all_members(group_id)

        # If user is HEAD_CHEF and there are other members, they cannot leave
        if membership.role == GroupRole.HEAD_CHEF and len(all_members) > 1:
            raise Forbidden("HEAD_CHEF cannot leave group while other members exist. Please transfer ownership or remove other members first.")

        # If this is the last member (regardless of role), allow them to leave (equivalent to deleting the group)
        if len(all_members) <= 1:
            await self.member_repo.remove_membership(user_id=user_id, group_id=group_id)
            logger.info(f"User {user_id} left group {group_id} (last member, group effectively deleted)")

            # Publish user leave group events
            group = await self.get(group_id) # Fetch group name after removal might still work if group exists until last member leaves
            await kafka_service.publish_user_leave_group_message(
                user_id=user_id,
                user_identifier=user_name if user_name else user_email,
                group_id=group_id,
                group_name=group.group_name
            )
            return

        # Regular member (or HEAD_CHEF as the last member) can leave
        await self.member_repo.remove_membership(user_id=user_id, group_id=group_id)
        logger.info(f"User {user_id} left group {group_id}")

        # Publish user leave group events
        group = await self.get(group_id)
        await kafka_service.publish_user_leave_group_message(
            user_id=user_id,
            user_identifier=user_name if user_name else user_email,
            group_id=group_id,
            group_name=group.group_name
        )


    async def _is_head_chef(self, user_id: UUID, group_id: UUID) -> bool:
        """Helper to check if user is HEAD_CHEF of the group."""
        membership = await self.member_repo.get_membership(user_id, group_id)
        return membership and membership.role == GroupRole.HEAD_CHEF
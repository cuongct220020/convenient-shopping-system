# user-service/app/services/family_group_service.py
from datetime import datetime, UTC
from uuid import UUID
from typing import Sequence, Tuple

from app.models import FamilyGroup, GroupMembership
from app.enums import GroupRole
from app.repositories.user_repository import UserRepository
from app.schemas.family_group_schema import FamilyGroupCreateSchema, FamilyGroupUpdateSchema
from app.repositories.family_group_repository import FamilyGroupRepository
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.services.kafka_service import kafka_service
from app.services.redis_service import redis_service
from shopping_shared.caching.redis_keys import RedisKeys

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


    async def get_group_with_members(self, group_id: UUID) -> FamilyGroup:
        """
        Get a group with its members and creator info loaded.
        """
        group = await self.repository.get_with_details(group_id)
        if not group:
            raise NotFound(f"Family group with id {group_id} not found")
        return group


    async def get_user_groups(self, user_id: UUID) -> Sequence[tuple[GroupMembership, int]]:
        """
        Get all groups that a user is a member of.
        Returns: List of (membership, member_count)
        """
        return await self.member_repo.get_user_groups(user_id)


    async def create_group_by_user(
        self,
        user_id: UUID,
        group_data: FamilyGroupCreateSchema
    ) -> FamilyGroup:
        """Creates a new family group, assigns creator, and adds creator as HEAD_CHEF."""

        # 1. Create Group using BaseRepository's create
        # Note: created_by_user_id is set manually as it's likely not in the schema
        group = await self.repository.create(group_data)
        
        group.created_by_user_id = user_id
        group.created_at = datetime.now(UTC)
        await self.repository.session.flush()

        # 2. Add Creator as HEAD_CHEF member (creator adds themselves)
        await self.member_repo.add_membership(
            user_id=user_id,
            group_id=group.id,
            role=GroupRole.HEAD_CHEF,
            added_by_user_id=user_id
        )
        
        # 3. Fetch full group details for response
        full_group = await self.repository.get_with_details(group.id)
        
        logger.info(f"Created family group {group.id} with HEAD_CHEF {user_id}")

        # 4. Invalidate user's group list cache
        await redis_service.delete_pattern(RedisKeys.user_groups_list_key(user_id=str(user_id)))

        return full_group


    async def update_group_info_by_head_chef(
        self,
        user_id: UUID,
        group_id: UUID,
        validated_data: FamilyGroupUpdateSchema
    ) -> FamilyGroup:
        """Updates group details. Only HEAD_CHEF can update."""
        
        # 1. Check permission
        if not await self._is_head_chef(user_id, group_id):
            raise Forbidden("Only Head Chef can update group details.")

        # 2. Update group
        updated_group = await self.repository.update(group_id, validated_data)
        
        if not updated_group:
            raise NotFound(f"Group with id {group_id} not found")

        # Invalidate cache
        await redis_service.delete_pattern(RedisKeys.group_detail_key(str(group_id)))

        # 3. Return full details
        return await self.repository.get_with_details(group_id)


    async def delete_group_by_head_chef(self, user_id: UUID, group_id: UUID) -> None:
        """Deletes a group. Only the creator (Head Chef) can delete."""
        if not await self._is_head_chef(user_id, group_id):
            raise Forbidden("Only the head_chef can delete this group.")

        await self.repository.delete(group_id)
        
        # Invalidate cache
        await redis_service.delete_pattern(RedisKeys.group_detail_key(str(group_id)))
        await redis_service.delete_pattern(RedisKeys.user_groups_list_key(user_id=str(user_id)))
        
        logger.info(f"Deleted family group {group_id} by user {user_id}")


    async def add_member_by_identifier(
        self,
        requester_id: UUID,
        requester_username: str,
        group_id: UUID,
        user_to_add_identifier: str
    ) -> GroupMembership:
        """Adds a user to the group by email or username"""

        # Find the target user by identifier (email or username)
        target_user = await self.user_repo.get_by_identifier(user_to_add_identifier)

        if not target_user:
            raise NotFound(f"User with identifier '{user_to_add_identifier}' not found")

        # 1. Check permission (Only HEAD_CHEF can add)
        if not await self._is_head_chef(requester_id, group_id): # Add 'await' here
            raise Forbidden("Only Head Chef can add members.")

        # 2. Check existing membership
        existing = await self.member_repo.get_membership(target_user.id, group_id)
        if existing:
            raise Conflict("User is already a member of this group.")

        # 3. Get group name and group membership ids before adding the member
        # OPTIMIZED: Use single query to get group info and member IDs
        group_result = await self.repository.get_group_with_members_and_info(group_id)
        if not group_result:
            raise NotFound(f"Group with id {group_id} not found")

        group, member_count, group_members_ids = group_result
        group_name = group.group_name
        user_to_add_identifier = self._get_user_identifier(target_user)

        # 4. Publish message to kafka topics
        await kafka_service.publish_add_user_group_message(
            requester_id=requester_id,
            requester_username=requester_username,
            group_id=group_id,
            group_name=group_name,
            user_to_add_id=target_user.id,
            user_to_add_identifier=user_to_add_identifier,
            group_members_ids=group_members_ids
        )

        # 5. Add Member (requester adds target user)
        logger.info(f"Added user {target_user.id} to group {group_id}")
        membership = await self.member_repo.add_membership(target_user.id, group_id, GroupRole.MEMBER, requester_id)

        # Invalidate cache
        await redis_service.delete_key(RedisKeys.user_groups_list_key(user_id=str(target_user.id)))
        await redis_service.delete_key(RedisKeys.group_detail_key(str(group_id)))
        await redis_service.delete_key(RedisKeys.group_members_list_key(str(group_id)))

        return membership


    async def remove_member_by_head_chef(
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

        # OPTIMIZED: Use single query to get both group and member details
        result = await self.member_repo.get_group_with_member_and_info(group_id, target_user_id)
        if not result:
            raise NotFound("Membership not found.")

        group, existing_member, member_count, member_ids = result
        # Access the user's email/username from the fetched member object
        target_user_identifier = self._get_user_identifier(existing_member.user)
        group_name = group.group_name

        await self.member_repo.remove_membership(target_user_id, group_id)
        logger.info(f"Removed user {target_user_id} from group {group_id}")

        # Invalidate cache
        await redis_service.delete_key(RedisKeys.user_groups_list_key(user_id=str(target_user_id)))
        await redis_service.delete_key(RedisKeys.group_detail_key(str(group_id)))
        await redis_service.delete_key(RedisKeys.group_members_list_key(str(group_id)))

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

        # OPTIMIZED: Use single query to get both group and member details
        result = await self.member_repo.get_group_with_member_and_info(group_id, target_user_id)
        if not result:
            raise NotFound("Membership not found.")

        group, existing_membership, member_count, member_ids = result
        group_name = group.group_name

        membership = await self.member_repo.update_role(target_user_id, group_id, new_role)
        if not membership:
            raise NotFound("Failed to update membership role.")

        logger.info(f"Updated role for user {target_user_id} in group {group_id} to {new_role}")

        # Invalidate cache
        await redis_service.delete_key(RedisKeys.group_detail_key(str(group_id)))
        await redis_service.delete_key(RedisKeys.user_groups_list_key(user_id=str(target_user_id)))
        await redis_service.delete_key(RedisKeys.group_members_list_key(str(group_id)))


        if new_role == GroupRole.HEAD_CHEF:
            # Access the user's email/username from the fetched membership object
            target_user_identifier = self._get_user_identifier(existing_membership.user)

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

        # OPTIMIZED: Use single query to get group info and all members
        group_result = await self.repository.get_group_with_members_and_info(group_id)
        if not group_result:
            raise NotFound(f"Group with id {group_id} not found")

        group, member_count, member_ids = group_result
        group_name = group.group_name

        # Get all members with user info in a single query
        all_members = await self.member_repo.get_all_members(group_id)

        # Regular member (or HEAD_CHEF as the last member) can leave
        # If user is HEAD_CHEF and there are other members, they cannot leave
        if membership.role == GroupRole.HEAD_CHEF and len(all_members) > 1:
            new_head_chef = min(
                (m for m in all_members if m.user_id != user_id),
                key=lambda m: m.jointed_at
            )

            await self.member_repo.update_role(
                user_id=new_head_chef.user_id,
                group_id=group_id,
                new_role=GroupRole.HEAD_CHEF
            )

            logger.info(f"Transferred HEAD_CHEF from {user_id} to {new_head_chef.user_id}")

            await kafka_service.publish_update_headchef_group_message(
                requester_id=str(user_id),
                requester_username=str(user_name),
                group_id=str(group_id),
                group_name=str(group_name),
                old_head_chef_id=str(user_id),
                old_head_chef_identifier=str(user_name),
                new_head_chef_id=str(new_head_chef.user_id),
                new_head_chef_identifier=self._get_user_identifier(new_head_chef.user)
            )

        if len(all_members) <= 1:
            await self.member_repo.remove_membership(user_id=user_id, group_id=group_id)
            logger.info(f"User {user_id} left group {group_id} (last member, group effectively deleted)")

            # Publish user leave group events
            await kafka_service.publish_user_leave_group_message(
                user_id=user_id,
                user_identifier=user_name if user_name else user_email,
                group_id=group_id,
                group_name=group_name
            )
            return

        await self.member_repo.remove_membership(user_id=user_id, group_id=group_id)
        logger.info(f"User {user_id} left group {group_id}")

        # Invalidate cache
        await redis_service.delete_key(RedisKeys.user_groups_list_key(user_id=str(user_id)))
        await redis_service.delete_key(RedisKeys.group_detail_key(str(group_id)))
        await redis_service.delete_key(RedisKeys.group_members_list_key(str(group_id)))

        # Publish user leave group events
        await kafka_service.publish_user_leave_group_message(
            user_id=user_id,
            user_identifier=user_name if user_name else user_email,
            group_id=group_id,
            group_name=group_name
        )

    async def check_group_access(
        self,
        user_id: UUID,
        group_id: UUID,
        check_head_chef: bool
    ) -> Tuple[bool, bool]:

        is_group_membership = await self._is_group_membership(user_id=user_id, group_id=group_id)
        if check_head_chef:
            is_head_chef = await self._is_head_chef(user_id=user_id, group_id=group_id)

            return is_group_membership, is_head_chef

        return is_group_membership, False


    @staticmethod
    def _get_user_identifier(user) -> str:
        """Helper to get user identifier (username or email) for Kafka events."""
        return user.username if user.username else user.email

    async def _is_head_chef(self, user_id: UUID, group_id: UUID) -> bool:
        """Helper to check if user is HEAD_CHEF of the group."""
        membership = await self.member_repo.get_membership(user_id, group_id)
        return membership and membership.role == GroupRole.HEAD_CHEF

    async def _is_group_membership(self, user_id: UUID, group_id: UUID) -> bool:
        """Helper to check if user is member of the group."""
        membership = await self.member_repo.get_membership(user_id, group_id)
        return True if membership is not None else False
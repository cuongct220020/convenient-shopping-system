# user-service/app/views/groups/group_members_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi

from app.decorators import validate_request, require_group_role
from app.views.groups.base_group_view import BaseGroupView
from app.enums import GroupRole
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.repositories.user_repository import UserRepository
from app.schemas.family_group_schema import (
    AddMemberRequestSchema,
    GroupMembershipUpdateSchema,
    GroupMembershipSchema,
    FamilyGroupDetailedSchema
)

from shopping_shared.exceptions import NotFound, Forbidden
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Group Members View")


class GroupMembersView(BaseGroupView):
    """Handles operations on group members."""

    decorators = [
        require_group_role(GroupRole.HEAD_CHEF),  # Only HEAD_CHEF can manage members
        openapi.tag("Group Members"),
        openapi.secured("bearerAuth")
    ]

    @openapi.summary("List group members")
    @openapi.description("Lists all members of a specific family group.")
    @openapi.response(200, FamilyGroupDetailedSchema)
    async def get(self, request: Request, group_id: UUID):
        """List all members of a specific family group."""
        membership_repo = GroupMembershipRepository(session=request.ctx.db_session)

        try:
            members = await membership_repo.get_all_members(group_id)



            return self.success_response(
                data=None,
                message="Group members listed successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Error listing group members", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to list group members",
                status_code=500
            )

    @openapi.summary("Add a member to group")
    @openapi.description("Adds a user to a specific family group.")
    @openapi.body(AddMemberRequestSchema)
    @openapi.response(201, GroupMembershipSchema)
    @validate_request(AddMemberRequestSchema)
    async def post(self, request: Request, group_id: UUID):
        """Add a member to a specific family group."""
        validated_data = request.ctx.validated_data
        membership_repo = GroupMembershipRepository(session=request.ctx.db_session)
        user_repo = UserRepository(session=request.ctx.db_session)

        try:
            # Verify the user exists
            user = await user_repo.get_by_id(validated_data.user_id)
            if not user:
                raise NotFound("User not found")

            # Add member to group
            membership = await membership_repo.add_membership(
                group_id=group_id,
                user_id=validated_data.user_id,
                role=validated_data.role
            )

            # Use helper method from base class
            return self.success_response(
                data=GroupMembershipSchema.model_validate(membership),
                message="Member added successfully",
                status_code=201
            )
        except Exception as e:
            logger.error("Error adding membership", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to add member",
                status_code=500
            )


class GroupMemberDetailView(BaseGroupView):
    """Handles operations on a specific group member."""

    decorators = [
        require_group_role(GroupRole.HEAD_CHEF),  # Only HEAD_CHEF can manage specific members
        openapi.tag("Group Members"),
        openapi.secured("bearerAuth")
    ]

    @openapi.summary("Update member role")
    @openapi.description("Updates the role of a specific member in a family group.")
    @openapi.body(GroupMembershipUpdateSchema)
    @openapi.response(200, GroupMembershipSchema)
    @validate_request(GroupMembershipUpdateSchema)
    async def patch(self, request: Request, group_id: UUID, user_id: UUID):
        """Update the role of a specific member in a family group."""
        validated_data = request.ctx.validated_data
        membership_repo = GroupMembershipRepository(session=request.ctx.db_session)

        try:
            membership = await membership_repo.update_role(
                group_id=group_id,
                user_id=user_id,
                new_role=validated_data.role
            )

            # Use helper method from base class
            return self.success_response(
                data=GroupMembershipSchema.model_validate(membership),
                message="Member role updated successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Error updating membership", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to update member role",
                status_code=500
            )

    @openapi.summary("Remove member from group")
    @openapi.description("Removes a specific member from a family group.")
    @openapi.response(200, GenericResponse)
    async def delete(self, request: Request, group_id: UUID, user_id: UUID):
        """Remove a specific member from a family group."""
        membership_repo = GroupMembershipRepository(session=request.ctx.db_session)

        try:
            await membership_repo.remove_membership(
                group_id=group_id,
                user_id=user_id
            )

        # Use helper method from base class
            return self.success_response(
                message="Member removed successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Error removing membership", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to remove member",
                status_code=500
            )


class GroupMemberMeView(BaseGroupView):
    """Handles operations for the authenticated user in their groups."""

    decorators = [
        require_group_role(),  # Any group member can access these endpoints
        openapi.tag("Group Members"),
        openapi.secured("bearerAuth")
    ]

    @openapi.summary("Leave a group")
    @openapi.description("Allows a member to leave a specific family group.")
    @openapi.response(200, GenericResponse)
    async def delete(self, request: Request, group_id: UUID):
        """Allow a member to leave a specific family group."""
        user_id = request.ctx.auth_payload["sub"]
        membership_repo = GroupMembershipRepository(session=request.ctx.db_session)

        try:
            # Check if user is HEAD_CHEF and prevent leaving if they are the only one
            membership = await membership_repo.get_membership(group_id, user_id)
            if membership.role == GroupRole.HEAD_CHEF:
                # Check if there are other HEAD_CHEF members
                head_chefs = await membership_repo.get_members_by_role(group_id, GroupRole.HEAD_CHEF)
                if len(head_chefs) <= 1:
                    raise Forbidden("HEAD_CHEF cannot leave group if they are the only HEAD_CHEF")

            await membership_repo.remove_membership(group_id, user_id)

            # Use helper method from base class
            return self.success_response(
                message="Successfully left the group",
                status_code=200
            )
        except Exception as e:
            logger.error("Error removing membership", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to leave group",
                status_code=500
            )
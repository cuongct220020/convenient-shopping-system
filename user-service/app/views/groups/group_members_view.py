# user-service/app/views/groups/group_members_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request, require_group_role
from app.views.groups.base_group_view import BaseGroupView
from app.enums import GroupRole
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.schemas.family_group_schema import (
    AddMemberRequestSchema,
    GroupMembershipUpdateSchema,
    GroupMembershipSchema,
    FamilyGroupDetailedSchema
)

from shopping_shared.exceptions import NotFound, Forbidden
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

logger = get_logger("Group Members View")


class GroupMembersView(BaseGroupView):
    """Handles operations on group members."""

    @openapi.definition(
        summary="List all group members",
        description="List all members of a specific family group.",
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse[FamilyGroupDetailedSchema]),
                status=200,
                description="Group members listed successfully"
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=500,
                description="Internal Server Error"
            )
        ]
    )
    @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
    async def get(self, request: Request, group_id: UUID):
        """List all members of a specific family group."""
        service = self._get_service(request)

        try:
            # Get the group with its members using the service method
            group = await service.get_group_with_members(group_id)

            # Validate the group data to create FamilyGroupDetailedSchema
            # This will include the members through the group_memberships relationship
            group_detailed = FamilyGroupDetailedSchema.model_validate(group)

            return self.success_response(
                data=group_detailed,
                message="Group members listed successfully",
                status_code=200
            )
        except NotFound:
            logger.error(f"Group with id {group_id} not found")
            return self.error_response(
                message="Group not found",
                status_code=404
            )
        except Exception as e:
            logger.error("Error listing group members", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to list group members",
                status_code=500
            )


    @openapi.definition(
        summary="Add a member to group",
        description="Adds a user to a specific family group. Only HEAD_CHEF can add members.",
        body=get_openapi_body(AddMemberRequestSchema),
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GroupMembershipSchema),
                status=201,
                description="Member added successfully"
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=403,
                description="Forbidden - Only HEAD_CHEF can add members"
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=404,
                description="User not found"
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=500,
                description="Internal Server Error"
            )
        ]
    )
    @validate_request(AddMemberRequestSchema)
    @require_group_role(GroupRole.HEAD_CHEF)  # Only HEAD_CHEF can add members to the group
    async def post(self, request: Request, group_id: UUID):
        """Add a member to a specific family group."""
        requester_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data
        identifier = validated_data.identifier

        service = self._get_service(request)

        try:
            # Find the target user by identifier (email or username)
            # First, try to find by email
            target_user = await service.user_repo.get_by_email(identifier)

            # If not found by email, try to find by username
            if not target_user:
                target_user = await service.user_repo.get_by_username(identifier)

            if not target_user:
                raise NotFound(f"User with identifier '{identifier}' not found")

            # Use the service method to add member by email (which internally handles the permission logic)
            membership = await service.add_member_by_email(
                requester_id=requester_id,
                group_id=group_id,
                email=target_user.email  # Use the email from the found user
            )

            # Use helper method from base class
            return self.success_response(
                data=GroupMembershipSchema.model_validate(membership),
                message="Member added successfully",
                status_code=201
            )
        except NotFound as e:
            logger.error(f"User not found: {identifier}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=404
            )
        except Forbidden as e:
            logger.error(f"Permission denied adding member: {identifier}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=403
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

    @openapi.definition(
        summary="Update member role",
        description="Updates the role of a specific member in a family group.",
        body=get_openapi_body(GroupMembershipUpdateSchema),
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GroupMembershipSchema),
                status=200,
                description="Member role updated successfully"
            )
        ]
    )
    @validate_request(GroupMembershipUpdateSchema)
    @require_group_role(GroupRole.HEAD_CHEF)
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


    @openapi.definition(
        summary="Remove member from group",
        description="Removes a member from a specific family group.",
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse),
                status=200,
                description="Member role removed successfully"
            )
        ]
    )
    @require_group_role(GroupRole.HEAD_CHEF)
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

    @openapi.definition(
        summary="Leave a group member",
        description="Allows a member to leave a specific family group.",
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse),
                status=200,
                description="Group member leave successfully"
            )
        ]
    )
    @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
    async def delete(self, request: Request, group_id: UUID):
        """Allow a member to leave a specific family group."""
        user_id = request.ctx.auth_payload["sub"]
        membership_repo = GroupMembershipRepository(session=request.ctx.db_session)

        try:
            # Check if user is HEAD_CHEF and prevent leaving if they are the only one
            membership = await membership_repo.get_membership(user_id=user_id, group_id=group_id)
            
            if not membership:
                raise NotFound("You are not a member of this group")

            if membership.role == GroupRole.HEAD_CHEF:
                # Check if there are other HEAD_CHEF members
                head_chefs = await membership_repo.get_members_by_role(group_id, GroupRole.HEAD_CHEF)
                if len(head_chefs) <= 1:
                    raise Forbidden("HEAD_CHEF cannot leave group if they are the only HEAD_CHEF. Please transfer ownership first.")

            await membership_repo.remove_membership(user_id=user_id, group_id=group_id)

            # Use helper method from base class
            return self.success_response(
                message="Successfully left the group",
                status_code=200
            )
        except (Forbidden, NotFound) as e:
            return self.error_response(
                message=str(e),
                status_code=e.status_code
            )
        except Exception as e:
            logger.error("Error removing membership", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to leave group",
                status_code=500
            )
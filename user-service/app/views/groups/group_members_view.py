# user-service/app/views/groups/group_members_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request, require_group_role
from app.views.groups.base_group_view import BaseGroupView
from app.enums import GroupRole
from app.schemas.family_group_schema import (
    AddMemberRequestSchema,
    GroupMembershipUpdateSchema,
    GroupMembershipSchema,
    FamilyGroupDetailedSchema
)

from shopping_shared.exceptions import NotFound, Forbidden, Conflict
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

logger = get_logger("Group Members View")


class GroupMembersView(BaseGroupView):
    """Handles operations on group members."""

    @openapi.definition(
        summary="List all members in a family group",
        description="Retrieves a list of all members in a specific family group, including their roles, profile information, and membership details.",
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse[FamilyGroupDetailedSchema]),
                status=200,
                description="Successfully retrieved the list of members in the specified family group."
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=500,
                description="Internal Server Error occurred while retrieving group members."
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
        summary="Add a member to a family group",
        description="Adds an existing user to a specific family group. Only the HEAD_CHEF (group administrator) has permission to add new members to the group.",
        body=get_openapi_body(AddMemberRequestSchema),
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GroupMembershipSchema),
                status=201,
                description="Successfully added the member to the family group."
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=403,
                description="Forbidden - Only HEAD_CHEF can add members to the group."
            )
        ]
    )
    @validate_request(AddMemberRequestSchema)
    @require_group_role(GroupRole.HEAD_CHEF)  # Only HEAD_CHEF can add members to the group
    async def post(self, request: Request, group_id: UUID):
        """Add a member to a specific family group."""
        requester_id = request.ctx.auth_payload["sub"]
        requester_username = request.ctx.auth_payload["username"]
        validated_data = request.ctx.validated_data
        user_to_add_identifier = validated_data.identifier

        service = self._get_service(request)

        try:
            # Use the service method to add member by email (which internally handles the permission logic)
            membership = await service.add_member_by_identifier(
                requester_id=requester_id,
                requester_username=requester_username,
                group_id=group_id,
                user_to_add_identifier=user_to_add_identifier
            )

            # Use helper method from base class
            return self.success_response(
                data=GroupMembershipSchema.model_validate(membership),
                message="Member added successfully",
                status_code=201
            )
        except NotFound as e:
            logger.error(f"User not found: {user_to_add_identifier}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=404
            )
        except Forbidden as e:
            logger.error(f"Permission denied adding member: {user_to_add_identifier}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=403
            )
        except Conflict as e:
            logger.warning(f"Conflict when adding member: {user_to_add_identifier}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=409
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
        summary="Update a member's role in a family group",
        description="Updates the role of a specific member in a family group. Only the HEAD_CHEF (group administrator) can modify member roles within the group.",
        body=get_openapi_body(GroupMembershipUpdateSchema),
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GroupMembershipSchema),
                status=200,
                description="Successfully updated the member's role in the family group."
            )
        ]
    )
    @validate_request(GroupMembershipUpdateSchema)
    @require_group_role(GroupRole.HEAD_CHEF)
    async def patch(self, request: Request, group_id: UUID, user_id: UUID):
        """Update the role of a specific member in a family group."""
        validated_data = request.ctx.validated_data
        requester_id = request.ctx.auth_payload["sub"]
        requester_username = request.ctx.auth_payload["username"]
        requester_email = request.ctx.auth_payload["email"]
        service = self._get_service(request)

        try:
            membership = await service.update_member_role(
                requester_id=requester_id,
                requester_username=requester_username,
                requester_email=requester_email,
                group_id=group_id,
                target_user_id=user_id,
                new_role=validated_data.role
            )

            # Use helper method from base class
            return self.success_response(
                data=GroupMembershipSchema.model_validate(membership),
                message="Member role updated successfully",
                status_code=200
            )
        except NotFound as e:
            logger.error(f"Membership not found: group_id={group_id}, user_id={user_id}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=404
            )
        except Forbidden as e:
            logger.error(f"Permission denied updating role: group_id={group_id}, user_id={user_id}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=403
            )
        except Exception as e:
            logger.error("Error updating membership", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to update member role",
                status_code=500
            )


    @openapi.definition(
        summary="Remove a member from a family group",
        description="Removes a specific member from a family group. Only the HEAD_CHEF (group administrator) can remove members from the group.",
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse),
                status=200,
                description="Successfully removed the member from the family group."
            )
        ]
    )
    @require_group_role(GroupRole.HEAD_CHEF)
    async def delete(self, request: Request, group_id: UUID, user_id: UUID):
        """Remove a specific member from a family group."""
        requester_id = request.ctx.auth_payload["sub"]
        requester_username = request.ctx.auth_payload["username"]
        service = self._get_service(request)

        try:
            await service.remove_member_by_head_chef(
                requester_id=requester_id,
                requester_username=requester_username,
                group_id=group_id,
                target_user_id=user_id
            )

            # Use helper method from base class
            return self.success_response(
                message="Member removed successfully",
                status_code=200
            )
        except NotFound as e:
            logger.error(f"Membership not found: group_id={group_id}, user_id={user_id}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=404
            )
        except Forbidden as e:
            logger.error(f"Permission denied removing member: group_id={group_id}, user_id={user_id}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=403
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
        summary="Leave a family group",
        description="Allows a member to voluntarily leave a specific family group. HEAD_CHEF members cannot leave if they are the only administrator of the group.",
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse),
                status=200,
                description="Successfully left the family group."
            )
        ]
    )
    @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
    async def delete(self, request: Request, group_id: UUID):
        """Allow a member to leave a specific family group."""
        user_id = request.ctx.auth_payload["sub"]
        user_name = request.ctx.auth_payload["username"]
        user_email = request.ctx.auth_payload["email"]
        service = self._get_service(request)

        try:
            await service.leave_group(
                user_id=user_id,
                user_name=user_name,
                user_email=user_email,
                group_id=group_id
            )

            # Use helper method from base class
            return self.success_response(
                message="Successfully left the group",
                status_code=200
            )
        except NotFound as e:
            logger.error(f"User {user_id} is not a member of group {group_id}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=404
            )
        except Forbidden as e:
            logger.error(f"User {user_id} cannot leave group {group_id}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=403
            )
        except Exception as e:
            logger.error("Error leaving group", exc_info=e)
            return self.error_response(
                message="Failed to leave group",
                status_code=500
            )

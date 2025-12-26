# user-service/app/views/groups/group_management_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi

from app.enums import GroupRole
from shopping_shared.sanic.schemas import DocGenericResponse
from shopping_shared.utils.logger_utils import get_logger

from app.decorators import validate_request, idempotent, require_group_role, api_response
from app.views.groups.base_group_view import BaseGroupView
from app.schemas import (
    FamilyGroupCreateSchema,
    FamilyGroupDetailedSchema,
    FamilyGroupDetailedResponseSchema,
    GroupMembershipListResponseSchema,
    GroupMembershipSchema
)

logger = get_logger(__name__)


class GroupView(BaseGroupView):
    """Handles creation and listing of family groups for the authenticated user."""

    decorators = [
        require_group_role(),  # Allow any authenticated user to create/list their own groups
        openapi.tag("Groups"),
        openapi.secured("bearerAuth")
    ]

    @openapi.summary("Create a new family group")
    @openapi.description("Creates a new family group with the authenticated user as HEAD_CHEF.")
    @openapi.body(FamilyGroupCreateSchema)
    @openapi.response(201, FamilyGroupDetailedResponseSchema)
    @validate_request(FamilyGroupCreateSchema)
    @idempotent()
    @api_response(
        success_schema=FamilyGroupDetailedResponseSchema,
        success_status=201,
        success_description="Group created successfully"
    )
    async def post(self, request: Request):
        """Create a new family group."""
        validated_data = request.ctx.validated_data
        user_id = request.ctx.auth_payload["sub"]

        service = self._get_service(request)

        try:
            group = await service.create_group(
                user_id=user_id,
                group_data=validated_data
            )

            # Use helper method from base class
            return self.success_response(
                data=FamilyGroupDetailedSchema.model_validate(group),
                message="Group created successfully",
                status_code=201
            )
        except Exception as e:
            # Use helper method from base class
            logger.error(f"Failed to create group: {str(e)}", exc_info=True)
            return self.error_response(
                message="Failed to create group",
                status_code=500
            )


    @openapi.summary("List user's family groups")
    @openapi.description("Lists all family groups the authenticated user is a member of.")
    @openapi.response(200, GroupMembershipListResponseSchema)
    @api_response(
        success_schema=GroupMembershipListResponseSchema,
        success_status=200,
        success_description="Groups listed successfully"
    )
    async def get(self, request: Request):
        """List all groups the authenticated user is a member of."""
        user_id = request.ctx.auth_payload["sub"]
        service = self._get_service(request)

        try:
            memberships = await service.get_user_groups(user_id)

            # Use helper method from base class
            # memberships is a list of GroupMembership objects, need to convert to GroupMembershipSchema
            membership_schemas = [GroupMembershipSchema.model_validate(m) for m in memberships]
            return self.success_response(
                data=membership_schemas,
                message="Groups listed successfully",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            logger.error(f"Failed to list groups: {str(e)}", exc_info=True)
            return self.error_response(
                message="Failed to list groups",
                status_code=500
            )


class GroupDetailView(BaseGroupView):
    """Handles operations on a specific family group."""

    decorators = [
        require_group_role(GroupRole.HEAD_CHEF),  # Only HEAD_CHEF can manage group details
        openapi.tag("Groups"),
        openapi.secured("bearerAuth")
    ]

    @openapi.summary("Get family group details")
    @openapi.description("Retrieves details of a specific family group.")
    @openapi.response(200, FamilyGroupDetailedResponseSchema)
    @api_response(
        success_schema=FamilyGroupDetailedResponseSchema,
        success_status=200,
        success_description="Group details retrieved successfully"
    )
    async def get(self, request: Request, group_id: UUID):
        """Get details of a specific family group."""
        service = self._get_service(request)

        try:
            group = await service.get(group_id)

            # Use helper method from base class
            return self.success_response(
                data=FamilyGroupDetailedSchema.model_validate(group),
                message="Group details retrieved successfully",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            logger.error(f"Failed to retrieve group details: {str(e)}", exc_info=True)
            return self.error_response(
                message="Failed to retrieve group details",
                status_code=500
            )

    @openapi.summary("Update family group details")
    @openapi.description("Updates details of a specific family group.")
    @openapi.body(FamilyGroupCreateSchema)  # Using create schema for update as fields are similar
    @openapi.response(200, FamilyGroupDetailedResponseSchema)
    @validate_request(FamilyGroupCreateSchema)
    @api_response(
        success_schema=FamilyGroupDetailedResponseSchema,
        success_status=200,
        success_description="Group updated successfully"
    )
    async def put(self, request: Request, group_id: UUID):
        """Update details of a specific family group."""
        validated_data = request.ctx.validated_data
        service = self._get_service(request)

        try:
            updated_group = await service.update(group_id, validated_data)

            # Use helper method from base class
            return self.success_response(
                data=FamilyGroupDetailedSchema.model_validate(updated_group),
                message="Group updated successfully",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            logger.error(f"Failed to update group: {str(e)}", exc_info=True)
            return self.error_response(
                message="Failed to update group",
                status_code=500
            )

    @openapi.summary("Delete a family group")
    @openapi.description("Deletes a specific family group.")
    @openapi.response(200, DocGenericResponse)
    @api_response(
        success_schema=DocGenericResponse,
        success_status=200,
        success_description="Group deleted successfully"
    )
    async def delete(self, request: Request, group_id: UUID):
        """Delete a specific family group."""
        service = self._get_service(request)

        try:
            await service.delete(group_id)

            # Use helper method from base class
            return self.success_response(
                message="Group deleted successfully",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            logger.error(f"Failed to delete group: {str(e)}", exc_info=True)
            return self.error_response(
                message="Failed to delete group",
                status_code=500
            )
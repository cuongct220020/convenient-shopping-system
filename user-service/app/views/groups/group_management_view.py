# user-service/app/views/groups/group_management_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi

from app.enums import GroupRole
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

from app.decorators import validate_request, idempotent, require_group_role
from app.views.groups.base_group_view import BaseGroupView
from app.schemas.family_group_schema import (
    FamilyGroupCreateSchema,
    FamilyGroupDetailedSchema,
    GroupMembershipSchema
)

logger = get_logger("Group Management View")


class GroupView(BaseGroupView):
    """Handles creation and listing of family groups for the authenticated user."""

    decorators = [
        require_group_role(),  # Allow any authenticated user to create/list their own groups
        openapi.tag("Groups"),
        openapi.secured("bearerAuth")
    ]

    @openapi.definition(
        summary="Create a new family group",
        description="Creates a new family group with the authenticated user as HEAD_CHEF.",
        body=get_openapi_body(FamilyGroupCreateSchema),
        response=[
            {"status": 201, "model": FamilyGroupDetailedSchema, "description": "Group created successfully"},
            {"status": 400, "model": GenericResponse, "description": "Bad Request"},
            {"status": 401, "model": GenericResponse, "description": "Unauthorized"},
            {"status": 409, "model": GenericResponse, "description": "Conflict"},
            {"status": 500, "model": GenericResponse, "description": "Internal Server Error"}
        ]
    )
    @validate_request(FamilyGroupCreateSchema, auto_document=False)
    @idempotent(auto_document=False)
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
    @openapi.response(200)
    async def get(self, request: Request):
        """List all groups the authenticated user is a member of."""
        user_id = request.ctx.auth_payload["sub"]
        service = self._get_service(request)

        try:
            memberships = await service.get_user_groups(user_id)

            # Use helper method from base class
            # memberships is a list of GroupMembership objects, need to convert to GroupMembershipSchema


            return self.success_response(
                data=None,
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
    @openapi.response(200, FamilyGroupDetailedSchema)
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
    @openapi.response(200, FamilyGroupDetailedSchema)
    @validate_request(FamilyGroupCreateSchema)
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
    @openapi.response(200, GenericResponse)
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
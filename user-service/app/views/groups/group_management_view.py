# user-service/app/views/groups/group_management_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.enums import GroupRole
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

from app.decorators import validate_request, idempotent, require_group_role
from app.views.groups.base_group_view import BaseGroupView
from app.schemas.family_group_schema import (
    FamilyGroupCreateSchema,
    FamilyGroupDetailedSchema,
    UserGroupSchema,
    UserGroupListResponseSchema,
    FamilyGroupUpdateSchema,
)

logger = get_logger("Group Management View")


class GroupView(BaseGroupView):
    """Handles creation and listing of family groups for the authenticated user."""

    @openapi.definition(
        summary="Create a new family group",
        description="Creates a new family group with the authenticated user as HEAD_CHEF.",
        body=get_openapi_body(FamilyGroupCreateSchema),
        tag=["Family Groups"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(FamilyGroupDetailedSchema),
                status=201,
                description="Group created successfully",
            )
        ]
    )
    @validate_request(FamilyGroupCreateSchema, auto_document=True)
    @idempotent(auto_document=True)
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

    @openapi.definition(
        summary="List user's family groups",
        description="Lists all family groups the authenticated user is a member of.",
        tag=["Family Groups"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse[UserGroupListResponseSchema]),
                status=200,
                description="Groups listed successfully",
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=500,
                description="Internal Server Error",
            )
        ]
    )
    async def get(self, request: Request):
        """List all groups the authenticated user is a member of."""
        user_id = request.ctx.auth_payload["sub"]
        service = self._get_service(request)

        try:
            memberships = await service.get_user_groups(user_id)

            # Convert memberships to user group details
            groups = []
            for membership in memberships:
                # Get the group details
                group = membership.group

                # Create UserGroupSchema with the user's role in this specific group
                user_group = UserGroupSchema(
                    id=group.id,
                    group_name=group.group_name,
                    group_avatar_url=group.group_avatar_url,
                    creator=group.creator,
                    role_in_group=membership.role,
                    member_count=len(group.group_memberships)  # Use the eager loaded memberships for count
                )

                groups.append(user_group)

            # Create the response using UserGroupListResponseSchema
            response_data = UserGroupListResponseSchema(groups=groups)

            return self.success_response(
                data=response_data,
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
    ]

    @openapi.definition(
        summary="Get a specific family group",
        description="Retrieves details of a specific family group.",
        tag=["Family Groups"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(FamilyGroupDetailedSchema),
                status=200,
                description="Group retrieved successfully",
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=404,
                description="Not Found",
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=400,
                description="Bad Request",
            )
        ]
    )
    async def get(self, request: Request, group_id: UUID):
        """Get details of a specific family group."""
        service = self._get_service(request)

        try:
            group = await service.get_group_with_members(group_id)

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



    @openapi.definition(
        summary="Update a specific family group",
        description="Updates details of a specific family group.",
        body=get_openapi_body(FamilyGroupUpdateSchema),
        tag=["Family Groups"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(FamilyGroupDetailedSchema),
                status=200,
                description="Group updated successfully",
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=400,
                description="Bad Request",
            )
        ]
    )
    @validate_request(FamilyGroupUpdateSchema)
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


    @openapi.definition(
        summary="Delete a specific family group",
        description="Deletes details of a specific family group.",
        tag=["Family Groups"],
        secured={"bearerAuth": []},
        response=[
            Response(content=get_openapi_body(GenericResponse), status=200, description="Group deleted successfully"),
            Response(content=get_openapi_body(GenericResponse), status=404, description="Not Found")
        ]
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
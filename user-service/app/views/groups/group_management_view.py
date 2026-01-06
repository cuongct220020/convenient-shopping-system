# user-service/app/views/groups/group_management_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators.cache_response import cache_response
from app.enums import GroupRole
from shopping_shared.caching.redis_keys import RedisKeys
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

from app.decorators import validate_request, idempotent, require_group_role
from shopping_shared.exceptions import NotFound, Forbidden
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
        description="Creates a new family group with the authenticated user as the HEAD_CHEF (group administrator). The creator automatically becomes the group leader with full management privileges.",
        body=get_openapi_body(FamilyGroupCreateSchema),
        tag=["Family Groups"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(FamilyGroupDetailedSchema),
                status=201,
                description="Family group created successfully with the authenticated user as HEAD_CHEF.",
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
            group = await service.create_group_by_user(
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
        summary="List authenticated user's family groups",
        description="Retrieves a list of all family groups that the authenticated user is a member of, including their role in each group and basic group information.",
        tag=["Family Groups"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse[UserGroupListResponseSchema]),
                status=200,
                description="Successfully retrieved the list of family groups for the authenticated user.",
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=500,
                description="Internal Server Error occurred while retrieving family groups.",
            )
        ]
    )
    @cache_response(key_pattern=RedisKeys.USER_GROUPS_LIST, ttl=300)
    async def get(self, request: Request):
        """List all groups the authenticated user is a member of."""
        user_id = request.ctx.auth_payload["sub"]
        service = self._get_service(request)

        try:
            memberships_data = await service.get_user_groups(user_id)

            # Convert memberships to user group details
            groups = []
            for membership, member_count in memberships_data:
                # Get the group details
                group = membership.group

                # Create UserGroupSchema with the user's role in this specific group
                user_group = UserGroupSchema(
                    id=group.id,
                    group_name=group.group_name,
                    group_avatar_url=group.group_avatar_url,
                    creator=group.creator,
                    role_in_group=membership.role,
                    member_count=member_count
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

    @openapi.definition(
        summary="Retrieve detailed family group information",
        description="Retrieves comprehensive details of a specific family group, including group information, member list, and their roles within the group.",
        tag=["Family Groups"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(FamilyGroupDetailedSchema),
                status=200,
                description="Successfully retrieved detailed information for the specified family group.",
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=404,
                description="Family group not found.",
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=400,
                description="Invalid request parameters.",
            )
        ]
    )
    @require_group_role(GroupRole.HEAD_CHEF)
    @cache_response(key_pattern=RedisKeys.GROUP_DETAIL, ttl=300)
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
        except NotFound as e:
            logger.error(f"Group with id {group_id} not found", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=404
            )
        except Forbidden as e:
            logger.error(f"Permission denied accessing group {group_id}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=403
            )
        except Exception as e:
            # Use helper method from base class
            logger.error(f"Failed to retrieve group details: {str(e)}", exc_info=True)
            return self.error_response(
                message="Failed to retrieve group details",
                status_code=500
            )



    @openapi.definition(
        summary="Update family group details",
        description="Updates the details of a specific family group including name, description, and other group attributes. Only accessible to the group HEAD_CHEF.",
        body=get_openapi_body(FamilyGroupUpdateSchema),
        tag=["Family Groups"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(FamilyGroupDetailedSchema),
                status=200,
                description="Successfully updated the family group details.",
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=400,
                description="Invalid request parameters or insufficient permissions.",
            )
        ]
    )
    @validate_request(FamilyGroupUpdateSchema)
    @require_group_role(GroupRole.HEAD_CHEF)
    async def put(self, request: Request, group_id: UUID):
        """Update details of a specific family group."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data
        service = self._get_service(request)

        try:
            updated_group = await service.update_group_info_by_head_chef(
                user_id=user_id,
                group_id=group_id,
                validated_data=validated_data
            )

            # Use helper method from base class
            return self.success_response(
                data=FamilyGroupDetailedSchema.model_validate(updated_group),
                message="Group updated successfully",
                status_code=200
            )
        except NotFound as e:
            logger.error(f"Group with id {group_id} not found", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=404
            )
        except Forbidden as e:
            logger.error(f"Permission denied updating group {group_id}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=403
            )
        except Exception as e:
            # Use helper method from base class
            logger.error(f"Failed to update group: {str(e)}", exc_info=True)
            return self.error_response(
                message="Failed to update group",
                status_code=500
            )


    @openapi.definition(
        summary="Delete a family group",
        description="Permanently deletes a specific family group and all associated memberships. This action is irreversible and can only be performed by the group HEAD_CHEF.",
        tag=["Family Groups"],
        secured={"bearerAuth": []},
        response=[
            Response(content=get_openapi_body(GenericResponse), status=200, description="Family group deleted successfully."),
            Response(content=get_openapi_body(GenericResponse), status=404, description="Family group not found.")
        ]
    )
    @require_group_role(GroupRole.HEAD_CHEF)
    async def delete(self, request: Request, group_id: UUID):
        """Delete a specific family group."""
        user_id = request.ctx.auth_payload["sub"]
        service = self._get_service(request)

        try:
            await service.delete_group_by_head_chef(
                user_id=user_id,
                group_id=group_id
            )

            # Use helper method from base class
            return self.success_response(
                message="Group deleted successfully",
                status_code=200
            )
        except NotFound as e:
            logger.error(f"Group with id {group_id} not found", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=404
            )
        except Forbidden as e:
            logger.error(f"Permission denied deleting group {group_id}", exc_info=e)
            return self.error_response(
                message=str(e),
                status_code=403
            )
        except Exception as e:
            # Use helper method from base class
            logger.error(f"Failed to delete group: {str(e)}", exc_info=True)
            return self.error_response(
                message="Failed to delete group",
                status_code=500
            )
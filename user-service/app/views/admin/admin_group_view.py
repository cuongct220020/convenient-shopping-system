# user-service/app/views/admin/admin_group_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request, require_system_role
from app.views.base_view import BaseAPIView
from app.enums import SystemRole
from app.repositories.family_group_repository import FamilyGroupRepository
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.repositories.user_repository import UserRepository
from app.services.admin_service import AdminGroupService
from app.schemas.family_group_schema import FamilyGroupDetailedSchema, GroupMembershipUpdateSchema, \
    PaginatedFamilyGroupsResponseSchema, GroupMembershipSchema, AddMemberRequestSchema
from app.schemas.family_group_admin_schema import FamilyGroupAdminUpdateSchema

from shopping_shared.exceptions import NotFound, Conflict
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

logger = get_logger("Admin Group View")


class BaseAdminGroupsView(BaseAPIView):

    @staticmethod
    def _get_service(request: Request) -> AdminGroupService:
        user_repo = UserRepository(session=request.ctx.db_session)
        member_repo = GroupMembershipRepository(session=request.ctx.db_session)
        group_repo = FamilyGroupRepository(session=request.ctx.db_session)
        return AdminGroupService(user_repo, member_repo, group_repo)



class AdminGroupsView(BaseAdminGroupsView):
    """Admin endpoints for listing all family groups. Requires ADMIN role."""

    @openapi.definition(
        summary="List all family groups (Admin)",
        description="Retrieves a paginated list of all family groups in the system. This endpoint is accessible only to administrators for group management and oversight purposes.",
        parameter=[
            {
                "name": "page",
                "in": "query",
                "required": False,
                "description": "Page number for pagination (default: 1)",
                "schema": {"type": "integer", "default": 1, "minimum": 1}
            },
            {
                "name": "page_size",
                "in": "query",
                "required": False,
                "description": "Number of items per page (default: 10, max: 100)",
                "schema": {"type": "integer", "default": 10, "minimum": 1, "maximum": 100}
            }
        ],
        secured={"bearerAuth": []},
        tag=["Admin Groups Management"],
        response=[
            Response(
                content=get_openapi_body(PaginatedFamilyGroupsResponseSchema),
                status=200,
                description="Successfully retrieved paginated list of all family groups.",
            )
        ]
    )
    @require_system_role(SystemRole.ADMIN)
    async def get(self, request: Request):
        """
        List all family groups with pagination.
        GET /api/v1/user-service/admin/groups
        """
        try:
            # Validate and convert query parameters with proper error handling
            page_param = request.args.get("page", "1")
            page_size_param = request.args.get("page_size", "10")

            # Validate that parameters are numeric
            try:
                page = int(page_param)
                page_size = int(page_size_param)
            except ValueError:
                return self.error_response(
                    message="Page and page_size must be valid integers",
                    status_code=400
                )

            # Validate positive values
            if page < 1:
                return self.error_response(
                    message="Page must be a positive integer",
                    status_code=400
                )

            if page_size < 1:
                return self.error_response(
                    message="Page size must be a positive integer",
                    status_code=400
                )

            # Validate maximum page size
            if page_size > 100:
                return self.error_response(
                    message="Page size cannot exceed 100",
                    status_code=400
                )

            service = self._get_service(request)
            groups, total = await service.get_all_groups_paginated(page=page, page_size=page_size)

            # Create the paginated response using the schema
            paginated_response = PaginatedFamilyGroupsResponseSchema(
                data=[FamilyGroupDetailedSchema.model_validate(group) for group in groups],
                page=page,
                page_size=page_size,
                total_items=total,
                total_pages=(total + page_size - 1) // page_size
            )

            # Use helper method from base class
            return self.success_response(
                data=paginated_response,
                message="Groups listed successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to list family groups", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to list groups",
                status_code=500
            )


class AdminGroupDetailView(BaseAdminGroupsView):
    """Admin endpoints for managing a specific family group."""

    @openapi.definition(
        summary="Retrieve family group details by ID (Admin)",
        description="Retrieves comprehensive details for a specific family group by its unique identifier. This endpoint is accessible only to administrators for detailed group information and management.",
        tag=["Admin Groups Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(FamilyGroupDetailedSchema),
                status=200,
                description="Successfully retrieved detailed information for the specified family group.",
            )
        ]
    )
    @require_system_role(SystemRole.ADMIN)
    async def get(self, request: Request, group_id: UUID):
        """
        Get a specific family group by ID.
        GET api/v1/user-service/admin/groups/<group_id>
        """
        service = self._get_service(request)

        try:
            group = await service.get_group_by_id(group_id)

            # Use helper method from base class
            return self.success_response(
                data=FamilyGroupDetailedSchema.model_validate(group),
                message="Group retrieved successfully",
                status_code=200
            )
        except NotFound as e:
            return self.error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error("Failed to get family group", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve group",
                status_code=500
            )


    @openapi.definition(
        summary="Update family group details by ID (Admin)",
        description="Updates the details of a specific family group by its unique identifier. This endpoint allows administrators to modify group information such as name, description, and other attributes.",
        body=get_openapi_body(FamilyGroupAdminUpdateSchema),
        tag=["Admin Groups Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(FamilyGroupDetailedSchema),
                status=200,
                description="Successfully updated the specified family group details.",
            )
        ]
    )
    @validate_request(FamilyGroupAdminUpdateSchema)
    @require_system_role(SystemRole.ADMIN)
    async def put(self, request: Request, group_id: UUID):
        """
        Update a specific family group by ID."
        PUT /api/v1/user-service/admin/groups/{group_id}
        """
        validated_data = request.ctx.validated_data
        service = self._get_service(request)

        try:
            updated_group = await service.update_group(group_id, validated_data)

            # Use helper method from base class
            return self.success_response(
                data=FamilyGroupDetailedSchema.model_validate(updated_group),
                message="Group updated successfully",
                status_code=200
            )
        except NotFound as e:
            return self.error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error("Failed to update family group", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to update group",
                status_code=500
            )


    @openapi.definition(
        summary="Delete family group by ID (Admin)",
        description="Permanently deletes a specific family group by its unique identifier. This action is irreversible and will remove all group data and memberships from the system.",
        tag=["Admin Groups Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse),
                status=200,
                description="Successfully deleted the specified family group.",
            )
        ]
    )
    @require_system_role(SystemRole.ADMIN)
    async def delete(self, request: Request, group_id: UUID):
        """
        Delete a specific family group by ID.
        DELETE /api/v1/user-service/admin/groups/{group_id}
        """
        service = self._get_service(request)

        try:
            await service.delete_group(group_id)

            # Use helper method from base class
            return self.success_response(
                message="Group deleted successfully",
                status_code=200
            )
        except NotFound as e:
            return self.error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error("Failed to delete family group", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to delete group",
                status_code=500
            )


class AdminGroupMembersView(BaseAdminGroupsView):
    """Admin endpoints for managing group members."""

    @openapi.definition(
        summary="List all members in a family group (Admin)",
        description="Retrieves a list of all members in a specific family group, including their roles and membership details. This endpoint is accessible only to administrators for group oversight.",
        tag=["Admin Groups Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse[list[GroupMembershipSchema]]),
                status=200,
                description="Successfully retrieved the list of members in the specified family group.",
            )
        ]
    )
    @require_system_role(SystemRole.ADMIN)
    async def get(self, request: Request, group_id: UUID):
        """
        List all members of a specific family group.
        GET /api/v1/user-service/admin/groups/<group_id>/members/
        """

        service = self._get_service(request)

        try:
            members = await service.get_group_members(group_id)

            # Convert members to GroupMembershipSchema objects
            members_schemas = [GroupMembershipSchema.model_validate(member) for member in members]

            # Use helper method from base class
            return self.success_response(
                data=members_schemas,
                message="Group members listed successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to list group members", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to list group members",
                status_code=500
            )

    @openapi.definition(
        summary="Add a member to a family group (Admin)",
        description="Allows an administrator to directly add a user to a family group. This bypasses the normal invitation process and immediately adds the user with the specified role.",
        body=get_openapi_body(AddMemberRequestSchema),
        tag=["Admin Groups Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GroupMembershipSchema),
                status=201,
                description="Successfully added the member to the family group.",
            )
        ]
    )
    @validate_request(AddMemberRequestSchema)
    @require_system_role(SystemRole.ADMIN)
    async def post(self, request: Request, group_id: UUID):
        """
        Add a member to a group (Admin).
        POST /api/v1/user-service/admin/groups/<group_id>/members/
        """
        validated_data = request.ctx.validated_data
        service = self._get_service(request)

        try:
            admin_user_id = UUID(request.ctx.auth_payload["sub"])
            membership = await service.add_member_by_admin(group_id, validated_data.identifier, admin_user_id)
            return self.success_response(
                data=GroupMembershipSchema.model_validate(membership),
                message="Member added successfully",
                status_code=201
            )
        except (NotFound, Conflict) as e:
            return self.error_response(message=str(e), status_code=409 if isinstance(e, Conflict) else 404)
        except Exception as e:
            logger.error("Failed to add member", exc_info=e)
            return self.error_response(message="Failed to add member", status_code=500)


class AdminGroupMembersManageView(BaseAdminGroupsView):
    """Admin endpoints for managing group member roles."""

    @openapi.definition(
        summary="Update member role in family group (Admin)",
        description="Allows an administrator to update the role of a specific member within a family group. This endpoint enables role changes without requiring the member to leave and rejoin the group.",
        tag=["Admin Groups Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GroupMembershipSchema),
                status=200,
                description="Successfully updated the member's role in the family group.",
            )
        ]
    )
    @validate_request(GroupMembershipUpdateSchema)
    @require_system_role(SystemRole.ADMIN)
    async def patch(self, request: Request, group_id: UUID, user_id: UUID):
        """
        Update the role of a member in a specific family group.
        PATCH api/v1/user-service/admin/groups/<group_id>/members/<user_id>
        """
        validated_data = request.ctx.validated_data
        service = self._get_service(request)

        try:
            updated_membership = await service.update_member_role_by_admin(
                group_id=group_id,
                user_id=user_id,
                new_role=validated_data.role
            )

            # Convert to GroupMembershipSchema for proper response format
            membership_schema = GroupMembershipSchema.model_validate(updated_membership)

            # Use helper method from base class
            return self.success_response(
                data=membership_schema,
                message="Member role updated successfully",
                status_code=200
            )
        except NotFound as e:
            return self.error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error("Failed to update member role", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to update member role",
                status_code=500
            )

    @openapi.definition(
        summary="Remove a member from family group (Admin)",
        description="Allows an administrator to remove a specific member from a family group. This action will revoke the member's access to group resources and remove their membership permanently.",
        tag=["Admin Groups Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse),
                status=200,
                description="Successfully removed the member from the family group.",
            )
        ]
    )
    @require_system_role(SystemRole.ADMIN)
    async def delete(self, request: Request, group_id: UUID, user_id: UUID):
        """
        Remove a member from a group (Admin).
        DELETE api/v1/user-service/admin/groups/<group_id>/members/<user_id>
        """
        service = self._get_service(request)

        try:
            await service.remove_member_by_admin(group_id, user_id)
            return self.success_response(
                message="Member removed successfully",
                status_code=200
            )
        except NotFound as e:
            return self.error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error("Failed to remove member", exc_info=e)
            return self.error_response(message="Failed to remove member", status_code=500)

# user-service/app/views/admin/admin_group_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi

from app.decorators import validate_request, require_system_role
from app.views.base_view import BaseAPIView
from app.enums import SystemRole
from app.repositories.family_group_repository import FamilyGroupRepository
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.repositories.user_repository import UserRepository
from app.services.admin_service import AdminGroupService
from app.schemas.family_group_schema import FamilyGroupDetailedSchema, GroupMembershipUpdateSchema
from app.schemas.family_group_admin_schema import FamilyGroupAdminUpdateSchema

from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Admin Group View")

class AdminGroupsView(BaseAPIView):
    """Admin endpoints for listing all family groups. Requires ADMIN role."""
    decorators = [
        require_system_role(SystemRole.ADMIN),
        openapi.tag("Admin - Group Management"),
        openapi.secured("bearerAuth")
    ]

    @staticmethod
    def _get_service(request: Request) -> AdminGroupService:
        user_repo = UserRepository(session=request.ctx.db_session)
        member_repo = GroupMembershipRepository(session=request.ctx.db_session)
        group_repo = FamilyGroupRepository(session=request.ctx.db_session)
        return AdminGroupService(user_repo, member_repo, group_repo)

    @openapi.summary("List all groups")
    @openapi.description("Lists all family groups in the system with pagination.")
    @openapi.parameter("page", int, "query")
    @openapi.parameter("page_size", int, "query")
    @openapi.response(200, GenericResponse)
    @openapi.tag("Admin Group Management")
    async def get(self, request: Request):
        """List all family groups with pagination."""
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))

        service = self._get_service(request)

        try:
            groups, total = await service.get_all_groups_paginated(page=page, page_size=page_size)

            # Use helper method from base class
            return self.success_response(
                data={
                    "items": [FamilyGroupDetailedSchema.model_validate(group).model_dump() for group in groups],
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                },
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


class AdminGroupDetailView(BaseAPIView):
    """Admin endpoints for managing a specific family group."""
    decorators = [
        require_system_role(SystemRole.ADMIN),
        openapi.tag("Admin - Group Management"),
        openapi.secured("bearerAuth")
    ]

    @staticmethod
    def _get_service(request: Request) -> AdminGroupService:
        user_repo = UserRepository(session=request.ctx.db_session)
        member_repo = GroupMembershipRepository(session=request.ctx.db_session)
        group_repo = FamilyGroupRepository(session=request.ctx.db_session)
        return AdminGroupService(user_repo, member_repo, group_repo)

    @openapi.summary("Get group by ID")
    @openapi.description("Retrieves a specific family group by its ID.")
    @openapi.response(200, FamilyGroupDetailedSchema)
    async def get(self, request: Request, group_id: UUID):
        """Get a specific family group by ID."""
        service = self._get_service(request)

        try:
            group = await service.get_group_by_id(group_id)

            # Use helper method from base class
            return self.success_response(
                data=FamilyGroupDetailedSchema.model_validate(group),
                message="Group retrieved successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to get family group", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve group",
                status_code=500
            )


    @openapi.summary("Update group by ID")
    @openapi.description("Updates a specific family group by its ID.")
    @openapi.body(FamilyGroupAdminUpdateSchema)
    @openapi.response(200, FamilyGroupDetailedSchema)
    @validate_request(FamilyGroupAdminUpdateSchema)
    async def put(self, request: Request, group_id: UUID):
        """Update a specific family group by ID."""
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
        except Exception as e:
            logger.error("Failed to update family group", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to update group",
                status_code=500
            )

    @openapi.summary("Delete group by ID")
    @openapi.description("Deletes a specific family group by its ID.")
    @openapi.response(200, GenericResponse)
    async def delete(self, request: Request, group_id: UUID):
        """Delete a specific family group by ID."""
        service = self._get_service(request)

        try:
            await service.delete_group(group_id)

            # Use helper method from base class
            return self.success_response(
                message="Group deleted successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to delete family group", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to delete group",
                status_code=500
            )


class AdminGroupMembersView(BaseAPIView):
    """Admin endpoints for managing group members."""
    decorators = [
        require_system_role(SystemRole.ADMIN),
        openapi.tag("Admin - Group Management"),
        openapi.secured("bearerAuth")
    ]

    @staticmethod
    def _get_service(request: Request) -> AdminGroupService:
        user_repo = UserRepository(session=request.ctx.db_session)
        member_repo = GroupMembershipRepository(session=request.ctx.db_session)
        group_repo = FamilyGroupRepository(session=request.ctx.db_session)
        return AdminGroupService(user_repo, member_repo, group_repo)

    @openapi.summary("List members of a group")
    @openapi.description("Lists all members of a specific family group.")
    @openapi.response(200, GenericResponse)
    async def get(self, request: Request, group_id: UUID):
        """List all members of a specific family group."""
        service = self._get_service(request)

        try:
            members = await service.get_group_members(group_id)

            # Use helper method from base class
            return self.success_response(
                data=members,
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


class AdminGroupMembersManageView(BaseAPIView):
    """Admin endpoints for managing group member roles."""
    decorators = [
        require_system_role(SystemRole.ADMIN),
        openapi.tag("Admin - Group Management"),
        openapi.secured("bearerAuth")
    ]

    @staticmethod
    def _get_service(request: Request) -> AdminGroupService:
        user_repo = UserRepository(session=request.ctx.db_session)
        member_repo = GroupMembershipRepository(session=request.ctx.db_session)
        group_repo = FamilyGroupRepository(session=request.ctx.db_session)
        return AdminGroupService(user_repo, member_repo, group_repo)

    @openapi.summary("Update member role in group")
    @openapi.description("Updates the role of a member in a specific family group.")
    @openapi.body(GroupMembershipUpdateSchema)
    @openapi.response(200, GenericResponse)
    @validate_request(GroupMembershipUpdateSchema)
    async def patch(self, request: Request, group_id: UUID, user_id: UUID):
        """Update the role of a member in a specific family group."""
        validated_data = request.ctx.validated_data
        service = self._get_service(request)

        try:
            updated_membership = await service.update_member_role_by_admin(
                group_id=group_id,
                user_id=user_id,
                new_role=validated_data.role
            )

            # Use helper method from base class
            return self.success_response(
                data=updated_membership,
                message="Member role updated successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to update member role", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to update member role",
                status_code=500
            )
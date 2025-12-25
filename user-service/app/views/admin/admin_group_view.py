# user-service/app/views/admin/admin_group_view.py
from uuid import UUID
from sanic import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators import validate_request, require_system_role
from app.enums import SystemRole, GroupRole
from app.repositories.family_group_repository import FamilyGroupRepository, GroupMembershipRepository
from app.repositories.user_repository import UserRepository
from app.services.family_group_service import FamilyGroupService
from app.services.admin_service import AdminGroupService
from app.schemas.family_group_schema import FamilyGroupDetailedSchema
from app.schemas.family_group_admin_schema import FamilyGroupAdminUpdateSchema

from shopping_shared.exceptions import BadRequest
from shopping_shared.schemas.response_schema import GenericResponse, PaginationResponse


class AdminGroupsView(HTTPMethodView):
    """
    Admin endpoints for listing all family groups. Requires ADMIN role.
    """

    decorators = [require_system_role(SystemRole.ADMIN)]

    @staticmethod
    async def get(request: Request):
        """Lists all family groups in the system with pagination."""
        try:
            page = int(request.args.get("page", 1))
            page_size = int(request.args.get("page_size", 20))
        except ValueError:
            raise BadRequest("Invalid pagination parameters.")

        # Init service
        session = request.ctx.db_session
        service = FamilyGroupService(
            FamilyGroupRepository(session),
            GroupMembershipRepository(session),
            UserRepository(session)
        )

        paginated_result = await service.get_all(page=page, page_size=page_size)

        response = PaginationResponse(
            status="success",
            data=[FamilyGroupDetailedSchema.model_validate(g) for g in paginated_result.items],
            page=paginated_result.current_page,
            page_size=paginated_result.page_size,
            total_items=paginated_result.total_items,
            total_pages=paginated_result.total_pages
        )
        return json(response.model_dump(exclude_none=True, mode='json'), status=200)


class AdminGroupDetailView(HTTPMethodView):
    """
    Admin endpoints for managing a specific family group. Requires ADMIN role.
    """

    decorators = [require_system_role(SystemRole.ADMIN)]

    @staticmethod
    def _get_service(request: Request) -> FamilyGroupService:
        session = request.ctx.db_session
        return FamilyGroupService(
            FamilyGroupRepository(session),
            GroupMembershipRepository(session),
            UserRepository(session)
        )

    async def get(self, request: Request, group_id: UUID):
        """Retrieves detailed information about a specific family group."""
        service = self._get_service(request)
        group = await service.get(group_id)

        response = GenericResponse(
            status="success",
            data=FamilyGroupDetailedSchema.model_validate(group)
        )

        return json(response.model_dump(exclude_none=True, mode='json'), status=200)

    @validate_request(FamilyGroupAdminUpdateSchema)
    async def patch(self, request: Request, group_id: UUID):
        """Updates information of a specific family group."""
        validated_data = request.ctx.validated_data

        service = self._get_service(request)
        updated_group = await service.update(group_id, validated_data)
        
        response = GenericResponse(
            status="success",
            message="Group updated successfully.",
            data=FamilyGroupDetailedSchema.model_validate(updated_group)
        )
        return json(response.model_dump(exclude_none=True, mode='json'), status=200)

    async def delete(self, request: Request, group_id: UUID):
        """Deletes a specific family group."""
        service = self._get_service(request)
        await service.delete(group_id)

        response = GenericResponse(
            status="success",
            message="Group deleted successfully.",
            data=None
        )

        return json(response.model_dump(mode='json'), status=200)


class AdminGroupMembersView(HTTPMethodView):
    """
    Admin endpoints for adding members to a group. Requires ADMIN role.
    """

    decorators = [require_system_role(SystemRole.ADMIN)]

    @staticmethod
    def _get_service(request: Request) -> AdminGroupService:
        session = request.ctx.db_session
        return AdminGroupService(
            UserRepository(session),
            GroupMembershipRepository(session)
        )

    async def post(self, request: Request, group_id: UUID):
        """Adds a user to a family group."""
        email = request.json.get("email")
        if not email:
            raise BadRequest("Email is required.")
            
        service = self._get_service(request)
        await service.add_member_by_admin(group_id, email)
        
        response = GenericResponse(
            status="success",
            message="Member added successfully by admin."
        )
        return json(response.model_dump(mode='json'), status=201)


class AdminGroupMembersManageView(HTTPMethodView):
    """
    Admin endpoints for managing existing members (Delete/Update). Requires ADMIN role.
    """

    decorators = [require_system_role(SystemRole.ADMIN)]

    @staticmethod
    def _get_service(request: Request) -> AdminGroupService:
        session = request.ctx.db_session
        return AdminGroupService(
            UserRepository(session),
            GroupMembershipRepository(session)
        )

    async def delete(self, request: Request, group_id: UUID, user_id: UUID):
        """Removes a member from a family group."""
        service = self._get_service(request)
        await service.remove_member_by_admin(group_id, user_id)

        response = GenericResponse(
            status="success",
            message="Member removed successfully by admin.",
            data=None
        )

        return json(response.model_dump(mode='json'), status=200)


    async def patch(self, request: Request, group_id: UUID, user_id: UUID):
        """Updates the role of a member in a family group."""
        role_str = request.json.get("role")
        if not role_str or role_str not in [r.value for r in GroupRole]:
             raise BadRequest("Valid role is required.")
        new_role = GroupRole(role_str)
        
        service = self._get_service(request)
        await service.update_member_role_by_admin(group_id, user_id, new_role)

        response = GenericResponse(
            status="success",
            message="Member role updated successfully by admin.",
            data=None,
        )

        return json(response.model_dump(mode='json'), status=200)

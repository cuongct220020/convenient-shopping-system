# user-service/app/views/admin/admin_group_view.py
from uuid import UUID
from sanic import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from shopping_shared.exceptions import Forbidden, BadRequest, NotFound, Conflict
from shopping_shared.schemas.response_schema import GenericResponse, PaginationResponse

from app.decorators.validate_request import validate_request
from app.repositories.family_group_repository import FamilyGroupRepository, GroupMembershipRepository
from app.repositories.user_repository import UserRepository
from app.services.family_group_service import FamilyGroupService
from app.schemas.family_group_schema import (
    FamilyGroupCreateSchema,
    FamilyGroupDetailedSchema,
    FamilyGroupMemberSchema
)
from app.enums import GroupRole
from app.models import GroupMembership


class AdminGroupsView(HTTPMethodView):

    @staticmethod
    async def get(request: Request):
        """Lists all groups with pagination."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

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
        return json(response.model_dump(exclude_none=True), status=200)


class AdminGroupDetailView(HTTPMethodView):

    @staticmethod
    async def get(request: Request, group_id: UUID):
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")
        

        session = request.ctx.db_session
        family_group_repo = FamilyGroupRepository(session)
        group_membership_repo = GroupMembershipRepository(session)
        user_repo = UserRepository(session)


        family_group_service = FamilyGroupService(
            repo=family_group_repo,
            member_repo=group_membership_repo,
            user_repo=user_repo
        )

        group = await family_group_service.get(group_id)

        response = GenericResponse(
            status="success",
            data=FamilyGroupDetailedSchema.model_validate(group)
        )

        return json(response.model_dump(exclude_none=True), status=200)

    @validate_request(FamilyGroupCreateSchema)
    async def patch(self, request: Request, group_id: UUID):
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")
            
        service = await self._get_service(request)
        updated_group = await service.update(group_id, request.ctx.validated_data)
        
        response = GenericResponse(
            status="success",
            message="Group updated successfully.",
            data=FamilyGroupDetailedSchema.model_validate(updated_group)
        )
        return json(response.model_dump(exclude_none=True), status=200)

    async def delete(self, request: Request, group_id: UUID):
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")
            
        service = await self._get_service(request)
        # BaseService.delete does not check ownership, so safe to use for admin
        await service.delete(group_id)

        resposne = GenericResponse(
            status="success",
            message="Group deleted successfully.",
            data=None
        )

        return json(response.model_dump(), status=200)


class AdminGroupMembersView(HTTPMethodView):
    """View to add members to a group by Admin."""
    
    async def post(self, request: Request, group_id: UUID):
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")
            
        email = request.json.get("email")
        if not email:
            raise BadRequest("Email is required.")
            
        # Direct Logic for Admin (Bypass Service's Head Chef Check)
        session = request.ctx.db_session
        user_repo = UserRepository(session)
        member_repo = GroupMembershipRepository(session)
        
        user_to_add = await user_repo.get_by_email(email)
        if not user_to_add:
            raise NotFound(f"User with email {email} not found.")
            
        existing = await member_repo.session.get(GroupMembership, (user_to_add.id, group_id))
        if existing:
            raise Conflict("User is already a member of this group.")
            
        membership = GroupMembership(
            user_id=user_to_add.id,
            group_id=group_id,
            role=GroupRole.MEMBER
        )
        member_repo.session.add(membership)
        await member_repo.session.flush()
        
        response = GenericResponse(
            status="success",
            message="Member added successfully by admin."
        )
        return json(response.model_dump(), status=201)


class AdminGroupMembersManageView(HTTPMethodView):
    """View to manage existing members (Delete/Update) by Admin."""

    async def delete(self, request: Request, group_id: UUID, user_id: UUID):
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")
            
        session = request.ctx.db_session
        member_repo = GroupMembershipRepository(session)
        
        membership = await member_repo.session.get(GroupMembership, (user_id, group_id))
        if not membership:
            raise NotFound("Membership not found.")
            
        await member_repo.session.delete(membership)
        
        response = SuccessResponse(message="Member removed successfully by admin.")
        return json(response.model_dump(), status=200)

    async def patch(self, request: Request, group_id: UUID, user_id: UUID):
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")
            
        role_str = request.json.get("role")
        if not role_str or role_str not in [r.value for r in GroupRole]:
             raise BadRequest("Valid role is required.")
        new_role = GroupRole(role_str)
        
        session = request.ctx.db_session
        member_repo = GroupMembershipRepository(session)
        
        membership = await member_repo.session.get(GroupMembership, (user_id, group_id))
        if not membership:
            raise NotFound("Membership not found.")
            
        membership.role = new_role
        await member_repo.session.flush()

        response = GenericResponse(
            status="success",
            message="Member role updated successfully by admin.",
            data=None,
        )

        return json(response.model_dump(), status=200)


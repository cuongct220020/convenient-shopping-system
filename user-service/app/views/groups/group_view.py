# user-service/app/views/groups/group_view.py
from uuid import UUID
from sanic import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from shopping_shared.exceptions import Forbidden, NotFound
from shopping_shared.schemas.response_schema import GenericResponse

from app.decorators.validate_request import validate_request
from app.decorators.idempotency import idempotent
from app.repositories.family_group_repository import FamilyGroupRepository, GroupMembershipRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_profile_repository import UserIdentityProfileRepository, UserHealthProfileRepository
from app.services.family_group_service import FamilyGroupService
from app.services.user_profile_service import UserIdentityProfileService, UserHealthProfileService
from app.schemas.family_group_schema import (
    FamilyGroupCreateSchema,
    FamilyGroupDetailedSchema,
    GroupMembershipSchema,
    AddMemberRequestSchema,
    UpdateMemberRoleRequestSchema
)
from app.schemas.user_profile_schema import UserIdentityProfileSchema, UserHealthProfileSchema
from app.models import GroupMembership


class BaseGroupView(HTTPMethodView):
    """Base view with helper to get FamilyGroupService."""
    
    @staticmethod
    def _get_service(request: Request) -> FamilyGroupService:
        session = request.ctx.db_session
        return FamilyGroupService(
            FamilyGroupRepository(session),
            GroupMembershipRepository(session),
            UserRepository(session)
        )


class GroupView(BaseGroupView):
    """Handles /groups"""

    @validate_request(FamilyGroupCreateSchema)
    @idempotent()
    async def post(self, request: Request):
        """Creates a new family group."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        service = self._get_service(request)
        group = await service.create_group(user_id, validated_data)

        response = GenericResponse(
            status="success",
            message="Group created successfully.",
            data=FamilyGroupDetailedSchema.model_validate(group)
        )
        return json(response.model_dump(exclude_none=True), status=201)


class GroupDetailView(BaseGroupView):
    """Handles /groups/{groupId}"""

    async def delete(self, request: Request, group_id: UUID):
        """Deletes a family group."""
        user_id = request.ctx.auth_payload["sub"]
        service = self._get_service(request)
        
        # Uses business logic that checks ownership
        await service.delete_group_by_creator(user_id, group_id)

        response = GenericResponse(status="success", message="Group deleted successfully.")
        return json(response.model_dump(), status=200)


class GroupMembersView(BaseGroupView):
    """Handles /groups/{groupId}/members"""

    @validate_request(AddMemberRequestSchema)
    async def post(self, request: Request, group_id: UUID):
        """Adds a member to the group (Head Chef only)."""
        requester_id = request.ctx.auth_payload["sub"]
        email = request.ctx.validated_data.email
        
        service = self._get_service(request)
        membership = await service.add_member_by_email(requester_id, group_id, email)
        
        # We need to construct the response data properly. 
        # membership.user might not be loaded if lazy. 
        # But let's assume service/repo logic handles loading or we re-fetch.
        # For this refactor, I'll rely on what's returned.
        # If membership.user is missing, I might need to fetch it.
        # FamilyGroupService.add_member_by_email returns the membership object.
        
        # Force load user if needed or assume it's there/loaded by repo? 
        # BaseRepository doesn't auto-load relationships unless configured.
        # I'll rely on schema validation to fail if data is missing, or better, 
        # fetch the user details to return 'GroupMemberSchema'.
        
        # For now, let's assume we can construct the response.
        
        # Fetching user details for response
        user_repo = UserRepository(request.ctx.db_session)
        user = await user_repo.get_by_id(membership.user_id)
        
        # Construct explicit dict to avoid lazy loading issues if user relationship isn't loaded on membership
        response_data = {
            "user": user,
            "role": membership.role
        }

        response = GenericResponse(
            status="success",
            message="Member added successfully.",
            data=GroupMembershipSchema.model_validate(response_data)
        )
        return json(response.model_dump(exclude_none=True), status=201)


class GroupMemberDetailView(BaseGroupView):
    """Handles /groups/{groupId}/members/{userId}"""

    async def delete(self, request: Request, group_id: UUID, user_id: UUID):
        """Removes a member (Head Chef only)."""
        requester_id = request.ctx.auth_payload["sub"]
        service = self._get_service(request)
        
        await service.remove_member(requester_id, group_id, user_id)
        
        response = GenericResponse(status="success", message="Member removed successfully.")
        return json(response.model_dump(), status=200)

    @validate_request(UpdateMemberRoleRequestSchema)
    async def patch(self, request: Request, group_id: UUID, user_id: UUID):
        """Updates member role (Head Chef only)."""
        requester_id = request.ctx.auth_payload["sub"]
        new_role = request.ctx.validated_data.role
        
        service = self._get_service(request)
        membership = await service.update_member_role(requester_id, group_id, user_id, new_role)
        
        # Fetch user for response similar to POST
        user_repo = UserRepository(request.ctx.db_session)
        user = await user_repo.get_by_id(membership.user_id)

        response_data = {
            "user": user,
            "role": membership.role
        }
        
        response = GenericResponse(
            status="success",
            message="Member role updated successfully.",
            data=GroupMembershipSchema.model_validate(response_data)
        )
        return json(response.model_dump(exclude_none=True), status=200)


class GroupMemberMeView(BaseGroupView):
    """Handles /groups/{groupId}/members/me"""
    
    async def delete(self, request: Request, group_id: UUID):
        """Member leaves the group."""
        requester_id = request.ctx.auth_payload["sub"]
        service = self._get_service(request)
        
        # remove_member allows self-removal
        await service.remove_member(requester_id, group_id, requester_id)
        
        response = GenericResponse(status="success", message="You have left the group.")
        return json(response.model_dump(), status=200)


class MemberIdentityProfileView(HTTPMethodView):

    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """Allows members of the same group to view identity profiles."""
        requester_id = request.ctx.auth_payload["sub"]
        
        session = request.ctx.db_session
        member_repo = GroupMembershipRepository(session)
        
        # Ensure both are in the same group
        requester_membership = await member_repo.get_membership(requester_id, group_id)
        target_membership = await member_repo.get_membership(user_id, group_id)
        
        if not requester_membership or not target_membership:
            raise Forbidden("You must be in the same group to view this profile.")
            
        service = UserIdentityProfileService(UserIdentityProfileRepository(session))
        profile = await service.get(user_id)
        
        if not profile:
             raise NotFound("Profile not found.")

        response = GenericResponse(status="success", data=UserIdentityProfileSchema.model_validate(profile))
        return json(response.model_dump(exclude_none=True), status=200)


class MemberHealthProfileView(HTTPMethodView):
    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """Allows members of the same group to view health profiles."""
        requester_id = request.ctx.auth_payload["sub"]
        
        session = request.ctx.db_session
        member_repo = GroupMembershipRepository(session)
        
        requester_membership = await member_repo.get_membership(requester_id, group_id)
        target_membership = await member_repo.get_membership(user_id, group_id)
        
        if not requester_membership or not target_membership:
            raise Forbidden("You must be in the same group to view this profile.")
            
        service = UserHealthProfileService(UserHealthProfileRepository(session))
        profile = await service.get(user_id)
        
        if not profile:
             raise NotFound("Profile not found.")
        
        response = GenericResponse(status="success", data=UserHealthProfileSchema.model_validate(profile))
        return json(response.model_dump(exclude_none=True), status=200)
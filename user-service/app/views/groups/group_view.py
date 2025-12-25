# user-service/app/views/groups/group_view.py
from uuid import UUID
from sanic import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from shopping_shared.exceptions import Forbidden, NotFound
from shopping_shared.schemas.response_schema import GenericResponse

from app.decorators import validate_request, idempotent, require_group_role
from app.enums import GroupRole
from app.repositories.family_group_repository import FamilyGroupRepository, GroupMembershipRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_profile_repository import UserIdentityProfileRepository, UserHealthProfileRepository
from app.services.family_group_service import FamilyGroupService
from app.services.user_profile_service import UserIdentityProfileService, UserHealthProfileService
from app.schemas.family_group_schema import (
    FamilyGroupCreateSchema,
    FamilyGroupDetailedSchema,
    GroupMembershipSchema,
    GroupMembershipDetailedSchema,
    AddMemberRequestSchema,
    GroupMembershipUpdateSchema
)
from app.schemas.user_profile_schema import UserIdentityProfileSchema, UserHealthProfileSchema


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
    """
    Handles /groups
    - POST: Create new group (authenticated user becomes HEAD_CHEF)
    """

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
        return json(response.model_dump(exclude_none=True, mode="json"), status=201)


class GroupDetailView(BaseGroupView):
    """
    Handles /groups/{group_id}
    - GET: View group details (any member)
    - DELETE: Delete group (HEAD_CHEF only)
    """

    @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
    async def get(self, request: Request, group_id: UUID):
        """Gets group details. Requires membership in the group."""
        service = self._get_service(request)
        group = await service.get(group_id)

        response = GenericResponse(
            status="success",
            data=FamilyGroupDetailedSchema.model_validate(group)
        )
        return json(response.model_dump(exclude_none=True, mode='json'), status=200)

    @require_group_role(GroupRole.HEAD_CHEF)
    async def delete(self, request: Request, group_id: UUID):
        """Deletes a family group. Requires HEAD_CHEF role."""
        service = self._get_service(request)
        await service.delete(group_id)

        response = GenericResponse(status="success", message="Group deleted successfully.")
        return json(response.model_dump(mode='json'), status=200)


class GroupMembersView(BaseGroupView):
    """
    Handles /groups/{group_id}/members
    - GET: List all members (any member)
    - POST: Add new member (HEAD_CHEF only)
    """

    def _get_service(self, request) -> FamilyGroupService:
        session = request.ctx.db_session
        return FamilyGroupService(
            FamilyGroupRepository(session),
            GroupMembershipRepository(session),
            UserRepository(session)
        )

    @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
    async def get(self, request: Request, group_id: UUID):
        """Lists all members of the group. Requires membership."""
        service = self._get_service(request)
        # Optimized fetch
        members = await service.get_group_members(group_id)

        response = GenericResponse(
            status="success",
            data=[GroupMembershipSchema.model_validate(m) for m in members]
        )
        return json(response.model_dump(exclude_none=True, mode='json'), status=200)


    @require_group_role(GroupRole.HEAD_CHEF)
    @validate_request(AddMemberRequestSchema)
    async def post(self, request: Request, group_id: UUID):
        """Adds a member to the group. Requires HEAD_CHEF role."""
        requester_id = request.ctx.auth_payload["sub"]
        email = request.ctx.validated_data.email
        
        service = self._get_service(request)
        membership = await service.add_member_by_email(requester_id, group_id, email)
        
        # Fetch user details for response
        user_repo = UserRepository(request.ctx.db_session)
        user = await user_repo.get_by_id(membership.user_id)
        
        response_data = {
            "user": user,
            "role": membership.role
        }

        response = GenericResponse(
            status="success",
            message="Member added successfully.",
            data=GroupMembershipSchema.model_validate(response_data)
        )
        return json(response.model_dump(exclude_none=True, mode='json'), status=201)


class GroupMemberDetailView(BaseGroupView):
    """
    Handles /groups/{group_id}/members/{user_id}
    - GET: View detailed member info (User + Identity + Health)
    - PATCH: Update member role (HEAD_CHEF only - chuyển quyền HEAD_CHEF)
    - DELETE: Remove member (HEAD_CHEF only)
    """

    @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """
        View detailed member info. 
        Returns composite data: User Info + Role + Identity Profile + Health Profile.
        """
        service = self._get_service(request)
        # Optimized fetch with eager loading
        member_detailed = await service.get_group_member_detailed(group_id, user_id)

        response = GenericResponse(
            status="success",
            data=GroupMembershipDetailedSchema.model_validate(member_detailed)
        )
        return json(response.model_dump(exclude_none=True, mode='json'), status=200)

    @require_group_role(GroupRole.HEAD_CHEF)
    async def delete(self, request: Request, group_id: UUID, user_id: UUID):
        """Removes a member from the group. Requires HEAD_CHEF role."""
        requester_id = request.ctx.auth_payload["sub"]
        service = self._get_service(request)
        
        await service.remove_member(requester_id, group_id, user_id)
        
        response = GenericResponse(status="success", message="Member removed successfully.")
        return json(response.model_dump(mode='json'), status=200)


    @require_group_role(GroupRole.HEAD_CHEF)
    @validate_request(GroupMembershipUpdateSchema)
    async def patch(self, request: Request, group_id: UUID, user_id: UUID):
        """Updates member role (chuyển quyền HEAD_CHEF). Requires HEAD_CHEF role."""
        requester_id = request.ctx.auth_payload["sub"]
        new_role = request.ctx.validated_data.role
        
        service = self._get_service(request)
        membership = await service.update_member_role(requester_id, group_id, user_id, new_role)
        
        # Fetch user for response
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
        return json(response.model_dump(exclude_none=True, mode='json'), status=200)


class GroupMemberMeView(BaseGroupView):
    """
    Handles /groups/{group_id}/members/me
    - DELETE: Leave the group (any member, nhưng HEAD_CHEF phải chuyển quyền trước)
    """

    @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
    async def delete(self, request: Request, group_id: UUID):
        """Member leaves the group. Requires membership."""
        requester_id = request.ctx.auth_payload["sub"]
        service = self._get_service(request)
        
        # remove_member allows self-removal
        await service.remove_member(requester_id, group_id, requester_id)
        
        response = GenericResponse(status="success", message="You have left the group.")
        return json(response.model_dump(mode='json'), status=200)


class MemberIdentityProfileView(HTTPMethodView):
    """
    Handles /groups/{group_id}/members/{user_id}/identity-profile
    Allows members of the same group to view identity profiles.
    """

    @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """View member's identity profile. Requires membership in the group."""
        session = request.ctx.db_session
        member_repo = GroupMembershipRepository(session)
        
        # Ensure target user is also in the same group
        target_membership = await member_repo.get_membership(user_id, group_id)
        
        if not target_membership:
            raise Forbidden("Target user is not a member of this group.")

        service = UserIdentityProfileService(UserIdentityProfileRepository(session))
        profile = await service.get(user_id)
        
        if not profile:
             raise NotFound("Profile not found.")

        response = GenericResponse(status="success", data=UserIdentityProfileSchema.model_validate(profile))
        return json(response.model_dump(exclude_none=True, mode='json'), status=200)


class MemberHealthProfileView(HTTPMethodView):
    """
    Handles /groups/{group_id}/members/{user_id}/health-profile
    Allows members of the same group to view health profiles.
    """

    @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """View member's health profile. Requires membership in the group."""
        session = request.ctx.db_session
        member_repo = GroupMembershipRepository(session)
        
        # Ensure target user is also in the same group
        target_membership = await member_repo.get_membership(user_id, group_id)
        
        if not target_membership:
            raise Forbidden("Target user is not a member of this group.")

        service = UserHealthProfileService(UserHealthProfileRepository(session))
        profile = await service.get(user_id)
        
        if not profile:
             raise NotFound("Profile not found.")
        
        response = GenericResponse(status="success", data=UserHealthProfileSchema.model_validate(profile))
        return json(response.model_dump(exclude_none=True, mode='json'), status=200)
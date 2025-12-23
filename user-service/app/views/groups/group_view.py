# app/views/groups/group_view.py
from uuid import UUID
from sanic import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from shopping_shared.schemas.response_schema import GenericResponse, SuccessResponse
from shopping_shared.exceptions import BadRequest

from app.decorators.validate_request import validate_request
from app.decorators.idempotency import idempotent
from app.schemas.family_group_schema import (
    FamilyGroupCreateSchema,
    FamilyGroupDetailedSchema,
    FamilyGroupMemberSchema
)
from app.enums import GroupRole
from app.repositories.family_group_repository import FamilyGroupRepository, GroupMembershipRepository
from app.repositories.user_repository import UserRepository
from app.services.family_group_service import FamilyGroupService


class GroupView(HTTPMethodView):

    @validate_request(FamilyGroupCreateSchema)
    @idempotent()
    async def post(self, request: Request):
        """Creates a new family group."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        # Init dependencies
        session = request.ctx.db_session
        service = FamilyGroupService(
            FamilyGroupRepository(session),
            GroupMembershipRepository(session),
            UserRepository(session)
        )

        group = await service.create_group(user_id, validated_data)

        # Refresh or fetch detailed info to include members/creator for response
        # Assuming Lazy loading works or we re-fetch with eager loading if needed.
        # For simplicity, returning the group object which Pydantic will serialize.
        # Note: Ideally, use a service method to get_detailed_group.
        
        response = GenericResponse(
            status="success",
            message="Group created successfully.",
            data=FamilyGroupDetailedSchema.model_validate(group)
        )
        return json(response.model_dump(exclude_none=True), status=201)

    async def delete(self, request: Request, group_id: UUID):
        """Deletes a family group."""
        user_id = request.ctx.auth_payload["sub"]

        session = request.ctx.db_session
        service = FamilyGroupService(
            FamilyGroupRepository(session),
            GroupMembershipRepository(session),
            UserRepository(session)
        )

        await service.delete_group(user_id, group_id)

        response = SuccessResponse(message="Group deleted successfully.")
        return json(response.model_dump(), status=200)


class GroupMemberView(HTTPMethodView):
    # ... (giữ nguyên các method cũ) ...
    pass # placeholder for existing GroupMemberView

class MemberIdentityProfileView(HTTPMethodView):
    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """Allows members of the same group to view identity profiles."""
        requester_id = request.ctx.auth_payload["sub"]
        
        session = request.ctx.db_session
        # Permission Check
        member_repo = GroupMembershipRepository(session)
        
        # Ensure both are in the same group
        requester_membership = await member_repo.session.get(GroupMembership, (requester_id, group_id))
        target_membership = await member_repo.session.get(GroupMembership, (user_id, group_id))
        
        if not requester_membership or not target_membership:
            raise Forbidden("You must be in the same group to view this profile.")
            
        # Fetch Profile
        service = UserIdentityProfileService(UserIdentityProfileRepository(session))
        profile = await service.get(user_id)
        
        response = GenericResponse(status="success", data=UserIdentityProfileSchema.model_validate(profile))
        return json(response.model_dump(exclude_none=True), status=200)


class MemberHealthProfileView(HTTPMethodView):
    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """Allows members of the same group to view health profiles."""
        requester_id = request.ctx.auth_payload["sub"]
        
        session = request.ctx.db_session
        member_repo = GroupMembershipRepository(session)
        
        requester_membership = await member_repo.session.get(GroupMembership, (requester_id, group_id))
        target_membership = await member_repo.session.get(GroupMembership, (user_id, group_id))
        
        if not requester_membership or not target_membership:
            raise Forbidden("You must be in the same group to view this profile.")
            
        service = UserHealthProfileService(UserHealthProfileRepository(session))
        profile = await service.get(user_id)
        
        response = GenericResponse(status="success", data=UserHealthProfileSchema.model_validate(profile))
        return json(response.model_dump(exclude_none=True), status=200)

# user-service/app/views/groups/group_profile_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import require_group_role
from app.enums import GroupRole
from app.views.base_view import BaseAPIView
from app.repositories.user_profile_repository import (
    UserIdentityProfileRepository,
    UserHealthProfileRepository
)
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.services.user_profile_service import (
    UserIdentityProfileService,
    UserHealthProfileService
)
from app.schemas.user_profile_schema import (
    UserIdentityProfileSchema,
    UserHealthProfileSchema
)

from shopping_shared.exceptions import NotFound
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

logger = get_logger("Group Profile View")


class MemberIdentityProfileView(BaseAPIView):
    """Handles identity profile of group members."""

    @openapi.definition(
        summary="User identity profile of a group member.v",
        description="Retrieves the identity profile of a specific group member.",
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserIdentityProfileSchema),
                status=200,
                description="User identity profile of a specific group member."
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=404,
                description="Unauthorize"
            )
        ]
    )
    @require_group_role(GroupRole.MEMBER, GroupRole.HEAD_CHEF)
    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """Get identity profile of a specific group member."""
        profile_repo = UserIdentityProfileRepository(session=request.ctx.db_session)
        membership_repo = GroupMembershipRepository(session=request.ctx.db_session)
        profile_service = UserIdentityProfileService(profile_repo)

        try:
            # Verify that user_id is a member of group_id
            membership = await membership_repo.get_membership(user_id, group_id)
            if not membership:
                return self.error_response(
                    message="User is not a member of this group",
                    status_code=404
                )

            profile = await profile_service.get(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserIdentityProfileSchema.model_validate(profile),
                message="Identity profile retrieved successfully",
                status_code=200
            )
        except NotFound:
            # Use helper method from base class
            return self.error_response(
                message="Identity profile not found",
                status_code=404
            )
        except Exception as e:
            logger.error("Failed to retrieve identity profile", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve identity profile",
                status_code=500
            )


class MemberHealthProfileView(BaseAPIView):
    """Handles health profile of group members."""

    @openapi.definition(
        summary="User health profile of a group member.",
        description="Retrieves the health profile of a specific group member.",
        tag=["Family Groups", "Group Memberships"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserHealthProfileSchema),
                status=200,
                description="User health profile of a specific group member."
            )
        ]
    )
    @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """Get health profile of a specific group member."""
        profile_repo = UserHealthProfileRepository(session=request.ctx.db_session)
        membership_repo = GroupMembershipRepository(session=request.ctx.db_session)
        profile_service = UserHealthProfileService(profile_repo)

        try:
            # Verify that user_id is a member of group_id
            membership = await membership_repo.get_membership(user_id, group_id)
            if not membership:
                return self.error_response(
                    message="User is not a member of this group",
                    status_code=404
                )

            profile = await profile_service.get(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserHealthProfileSchema.model_validate(profile),
                message="Health profile retrieved successfully",
                status_code=200
            )
        except NotFound:
            # Use helper method from base class
            return self.error_response(
                message="Health profile not found",
                status_code=404
            )
        except Exception as e:
            logger.error("Failed to retrieve health profile", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve health profile",
                status_code=500
            )
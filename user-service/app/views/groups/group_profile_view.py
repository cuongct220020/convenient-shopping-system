# user-service/app/views/groups/group_profile_view.py
from uuid import UUID
from sanic import Request
from sanic_ext import openapi

from shopping_shared.exceptions import NotFound
from shopping_shared.sanic.schemas import DocGenericResponse

from app.decorators import require_group_role, api_response
from app.views.base_view import BaseAPIView
from app.enums import GroupRole
from app.repositories.user_profile_repository import (
    UserIdentityProfileRepository,
    UserHealthProfileRepository
)
from app.services.user_profile_service import (
    UserIdentityProfileService,
    UserHealthProfileService
)
from app.schemas import (
    UserIdentityProfileSchema,
    UserHealthProfileSchema,
    UserIdentityProfileResponseSchema,
    UserHealthProfileResponseSchema
)


class MemberIdentityProfileView(BaseAPIView):
    """Handles identity profile of group members."""

    decorators = [
        require_group_role(),  # Any group member can access member profiles
        openapi.tag("Group Members - Profiles"),
        openapi.secured("bearerAuth")
    ]

    @openapi.summary("Get member's identity profile")
    @openapi.description("Retrieves the identity profile of a specific group member.")
    @openapi.response(200, UserIdentityProfileResponseSchema)
    @api_response(
        success_schema=UserIdentityProfileResponseSchema,
        success_status=200,
        success_description="Identity profile retrieved successfully"
    )
    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """Get identity profile of a specific group member."""
        profile_repo = UserIdentityProfileRepository(session=request.ctx.db_session)
        profile_service = UserIdentityProfileService(profile_repo)

        try:
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
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve identity profile",
                status_code=500
            )


class MemberHealthProfileView(BaseAPIView):
    """Handles health profile of group members."""

    decorators = [
        require_group_role(),  # Any group member can access member profiles
        openapi.tag("Group Members - Profiles"),
        openapi.secured("bearerAuth")
    ]

    @openapi.summary("Get member's health profile")
    @openapi.description("Retrieves the health profile of a specific group member.")
    @openapi.response(200, UserHealthProfileResponseSchema)
    @api_response(
        success_schema=UserHealthProfileResponseSchema,
        success_status=200,
        success_description="Health profile retrieved successfully"
    )
    async def get(self, request: Request, group_id: UUID, user_id: UUID):
        """Get health profile of a specific group member."""
        profile_repo = UserHealthProfileRepository(session=request.ctx.db_session)
        profile_service = UserHealthProfileService(profile_repo)

        try:
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
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve health profile",
                status_code=500
            )
# user-service/app/views/users/me_profile_view.py
from sanic import Request
from sanic.views import HTTPMethodView
from sanic_ext import openapi

from shopping_shared.exceptions import NotFound
from shopping_shared.sanic.schemas import DocGenericResponse

from app.decorators import validate_request, api_response
from app.views.base_view import BaseAPIView
from app.decorators.auth_decorators import auth_required
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
    UserIdentityProfileUpdateSchema,
    UserHealthProfileSchema,
    UserHealthProfileUpdateSchema,
    UserIdentityProfileResponseSchema,
    UserHealthProfileResponseSchema
)

from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Me Profile View")


class MeIdentityProfileView(BaseAPIView):
    """Manages the identity profile for the authenticated user."""

    @openapi.summary("Get identity profile")
    @openapi.description("Retrieves the identity profile (gender, DOB, etc.) of the authenticated user.")
    @auth_required()
    @api_response(
        success_schema=UserIdentityProfileResponseSchema,
        success_status=200,
        success_description="Identity profile retrieved successfully"
    )
    @openapi.tag("Profile")
    async def get(self, request: Request):
        """Retrieves the identity profile of the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]

        user_identity_profile_repo = UserIdentityProfileRepository(session=request.ctx.db_session)
        user_identity_profile_service = UserIdentityProfileService(user_identity_profile_repo)

        try:
            profile = await user_identity_profile_service.get(user_id)
            data = UserIdentityProfileSchema.model_validate(profile)

            # Use helper method from base class
            return self.success_response(
                data=data,
                message="Identity profile found",
                status_code=200
            )
        except NotFound:
            # Use helper method from base class
            return self.error_response(
                message="Identity profile not found.",
                status_code=404
            )
        except Exception as e:
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve identity profile",
                status_code=500
            )

    @openapi.summary("Update identity profile")
    @openapi.description("Updates (or creates) the identity profile for the authenticated user.")
    @auth_required()
    @api_response(
        success_schema=UserIdentityProfileResponseSchema,
        success_status=200,
        success_description="Identity profile updated successfully"
    )
    @openapi.tag("Profile")
    @validate_request(UserIdentityProfileUpdateSchema)
    async def patch(self, request: Request):
        """Updates the identity profile of the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_identity_profile_repo = UserIdentityProfileRepository(session=request.ctx.db_session)
        user_identity_profile_service = UserIdentityProfileService(user_identity_profile_repo)

        try:
            updated_profile = await user_identity_profile_service.update(user_id, validated_data)

            # Use helper method from base class
            return self.success_response(
                data=UserIdentityProfileSchema.model_validate(updated_profile),
                message="Identity profile updated.",
                status_code=200
            )
        except NotFound:
            # Upsert logic
            create_data = validated_data.model_dump()
            create_data['user_id'] = user_id
            updated_profile = await user_identity_profile_repo.create(create_data)

            # Use helper method from base class
            return self.success_response(
                data=UserIdentityProfileSchema.model_validate(updated_profile),
                message="Identity profile created.",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            return self.error_response(
                message="Failed to update identity profile",
                status_code=500
            )


class MeHealthProfileView(BaseAPIView):
    """Manages the health profile for the authenticated user."""

    @openapi.summary("Get health profile")
    @openapi.description("Retrieves the health profile (height, weight, etc.) of the authenticated user.")
    @auth_required()
    @api_response(
        success_schema=UserHealthProfileResponseSchema,
        success_status=200,
        success_description="Health profile retrieved successfully"
    )
    @openapi.tag("Profile")
    async def get(self, request: Request):
        """Retrieves the health profile of the authenticated user."""

        user_id = request.ctx.auth_payload["sub"]

        user_health_profile_repo = UserHealthProfileRepository(request.ctx.db_session)
        user_health_service = UserHealthProfileService(user_health_profile_repo)

        try:
            profile = await user_health_service.get(user_id)
            data = UserHealthProfileSchema.model_validate(profile)

            # Use helper method from base class
            return self.success_response(
                data=data,
                status_code=200
            )
        except NotFound:
            # Use helper method from base class
            return self.error_response(
                message="Health profile not found.",
                status_code=404
            )
        except Exception as e:
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve health profile",
                status_code=500
            )

    @openapi.summary("Update health profile")
    @openapi.description("Updates (or creates) the health profile for the authenticated user.")
    @auth_required()
    @api_response(
        success_schema=UserHealthProfileResponseSchema,
        success_status=200,
        success_description="Health profile updated successfully"
    )
    @openapi.tag("Profile")
    @validate_request(UserHealthProfileUpdateSchema)
    async def patch(self, request: Request):
        """Updates the health profile of the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_health_profile_repo = UserHealthProfileRepository(request.ctx.db_session)
        user_health_service = UserHealthProfileService(user_health_profile_repo)

        try:
            updated_profile = await user_health_service.update(user_id, validated_data)
        except NotFound:
            # Upsert logic
            create_data = validated_data.model_dump()
            create_data['user_id'] = user_id
            updated_profile = await user_health_profile_repo.create(create_data)

        # Use helper method from base class
        return self.success_response(
            data=UserHealthProfileSchema.model_validate(updated_profile),
            message="Health profile updated.",
            status_code=200
        )
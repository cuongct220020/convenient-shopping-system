# user-service/app/views/users/me_profile_view.py
from sanic import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request
from app.decorators.cache_response import cache_response
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.views.base_view import BaseAPIView
from app.repositories.user_profile_repository import (
    UserIdentityProfileRepository,
    UserHealthProfileRepository
)
from app.services.user_profile_service import (
    UserIdentityProfileService,
    UserHealthProfileService
)
from app.schemas.user_profile_schema import (
    UserIdentityProfileSchema,
    UserIdentityProfileUpdateSchema,
    UserHealthProfileSchema,
    UserHealthProfileUpdateSchema
)
from shopping_shared.caching.redis_keys import RedisKeys

from shopping_shared.exceptions import NotFound
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

logger = get_logger("Me Profile View")


class MeIdentityProfileView(BaseAPIView):
    """Manages the identity profile for the authenticated user."""


    @openapi.definition(
        summary="Retrieve authenticated user's identity profile",
        description="Retrieves the identity profile information for the authenticated user, including gender, date of birth, first name, last name, and other personal identity details.",
        tag=["User Profile"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserIdentityProfileSchema),
                status=200,
                description="Successfully retrieved the authenticated user's identity profile information.",
            )
        ]
    )
    @cache_response(key_pattern=RedisKeys.USER_PROFILE_IDENTITY, ttl=900)
    async def get(self, request: Request):
        """
        Retrieves the identity profile of the authenticated user.
        GET /api/v1/user-service/users/me/profile/identity
        """
        user_id = request.ctx.auth_payload["sub"]

        user_identity_profile_repo = UserIdentityProfileRepository(session=request.ctx.db_session)
        group_membership_repo = GroupMembershipRepository(session=request.ctx.db_session)
        user_identity_profile_service = UserIdentityProfileService(user_identity_profile_repo, group_membership_repo)

        try:
            profile = await user_identity_profile_service.get_identity_profile(user_id)
            data = UserIdentityProfileSchema.model_validate(profile)

            # Use helper method from base class
            return self.success_response(
                data=data,
                message="Identity profile found",
                status_code=200
            )
        except NotFound:
            # Use helper method from base class
            return self.fail_response(
                message="Identity profile not found.",
                status_code=404
            )
        except Exception as e:
            logger.error("Failed to retrieve identity profile", exc_info=e)
            # Use helper method from base class
            return self.fail_response(
                message="Failed to retrieve identity profile",
                status_code=500
            )


    @openapi.definition(
        summary="Update authenticated user's identity profile",
        description="Updates the identity profile information for the authenticated user. If no profile exists, creates a new one. Only provided fields will be updated.",
        body=get_openapi_body(UserIdentityProfileUpdateSchema),
        tag=["User Profile"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserIdentityProfileSchema),
                status=200,
                description="Successfully updated the authenticated user's identity profile information.",
            )
        ]
    )
    @validate_request(UserIdentityProfileUpdateSchema)
    async def patch(self, request: Request):
        """
        Updates the identity profile of the authenticated user."
        PATCH /api/v1/user-service/users/me/profile/identity
        """
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_identity_profile_repo = UserIdentityProfileRepository(session=request.ctx.db_session)
        group_membership_repo = GroupMembershipRepository(session=request.ctx.db_session)
        user_identity_profile_service = UserIdentityProfileService(user_identity_profile_repo, group_membership_repo)

        try:
            updated_profile = await user_identity_profile_service.update_identity_profile(user_id, validated_data)

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
            logger.error("Failed to update identity profile", exc_info=e)
            # Use helper method from base class
            return self.fail_response(
                message="Failed to update identity profile",
                status_code=500
            )


class MeHealthProfileView(BaseAPIView):
    """Manages the health profile for the authenticated user."""

    @openapi.definition(
        summary="Retrieve authenticated user's health profile",
        description="Retrieves the health profile information for the authenticated user, including height, weight, medical conditions, allergies, and other health-related details.",
        tag=["User Profile"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserHealthProfileSchema),
                status=200,
                description="Successfully retrieved the authenticated user's health profile information.",
            )
        ]
    )
    @cache_response(key_pattern=RedisKeys.USER_PROFILE_HEALTH, ttl=900)
    async def get(self, request: Request):
        """
        Retrieves the health profile of the authenticated user.
        GET /api/v1/user-service/users/me/profile/health
        """

        user_id = request.ctx.auth_payload["sub"]

        user_health_profile_repo = UserHealthProfileRepository(request.ctx.db_session)
        group_membership_repo = GroupMembershipRepository(request.ctx.db_session)
        user_health_service = UserHealthProfileService(user_health_profile_repo, group_membership_repo)

        try:
            profile = await user_health_service.get_health_profile(user_id)
            data = UserHealthProfileSchema.model_validate(profile)

            # Use helper method from base class
            return self.success_response(
                data=data,
                status_code=200
            )
        except NotFound:
            # Use helper method from base class
            return self.fail_response(
                message="Health profile not found.",
                status_code=404
            )
        except Exception as e:
            logger.error("Failed to retrieve health profile", exc_info=e)
            # Use helper method from base class
            return self.fail_response(
                message="Failed to retrieve health profile",
                status_code=500
            )


    @openapi.definition(
        summary="Update authenticated user's health profile",
        description="Updates the health profile information for the authenticated user. If no profile exists, creates a new one. Only provided fields will be updated.",
        body=get_openapi_body(UserHealthProfileUpdateSchema),
        tag=["User Profile"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserHealthProfileSchema),
                status=200,
                description="Successfully updated the authenticated user's health profile information.",
            )
        ]
    )
    @validate_request(UserHealthProfileUpdateSchema)
    async def patch(self, request: Request):
        """
        Updates the health profile of the authenticated user.
        PATCH /api/v1/user-service/users/me/profile/health
        """
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_health_profile_repo = UserHealthProfileRepository(request.ctx.db_session)
        group_membership_repo = GroupMembershipRepository(request.ctx.db_session)
        user_health_service = UserHealthProfileService(user_health_profile_repo, group_membership_repo)

        try:
            updated_profile = await user_health_service.update_health_profile(user_id, validated_data)
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
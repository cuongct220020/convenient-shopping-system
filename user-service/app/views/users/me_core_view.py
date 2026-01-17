# user-service/app/views/users/me_core_view.py
from sanic.request import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request
from app.decorators.cache_response import cache_response
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user_schema import UserInfoUpdateSchema, UserCoreInfoSchema

from shopping_shared.utils.openapi_utils import get_openapi_body
from shopping_shared.caching.redis_keys import RedisKeys


class MeView(BaseAPIView):
    """View to manage the authenticated user's core information."""

    @openapi.definition(
        summary="Retrieve current user's profile information",
        description="Retrieves the authenticated user's core profile information including user ID, username, email address, first name, last name, phone number, and avatar URL.",
        tag=["User Profile"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserCoreInfoSchema),
                status=200,
                description="Successfully retrieved the authenticated user's profile information.",
            )
        ]
    )
    @cache_response(key_pattern=RedisKeys.USER_CORE, ttl=900)
    async def get(self, request: Request):
        """
        Get current user info.
        GET /api/v1/user-service/users/me
        """
        user_id = request.ctx.auth_payload["sub"]

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo=user_repo)

        try:
            user = await user_service.get_user_core_info(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserCoreInfoSchema.model_validate(user),
                message="User information retrieved successfully.",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            return self.fail_response(
                message="Failed to retrieve user information",
                status_code=500
            )



    @openapi.definition(
        summary="Update current user's profile information",
        description="Updates the authenticated user's core profile information such as username, first name, last name, phone number, and avatar URL. Only provided fields will be updated.",
        tag=["User Profile"],
        body=get_openapi_body(UserInfoUpdateSchema),
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserCoreInfoSchema),
                status=200,
                description="Successfully updated the authenticated user's profile information.",
            )
        ]
    )
    @validate_request(UserInfoUpdateSchema)
    async def patch(self, request: Request):
        """
        Update current user info.
        PATCH /api/v1/user-service/users/me
        """
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(session=request.ctx.db_session)
        user_service = UserService(user_repo=user_repo)

        try:
            updated_user = await user_service.update_user_core_info(user_id, validated_data)

            # Use helper method from base class
            return self.success_response(
                data=UserCoreInfoSchema.model_validate(updated_user),
                message="User information updated.",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            return self.fail_response(
                message="Failed to update user information",
                status_code=500
            )
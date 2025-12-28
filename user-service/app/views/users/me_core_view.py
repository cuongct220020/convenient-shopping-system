# user-service/app/views/users/me_core_view.py
from sanic.request import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user_schema import UserInfoUpdateSchema, UserCoreInfoSchema

from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

logger = get_logger("Me Core View")

class MeView(BaseAPIView):
    """View to manage the authenticated user's core information."""

    @openapi.definition(
        summary="Get current user's core info",
        description="Retrieves the core information (id, username, email, names, etc.) for the authenticated user.",
        tag=["User Profile"],
        secured={"bearAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserCoreInfoSchema),
                status=200,
                description="Get core information (id, username, email, names, etc.) successfully.",
            )
        ]
    )
    async def get(self, request: Request):
        """
        Get current user info.
        GET /api/v1/user-service/users/me
        """
        user_id = request.ctx.auth_payload["sub"]

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo=user_repo)

        try:
            user = await user_service.get(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserCoreInfoSchema.model_validate(user),
                message="User information retrieved successfully.",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to retrieve user info", exc_info=e)
            # Use helper method from base class
            return self.fail_response(
                message="Failed to retrieve user information",
                status_code=500
            )



    @openapi.definition(
        summary="Get current user's core info",
        description="Retrieves the core information from the authenticated user.",
        tag=["User Profile"],
        body=get_openapi_body(UserInfoUpdateSchema),
        secured={"bearAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserCoreInfoSchema),
                status=200,
                description="Update core information (id, username, email, names, etc.) successfully.",
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
            updated_user = await user_service.update(user_id, validated_data)

            # Use helper method from base class
            return self.success_response(
                data=UserCoreInfoSchema.model_validate(updated_user),
                message="User information updated.",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to update user info", exc_info=e)
            # Use helper method from base class
            return self.fail_response(
                message="Failed to update user information",
                status_code=500
            )
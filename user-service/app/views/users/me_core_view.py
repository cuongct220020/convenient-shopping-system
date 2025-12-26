# user-service/app/views/users/me_core_view.py
from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic_ext import openapi

from app.decorators import validate_request, api_response
from app.views.base_view import BaseAPIView
from app.decorators.auth_decorators import auth_required
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas import UserInfoUpdateSchema, UserInfoResponseSchema
from app.schemas.user_schema import UserInfoSchema

from shopping_shared.sanic.schemas import DocGenericResponse


class MeView(BaseAPIView):
    """View to manage the authenticated user's core information."""

    @openapi.summary("Get current user's core info")
    @openapi.description("Retrieves the core information (id, username, email, names, etc.) for the authenticated user.")
    @auth_required()
    @api_response(
        success_schema=UserInfoResponseSchema,
        success_status=200,
        success_description="User information retrieved successfully"
    )
    @openapi.tag("Profile")
    async def get(self, request: Request):
        """Get current user info."""
        user_id = request.ctx.auth_payload["sub"]

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo=user_repo)

        try:
            user = await user_service.get(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserInfoSchema.model_validate(user),
                message="User information retrieved successfully.",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve user information",
                status_code=500
            )

    @openapi.summary("Update current user's core info")
    @openapi.description("Updates the core information for the authenticated user.")
    @auth_required()
    @api_response(
        success_schema=UserInfoResponseSchema,
        success_status=200,
        success_description="User information updated successfully"
    )
    @openapi.tag("Profile")
    @validate_request(UserInfoUpdateSchema)
    async def patch(self, request: Request):
        """Update current user info."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(session=request.ctx.db_session)
        user_service = UserService(user_repo=user_repo)

        try:
            updated_user = await user_service.update(user_id, validated_data)

            # Use helper method from base class
            return self.success_response(
                data=UserInfoSchema.model_validate(updated_user),
                message="User information updated.",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            return self.error_response(
                message="Failed to update user information",
                status_code=500
            )
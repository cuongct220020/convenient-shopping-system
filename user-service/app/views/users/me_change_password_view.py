# user-service/app/views/users/me_change_password_view.py
from sanic.request import Request
from sanic_ext import openapi

from app.decorators import validate_request
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import ChangePasswordRequestSchema
from app.services.user_service import UserService

from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Me Change Password View")

class ChangePasswordView(BaseAPIView):
    """Handles changing the password for an authenticated user."""

    @openapi.summary("Change password (when logged in)")
    @openapi.description("Allows an authenticated user to change their own password by providing the current password.")
    @openapi.tag("Profile")
    @validate_request(ChangePasswordRequestSchema)
    async def post(self, request: Request):
        """Handles changing the password for the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(session=request.ctx.db_session)
        user_service = UserService(user_repo=user_repo)

        try:
            await user_service.change_password(user_id=user_id, data=validated_data)

            # Use helper method from base class
            return self.success_response(
                message="Password changed successfully. All sessions have been logged out.",
                data=None,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to change password: {str(e)}", exc_info=True)
            # Use helper method from base class
            return self.error_response(
                message="Failed to change password. Please try again.",
                status_code=500
            )
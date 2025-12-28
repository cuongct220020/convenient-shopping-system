# user-service/app/views/auth/reset_password_view.py
from sanic.request import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import ResetPasswordRequestSchema
from app.services.auth_service import AuthService

from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.openapi_utils import get_openapi_body


class ResetPasswordView(BaseAPIView):
    """Handles resetting the user's password using a valid OTP."""

    @openapi.definition(
        summary="Reset forgotten password",
        description="Resets a user's password after verifying a valid OTP for the 'reset_password' action",
        body=get_openapi_body(ResetPasswordRequestSchema),
        tag=["Authentication"],
        response=[
            Response(content=get_openapi_body(GenericResponse), status=200, description="Reset password successfully."),
            Response(content=get_openapi_body(GenericResponse), status=401, description="Invalid or missing authentication token")
        ]
    )
    @validate_request(ResetPasswordRequestSchema)
    async def post(self, request: Request):
        """Handles resetting the user's password using a valid OTP."""
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(session=request.ctx.db_session)

        # Updated to call the explicit service method
        await AuthService.reset_password_with_otp(
            reset_pw_data=validated_data,
            user_repo=user_repo
        )

        # Use helper method from base class
        return self.success_response(
            message="Password has been reset successfully.",
            data=None,
            status_code=200
        )
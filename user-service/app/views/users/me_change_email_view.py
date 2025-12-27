# user-service/app/views/users/me_change_email_view.py
from sanic.request import Request
from sanic_ext import openapi

from app.decorators import validate_request
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import RequestEmailChangeSchema, ConfirmEmailChangeRequestSchema
from app.schemas.otp_schema import OTPRequestSchema
from app.services.auth_service import AuthService
from app.enums import OtpAction

from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Me Change Email View")


class MeRequestChangeEmailView(BaseAPIView):
    """View for Step 1 of changing email: Requesting an OTP."""

    @openapi.summary("Request email change (Step 1)")
    @openapi.description("Requests an OTP to be sent to the desired new email address.")
    @openapi.tag("Profile")
    @validate_request(RequestEmailChangeSchema)
    async def post(self, request: Request):
        """Step 1: Request an OTP to change email."""
        new_email = request.ctx.validated_data.new_email
        user_repo = UserRepository(session=request.ctx.db_session)

        try:
            # Re-use the centralized logic in AuthService for sending OTP
            otp_req = OTPRequestSchema(email=new_email, action=OtpAction.CHANGE_EMAIL)

            # Capture OTP code (useful for debug mode)
            otp_code = await AuthService.request_otp(
                otp_data=otp_req,
                user_repo=user_repo
            )

            response_data = None
            if request.app.config.get("DEBUG"):
                response_data = {"otp_code": otp_code}

            # Use helper method from base class
            return self.success_response(
                message="OTP sent to your new email address.",
                data=response_data,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to send OTP to new email address: {e}")
            # Use helper method from base class
            return self.error_response(
                message="Failed to send OTP. Please try again.",
                status_code=500
            )


class MeConfirmChangeEmailView(BaseAPIView):
    """View for Step 2 of changing email: Confirming with OTP."""

    @openapi.summary("Confirm email change (Step 2)")
    @openapi.description("Confirms the email address change by providing the OTP sent to the new email.")
    @openapi.tag("Profile")
    @validate_request(ConfirmEmailChangeRequestSchema)
    async def post(self, request: Request):
        """Step 2: Confirm email change with OTP."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(request.ctx.db_session)

        try:
            # Delegate to AuthService for atomic verification and update
            await AuthService.change_email_with_otp(
                user_id=user_id,
                change_data=validated_data,
                user_repo=user_repo
            )

            # Use helper method from base class
            return self.success_response(
                message="Email updated successfully. Please login again.",
                data=None,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to send OTP to new email address: {e}")
            # Use helper method from base class
            return self.error_response(
                message="Failed to confirm email change. Please try again.",
                status_code=500
            )
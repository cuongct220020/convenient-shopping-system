# user-service/app/views/auth/otp_view.py
from sanic.request import Request
from sanic_ext import openapi

from app.decorators import validate_request, api_response
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.schemas import OTPRequestSchema, RegisterVerifyRequestSchema
from app.services.auth_service import AuthService
from shopping_shared.sanic.schemas import DocGenericResponse


class OTPRequestView(BaseAPIView):
    """View to handle the generation and sending of a new OTP."""

    @validate_request(OTPRequestSchema)
    @api_response(
        success_schema=DocGenericResponse,
        success_status=200,
        success_description="OTP sent successfully"
    )
    async def post(self, request: Request):
        """Handles the logic to request and send an OTP for a specific action."""
        otp_data = request.ctx.validated_data
        user_repo = UserRepository(session=request.ctx.db_session)

        # Capture the returned OTP code from the service
        otp_code = await AuthService.request_otp(
            otp_data=otp_data,
            user_repo=user_repo
        )

        # Prepare response data, including the OTP only if in DEBUG mode
        response_data = None
        if request.app.config.get("DEBUG"):
            response_data = {"otp_code": otp_code}

        # For security, always return a generic success message.
        # Use helper method from base class
        return self.success_response(
            message="If your request was valid, an OTP has been sent to the specified email address.",
            data=response_data,
            status_code=200
        )


class RegisterVerificationView(BaseAPIView):
    """Handles the verification of an OTP for account registration."""

    @openapi.summary("Verify Registration (Activate Account)")
    @openapi.description("Verifies the OTP to complete the registration process and activate the user account.")
    @openapi.body(RegisterVerifyRequestSchema)
    @openapi.response(200, DocGenericResponse)
    @openapi.tag("Authentication")
    @validate_request(RegisterVerifyRequestSchema)
    @api_response(
        success_schema=DocGenericResponse,
        success_status=200,
        success_description="Account activated successfully"
    )
    async def post(self, request: Request):
        """
        Verifies the submitted OTP to activate an account.
        """
        validated_data = request.ctx.validated_data
        user_repo = UserRepository(session=request.ctx.db_session)

        await AuthService.activate_account_with_otp(
            verify_data=validated_data,
            user_repo=user_repo
        )
        message = "Account activated successfully."

        # Use helper method from base class
        return self.success_response(
            message=message,
            data=None,
            status_code=200
        )
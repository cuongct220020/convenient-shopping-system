# user-service/app/views/auth/otp_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas import OTPRequestSchema, RegisterVerifyRequestSchema
from app.services.auth_service import AuthService
from app.enums import OtpAction
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.exceptions import BadRequest


class OTPRequestView(HTTPMethodView):
    """View to handle the generation and sending of a new OTP."""

    @validate_request(OTPRequestSchema)
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
        response = GenericResponse(
            status="success",
            message="If your request was valid, an OTP has been sent to the specified email address.",
            data=response_data
        )

        return json(response.model_dump(mode="json"), status=200)


class RegisterVerificationView(HTTPMethodView):
    """Handles the verification of an OTP for account registration."""

    @validate_request(RegisterVerifyRequestSchema)
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
        
        response = GenericResponse(
            status="success",
            message=message,
            data=None
        )

        return json(response.model_dump(mode="json"), status=200)
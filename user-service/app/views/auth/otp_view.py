# user-service/app/views/auth/otp_view.py
from sanic.request import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.schemas.otp_schema import OTPRequestSchema, OTPVerifyRequestSchema
from app.services.auth_service import AuthService
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.openapi_utils import get_openapi_body


class OTPRequestView(BaseAPIView):
    """View to handle the generation and sending of a new OTP."""

    @openapi.definition(
        summary="OTP",
        description="Generate a new OTP using an existing OTP",
        body=get_openapi_body(OTPRequestSchema),
        tag=["Authentication"],
        response=[
            Response(
                content=get_openapi_body(GenericResponse),
                status=200,
                description="Successfully."
            )
        ]
    )
    @validate_request(OTPRequestSchema)
    async def post(self, request: Request):
        """
        Handles the logic to request and send an OTP for a specific action.
        POST /api/v1/user-service/auth/otp/send
        """
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


class OTPVerificationView(BaseAPIView):
    """Handles the verification of an OTP for account registration."""

    @openapi.definition(
        summary="OTP Verification",
        description="Verify summited OTP",
        body=get_openapi_body(OTPVerifyRequestSchema),
        tag=["Authentication"],
        response=[
            Response(GenericResponse, status=200, description="Verify OTP Successfully."),
        ]
    )
    @validate_request(OTPVerifyRequestSchema)
    async def post(self, request: Request):
        """
        Verifies the submitted OTP to activate an account.
        POST /api/v1/user-service/auth/otp/verify
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
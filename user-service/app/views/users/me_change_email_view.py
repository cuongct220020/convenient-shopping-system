# user-service/app/views/users/me_change_email_view.py
from sanic.request import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import RequestEmailChangeSchema, ConfirmEmailChangeRequestSchema
from app.schemas.otp_schema import OTPRequestSchema
from app.services.auth_service import AuthService
from app.enums import OtpAction
from shopping_shared.schemas.response_schema import GenericResponse

from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

logger = get_logger("Me Change Email View")


class MeRequestChangeEmailView(BaseAPIView):
    """View for Step 1 of changing email: Requesting an OTP."""


    @openapi.definition(
        summary="Request email address change",
        description="Initiates the process of changing the authenticated user's email address by sending a One-Time Password (OTP) to the new email address for verification.",
        secured={"bearerAuth": []},
        body=get_openapi_body(RequestEmailChangeSchema),
        tag=["User Profile"],
        response=[
            Response(
                content=get_openapi_body(GenericResponse),
                status=200,
                description="OTP sent successfully to the new email address for verification.",
            )
        ]
    )
    @validate_request(RequestEmailChangeSchema)
    async def post(self, request: Request):
        """
        Request an OTP to change email
        POST /api/v1/user-service/users/me/email/request-change
        """

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
            return self.fail_response(
                message="Failed to send OTP. Please try again.",
                status_code=500
            )


class MeConfirmChangeEmailView(BaseAPIView):
    """View for Step 2 of changing email: Confirming with OTP."""

    @openapi.definition(
        summary="Confirm email address change with OTP",
        description="Completes the email address change process by verifying the One-Time Password (OTP) sent to the new email address and updating the user's email in the system.",
        secured={"bearerAuth": []},
        body=get_openapi_body(ConfirmEmailChangeRequestSchema),
        tag=["User Profile"],
        response=[
            Response(
                content=get_openapi_body(GenericResponse),
                status=200,
                description="Email address updated successfully. Please log in again with the new email.",
            )
        ]
    )
    @validate_request(ConfirmEmailChangeRequestSchema)
    async def post(self, request: Request):
        """
        Confirm email change with OTP.
        POST /api/v1/user-service/users/me/email/confirm-change
        """

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
            return self.fail_response(
                message="Failed to confirm email change. Please try again.",
                status_code=500
            )
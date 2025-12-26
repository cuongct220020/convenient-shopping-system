# user-service/app/views/users/me_change_email_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas import RequestEmailChangeSchema, ConfirmEmailChangeRequestSchema, OTPRequestSchema
from app.services.auth_service import AuthService
from app.enums import OtpAction

from shopping_shared.schemas.response_schema import GenericResponse


class MeRequestChangeEmailView(HTTPMethodView):

    @validate_request(RequestEmailChangeSchema)
    async def post(self, request: Request):
        """Step 1: Request an OTP to change email."""
        new_email = request.ctx.validated_data.new_email
        user_repo = UserRepository(session=request.ctx.db_session)

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

        response = GenericResponse(
            status="success",
            message="OTP sent to your new email address.",
            data=response_data
        )

        return json(response.model_dump(mode="json"), status=200)


class MeConfirmChangeEmailView(HTTPMethodView):

    @validate_request(ConfirmEmailChangeRequestSchema)
    async def post(self, request: Request):
        """Step 2: Confirm email change with OTP."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data
        
        user_repo = UserRepository(request.ctx.db_session)

        # Delegate to AuthService for atomic verification and update
        await AuthService.change_email_with_otp(
            user_id=user_id,
            change_data=validated_data,
            user_repo=user_repo
        )

        response = GenericResponse(
            status="success",
            message="Email updated successfully. Please login again.",
            data=None
        )

        return json(response.model_dump(mode="json"), status=200)

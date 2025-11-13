# app/views/auth/otp_verification_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas import VerifyAccountRequestSchema, SuccessResponse
from app.services.auth_service import AuthService


class OTPVerificationView(HTTPMethodView):
    """Handles the verification of an OTP for various actions (e.g., registration, password reset)."""

    @validate_request(VerifyAccountRequestSchema)
    async def post(self, request: Request):
        """
        Verifies the submitted OTP and performs the corresponding action based on the OTP type.
        """
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(session=request.ctx.db_session)

        await AuthService.verify_otp_and_perform_action(
            data=validated_data,
            user_repo=user_repo
        )

        response = SuccessResponse(
            message="OTP verified successfully and action performed."
        )
        return json(response.model_dump(), status=200)



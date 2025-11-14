# app/views/auth/reset_password_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas.auth.reset_password_schema import ResetPasswordRequest
from app.services.auth_service import AuthService
from shared.shopping_shared.schemas import GenericResponse


class ResetPasswordView(HTTPMethodView):

    @validate_request(ResetPasswordRequest)
    async def post(self, request: Request):
        """Handles resetting the user's password using a valid OTP."""
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(session=request.ctx.db_session)

        await AuthService.reset_password_with_otp(
            data=validated_data,
            user_repo=user_repo,
        )

        response = GenericResponse(
            status="success",
            message="Password has been reset successfully."
        )
        return json(response.model_dump(), status=200)

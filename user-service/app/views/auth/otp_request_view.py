# microservices/user-service/app/views/auth/otp_request_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas import OTPRequestSchema
from app.services.auth_service import AuthService
from shopping_shared.schemas.response_schema import GenericResponse


class OTPRequestView(HTTPMethodView):
    """View to handle the generation and sending of a new OTP."""

    @validate_request(OTPRequestSchema)
    async def post(self, request: Request):
        """Handles the logic to request and send an OTP for a specific action."""
        otp_data = request.ctx.validated_data

        # Instantiate required repositories
        user_repo = UserRepository(session=request.ctx.db_session)

        # Delegate all business logic to the service layer, passing the request
        # for context-aware operations like handling authenticated users.
        await AuthService.request_otp(
            otp_data=otp_data,
            user_repo=user_repo
        )

        # For security, always return a generic success message.
        response = GenericResponse(
            message="If your request was valid, an OTP has been sent to the specified email address."
        )

        return json(response.model_dump(exclude_none=True), status=200)
# user-service/app/views/auth/register_view.py
from sanic.request import Request
from sanic_ext import openapi

from app.decorators import validate_request, idempotent, api_response
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.schemas import UserInfoSchema, RegisterRequestSchema, UserInfoResponseSchema
from app.services.auth_service import AuthService


class RegisterView(BaseAPIView):
    @openapi.summary("Register a new account")
    @openapi.description("Creates a new user account with an inactive status and sends a verification OTP.")
    @openapi.body(RegisterRequestSchema)
    @openapi.response(201, UserInfoResponseSchema)
    @openapi.tag("Authentication")
    @validate_request(RegisterRequestSchema)
    @idempotent()
    @api_response(
        success_schema=UserInfoResponseSchema,
        success_status=201,
        success_description="User registered successfully"
    )
    async def post(self, request: Request):
        """Handles new user registration."""
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(session=request.ctx.db_session)

        # Service now returns the created User object
        user = await AuthService.register_account(
            reg_data=validated_data,
            user_repo=user_repo
        )

        # Use helper method from base class
        return self.success_response(
            data=UserInfoSchema(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone_number=user.phone_num,
                avatar_url=user.avatar_url
            ),
            message="Registration successful. Please check your email for a verification OTP.",
            status_code=201
        )
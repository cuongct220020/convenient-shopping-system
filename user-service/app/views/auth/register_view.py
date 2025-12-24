# user-service/app/views/auth/register_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.decorators.idempotency import idempotent
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import RegisterRequestSchema
from app.services.auth_service import AuthService
from shopping_shared.schemas.response_schema import GenericResponse


class RegisterView(HTTPMethodView):
    @validate_request(RegisterRequestSchema)
    @idempotent()
    async def post(self, request: Request):
        """Handles new user registration."""
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(session=request.ctx.db_session)

        # Service now returns the created User object
        user = await AuthService.register_account(
            reg_data=validated_data,
            user_repo=user_repo
        )
        
        # Prepare response data matching UserPublicProfileSchema
        from app.schemas import UserPublicProfileSchema
        user_profile = UserPublicProfileSchema.model_validate(user)

        response = GenericResponse(
            status="success",
            message="Registration successful. Please check your email for a verification OTP.",
            data=user_profile
        )

        return json(response.model_dump(), status=201)

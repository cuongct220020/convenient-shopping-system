# app/views/auth/login_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequestSchema, AccessTokenResponseSchema
from app.services.auth_service import AuthService

from shopping_shared.schemas.response_schema import GenericResponse


class LoginView(HTTPMethodView):
    decorators = [validate_request(LoginRequestSchema)]

    async def post(self, request: Request):
        """Handles user login and token generation."""
        validated_data = request.ctx.validated_data

        # Instantiate required repositories with the request's DB session
        user_repo = UserRepository(session=request.ctx.db_session)

        token_data: AccessTokenResponseSchema = await AuthService.login_account(
            login_data=validated_data,
            user_repo=user_repo
        )

        response_data = GenericResponse(
            status="success",
            message="Login successful",
            data=token_data
        )

        response = json(response_data.model_dump(by_alias=True), status=200)

        # Attach Refresh Token to cookie
        AuthService.attach_refresh_token_to_response(response)

        return response
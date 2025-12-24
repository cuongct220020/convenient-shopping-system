# user-service/app/views/auth/login_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequestSchema
from app.services.auth_service import AuthService

from shopping_shared.schemas.response_schema import GenericResponse


class LoginView(HTTPMethodView):

    @validate_request(LoginRequestSchema)
    async def post(self, request: Request):
        """Handles user login and token generation."""
        validated_data = request.ctx.validated_data

        # Instantiate required repositories with the request's DB session
        user_repo = UserRepository(session=request.ctx.db_session)

        token_response, refresh_token = await AuthService.login_account(
            login_data=validated_data,
            user_repo=user_repo
        )

        response_data = GenericResponse(
            status="success",
            message="Login successful",
            data=token_response
        )

        response = json(response_data.model_dump(by_alias=True), status=200)

        # Attach Refresh Token to cookie
        config = request.app.config
        refresh_ttl_days = config.get("REFRESH_TOKEN_EXPIRE_DAYS", 7)
        refresh_ttl_seconds = refresh_ttl_days * 24 * 60 * 60

        response.set_cookie(
            key = "refresh_token",
            value = refresh_token,
            httponly = True,
            secure = not config.get("DEBUG", False),
            samesite = "strict",
            path="/api/v1/user-service/auth/refresh-token",
            max_age = refresh_ttl_seconds,
        )

        return response
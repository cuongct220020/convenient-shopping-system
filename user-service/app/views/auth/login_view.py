# user-service/app/views/auth/login_view.py
from sanic.request import Request
from sanic_ext import openapi

from app.decorators import validate_request
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequestSchema, LoginResponse
from app.services.auth_service import AuthService



class LoginView(BaseAPIView):
    """Handles user login and token generation."""

    @openapi.summary("Login")
    @openapi.description("Logs in a user, returning an access token in the response body and a refresh token in an HttpOnly cookie.")
    @openapi.response(200, LoginResponse, "Login successful")
    @openapi.tag("Authentication")
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

        # Use helper method from base class
        response = self.success_response(
            data=token_response,
            message="Login successful",
            status_code=200
        )

        # Attach Refresh Token to cookie
        config = request.app.config
        refresh_ttl_days = config.get("REFRESH_TOKEN_EXPIRE_DAYS", 7)
        refresh_ttl_seconds = refresh_ttl_days * 24 * 60 * 60

        response.cookies['refresh_token'] = refresh_token
        response.cookies['refresh_token']['httponly'] = True
        response.cookies['refresh_token']['secure'] = not config.get("DEBUG", False)
        response.cookies['refresh_token']['samesite'] = 'Strict'
        response.cookies['refresh_token']['path'] = '/api/v1/user-service/auth/refresh-token'
        response.cookies['refresh_token']['max_age'] = refresh_ttl_seconds

        return response
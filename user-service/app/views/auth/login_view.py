# user-service/app/views/auth/login_view.py
from sanic.request import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequestSchema, AccessTokenResponseSchema
from app.services.auth_service import AuthService
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.openapi_utils import get_openapi_body


class LoginView(BaseAPIView):
    """Handles user login and token generation."""

    @openapi.definition(
        summary="Authenticate user and generate tokens",
        description="Authenticate a user with email and password. On successful authentication, returns an access token in the response body and sets a refresh token in an HttpOnly cookie for secure session management.",
        body=get_openapi_body(LoginRequestSchema),
        tag="Authentication",
        response=[
            Response(
                content=get_openapi_body(AccessTokenResponseSchema),
                status=200,
                description="Successfully authenticated and tokens generated.",
            )
        ],
    )
    @validate_request(LoginRequestSchema)
    async def post(self, request: Request):
        """
        Handles user login and token generation.
        POST /api/v1/user-service/auth/login
        """
        validated_data = request.ctx.validated_data

        # Instantiate required repositories with the request's DB session
        user_repo = UserRepository(session=request.ctx.db_session)

        token_response, refresh_token = await AuthService.login_account(
            login_data=validated_data, user_repo=user_repo
        )

        # Use helper method from base class
        response = self.success_response(
            data=token_response, message="Login successful", status_code=200
        )

        # Attach Refresh Token to cookie
        config = request.app.config
        refresh_ttl_days = config.get("REFRESH_TOKEN_EXPIRE_DAYS", 7)
        refresh_ttl_seconds = refresh_ttl_days * 24 * 60 * 60

        response.add_cookie(
            "refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="None",
            path="/api/v1/user-service/auth/refresh-token",
            max_age=refresh_ttl_seconds,
        )

        return response

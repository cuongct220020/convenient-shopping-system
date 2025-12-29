# user-service/app/views/auth/refresh_view.py
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.views.base_view import BaseAPIView
from shopping_shared.exceptions import Forbidden, Unauthorized


from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import AccessTokenResponseSchema

from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.openapi_utils import get_openapi_body


class RefreshView(BaseAPIView):
    """Handles token refresh using a cookie."""

    @openapi.definition(
        summary="Refresh access token using refresh token",
        description="Generates a new access token using the refresh token stored in an HttpOnly cookie. Implements token rotation by issuing a new refresh token with each request, enhancing security by invalidating the previous refresh token.",
        secured={"bearerAuth": []},
        tag=["Authentication"],
        response=[
            Response(
                content=get_openapi_body(AccessTokenResponseSchema),
                status=200,
                description="New access token generated successfully with token rotation applied."
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=401,
                description="Invalid, expired, or missing refresh token."
            ),
        ]
    )
    async def post(self, request: Request) -> HTTPResponse:
        """
        Xử lý token refresh
        POST /api/v1/user-service/auth/refresh-token
        """
        # 1. Đọc refresh token từ cookie
        old_refresh_token = request.cookies.get("refresh_token")
        if not old_refresh_token:
            raise Unauthorized("Missing refresh token cookie.")

        config = request.app.config
        user_repo = UserRepository(session=request.ctx.db_session)

        try:
            # 2. Gọi service với token từ cookie
            #    Hàm này giờ trả về (TokenData, is_active)
            new_token_data, is_active = await AuthService.refresh_tokens(
                old_refresh_token=old_refresh_token,
                user_repo=user_repo,
            )

        except (Unauthorized, Forbidden) as e:
            # --- QUAN TRỌNG: Xóa cookie hỏng/bị thu hồi ---
            # Use helper method from base class
            response = self.fail_response(
                message=str(e),
                status_code=401
            )
            response.delete_cookie(
                "refresh_token",
                path='/api/v1/user-service/auth/refresh-token',
                httponly=True,
                secure=not config.get("DEBUG", False),
                samesite="Strict"
            )
            return response

        # 3. Prepare response with access token and user status
        access_token_data = AccessTokenResponseSchema(
            access_token=new_token_data.access_token,
            token_type="Bearer",
            expires_in_minutes=new_token_data.at_expires_in_minutes,
            is_active=is_active
        )

        # Use helper method from base class
        response = self.success_response(
            data=access_token_data,
            message="Tokens refreshed successfully",
            status_code=200
        )

        # 4. Đặt refresh token MỚI (đã được xoay vòng) vào cookie
        refresh_expires_days = int(config.get("REFRESH_TOKEN_EXPIRE_DAYS", 7))
        max_age = refresh_expires_days * 24 * 60 * 60

        response.add_cookie(
            "refresh_token",
            value=new_token_data.refresh_token,
            max_age=max_age,
            httponly=True,
            secure=not config.get("DEBUG", False),
            samesite="Strict",
            path='/api/v1/user-service/auth/refresh-token'
        )

        return response
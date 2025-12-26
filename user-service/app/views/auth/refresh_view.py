# user-service/app/views/auth/refresh_view.py
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic_ext import openapi

from app.decorators import api_response
from app.views.base_view import BaseAPIView
from shopping_shared.exceptions import Forbidden, Unauthorized


from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas import TokenResponseSchema, TokenDataResponseSchema


class RefreshView(BaseAPIView):
    """Handles token refresh using a cookie."""

    @staticmethod
    @openapi.summary("Refresh access token")
    @openapi.description(
        "Generates a new access token using the refresh token provided in an HttpOnly cookie. "
        "This endpoint implements token rotation, where a new refresh token is also returned in a new cookie."
    )
    @openapi.response(200, TokenDataResponseSchema)
    @openapi.tag("Authentication")
    @api_response(
        success_schema=TokenDataResponseSchema,
        success_status=200,
        success_description="Token refreshed successfully"
    )
    async def post(request: Request) -> HTTPResponse:
        """
        Xử lý token refresh
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
            response = BaseAPIView.fail_response(
                message=str(e),
                status_code=401
            )
            response.cookies['refresh_token'] = ""
            response.cookies['refresh_token']['max_age'] = 0
            response.cookies['refresh_token']['httponly'] = True
            response.cookies['refresh_token']['secure'] = not config.get("DEBUG", False)
            response.cookies['refresh_token']['samesite'] = 'Strict'
            response.cookies['refresh_token']['path'] = '/api/v1/user-service/auth/refresh-token'
            return response

        # 3. Prepare response with access token and user status
        access_token_data = TokenResponseSchema(
            access_token=new_token_data.access_token,
            token_type="Bearer",
            expires_in_minutes=new_token_data.at_expires_in_minutes,
            is_active=is_active
        )

        # Use helper method from base class
        response = BaseAPIView.success_response(
            data=access_token_data,
            message="Tokens refreshed successfully",
            status_code=200
        )

        # 4. Đặt refresh token MỚI (đã được xoay vòng) vào cookie
        refresh_expires_days = int(config.get("REFRESH_TOKEN_EXPIRE_DAYS", 7))
        max_age = refresh_expires_days * 24 * 60 * 60

        response.cookies['refresh_token'] = new_token_data.refresh_token
        response.cookies['refresh_token']['max_age'] = max_age
        response.cookies['refresh_token']['httponly'] = True
        response.cookies['refresh_token']['secure'] = not config.get("DEBUG", False)
        response.cookies['refresh_token']['samesite'] = 'Strict'
        response.cookies['refresh_token']['path'] = '/api/v1/user-service/auth/refresh-token'

        return response
# app/views/auth/refresh_view.py
from sanic.request import Request
from sanic.response import json, HTTPResponse
from sanic.views import HTTPMethodView

from shopping_shared.exceptions import Forbidden, Unauthorized
from shopping_shared.schemas.response_schema import GenericResponse

from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository


class RefreshView(HTTPMethodView):

    @staticmethod
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
            #    Hàm này giờ trả về TokenData DTO
            new_token_data = await AuthService.refresh_tokens(
                old_refresh_token=old_refresh_token,
                user_repo=user_repo,
            )

        except (Unauthorized, Forbidden) as e:
            # --- QUAN TRỌNG: Xóa cookie hỏng/bị thu hồi ---
            response_data = GenericResponse(status="fail", message=str(e))
            response = json(response_data.model_dump(), status=401)
            response.set_cookie(
                "refresh_token", "", max_age=0, httponly=True,
                secure=not config.get("DEBUG", False), samesite="Strict",
                path="/api/v1/user-service/auth/refresh-token"
            )
            return response

        # 3. Chuẩn bị response chỉ chứa access token mới
        access_token_data = {
            "access_token": new_token_data.access_token,
            "token_type": "Bearer", # Bạn có thể thêm vào TokenData DTO
            "expires_in_minutes": new_token_data.at_expires_in_minutes
        }
        response_data = GenericResponse(
            status="success",
            message="Tokens refreshed successfully",
            data=access_token_data
        )
        response = json(response_data.model_dump(by_alias=True), status=200)

        # 4. Đặt refresh token MỚI (đã được xoay vòng) vào cookie
        refresh_expires_days = int(config.get("REFRESH_TOKEN_EXPIRE_DAYS", 7))
        max_age = refresh_expires_days * 24 * 60 * 60

        response.set_cookie(
            "refresh_token",
            new_token_data.refresh_token,
            max_age=max_age,
            httponly=True,
            secure=not config.get("DEBUG", False),
            samesite="Strict",
            path="/api/v1/user-service/auth/refresh-token"
        )

        return response
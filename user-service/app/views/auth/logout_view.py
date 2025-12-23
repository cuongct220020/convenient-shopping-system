# app/views/auth/logout_view.py
from datetime import datetime, UTC
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.services.auth_service import AuthService
from shopping_shared.schemas.response_schema import GenericResponse


class LogoutView(HTTPMethodView):

    @staticmethod
    async def post(request: Request):
        """Handles user logout by revoking tokens and clearing the session from the database."""
        # 1. Lấy thông tin từ context (đã được set bởi middleware)
        auth_payload = request.ctx.auth_payload
        user_id = auth_payload["sub"]
        access_jti = auth_payload["jti"]
        access_exp = auth_payload["exp"]  # Unix timestamp

        # 2. Tính TTL còn lại (số giây từ bây giờ đến khi token hết hạn)
        current_timestamp = int(datetime.now(UTC).timestamp())
        remaining_ttl = max(0, access_exp - current_timestamp)

        # 3. Gọi service để thực hiện logout
        await AuthService.logout_account(
            user_id=user_id,
            access_token_jti=access_jti,
            remaining_ttl_seconds=remaining_ttl
        )

        # 4. Trả response thành công
        response_data = GenericResponse(status="success", message="Logout successful.")
        response = json(response_data.model_dump(), status=200)

        # 5. Xóa HttpOnly cookie
        response.delete_cookie("refresh_token")

        return response
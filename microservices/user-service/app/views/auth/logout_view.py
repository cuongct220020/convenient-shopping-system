# app/views/auth/logout_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.auth import protected
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from shopping_shared.schemas.response_schema import GenericResponse


class LogoutView(HTTPMethodView):
    decorators = [protected]  # Chỉ cần xác thực access token

    async def post(self, request: Request):
        """Handles user logout by revoking tokens and clearing the session from the database."""
        # 1. Lấy thông tin từ context và cookie
        access_jti = request.ctx.jti
        access_exp = request.ctx.exp
        user_id = request.ctx.user_id
        refresh_token = request.cookies.get("refresh_token")

        # 2. Khởi tạo repository
        user_repo = UserRepository(request.ctx.db_session)

        # 3. Gọi service để thực hiện logout
        await AuthService.logout(
            user_id=user_id,
            user_repo=user_repo,
            access_jti=access_jti,
            access_exp=access_exp,
            refresh_token=refresh_token
        )

        response_data = GenericResponse(status="success", message="Logout successful.")
        response = json(response_data.model_dump(), status=200)

        # 4. Xóa HttpOnly cookie khỏi trình duyệt
        response.delete_cookie("refresh_token")

        return response
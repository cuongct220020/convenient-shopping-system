# microservices/user-service/app/hooks/request_auth.py
from sanic import Request

from app.services.redis_service import RedisService
from shopping_shared.exceptions import Unauthorized


async def auth_middleware(request: Request):
    """
    Middleware để xử lý thông tin người dùng từ các header do API Gateway (Kong) thêm vào.
    Hook này chạy sau khi Kong đã xác thực JWT.
    """
    if not _is_auth_required(request):
        return  # Bỏ qua các endpoint public

    # Đọc thông tin người dùng từ các header do Kong thêm vào (đã được chuyển thành lowercase)
    user_id = request.headers.get("x-user-id")
    user_role = request.headers.get("x-user-role")
    access_jti = request.headers.get("x-jti")
    exp_str = request.headers.get("x-exp")
    iat_str = request.headers.get("x-iat")

    if not user_id:
        raise Unauthorized("Missing user identity from API Gateway.")

    if await RedisService.is_token_in_blocklist(access_token_jti=access_jti):
        raise Unauthorized("Access token has been revoked.")

    token_iat = int(iat_str)
    global_revoke_ts = await RedisService.get_global_revoke_timestamp(user_id)

    if global_revoke_ts and token_iat < global_revoke_ts:
        # Token này được tạo trước khi user đổi password -> không hợp lệ
        raise Unauthorized("Token has been revoked by a security event.")

    request.ctx.auth_payload = {
        "sub": user_id,
        "role": user_role,
        "jti": access_jti,
        "exp": int(exp_str),
        "iat": token_iat
    }


def _is_auth_required(request: Request) -> bool:
    """
    Xác định xem request hiện tại có cần xác thực hay không.
    """
    ignore_methods = {"OPTIONS"}
    ignore_paths = {
        "/",
        "/favicon.ico",
        "/auth/login",
        "/auth/register",
        "/auth/otp/send",
        "/auth/otp/verify",
        "/auth/reset-password"
    }
    ignore_prefixes = ["/docs/"]

    if request.method in ignore_methods:
        return False

    for prefix in ignore_prefixes:
        if request.path.startswith(prefix):
            return False

    if request.path in ignore_paths:
        return False

    if request.path == "/auth/refresh-token":
        return False  # Tạm thời bỏ qua, nó cần 1 logic riêng

    return True
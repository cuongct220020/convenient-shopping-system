from sanic import Request

from app.services.redis_service import RedisService
from shopping_shared.exceptions import Unauthorized
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Request Auth Middleware")

async def auth_middleware(request: Request):
    """
    Middleware to extract auth info added by API Gateway (Kong).
    """
    logger.debug("Auth middleware start: %s %s", request.method, request.path)

    if not _is_auth_required(request):
        logger.debug("Auth middleware skipped for path: %s", request.path)
        return  # skip public endpoints

    user_id = request.headers.get("x-user-id")
    user_role = request.headers.get("x-user-role")
    access_jti = request.headers.get("x-jti")
    exp_str = request.headers.get("x-exp")
    iat_str = request.headers.get("x-iat")

    if not user_id:
        logger.warning("Missing x-user-id header")
        raise Unauthorized("Missing user identity from API Gateway.")

    try:
        if await RedisService.is_token_in_blocklist(access_token_jti=access_jti):
            logger.info("Token jti found in blocklist: %s", access_jti)
            raise Unauthorized("Access token has been revoked.")
    except Exception as ex:
        logger.exception("Error while checking token blocklist: %s", ex)
        # escalate as unauthorized to be safe
        raise Unauthorized("Failed to validate token.") from ex

    try:
        token_iat = int(iat_str)
    except Exception:
        logger.exception("Invalid iat header: %s", iat_str)
        raise Unauthorized("Invalid token iat.")

    try:
        global_revoke_ts = await RedisService.get_global_revoke_timestamp(user_id)
    except Exception as ex:
        logger.exception("Failed to read global revoke timestamp for user %s: %s", user_id, ex)
        global_revoke_ts = None

    if global_revoke_ts and token_iat < global_revoke_ts:
        logger.info("Token iat older than global revoke for user %s", user_id)
        raise Unauthorized("Token has been revoked by a security event.")

    request.ctx.auth_payload = {
        "sub": user_id,
        "role": user_role,
        "jti": access_jti,
        "exp": int(exp_str) if exp_str else None,
        "iat": token_iat
    }
    logger.debug("Auth payload attached to request.ctx for user %s", user_id)


def _is_auth_required(request: Request) -> bool:
    """
    Xác định xem request hiện tại có cần xác thực hay không.
    """
    ignore_methods = {"OPTIONS"}
    
    # Prefix cho các API
    prefix = "/api/v1/user-service"
    
    # Các đường dẫn không cần xác thực
    ignore_paths = {
        "/",                  # Trang chủ service (trong run.py)
        "/favicon.ico",        # Favicon (trong run.py)
        "/docs",               # Swagger UI
        "/docs/",              # Swagger UI with trailing slash
        "/swagger",            # Alternative swagger path
        "/swagger/",
        "/openapi.json",       # OpenAPI spec
        "/redoc",              # ReDoc (if enabled)
        f"{prefix}/auth/login",
        f"{prefix}/auth/register",
        f"{prefix}/auth/otp/send",
        f"{prefix}/auth/otp/verify",
        f"{prefix}/auth/reset-password",
        f"{prefix}/auth/refresh-token"
    }
    ignore_prefixes = [f"{prefix}/docs/"]

    if request.method in ignore_methods:
        return False

    for p_prefix in ignore_prefixes:
        if request.path.startswith(p_prefix):
            return False

    if request.path in ignore_paths:
        return False

    return True
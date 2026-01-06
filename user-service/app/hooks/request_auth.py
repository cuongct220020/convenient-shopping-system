from sanic import Request
from shopping_shared.middleware.sanic_auth import create_auth_middleware

# Define configuration for the middleware
IGNORE_PATHS = {
    "/api/v1/user-service/health",
    "/api/v1/user-service/docs",
    "/api/v1/user-service/openapi.json",
    "/api/v1/user-service/auth/login",
    "/api/v1/user-service/auth/register",
    "/api/v1/user-service/auth/otp/send",
    "/api/v1/user-service/auth/otp/verify",
    "/api/v1/user-service/auth/reset-password",
    "/api/v1/user-service/auth/refresh-token",
    "/api/v1/user-service/groups/internal/<group_id:uuid>/members/<user_id:uuid>/access-check" # Internal API
}

IGNORE_PREFIXES = [
    "/api/v1/user-service/docs/"
]

LOGOUT_PATH = "/api/v1/user-service/auth/logout"

# Create the middleware instance using the shared factory
# This function matches the signature expected by Sanic's register_middleware
auth_middleware_handler = create_auth_middleware(
    ignore_paths=IGNORE_PATHS,
    ignore_prefixes=IGNORE_PREFIXES,
    logout_path=LOGOUT_PATH
)

async def auth_middleware(request: Request):
    """
    Wrapper to call the generated middleware.
    """
    await auth_middleware_handler(request)
from typing import Set, List
from sanic import Request
from shopping_shared.middleware.auth_utils import extract_kong_headers, validate_token_state
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Sanic Auth Middleware")

def create_auth_middleware(
    ignore_paths: Set[str] = None, 
    ignore_prefixes: List[str] = None,
    logout_path: str = None
):
    """
    Factory to create a Sanic authentication middleware.

    Args:
        ignore_paths: Set of exact paths to skip authentication.
        ignore_prefixes: List of path prefixes to skip authentication.
        logout_path: Path for logout (skips blocklist check but still extracts headers).
    """
    if ignore_paths is None:
        ignore_paths = set()
    if ignore_prefixes is None:
        ignore_prefixes = []

    async def auth_middleware(request: Request):
        # 1. Check if auth is required
        if request.method == "OPTIONS":
            return

        if request.path in ignore_paths:
            logger.debug(f"Skipping auth for path: {request.path}")
            return
            
        for prefix in ignore_prefixes:
            if request.path.startswith(prefix):
                logger.debug(f"Skipping auth for prefix: {prefix}")
                return

        # 2. Extract Headers
        logger.debug(f"Processing auth for: {request.path}")
        auth_payload = extract_kong_headers(dict(request.headers))
        
        # 3. Validate Token State (Redis Check)
        # Check if logout path
        check_blocklist = True
        if logout_path and request.path == logout_path:
            check_blocklist = False
            
        # Get Redis client (assumed to be injected into ctx by previous middleware)
        redis_client = getattr(request.ctx, "redis_client", None)
        
        await validate_token_state(
            user_id=auth_payload["sub"],
            jti=auth_payload["jti"],
            iat=auth_payload["iat"],
            redis_client=redis_client,
            check_blocklist=check_blocklist
        )

        # 4. Attach Payload to Request Context
        request.ctx.auth_payload = auth_payload
        logger.debug(f"Auth successful for user {auth_payload['sub']}")

    return auth_middleware

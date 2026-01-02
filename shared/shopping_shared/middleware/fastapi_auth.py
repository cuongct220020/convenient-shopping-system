from typing import Optional, Annotated
from fastapi import Request, Depends
from shopping_shared.exceptions import Unauthorized
from shopping_shared.middleware.auth_utils import extract_kong_headers, validate_token_state
from shopping_shared.caching.redis_manager import redis_manager

async def get_current_user(request: Request):
    """
    FastAPI Dependency to validate Kong headers and check Redis for token revocation.
    Returns the auth_payload dict.
    """
    # 1. Extract Headers
    auth_payload = extract_kong_headers(request.headers)
    
    # 2. Validate Token State
    # We use the singleton redis_manager directly since FastAPI doesn't usually inject it into request state like Sanic
    try:
        redis_client = redis_manager.client
    except Exception:
        # If Redis isn't initialized/available, we might want to warn or fail
        # Ideally, redis_manager.setup() should have been called in startup event
        redis_client = None

    await validate_token_state(
        user_id=auth_payload["sub"],
        jti=auth_payload["jti"],
        iat=auth_payload["iat"],
        redis_client=redis_client,
        check_blocklist=True 
    )
    
    # 3. Attach to request state for downstream use if needed
    request.state.user = auth_payload
    request.state.user_id = auth_payload["sub"]
    
    return auth_payload

# Type alias for easy use in routes
CurrentUser = Annotated[dict, Depends(get_current_user)]

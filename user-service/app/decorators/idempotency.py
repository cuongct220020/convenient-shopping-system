# user-service/app/decorators/idempotency.py
from functools import wraps
import json
from sanic.request import Request
from sanic.response import json as sanic_json
from sanic_ext import openapi

from shopping_shared.exceptions import Conflict
from shopping_shared.utils.logger_utils import get_logger
from app.services.redis_service import RedisService
from shopping_shared.schemas.response_schema import GenericResponse

logger = get_logger("Idempotency")

def idempotent(ttl_seconds: int = 60 * 60 * 24, auto_document: bool = True): # Default 24 hours
    """
    Decorator to ensure idempotency for POST/PATCH requests.
    Requires the client to send 'Idempotency-Key' or 'X-Request-ID' header.

    Logic:
    1. Check if key exists.
       - If PROCESSING: Raise 409 Conflict (Concurrent request).
       - If Result Found: Return cached result immediately.
    2. If key doesn't exist:
       - Acquire Lock (Set status PROCESSING).
       - Execute View.
       - If Success (2xx/4xx): Save Result.
       - If Error (5xx) or Exception: Release Lock so it can be retried.

    Args:
        ttl_seconds: Cache TTL in seconds (default: 24 hours)
        auto_document: Whether to automatically document OpenAPI responses (default: True)
    """
    def decorator(f):
        if auto_document:
            # Automatically document the header requirement
            f = openapi.parameter("Idempotency-Key", str, "header", required=False, description="Unique key to prevent duplicate operations")(f)
            # Automatically document the possible conflict error response
            f = openapi.response(409, GenericResponse, "Conflict - Concurrent operation in progress")(f)

        @wraps(f)
        async def decorated_function(view, request: Request, *args, **kwargs):
            # 1. Get Key
            idem_key = request.headers.get("Idempotency-Key") or request.headers.get("X-Request-ID")

            # If no key provided, skip idempotency logic and process normally
            # (Or strictly require it depending on policy. Here we allow optional)
            if not idem_key:
                return await f(view, request, *args, **kwargs)

            # Determine User ID (Authenticated or Anonymous/IP based)
            if hasattr(request.ctx, "auth_payload") and request.ctx.auth_payload:
                user_id = request.ctx.auth_payload.get("sub")
            else:
                # For public endpoints (like register), user_id isn't available yet.
                # Use "anon:{ip}" to prevent key collision between different users.
                user_id = f"anon:{request.remote_addr or request.ip}"

            # 2. Check State & Acquire Lock
            # Using SETNX via RedisService to atomically check and lock
            is_acquired = await RedisService.acquire_idempotency_lock(user_id, idem_key, lock_ttl=60) # 60s lock for processing time

            if not is_acquired:
                # Lock failed, meaning key exists. Check if it's a finished result or processing.
                cached_data_str = await RedisService.get_idempotency_result(user_id, idem_key)

                if cached_data_str == "PROCESSING":
                    # Concurrent request detected
                    logger.warning(f"Concurrent request blocked for key: {idem_key}, user: {user_id}")
                    raise Conflict("This operation is currently being processed. Please wait.")

                if cached_data_str:
                    # Idempotency HIT: Return cached response
                    logger.info(f"Idempotency hit for key: {idem_key}, user: {user_id}")
                    data = json.loads(cached_data_str)
                    return sanic_json(data["body"], status=data["status"])

                # Edge case: Key exists but value is empty/null (shouldn't happen with correct Redis logic)
                # Fallback to process to be safe
                pass

            # 3. Process Request
            try:
                response = await f(view, request, *args, **kwargs)

                # 4. Save Result (Only for stable HTTP codes)
                # We cache 200-499 codes. 500 errors should typically be retried (so we release lock).
                if 200 <= response.status < 500:
                    try:
                        # Decode response body (it's bytes in Sanic)
                        response_body = json.loads(response.body)
                        cache_payload = {
                            "status": response.status,
                            "body": response_body
                        }
                        await RedisService.save_idempotency_result(
                            user_id, idem_key, cache_payload, ttl_seconds
                        )
                    except Exception as e:
                        logger.error(f"Failed to serialize response for idempotency: {e}")
                        # Even if saving cache fails, we return the real response
                else:
                    # If server error, release lock to allow retry
                    await RedisService.release_idempotency_lock(user_id, idem_key)

                return response

            except Exception as e:
                # On application exception (Crash), release lock
                logger.error(f"Error during idempotent processing: {e}")
                await RedisService.release_idempotency_lock(user_id, idem_key)
                raise e # Re-raise for global error handler

        return decorated_function
    return decorator
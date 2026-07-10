from typing import Dict, Any
from shopping_shared.exceptions import Unauthorized
from shopping_shared.caching.redis_keys import RedisKeys
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("AuthUtils")

async def validate_token_state(
    user_id: str,
    jti: str,
    iat: int,
    redis_client: Any,
    check_blocklist: bool = True
) -> None:
    """
    Validates the state of the token against Redis (Blocklist and Global Revoke).
    
    Args:
        user_id: The user ID from the token.
        jti: The JWT ID.
        iat: The Issued At timestamp.
        redis_client: The Redis client instance.
        check_blocklist: Whether to check the blocklist (default: True).
                         Set to False for logout requests where we want to allow revoked tokens.
    
    Raises:
        Unauthorized: If the token is revoked or invalid.
    """
    if redis_client is None:
        logger.warning("Redis client not available. Skipping state check (Degraded mode).")
        return

    # 1. Check Blocklist
    if check_blocklist:
        try:
            blocklist_key = RedisKeys.jwt_blocklist(jti)
            is_blocked = await redis_client.get(blocklist_key)
            if is_blocked:
                logger.info(f"Token jti found in blocklist: {jti}")
                raise Unauthorized("Access token has been revoked.")
        except Unauthorized:
            raise
        except Exception as ex:
            logger.exception(f"Error checking token blocklist: {ex}")
            # Fail closed for blocklist checks
            raise Unauthorized("Failed to validate token.") from ex

    # 2. Check Global Revoke Timestamp
    try:
        revoke_key = RedisKeys.global_revoke(user_id)
        global_revoke_ts_str = await redis_client.get(revoke_key)
        
        if global_revoke_ts_str:
            global_revoke_ts = int(global_revoke_ts_str)
            if iat < global_revoke_ts:
                logger.info(f"Token iat {iat} older than global revoke {global_revoke_ts} for user {user_id}")
                raise Unauthorized("Token has been revoked by a security event.")
    except Unauthorized:
        raise
    except Exception as ex:
        # Log but fail open for global revoke (consistent with legacy behavior), 
        # or consider failing closed if stricter security is needed.
        logger.exception(f"Failed to read global revoke timestamp for user {user_id}: {ex}")


def extract_kong_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts and validates authentication headers injected by Kong.
    Handles case-insensitive headers manually for compatibility.
    """
    # Create a case-insensitive lookup dict
    lookup_headers = {k.lower(): v for k, v in headers.items()}
    
    # Debug log specific headers
    # logger.info(f"Auth Headers Received: {list(lookup_headers.keys())}")

    user_id = lookup_headers.get("x-user-id")
    user_role = lookup_headers.get("x-user-role")
    user_email = lookup_headers.get("x-user-email")
    username = lookup_headers.get("x-user-username")
    access_jti = lookup_headers.get("x-jti")
    exp_str = lookup_headers.get("x-exp")
    iat_str = lookup_headers.get("x-iat")
    aud_str = lookup_headers.get("x-aud")

    if not user_id:
        logger.warning(f"Missing x-user-id header. Available headers: {list(lookup_headers.keys())}")
        raise Unauthorized("Missing user identity from API Gateway.")

    if not access_jti:
        logger.warning("Missing x-jti header")
        raise Unauthorized("Missing token identifier from API Gateway.")

    # Validate numeric headers
    try:
        token_iat = int(iat_str) if iat_str else 0
    except (ValueError, TypeError):
        logger.warning(f"Invalid iat header: {iat_str}")
        raise Unauthorized("Invalid token iat.")

    try:
        token_exp = int(exp_str) if exp_str else None
    except (ValueError, TypeError):
        logger.warning(f"Invalid exp header: {exp_str}")
        token_exp = None

    return {
        "sub": user_id,
        "role": user_role,
        "username": username,
        "email": user_email,
        "jti": access_jti,
        "exp": token_exp,
        "iat": token_iat,
        "aud": aud_str,
    }

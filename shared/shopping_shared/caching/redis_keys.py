# shared/shopping_shared/caching/redis_keys.py

class RedisKeys:
    """
    Centralized Redis Key generator for the entire Shopping System.
    Follows convention: <service>:<domain>:<identifier>[:<suffix>]
    """

    # --- User Service Keys ---
    USER_SERVICE = "user-service"

    @staticmethod
    def user_session(user_id: str) -> str:
        """Key for Active User Session (Allowlist). Values: Refresh Token JTI."""
        return f"{RedisKeys.USER_SERVICE}:session:{user_id}"

    @staticmethod
    def jwt_blocklist(jti: str) -> str:
        """Key for Revoked Access Tokens (Blocklist). Values: 'true'."""
        return f"{RedisKeys.USER_SERVICE}:jwt-blocklist:{jti}"

    @staticmethod
    def otp(email: str, action: str) -> str:
        """Key for OTP codes. Values: JSON(code, timestamp...)."""
        # Normalize email and action to ensure key consistency
        normalized_email = email.strip().replace(" ", "").lower()
        identifier = f"{action.lower()}:{normalized_email}"
        return f"{RedisKeys.USER_SERVICE}:otp:{identifier}"

    @staticmethod
    def global_revoke(user_id: str) -> str:
        """Key for Global Token Revocation Timestamp."""
        return f"{RedisKeys.USER_SERVICE}:global_revoke_ts:{user_id}"

    @staticmethod
    def idempotency(user_id: str, idem_key: str) -> str:
        """Key for Idempotency Locks/Results."""
        return f"{RedisKeys.USER_SERVICE}:idempotency:{user_id}:{idem_key}"

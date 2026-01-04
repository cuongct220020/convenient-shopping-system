# shared/shopping_shared/caching/redis_keys.py

class RedisKeys:
    """
    Centralized Redis Key generator for the entire Shopping System.
    Follows convention: <service>:<domain>:<identifier>[:<suffix>]
    """

    # --- Service Prefixes ---
    USER_SERVICE = "user-service"

    # --- Cache Patterns (Constants used for Decorators & Wildcard Deletion) ---
    # Patterns contain placeholders like {page}, {id} for decorators to fill.
    
    # Admin: User List
    ADMIN_USERS_LIST = f"{USER_SERVICE}:admin:users:list:p{{page}}:s{{page_size}}"
    ADMIN_USERS_LIST_WILDCARD = f"{USER_SERVICE}:admin:users:list:*"
    
    # Admin: User Detail
    ADMIN_USER_DETAIL = f"{USER_SERVICE}:admin:users:detail:{{user_id}}"


    # --- Dynamic Key Generators (Methods used by Services) ---
    
    @staticmethod
    def user_session(user_id: str) -> str:
        """Key for Active User Session (Allowlist)."""
        return f"{RedisKeys.USER_SERVICE}:session:{user_id}"

    @staticmethod
    def jwt_blocklist(jti: str) -> str:
        """Key for Revoked Access Tokens (Blocklist)."""
        return f"{RedisKeys.USER_SERVICE}:jwt-blocklist:{jti}"

    @staticmethod
    def otp(email: str, action: str) -> str:
        """Key for OTP codes."""
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

    # --- Helper methods to format patterns manually (if needed outside decorators) ---

    @staticmethod
    def admin_user_detail_key(user_id: str) -> str:
        """Returns the specific key for a user detail using the constant pattern."""
        return RedisKeys.ADMIN_USER_DETAIL.format(user_id=user_id)
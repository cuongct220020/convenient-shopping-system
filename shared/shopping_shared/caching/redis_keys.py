# shared/shopping_shared/caching/redis_keys.py

class RedisKeys:
    """
    Centralized Redis Key generator for the entire Shopping System.
    Follows convention: <service>:<domain>:<identifier>[:<suffix>]
    """

    # --- Service Prefixes ---
    USER_SERVICE = "user-service"

    # --- Cache Patterns (Constants used for Decorators & Wildcard Deletion) ---

    # User Core & Profile (Unified for both 'Me' and 'Member' views)
    USER_CORE = f"{USER_SERVICE}:users:{{user_id}}:core"
    USER_PROFILE_IDENTITY = f"{USER_SERVICE}:users:{{user_id}}:profile:identity"
    USER_PROFILE_HEALTH = f"{USER_SERVICE}:users:{{user_id}}:profile:health"
    USER_TAGS = f"{USER_SERVICE}:users:{{user_id}}:tags"
    
    # User's Groups (List of groups a user belongs to)
    USER_GROUPS_LIST = f"{USER_SERVICE}:users:{{user_id}}:groups"

    # Group Public/Member Views
    GROUP_DETAIL = f"{USER_SERVICE}:groups:{{group_id}}:detail"
    GROUP_MEMBERS_LIST = f"{USER_SERVICE}:groups:{{group_id}}:members"

    # Admin User Keys
    ADMIN_USERS_LIST = f"{USER_SERVICE}:admin:users:list:p{{page}}:s{{page_size}}"
    ADMIN_USERS_LIST_WILDCARD = f"{USER_SERVICE}:admin:users:list:*"
    ADMIN_USER_DETAIL = f"{USER_SERVICE}:admin:users:{{user_id}}:detail"

    # Admin Group Keys
    ADMIN_GROUPS_LIST = f"{USER_SERVICE}:admin:groups:list:p{{page}}:s{{page_size}}"
    ADMIN_GROUPS_LIST_WILDCARD = f"{USER_SERVICE}:admin:groups:list:*"
    ADMIN_GROUP_DETAIL = f"{USER_SERVICE}:admin:groups:{{group_id}}:detail"
    ADMIN_GROUP_MEMBERS_LIST = f"{USER_SERVICE}:admin:groups:{{group_id}}:members"


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

    # --- Helper methods to format patterns manually ---
    
    @staticmethod
    def user_core_key(user_id: str) -> str:
        return RedisKeys.USER_CORE.format(user_id=user_id)

    @staticmethod
    def user_profile_identity_key(user_id: str) -> str:
        return RedisKeys.USER_PROFILE_IDENTITY.format(user_id=user_id)

    @staticmethod
    def user_profile_health_key(user_id: str) -> str:
        return RedisKeys.USER_PROFILE_HEALTH.format(user_id=user_id)

    @staticmethod
    def user_tags_key(user_id: str) -> str:
        return RedisKeys.USER_TAGS.format(user_id=user_id)
    
    @staticmethod
    def user_groups_list_key(user_id: str) -> str:
        return RedisKeys.USER_GROUPS_LIST.format(user_id=user_id)

    @staticmethod
    def group_detail_key(group_id: str) -> str:
        return RedisKeys.GROUP_DETAIL.format(group_id=group_id)

    @staticmethod
    def group_members_list_key(group_id: str) -> str:
        return RedisKeys.GROUP_MEMBERS_LIST.format(group_id=group_id)

    @staticmethod
    def admin_user_detail_key(user_id: str) -> str:
        return RedisKeys.ADMIN_USER_DETAIL.format(user_id=user_id)

    @staticmethod
    def admin_group_detail_key(group_id: str) -> str:
        return RedisKeys.ADMIN_GROUP_DETAIL.format(group_id=group_id)

    @staticmethod
    def admin_group_members_list_key(group_id: str) -> str:
        return RedisKeys.ADMIN_GROUP_MEMBERS_LIST.format(group_id=group_id)
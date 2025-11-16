# microservices/user-service/app/services/redis_service.py
from datetime import datetime, UTC

from shopping_shared.caching.redis_manager import redis_manager


class RedisService:
    _redis_client = redis_manager.client

    # --- Key Naming Convention ---
    # Format: <service_name>:<object_type>:<identifier>
    _service_prefix = "user-service"
    _allowlist_object = "session"
    _blocklist_object = "jwt-blocklist"
    _otp_object = "otp"
    _global_revoke_object = "global_revoke_ts"
    # ---------------------------

    @classmethod
    def _generate_key(
            cls,
            object_type: str,
            identifier: str
    ) -> str:
        """
        Generates a standardized Redis key based on the service's convention.
        Format: <service_prefix>:<object_type>:<identifier>
        """
        return f"{cls._service_prefix}:{object_type}:{identifier}"

    @classmethod
    def _get_allowlist_key(cls, user_id: str) -> str:
        """Generates the Redis key for the user session allowlist."""
        return cls._generate_key(cls._allowlist_object, user_id)

    @classmethod
    def _get_blocklist_key(cls, jti: str) -> str:
        """Generates the Redis key for the JWT blocklist."""
        return cls._generate_key(cls._blocklist_object, jti)

    @classmethod
    def _get_otp_key(cls, email: str, action: str) -> str:
        """Generates the Redis key for OTP storage."""
        identifier = f"{action.lower()}:{email.lower()}"
        return cls._generate_key(cls._otp_object, identifier)

    @classmethod
    def _get_global_revoke_key(cls, user_id: str) -> str:
        """Generates the key for storing the user's global token revocation timestamp."""
        return cls._generate_key(cls._global_revoke_object, user_id)

    # --- Session/Token Methods ---

    @classmethod
    async def add_session_to_allowlist(
        cls,
        user_id: str,
        new_refresh_jti: str,
        ttl_seconds: int
    ) -> None:
        """
        Lưu JTI của Refresh Token vào Allowlist để kích hoạt phiên.
        Ghi đè bất kỳ phiên cũ nào (support for /login endpoint).
        """
        allowlist_key = cls._get_allowlist_key(user_id)
        await cls._redis_client.set(
            allowlist_key,
            new_refresh_jti,
            ex=ttl_seconds
        )

    @classmethod
    async def validate_jti_in_allowlist(
        cls,
        user_id: str,
        jti_from_token: str
    ) -> bool:
        """
        Kiểm tra JTI từ token có khớp với JTI trong Allowlist không.
        (support for /refresh-token endpoint).
        """
        allowlist_key = cls._get_allowlist_key(user_id)
        stored_jti = await cls._redis_client.get(allowlist_key)

        if stored_jti is None:
            return False

        return stored_jti == jti_from_token

    @classmethod
    async def remove_session_from_allowlist(
            cls,
            user_id: str
    ) -> None:
        """
        Xóa Refresh Token JTI khỏi Allowlist khi user logout.
        """
        allowlist_key = cls._get_allowlist_key(user_id)
        await cls._redis_client.delete(allowlist_key)

    @classmethod
    async def add_token_to_blocklist(
        cls,
        access_token_jti: str,
        remaining_ttl_seconds: int
    ) -> None:
        """
        Thêm JTI của Access Token vào Blocklist để vô hiệu hóa nó.
        """
        blocklist_key = cls._get_blocklist_key(access_token_jti)
        if remaining_ttl_seconds > 0:
            await cls._redis_client.set(
                blocklist_key,
                "true",
                ex=remaining_ttl_seconds
            )

    @classmethod
    async def is_token_in_blocklist(
        cls,
        access_token_jti: str
    ) -> bool:
        """
        Kiểm tra JTI của Access Token có nằm trong Blocklist không.
        """
        blocklist_key = cls._get_blocklist_key(access_token_jti)
        is_blocked = await cls._redis_client.get(blocklist_key)
        return bool(is_blocked)

    # ---  Global Revoke ---
    @classmethod
    async def revoke_all_tokens_for_user(cls, user_id: str):
        """
        Đặt một "mốc thời gian thu hồi" toàn cục cho user.
        Việc này sẽ vô hiệu hóa tất cả token được cấp TRƯỚC thời điểm này.
        (Được gọi khi reset/đổi mật khẩu)
        """
        key = cls._get_global_revoke_key(user_id)
        current_timestamp = int(datetime.now(UTC).timestamp())

        # Chỉ cần set, không cần TTL (hoặc TTL dài, ví dụ 7 ngày)
        await cls._redis_client.set(key, current_timestamp)

    @classmethod
    async def get_global_revoke_timestamp(cls, user_id: str) -> int | None:
        """
        Lấy "mốc thời gian thu hồi" toàn cục của user.
        (Được gọi bởi Auth Middleware trên mọi request)
        """
        key = cls._get_global_revoke_key(user_id)
        ts_str = await cls._redis_client.get(key)

        return int(ts_str) if ts_str else None

    # --- OTP Methods ---
    @classmethod
    async def set_otp(cls, email: str, action: str, otp_hash: str, ttl_seconds: int):
        """Stores an OTP hash in Redis with a TTL."""
        key = cls._get_otp_key(email, action)
        await cls._redis_client.set(key, otp_hash, ex=ttl_seconds)

    @classmethod
    async def get_otp(cls, email: str, action: str) -> str | None:
        """Retrieves an OTP hash from Redis."""
        key = cls._get_otp_key(email, action)
        return await cls._redis_client.get(key)

    @classmethod
    async def delete_otp(cls, email: str, action: str):
        """Deletes an OTP from Redis."""
        key = cls._get_otp_key(email, action)
        await cls._redis_client.delete(key)




redis_service = RedisService()

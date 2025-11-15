

from redis.asyncio import Redis
from typing import Optional


class RedisService:
    @staticmethod
    async def add_session_to_allowlist(
        redis_client: Redis,
        user_id: str,
        new_refresh_jti: str,
        ttl_seconds: int
    ) -> None:
        """
        Lưu JTI của Refresh Token vào Allowlist để kích hoạt phiên.
        Ghi đè bất kỳ phiên cũ nào.
        """
        allowlist_key = f"user_session:{user_id}"
        await redis_client.set(
            allowlist_key,
            new_refresh_jti,
            ex=ttl_seconds
        )

    @staticmethod
    async def validate_jti_in_allowlist(
        redis_client: Redis,
        user_id: str,
        jti_from_token: str
    ) -> bool:
        """
        Kiểm tra JTI từ token có khớp với JTI trong Allowlist không.
        """
        allowlist_key = f"user_session:{user_id}"
        stored_jti = await redis_client.get(allowlist_key)

        if stored_jti is None:
            # Không tìm thấy key -> User đã logout hoặc hết hạn
            return False

        stored_jti = stored_jti.decode("utf-8")
        return stored_jti == jti_from_token

    @staticmethod
    async def remove_session_from_allowlist(redis_client: Redis, user_id: str) -> None:
        """
        Xóa JTI khỏi Allowlist khi user logout.
        """
        allowlist_key = f"user_session:{user_id}"
        await redis_client.delete(allowlist_key)

    @staticmethod
    async def add_token_to_blocklist(
        redis_client: Redis,
        access_token_jti: str,
        remaining_ttl_seconds: int
    ) -> None:
        """
        Thêm JTI của Access Token vào Blocklist để vô hiệu hóa nó.
        """
        blocklist_key = f"blocked_jwt:{access_token_jti}"

        # Đảm bảo TTL > 0 để tránh lỗi Redis
        if remaining_ttl_seconds > 0:
            await redis_client.set(
                blocklist_key,
                "true",
                ex=remaining_ttl_seconds
            )

    @staticmethod
    async def is_token_in_blocklist(
        redis_client: Redis,
        access_token_jti: str
    ) -> bool:
        """
        Kiểm tra JTI của Access Token có nằm trong Blocklist không.
        """
        blocklist_key = f"blocked_jwt:{access_token_jti}"
        is_blocked = await redis_client.get(blocklist_key)
        return bool(is_blocked)

    # async def is_token_in_blocklist(
    #         redis_client: Redis,
    #         access_token_jti: str
    # ) -> bool:
    #     """
    #     Kiểm tra JTI của Access Token có nằm trong Blocklist không.
    #     """
    #     blocklist_key = f"blocked_jwt:{access_token_jti}"
    #
    #     is_blocked = await redis_client.get(blocklist_key)
    #
    #     if is_blocked:
    #         print(f"BLOCKLIST: CHECK FAILED (JTI {access_token_jti} is blocked)")
    #         return True
    #
    #     # print(f"BLOCKLIST: CHECK SUCCESS (JTI {access_token_jti} is not blocked)")
    #     return False

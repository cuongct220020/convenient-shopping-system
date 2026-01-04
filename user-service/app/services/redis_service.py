# user-service/app/services/redis_service.py
import json
from datetime import datetime, UTC

from shopping_shared.caching.redis_manager import redis_manager
from shopping_shared.caching.redis_keys import RedisKeys
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Redis Service")

class RedisService:

    # --- Idempotency Methods ---

    @classmethod
    async def acquire_idempotency_lock(cls, user_id: str, idem_key: str, lock_ttl: int = 30) -> bool:
        """
        Tries to acquire a processing lock for the idempotency key.
        Returns True if acquired (first request), False if already processing or completed.
        Uses SETNX (set if not exists) behavior via `set(..., nx=True)`.
        """
        key = RedisKeys.idempotency(user_id, idem_key)
        # Value 'PROCESSING' indicates the request is currently being handled.
        # nx=True ensures we only set it if the key doesn't exist.
        return await redis_manager.client.set(key, "PROCESSING", ex=lock_ttl, nx=True)

    @classmethod
    async def save_idempotency_result(cls, user_id: str, idem_key: str, response_data: dict, ttl_seconds: int):
        """
        Saves the successful response payload to Redis, overwriting the 'PROCESSING' lock.
        """
        key = RedisKeys.idempotency(user_id, idem_key)
        await redis_manager.client.set(key, json.dumps(response_data), ex=ttl_seconds)

    @classmethod
    async def get_idempotency_result(cls, user_id: str, idem_key: str) -> str | None:
        """
        Retrieves the stored idempotency result or status.
        Returns:
            - None: Key does not exist.
            - "PROCESSING": Request is currently in progress.
            - JSON String: The cached response data.
        """
        key = RedisKeys.idempotency(user_id, idem_key)
        return await redis_manager.client.get(key)

    @classmethod
    async def release_idempotency_lock(cls, user_id: str, idem_key: str):
        """
        Removes the idempotency key (used if processing failed/crashed).
        """
        key = RedisKeys.idempotency(user_id, idem_key)
        await redis_manager.client.delete(key)

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
        allowlist_key = RedisKeys.user_session(user_id)
        await redis_manager.client.set(
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
        allowlist_key = RedisKeys.user_session(user_id)
        stored_jti = await redis_manager.client.get(allowlist_key)

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
        allowlist_key = RedisKeys.user_session(user_id)
        await redis_manager.client.delete(allowlist_key)

    @classmethod
    async def add_token_to_blocklist(
        cls,
        access_token_jti: str,
        remaining_ttl_seconds: int
    ) -> None:
        """
        Thêm JTI của Access Token vào Blocklist để vô hiệu hóa nó.
        """
        blocklist_key = RedisKeys.jwt_blocklist(access_token_jti)
        if remaining_ttl_seconds > 0:
            await redis_manager.client.set(
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
        blocklist_key = RedisKeys.jwt_blocklist(access_token_jti)
        is_blocked = await redis_manager.client.get(blocklist_key)
        return bool(is_blocked)

    # ---  Global Revoke ---
    @classmethod
    async def revoke_all_tokens_for_user(cls, user_id: str):
        """
        Đặt một "mốc thời gian thu hồi" toàn cục cho user.
        (Được gọi khi reset/đổi mật khẩu)
        """
        key = RedisKeys.global_revoke(user_id)
        current_timestamp = int(datetime.now(UTC).timestamp())

        await redis_manager.client.set(key, current_timestamp)

    @classmethod
    async def get_global_revoke_timestamp(cls, user_id: str) -> int | None:
        """
        Lấy "mốc thời gian thu hồi" toàn cục của user.
        (Được gọi bởi Auth Middleware trên mọi request)
        """
        key = RedisKeys.global_revoke(user_id)
        ts_str = await redis_manager.client.get(key)

        return int(ts_str) if ts_str else None

    # --- OTP Methods ---
    @classmethod
    async def set_otp(cls, email: str, action: str, otp_data: dict, ttl_seconds: int):
        """Lưu trữ dữ liệu OTP (dưới dạng JSON) vào Redis với TTL."""
        try:
            key = RedisKeys.otp(email, action)
            await redis_manager.client.set(key, json.dumps(otp_data), ex=ttl_seconds)
            logger.info(f"OTP stored successfully for {email} with key: {key}")
        except Exception as e:
            logger.error(f"Failed to set OTP for {email} in Redis: {str(e)}")
            raise

    @classmethod
    async def get_otp(cls, email: str, action: str) -> dict | None:
        """Lấy dữ liệu OTP (dưới dạng JSON) từ Redis."""
        try:
            key = RedisKeys.otp(email, action)
            data_str = await redis_manager.client.get(key)
            if data_str:
                return json.loads(data_str)
            return None
        except Exception as e:
            logger.error(f"Failed to get OTP for {email} from Redis: {str(e)}")
            return None

    @classmethod
    async def delete_otp(cls, email: str, action: str):
        """Deletes an OTP from Redis."""
        try:
            key = RedisKeys.otp(email, action)
            await redis_manager.client.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete OTP for {email} from Redis: {str(e)}")

    # --- General Caching Methods ---

    @classmethod
    async def get_cache(cls, key: str) -> dict | None:
        """Retrieves a cached JSON object."""
        try:
            data_str = await redis_manager.client.get(key)
            if data_str:
                return json.loads(data_str)
            return None
        except Exception as e:
            logger.error(f"Cache miss or error for {key}: {e}")
            return None


    @classmethod
    async def set_cache(cls, key: str, data: dict, ttl: int):
        """Stores a JSON object in cache with TTL."""
        try:
            await redis_manager.client.set(key, json.dumps(data), ex=ttl)
        except Exception as e:
            logger.error(f"Failed to set cache for {key}: {e}")


    @classmethod
    async def delete_pattern(cls, pattern: str):
        """Deletes all keys matching the pattern."""
        try:
            # Use scan_iter for efficient iteration
            keys = []
            async for key in redis_manager.client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await redis_manager.client.delete(*keys)
                logger.info(f"Deleted {len(keys)} keys matching {pattern}")
        except Exception as e:
            logger.error(f"Failed to delete pattern {pattern}: {e}")



redis_service = RedisService()

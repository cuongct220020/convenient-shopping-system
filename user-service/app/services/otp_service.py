# user-service/app/services/otp_service.py
import random
from datetime import timedelta

from pydantic import SecretStr

from shopping_shared.utils.logger_utils import get_logger

from app.utils.password_utils import hash_password, verify_password
from app.services.redis_service import RedisService


logger = get_logger("OTP Service")

class OTPService:
    _TTL = timedelta(minutes=5)  # OTPs are valid for 5 minutes

    @classmethod
    async def generate_and_store_otp(cls, email: str, action: str, data: dict = None) -> str:
        """
        Generates a 6-digit OTP, hashes it, and stores the hash and optional data in Redis.
        Returns the plain-text OTP to be sent to the user.
        """
        otp_code = str(random.randint(100000, 999999))
        hashed_otp = hash_password(otp_code)

        # Prepare data for storage
        stored_data = {"otp_hash": hashed_otp}
        if data:
            stored_data.update(data)

        await RedisService.set_otp(
            email=email,
            action=action,
            otp_data=stored_data,
            ttl_seconds=int(cls._TTL.total_seconds())
        )

        return otp_code

    @classmethod
    async def verify_otp(cls, email: str, action: str, submitted_code: str) -> dict | None:
        """
        Verifies the submitted OTP against the stored hash using RedisService.
        If verification is successful, the OTP key is deleted and the stored data is returned.
        """
        stored_data = await RedisService.get_otp(email, action)

        if not stored_data:
            # OTP does not exist or has expired
            return None

        stored_hash = stored_data.get("otp_hash")
        if not stored_hash:
            # Data is corrupted or in an old format
            return None

        # The redis client is configured with decode_responses=True, so no .decode() needed
        if await verify_password(SecretStr(submitted_code), stored_hash):
            # Correct OTP, delete it immediately to prevent reuse
            await RedisService.delete_otp(email, action)
            return stored_data

        # Incorrect OTP
        return None

otp_service = OTPService()

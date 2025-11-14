# app/utils/jwt_utils.py
"""
Utility module for handling JWT tokens with Redis-based revocation.
Provides methods for token creation, verification, and revocation.
"""

import jwt
from datetime import datetime, timedelta, UTC
import uuid
from typing import Literal, Optional, Tuple

from sanic import Sanic

from shopping_shared.caching.redis_manager import redis_manager
from shopping_shared.exceptions import Unauthorized


class JWTHandler:
    """
    Handles JWT creation, verification, and revocation using Redis for denylisting.
    Config is initialized via Sanic app's config.
    """
    def __init__(self, app: Optional[Sanic] = None):
        if app:
            self.init_app(app)

    def init_app(self, app: Sanic):
        self.app = app
        self.config = app.config
        self.redis = redis_manager
        # Cache các giá trị config
        self.secret_key = self._get_config_value('JWT_SECRET')
        self.algorithm = self._get_config_value('JWT_ALGORITHM', 'HS256')
        self.access_token_expire_minutes = self._get_config_value('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 15)
        self.refresh_token_expire_days = self._get_config_value('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30)

    def _get_config_value(self, key: str, default=None):
        return self.config.get(key, default)

    def _create_token_payload(
        self,
        user_id: str,
        token_type: str,
        expiry_delta: timedelta,
        user_role: str | None = None,
        jti: Optional[str] = None
    ) -> dict:
        """
        Tạo payload chung cho cả access và refresh token.
        """
        issued_at_time = datetime.now(UTC)
        payload = {
            'token_type': token_type,
            'exp': issued_at_time + expiry_delta,
            'iat': issued_at_time,
            'sub': str(user_id),
            'role': user_role
        }
        if jti:
            payload['jti'] = jti
        return payload

    def create_access_token(self, user_id: str, user_role: str | None = None) -> Tuple[str, str]:
        """
        Tạo access token và trả về (token, jti).
        """
        jti = str(uuid.uuid4())
        expiry_delta = timedelta(minutes=self.access_token_expire_minutes)
        payload = self._create_token_payload(
            user_id=user_id,
            token_type='access',
            expiry_delta=expiry_delta,
            user_role=user_role,
            jti=jti
        )
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti

    def create_refresh_token(self, user_id: str, user_role: str | None = None) -> Tuple[str, str]:
        """
        Tạo refresh token và trả về (token, jti).
        """
        jti = str(uuid.uuid4())
        expiry_delta = timedelta(days=self.refresh_token_expire_days)
        payload = self._create_token_payload(
            user_id=user_id,
            token_type='refresh',
            expiry_delta=expiry_delta,
            user_role=user_role,
            jti=jti
        )
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti

    def create_tokens(self, user_id: str, user_role: str | None = None) -> Tuple[str, str, str, float]:
        """
        Tạo cả access và refresh token.
        Trả về: (access_token, refresh_token, access_token_jti, expires_in_minutes)
        """
        access_token, access_jti = self.create_access_token(user_id, user_role)
        refresh_token, refresh_jti = self.create_refresh_token(user_id, user_role)

        return (access_token, refresh_token, access_jti, float(self.access_token_expire_minutes))

    async def verify(self, token: str, token_type: Literal['access', 'refresh'] = 'access', check_revocation: bool = True):
        """
        Xác minh token và kiểm tra xem có bị revoke không.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise Unauthorized("Token has expired")
        except jwt.InvalidTokenError:
            raise Unauthorized("Invalid token")

        if payload.get('token_type') != token_type:
            raise Unauthorized(f"Invalid token type. Expected '{token_type}'.")

        if check_revocation:
            # 1. Check for global revocation (password change, etc.)
            user_id = payload.get('sub')
            iat = payload.get('iat')
            global_revoke_key = f"user_revoke_all_timestamp:{user_id}"
            last_global_revoke_ts = await self.redis.client.get(global_revoke_key)

            if last_global_revoke_ts and iat < int(last_global_revoke_ts):
                raise Unauthorized("Token has been revoked by a security event.")

            # 2. Check for individual token revocation (logout)
            jti = payload.get('jti')
            if jti:
                is_revoked = await self.redis.client.get(f"revoked_jti:{jti}")
                if is_revoked:
                    raise Unauthorized("Token has been revoked.")

        return payload

    async def revoke(self, jti: str, exp: datetime):
        """
        Revoke một token bằng cách thêm JTI vào Redis với TTL.
        """
        now = datetime.now(UTC)
        ttl = exp - now
        if ttl.total_seconds() > 0:
            await self.redis.client.setex(f"revoked_jti:{jti}", int(ttl.total_seconds()), "revoked")


# Singleton instance
jwt_handler = JWTHandler()
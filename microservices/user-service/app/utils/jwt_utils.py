# app/utils/jwt_utils.py

import jwt
import uuid

from typing import Optional, Tuple
from datetime import datetime, timedelta, UTC
from sanic import Sanic

class JWTHandler:
    """
    Handles JWT creation
    """
    def __init__(self, app: Optional[Sanic] = None):
        if app:
            self.init_app(app)

    def init_app(self, app: Sanic):
        self.config = app.config
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
        }

        if user_role:
            payload['user_role'] = user_role

        if jti:
            payload['jti'] = jti

        return payload

    def create_token(
            self,
            user_id: str,
            token_type: str = 'access',
            user_role: str | None = None,
    ) -> Tuple[str, str]:
        """
        Tạo access token (refresh token) và trả về (token, jti).
        """
        jti = str(uuid.uuid4())
        expiry_delta = timedelta(minutes=self.access_token_expire_minutes)
        payload = self._create_token_payload(
            user_id=user_id,
            token_type=token_type,
            expiry_delta=expiry_delta,
            user_role=user_role,
            jti=jti
        )
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti

    def create_tokens(
            self,
            user_id: str,
            user_role: str | None = None
        ) -> Tuple[str, str, str, str]:

        """
        Tạo cả access và refresh token.
        Trả về: (access_token, refresh_token, access_token_jti, refresh_token_jti)
        """

        access_token, access_jti = self.create_token(user_id, 'access', user_role)
        refresh_token, refresh_jti = self.create_token(user_id, 'refresh', user_role)

        return (access_token, refresh_token, access_jti, refresh_jti)

# Singleton instance
jwt_handler = JWTHandler()
# microservices/user-service/app/utils/jwt_utils.py

import jwt
import uuid

from typing import Optional, Tuple, Literal
from datetime import datetime, timedelta, UTC

from sanic import Sanic

from shopping_shared.exceptions import Unauthorized
from shopping_shared.schemas.base_schema import BaseSchema


class TokenData(BaseSchema):
    access_token: str
    refresh_token: str
    access_jti: uuid.UUID
    refresh_jti: uuid.UUID
    at_expires_in_minutes: int
    rt_ttl_seconds: int

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

        self.access_token_expire_minutes = int(
            self._get_config_value('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 15)
        )
        self.refresh_token_expire_days = int(
            self._get_config_value('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30)
        )

    def _get_config_value(self, key: str, default=None):
        return self.config.get(key, default)

    def _create_token_payload(
            self,
            user_id: str,
            token_type: str,
            expiry_delta: timedelta,
            user_role: str | None = None
    ) -> Tuple[dict, str]:
        """
        Tạo payload chung và JTI cho token.
        """
        jti = str(uuid.uuid4())
        issued_at_time = datetime.now(UTC)

        payload = {
            'iss': 'app-user-consumer',  # Issuer claim for Kong
            'token_type': token_type,
            'exp': issued_at_time + expiry_delta,
            'iat': issued_at_time,
            'sub': str(user_id),
            'jti': jti
        }

        if user_role:
            payload['user_role'] = user_role

        return payload, jti


    def _build_access_token(
            self, user_id: str, user_role: str | None = None
    ) -> Tuple[str, str, int]:
        """
        Xây dựng Access Token với thời gian hết hạn ngắn.
        Trả về: (token_str, jti, expires_in_minutes)
        """
        expiry_delta = timedelta(minutes=self.access_token_expire_minutes)

        payload, jti = self._create_token_payload(
            user_id=user_id,
            token_type='access',
            expiry_delta=expiry_delta,
            user_role=user_role
        )

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti, self.access_token_expire_minutes

    def _build_refresh_token(
            self, user_id: str, user_role: str | None = None
    ) -> Tuple[str, str, int]:
        """
        Xây dựng Refresh Token với thời gian hết hạn dài.
        Trả về: (token_str, jti, ttl_seconds)
        """
        expiry_delta = timedelta(days=self.refresh_token_expire_days)

        payload, jti = self._create_token_payload(
            user_id=user_id,
            token_type='refresh',
            expiry_delta=expiry_delta,
            user_role=user_role
        )

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        ttl_seconds = int(expiry_delta.total_seconds())
        return token, jti, ttl_seconds


    def create_tokens(
            self,
            user_id: str,
            user_role: str | None = None
    ) -> TokenData:
        """
        Tạo cả access và refresh token.
        Trả về: (
            access_token,
            refresh_token,
            access_jti,
            refresh_jti,
            at_expires_in_minutes, (cho client)
            rt_ttl_seconds (cho Redis)
        )
        """
        # Gọi 2 hàm chuyên biệt
        access_token, access_jti, at_expires_in_minutes = self._build_access_token(
            user_id, user_role
        )

        refresh_token, refresh_jti, rt_ttl_seconds = self._build_refresh_token(
            user_id, user_role
        )

        return TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            access_jti=access_jti,
            refresh_jti=refresh_jti,
            at_expires_in_minutes=at_expires_in_minutes,
            rt_ttl_seconds=rt_ttl_seconds
        )

    def decode_token_stateless(
        self,
        token: str,
        expected_token_type: Literal['access', 'refresh']
    ) -> dict:
        """
        Giải mã token và thực hiện kiểm tra STATELESS.
        Chỉ kiểm tra Chữ ký, Thời gian hết hạn (exp), và loại token.
        KHÔNG kiểm tra Redis (Allowlist/Blocklist).

        Raise Unauthorized nếu thất bại.
        Trả về payload nếu thành công.
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

        except jwt.ExpiredSignatureError:
            raise Unauthorized("Token has expired")
        except jwt.InvalidTokenError:
            raise Unauthorized("Invalid token")
        except Exception as e:
            # Bắt các lỗi JWT khác
            raise Unauthorized(f"Token decoding error: {e}")

        # Kiểm tra loại token
        token_type = payload.get('token_type')
        if token_type != expected_token_type:
            raise Unauthorized(f"Invalid token type. Expected '{expected_token_type}'.")

        # Kiểm tra các trường bắt buộc
        if not payload.get('sub') or not payload.get('jti'):
            raise Unauthorized("Invalid token payload (missing 'sub' or 'jti').")

        return payload


# Singleton instance
jwt_handler = JWTHandler()
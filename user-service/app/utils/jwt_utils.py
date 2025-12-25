# user-service/app/utils/jwt_utils.py
import jwt
import uuid
from typing import Tuple, Literal, Optional
from datetime import datetime, timedelta, UTC
from sanic import Sanic

from shopping_shared.exceptions import Unauthorized
from shopping_shared.schemas.base_schema import BaseSchema


class TokenData(BaseSchema):
    access_token: str
    refresh_token: str
    access_jti: str
    refresh_jti: str
    at_expires_in_minutes: int
    rt_ttl_seconds: int


class JWTHandler:
    """Singleton JWT Handler for creating and validating tokens."""

    _instance: Optional['JWTHandler'] = None

    def __init__(self, app: Sanic):
        if JWTHandler._instance is not None:
            raise RuntimeError("JWTHandler already initialized. Use get_instance().")

        self.app = app
        self.access_token_expire_minutes = app.config.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 15)
        self.refresh_token_expire_days = app.config.get("REFRESH_TOKEN_EXPIRE_DAYS", 7)
        self.algorithm = app.config.get("JWT_ALGORITHM", "HS256")

        # Load keys based on algorithm
        if self.algorithm.startswith("RS"):
            self.private_key = app.config["JWT_PRIVATE_KEY"]
            self.public_key = app.config["JWT_PUBLIC_KEY"]
        else:
            self.secret_key = app.config["JWT_SECRET"]

    @classmethod
    def initialize(cls, app: Sanic) -> 'JWTHandler':
        """Initialize singleton instance with Sanic app."""
        if cls._instance is None:
            cls._instance = cls(app)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'JWTHandler':
        """Get singleton instance."""
        if cls._instance is None:
            raise RuntimeError("JWTHandler not initialized. Call initialize() first.")
        return cls._instance

    @staticmethod
    def _create_token_payload(
        user_id: str,
        token_type: str,
        expiry_delta: timedelta,
        user_role: str | None = None,
        email: str | None = None
    ) -> Tuple[dict, str]:
        """Create common token payload and JTI."""
        jti = str(uuid.uuid4())
        issued_at_time = datetime.now(UTC)

        payload = {
            'iss': 'shopping-user-service',
            'token_type': token_type,
            'exp': issued_at_time + expiry_delta,
            'iat': issued_at_time,
            'sub': str(user_id),
            'jti': jti,
            'aud': 'shopping-system-users'
        }

        if user_role:
            payload['system_role'] = user_role
        if email:
            payload['email'] = email

        return payload, jti

    def _build_access_token(
        self,
        user_id: str,
        user_role: str | None = None,
        email: str | None = None
    ) -> Tuple[str, str, int]:
        """Build Access Token with short expiry."""
        expiry_delta = timedelta(minutes=self.access_token_expire_minutes)
        payload, jti = self._create_token_payload(
            user_id=user_id,
            token_type='access',
            expiry_delta=expiry_delta,
            user_role=user_role,
            email=email
        )

        # Encode with appropriate key
        key = self.private_key if self.algorithm.startswith("RS") else self.secret_key
        token = jwt.encode(payload, key, algorithm=self.algorithm)
        return token, jti, self.access_token_expire_minutes

    def _build_refresh_token(
            self, user_id: str, user_role: str | None = None, email: str | None = None
    ) -> Tuple[str, str, int]:
        """Build Refresh Token with long expiry."""
        expiry_delta = timedelta(days=self.refresh_token_expire_days)
        payload, jti = self._create_token_payload(
            user_id=user_id,
            token_type='refresh',
            expiry_delta=expiry_delta,
            user_role=user_role,
            email=email
        )

        key = self.private_key if self.algorithm.startswith("RS") else self.secret_key
        token = jwt.encode(payload, key, algorithm=self.algorithm)
        ttl_seconds = int(expiry_delta.total_seconds())
        return token, jti, ttl_seconds

    def create_tokens(
        self,
        user_id: str,
        user_role: str | None = None,
        email: str | None = None
    ) -> TokenData:
        """Create both access and refresh tokens."""
        access_token, access_jti, at_expires_in_minutes = self._build_access_token(user_id, user_role, email)
        refresh_token, refresh_jti, rt_ttl_seconds = self._build_refresh_token(user_id, user_role, email)

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
        """Decode token with stateless validation (signature, expiry, type)."""
        try:
            key = self.public_key if self.algorithm.startswith("RS") else self.secret_key
            payload = jwt.decode(token, key, algorithms=[self.algorithm])

        except jwt.ExpiredSignatureError:
            raise Unauthorized("Token has expired")
        except jwt.InvalidTokenError:
            raise Unauthorized("Invalid token")
        except Exception as e:
            raise Unauthorized(f"Token decoding error: {e}")

        # Validate token type
        token_type = payload.get('token_type')
        if token_type != expected_token_type:
            raise Unauthorized(f"Invalid token type. Expected '{expected_token_type}'.")

        # Validate required fields
        if not payload.get('sub') or not payload.get('jti'):
            raise Unauthorized("Invalid token payload (missing 'sub' or 'jti').")

        return payload
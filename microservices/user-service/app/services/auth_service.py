# app/services/auth_service.py
from datetime import datetime, UTC, timedelta
from typing import Any
import jwt
from pydantic import BaseModel as PydanticBase, SecretStr, EmailStr

from shopping_shared.caching.redis_manager import redis_manager
from shopping_shared.exceptions import Unauthorized, Forbidden, Conflict, NotFound
from app.repositories.user_repository import UserRepository
from app.schemas.auth.login_schema import LoginRequest
from app.schemas.auth.otp_schema import OTPRequest, OtpAction, OTPVerifyRequest
from app.schemas.auth.register_schema import RegisterRequest
from app.schemas.auth.reset_password_schema import ResetPasswordRequest
from app.schemas.auth.token_schema import TokenData
from app.schemas.users.user_schema import UserUpdate
from app.utils.password_utils import verify_password, hash_password
from app.utils.jwt_utils import jwt_handler
from app.services.email_service import email_service
from app.services.otp_service import otp_service


# A private schema for creating user records
class _UserCreateSchema(PydanticBase):
    username: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = False  # Users are inactive until email is verified


class AuthService:

    @classmethod
    async def register_user(
            cls,
            reg_data: RegisterRequest,
            user_repo: UserRepository
    ):
        """Handles the first step of registration: creating an inactive user and sending a verification OTP."""
        existing_user = await user_repo.get_by_username(reg_data.email)
        if existing_user and existing_user.is_active:
            raise Conflict("An account with this email already exists.")

        if not existing_user:
            hashed_password = hash_password(reg_data.password.get_secret_value())
            user_create_data = _UserCreateSchema(
                username=reg_data.email,
                password=hashed_password,
                first_name=reg_data.first_name,
                last_name=reg_data.last_name,
                is_active=False
            )
            await user_repo.create(user_create_data)

        # Proceed to send OTP for the new or existing inactive user
        otp_request_data = OTPRequest(email=reg_data.email, action=OtpAction.REGISTER)
        await cls.request_otp(otp_request_data, user_repo)

    @classmethod
    async def login(
            cls,
            login_data: LoginRequest,
            user_repo: UserRepository
    ) -> TokenData:
        """
        Handles user login, creates JWTs, and saves the refresh token JTI
        to enforce a single session.
        """
        user = await user_repo.get_by_username(login_data.username)
        if not user or not verify_password(login_data.password.get_secret_value(), user.password):
            raise Unauthorized("Invalid username or password")

        if not user.is_active:
            raise Forbidden("Account is not active. Please verify your email.")

        # Reset failed login attempts if any
        if hasattr(user, 'failed_login_attempts') and user.failed_login_attempts > 0:
            await user_repo.reset_failed_attempts(user.user_id)

        # Generate new tokens
        access_token, refresh_token, _, refresh_jti, expires_in = jwt_handler.create_tokens(
            user_id=user.id, user_role=user.user_role.value)

        # Update user record with the new JTI and last login time
        user.active_refresh_jti = refresh_jti
        user.last_login = datetime.now(UTC)
        await user_repo.session.commit()

        return TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in_minutes=expires_in,
        )

    @classmethod
    async def logout(cls, user_id: Any, user_repo: UserRepository, access_jti: str, access_exp: int, refresh_token: str | None):
        """
        Logs out a user by revoking tokens in Redis and clearing the active JTI in the database.
        """
        # 1. Revoke the access token in Redis (mandatory)
        access_exp_datetime = datetime.fromtimestamp(access_exp, tz=UTC)
        await jwt_handler.revoke(jti=access_jti, exp=access_exp_datetime)

        # 2. Find user and clear their active JTI from the database
        user = await user_repo.get_by_id(user_id)
        if user:
            user.active_refresh_jti = None
            await user_repo.session.commit()

        # 3. Revoke the refresh token in Redis (if provided)
        if not refresh_token:
            return

        try:
            payload = await jwt_handler.verify(token=refresh_token, token_type="refresh", check_revocation=False)
            refresh_jti = payload.get("jti")
            refresh_exp = payload.get("exp")

            if refresh_jti and refresh_exp:
                refresh_exp_datetime = datetime.fromtimestamp(refresh_exp, tz=UTC)
                await jwt_handler.revoke(jti=refresh_jti, exp=refresh_exp_datetime)
        except (jwt.PyJWTError, Unauthorized):
            pass # Token is already invalid, no action needed

    @classmethod
    async def refresh_tokens(
            cls,
            old_refresh_token: str,
            user_repo: UserRepository,
    ) -> TokenData:
        """
        Handles token refresh with rotation, enforcing a single active session.
        """
        try:
            payload = await jwt_handler.verify(token=old_refresh_token, token_type="refresh")
        except (jwt.PyJWTError, Unauthorized) as e:
            raise Unauthorized("Invalid or expired refresh token") from e

        user_id = payload.get("sub")
        old_jti = payload.get("jti")

        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise Unauthorized("User account is inactive or not found.")

        # CRITICAL CHECK: Enforce single session
        if user.active_refresh_jti != old_jti:
            # This token is not the currently active one; it has been superseded by a new login.
            # As a security measure, revoke all tokens for the user.
            await cls.revoke_all_tokens_for_user(user_id, user_repo)
            raise Forbidden("This session has been invalidated by a newer login.")

        # Create a new pair of tokens
        access_token, new_refresh_token, _, new_refresh_jti, expires_in = jwt_handler.create_tokens(
            user_id=user.id, user_role=user.user_role.value)

        # Update the user's record with the new JTI
        user.active_refresh_jti = new_refresh_jti
        await user_repo.session.commit()

        return TokenData(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in_minutes=expires_in
        )

    @classmethod
    async def request_otp(
            cls,
            otp_data: OTPRequest,
            user_repo: UserRepository
    ):
        """Handles the business logic for requesting an OTP using Redis."""
        if otp_data.action == OtpAction.RESET_PASSWORD:
            user = await user_repo.get_by_username(otp_data.email)
            if not user:
                raise NotFound("No account found with this email address.")

        otp_code = await otp_service.generate_and_store_otp(otp_data.email, otp_data.action.value)
        await email_service.send_otp(email=otp_data.email, otp_code=otp_code, action=otp_data.action)

    @classmethod
    async def reset_password_with_otp(
            cls,
            data: ResetPasswordRequest,
            user_repo: UserRepository,
    ):
        """Verifies OTP, resets password, and revokes all sessions/tokens for the user."""
        is_valid = await otp_service.verify_otp(
            email=data.email,
            action=OtpAction.RESET_PASSWORD.value,
            submitted_code=data.otp_code.get_secret_value()
        )

        if not is_valid:
            raise Unauthorized("Invalid or expired OTP code.")

        user = await user_repo.get_by_username(data.email)
        if not user:
            raise NotFound("User account not found.")

        # Reset password
        hashed_new_password = hash_password(data.new_password.get_secret_value())
        user.password = hashed_new_password
        
        # Invalidate all sessions
        await cls.revoke_all_tokens_for_user(user.id, user_repo)

    @classmethod
    async def verify_registration_otp(cls, data: OTPVerifyRequest, user_repo: UserRepository):
        """Verifies an OTP from Redis for registration and activates the user account."""
        is_valid = await otp_service.verify_otp(
            email=data.email,
            action=OtpAction.REGISTER.value,
            submitted_code=data.otp_code.get_secret_value()
        )

        if not is_valid:
            raise Unauthorized("Invalid or expired OTP code.")

        user = await user_repo.get_by_username(data.email, include_deleted=True)
        if not user:
            raise NotFound("User account not found.")

        if not user.is_active:
            await user_repo.activate_user(user.id)

    @classmethod
    async def revoke_all_tokens_for_user(cls, user_id: Any, user_repo: UserRepository):
        """
        Instantly invalidates all tokens for a user by:
        1. Setting a global revocation timestamp in Redis.
        2. Clearing the active refresh token JTI from the user's database record.
        """
        # 1. Invalidate in DB
        user = await user_repo.get_by_id(user_id)
        if user:
            user.active_refresh_jti = None
            await user_repo.session.commit()

        # 2. Invalidate in Redis
        key = f"user_revoke_all_timestamp:{user_id}"
        refresh_token_days = 30 # Should ideally get from config
        await redis_manager.client.set(key, int(datetime.now(UTC).timestamp()), ex=timedelta(days=refresh_token_days + 1))
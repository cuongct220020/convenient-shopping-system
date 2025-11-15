# app/services/auth_service.py
from datetime import datetime, UTC, timedelta
from typing import Any, Tuple
import jwt
from pydantic import EmailStr

from shopping_shared.caching.redis_manager import redis_manager
from shopping_shared.exceptions import Unauthorized, Forbidden, Conflict, NotFound, BadRequest

from app.constants import OtpAction
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateSchema
from app.utils.password_utils import verify_password, hash_password
from app.utils.jwt_utils import jwt_handler
from app.services.otp_service import otp_service
from app.services.redis_service import RedisService

from app.schemas import (
    LoginRequestSchema,
    RegisterRequestSchema,
    AccessTokenSchema,
    SendVerificationOTPRequestSchema,
    VerifyAccountRequestSchema,
    ResetPasswordRequestSchema,
)


class AuthService:

    @classmethod
    async def register_account(
        cls,
        reg_data: RegisterRequestSchema,
        user_repo: UserRepository
    ):
        """Handles the first step of registration: creating an inactive user and sending a verification OTP."""
        existing_user = await user_repo.get_by_username(reg_data.email)
        if existing_user and existing_user.is_active:
            raise Conflict("An account with this email already exists.")

        if not existing_user:
            hashed_password = hash_password(reg_data.password.get_secret_value())
            # Use the new UserCreateSchema
            user_create_data = UserCreateSchema(
                user_name=reg_data.user_name,
                email=reg_data.email,
                password=hashed_password,
                first_name=reg_data.first_name,
                last_name=reg_data.last_name,
                is_active=False
            )
            await user_repo.create(user_create_data)

        # Proceed to send OTP for the new or existing inactive user
        otp_request_data = SendVerificationOTPRequestSchema(email=reg_data.email, action=OtpAction.REGISTER)
        await cls.request_otp(otp_request_data, user_repo)


    @classmethod
    async def login_account(
        cls,
        login_data: LoginRequestSchema,
        user_repo: UserRepository
    ) -> Tuple[AccessTokenSchema, str]:
        """
        Handles user login, creates JWTs, and saves the refresh token JTI
        to enforce a single session.
        """
        user_identifier = login_data.identifier

        if EmailStr(user_identifier):
            user = await user_repo.get_by_email(user_identifier)
        else:
            user = await user_repo.get_by_username(user_identifier)

        if not user or not verify_password(login_data.password.get_secret_value(), user.password_hash):
            raise Unauthorized("Invalid username or password")

        if not user.is_active:
            raise Forbidden("Account is not active. Please verify your email.")

        # Generate new tokens
        jwt_token, refresh_token, jwt_token_jti, refresh_token_jti = jwt_handler.create_tokens(
            user_id=str(user.id),
            user_role=user.system_role.value
        )

        access_token = AccessTokenSchema(
            access_token=jwt_token,
            token_type="Bearer",
            expires_in_minutes=int(jwt_token["expires_delta"])
        )

        # Cập nhật refresh token JTI cho user để thực hiện single session
        await user_repo.update_refresh_jti(user.id, refresh_token_jti)



        user.last_login = datetime.now()
        await user_repo.update(user)

        return access_token, refresh_token





    @classmethod
    async def logout_account(cls, user_id: Any, user_repo: UserRepository, access_jti: str, access_exp: int,
                     refresh_token: str | None):
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
            pass  # Token is already invalid, no action needed

    @classmethod
    async def refresh_tokens(
            cls,
            old_refresh_token: str,
            user_repo: UserRepository,
    ) -> AccessTokenResponseSchema:
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
        access_token, new_refresh_token, _, new_refresh_jti = jwt_handler.create_tokens(
            user_id=str(user.id), user_role=user.system_role.value)

        # Update the user's record with the new JTI
        user.active_refresh_jti = new_refresh_jti
        await user_repo.session.commit()

        return AccessTokenResponseSchema(
            access_token=access_token        )

    @classmethod
    async def request_otp(
            cls,
            otp_data: SendVerificationOTPRequestSchema,
            user_repo: UserRepository
    ):
        """Handles the business logic for requesting an OTP using Redis."""
        if otp_data.action == OtpAction.RESET_PASSWORD and otp_data.action == OtpAction.CHANGE_EMAIL:
            user = await user_repo.get_user_by_email(otp_data.email)
            if not user:
                raise NotFound("No account found with this email address.")
        elif otp_data.action == OtpAction.REGISTER:
            # For registration, user might not exist yet or be inactive.
            # The OTP is sent regardless, but the user creation happens in register_user.
            pass


        otp_code = await otp_service.generate_and_store_otp(otp_data.email, otp_data.action.value)


    @classmethod
    async def verify_otp_and_perform_action(
            cls,
            data: VerifyAccountRequestSchema,
            user_repo: UserRepository
    ) -> bool:
        """
        Verifies an OTP and performs the corresponding action based on the OtpAction.
        Returns True if OTP is valid and action is performed, False otherwise.
        """
        is_valid = await otp_service.verify_otp(
            email=data.email,
            action=data.action.value,
            submitted_code=data.otp
        )

        if not is_valid:
            raise Unauthorized("Invalid or expired OTP code.")

        user = await user_repo.get_by_username(data.email, include_deleted=True)
        if not user:
            raise NotFound("User account not found.")

        match data.action:
            case OtpAction.REGISTER:
                if not user.is_active:
                    await user_repo.activate_user(user.id)
                return True
            case OtpAction.RESET_PASSWORD:
                # For reset password, successful OTP verification means the user is authorized to reset.
                # The actual password reset happens in reset_password_with_otp, which is called separately.
                return True
            case OtpAction.CHANGE_EMAIL:
                # This action would typically involve updating the user's email in the database
                # after a successful OTP verification.
                # For now, we'll just return True, assuming the calling context will handle the email change.
                # A more complete implementation would involve a temporary email field on the user model
                # or a dedicated service method for email change confirmation.
                return True
            case _:
                raise ValueError(f"Unsupported OTP action: {data.action}")

    @classmethod
    async def reset_password_with_otp(
            cls,
            data: ResetPasswordRequestSchema,
            user_repo: UserRepository,
    ):
        """Verifies OTP, resets password, and revokes all sessions/tokens for the user."""
        # This method is called *after* a generic OTP verification for RESET_PASSWORD has occurred
        # or as a combined step if the client sends all data at once.
        # The generic verify_otp_and_perform_action can be used to validate the OTP first.
        is_valid = await otp_service.verify_otp(
            email=data.email,
            action=OtpAction.RESET_PASSWORD.value,
            submitted_code=data.otp.get_secret_value()
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
        refresh_token_days = 30  # Should ideally get from config
        await redis_manager.client.set(key, int(datetime.now(UTC).timestamp()),
                                      ex=timedelta(days=refresh_token_days + 1))
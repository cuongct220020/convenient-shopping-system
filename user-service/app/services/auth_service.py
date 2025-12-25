# user-service/app/services/auth_service.py
from typing import Tuple, cast
from uuid import UUID

from pydantic import EmailStr, ValidationError, TypeAdapter
from sqlalchemy import func

from app.enums import OtpAction
from app.repositories.user_repository import UserRepository
from app.utils.password_utils import verify_password, hash_password
from app.utils.jwt_utils import JWTHandler, TokenData
from app.services.otp_service import otp_service
from app.services.redis_service import RedisService, redis_service
from app.services.kafka_service import kafka_service
from app.models.user import User
from app.schemas import (
    UserCreateSchema,
    LoginRequestSchema,
    RegisterRequestSchema,
    TokenResponseSchema,
    OTPVerifyRequestSchema,
    OTPRequestSchema,
    ResetPasswordRequestSchema
)

from shopping_shared.exceptions import Unauthorized, Forbidden, Conflict, NotFound, CacheError
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Auth Service")

class AuthService:

    @classmethod
    async def register_account(
        cls,
        reg_data: RegisterRequestSchema,
        user_repo: UserRepository
    ) -> User:
        """Handles the first step of registration: creating an inactive user and sending a verification OTP."""
        existing_user = await user_repo.get_by_username(reg_data.username)
        if existing_user and existing_user.is_active:
            raise Conflict("An account with this email already exists.")

        user = existing_user
        if not user:
            hashed_password = hash_password(reg_data.password.get_secret_value())
            # Use the new UserCreateSchema
            user_create_data = UserCreateSchema(
                username=reg_data.username,
                email=reg_data.email,
                password_hash=hashed_password,
                first_name=reg_data.first_name,
                last_name=reg_data.last_name,
                is_active=False
            )
            user = await user_repo.create(user_create_data)

        # Proceed to send OTP for the new or existing inactive user
        otp_request_data = OTPRequestSchema(email=reg_data.email, action=OtpAction.REGISTER)
        await cls.request_otp(otp_request_data, user_repo)
        
        return user


    @classmethod
    async def login_account(
        cls,
        login_data: LoginRequestSchema,
        user_repo: UserRepository
    ) -> Tuple[TokenResponseSchema, str]:
        """
        Handles user login, creates JWTs, and saves the refresh token JTI
        to enforce a single session.
        """
        user_identifier = login_data.identifier

        try:
            # Check if identifier looks like an email
            TypeAdapter(EmailStr).validate_python(user_identifier)
            is_email = True
        except (ValidationError, ValueError):
            is_email = False

        if is_email:
            user = await user_repo.get_by_email(user_identifier)
        else:
            user = await user_repo.get_by_username(user_identifier)

        if not user or not await verify_password(login_data.password, str(user.password_hash)):
            raise Unauthorized("Invalid username or password")

        if not user.is_active:
            raise Forbidden("Account is not active. Please verify your email.")

        # Generate new tokens
        jwt_handler = JWTHandler.get_instance()
        token_data = jwt_handler.create_tokens(
            user_id=str(user.id),
            user_role=str(user.system_role.value) if hasattr(user.system_role, "value") else str(user.system_role),
            email=str(user.email)
        )

        access_token = TokenResponseSchema(
            access_token=token_data.access_token,
            token_type="Bearer",
            expires_in_minutes=token_data.at_expires_in_minutes,
            is_active=bool(user.is_active)
        )

        refresh_token_str = token_data.refresh_token

        # Cập nhật refresh token JTI cho user để thực hiện single session
        try:
            await RedisService.add_session_to_allowlist(
                user_id=str(user.id),
                new_refresh_jti=str(token_data.refresh_jti),
                ttl_seconds=int(token_data.rt_ttl_seconds)
            )
        except CacheError:
            raise CacheError("Could not get a new refresh token.")

        await user_repo.update_field(user.id, "last_login", func.now())

        return access_token, refresh_token_str

    @classmethod
    async def logout_account(
        cls,
        user_id: str,
        access_token_jti: str,
        remaining_ttl_seconds: int
    ) -> None:
        """Logs out a user by removing their session and blocking the access token."""

        try:
            # 1. Xoá session khỏi allowlist để vô hiệu hoá refresh token
            await RedisService.remove_session_from_allowlist(user_id=user_id)
        except Exception as e:
            # Log the error but continue with the next step to ensure best-effort logout
            logger.error(f"Error removing session from allowlist for user {user_id}: {str(e)}")
            # Don't raise the exception to allow the logout to continue

        try:
            # 2. Thêm access token vào blocklist nếu nó vẫn còn hạn
            if remaining_ttl_seconds > 0:
                await RedisService.add_token_to_blocklist(
                    access_token_jti=access_token_jti,
                    remaining_ttl_seconds=remaining_ttl_seconds
                )
        except Exception as e:
            # Log the error but continue
            logger.error(f"Error adding token to blocklist for jti {access_token_jti}: {str(e)}")
            # Don't raise the exception to allow the logout to complete


    @classmethod
    async def refresh_tokens(
            cls,
            old_refresh_token: str,
            user_repo: UserRepository,
    ) -> tuple[TokenData, bool]:  # Returns (token_data, is_active)
        """
        Xử lý token refresh với rotation, sử dụng Redis Allowlist.
        Endpoint này phải tự xác thực không tin tưởng Kong Gateway.
        """

        # Giải mã Stateless
        try:
            # Bạn cần một hàm trong jwt_handler chỉ giải mã,
            # không kiểm tra stateful (blocklist/allowlist)
            jwt_handler = JWTHandler.get_instance()

            payload = jwt_handler.decode_token_stateless(
                token=old_refresh_token,
                expected_token_type="refresh"
            )
        except Exception as e:
            # (View nên bắt lỗi này và xóa cookie)
            raise Unauthorized("Invalid or expired refresh token") from e

        user_id = payload.get("sub")
        old_jti = payload.get("jti")

        if not user_id or not old_jti:
            raise Unauthorized("Invalid token payload.")

        is_valid_in_allowlist = await RedisService.validate_jti_in_allowlist(user_id, old_jti)

        if not is_valid_in_allowlist:
            # RỦI RO BẢO MẬT:
            # Token này không có trong Allowlist.
            # Có thể user đã logout, HOẶC đây là token cũ bị trộm.
            # Hành động an toàn: Thu hồi tất cả phiên của user này.

            await RedisService.remove_session_from_allowlist(user_id)
            await RedisService.revoke_all_tokens_for_user(user_id)
            raise Forbidden("Session invalidated. Please log in again.")

        # Lấy dữ liệu mới
        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise Unauthorized("User account is inactive or not found.")

        # Tạo token mới (rotation)
        token_data = jwt_handler.create_tokens(
            user_id=str(user.id),
            user_role=str(user.system_role.value) if hasattr(user.system_role, "value") else str(user.system_role)
        )
        
        # Update session
        await RedisService.add_session_to_allowlist(
            user_id=str(user.id),
            new_refresh_jti=token_data.refresh_jti,
            ttl_seconds=token_data.rt_ttl_seconds
        )

        return token_data, bool(user.is_active)


    @classmethod
    async def request_otp(
        cls,
        otp_data: OTPRequestSchema,
        user_repo: UserRepository
    ):
        """Handles the business logic for requesting an OTP using Redis."""
        if otp_data.action == OtpAction.RESET_PASSWORD or otp_data.action == OtpAction.CHANGE_EMAIL:
            # Using get_by_email since get_user_by_email is not defined in provided repo code, assuming get_by_email
            user = await user_repo.get_by_email(str(otp_data.email))
            if not user:
                raise NotFound("No account found with this email address.")
        elif otp_data.action == OtpAction.REGISTER:
            # For registration, user might not exist yet or be inactive.
            # The OTP is sent regardless, but the user creation happens in register_user.
            pass

        otp_code = await otp_service.generate_and_store_otp(str(otp_data.email), str(otp_data.action))

        await kafka_service.publish_message(
            email=str(otp_data.email),
            otp_code=str(otp_code),
            action=str(otp_data.action)
        )

    @classmethod
    async def verify_submitted_otp(
        cls,
        data: OTPVerifyRequestSchema,
        user_repo: UserRepository
    ) -> bool:
        """
        Verifies an OTP and performs the corresponding action based on the OtpAction.
        Returns True if OTP is valid and action is performed, False otherwise.
        """

        is_valid = await otp_service.verify_otp(
            email=data.email,
            action=data.action,
            submitted_code=data.otp_code # schema uses otp_code, not otp
        )

        if not is_valid:
            raise Unauthorized("Invalid or expired OTP code.")

        # Corrected: use get_by_email for email lookup
        user = await user_repo.get_by_email(str(data.email))
        if not user and data.action != OtpAction.REGISTER: # For register, user might exist but be inactive.
             # Actually logic: if register, user MUST exist (created in step 1).
             # If user not found, it's weird.
             pass
        
        if not user:
             # In registration flow 1 -> register (creates user) -> request otp. 
             # So user should exist.
             raise NotFound("User account not found.")

        match data.action:
            case OtpAction.REGISTER.value:
                if not user.is_active:
                    await user_repo.activate_user(cast(UUID, user.id))
                return True
            case OtpAction.RESET_PASSWORD.value:
                # For reset password, successful OTP verification means the user is authorized to reset.
                # The actual password reset happens in reset_password_with_otp, which is called separately.
                return True
            case OtpAction.CHANGE_EMAIL.value:
                # This action would typically involve updating the user's email in the database
                # after a successful OTP verification.
                # For now, we'll just return True, assuming the calling context will handle the email change.
                # A more complete implementation would involve a temporary email field on the user model
                # or a dedicated service method for email change confirmation.
                return True
            case _:
                raise ValueError(f"Unsupported OTP action: {data.action}")



    @classmethod
    async def reset_password(
        cls,
        reset_pw_data: ResetPasswordRequestSchema,
        user_repo: UserRepository
    ):
        """
        Reset user password after validating OTP.
        This method handles OTP verification and password update atomically.
        """
        # Verify the OTP
        is_valid = await otp_service.verify_otp(
            email=reset_pw_data.email,
            action=OtpAction.RESET_PASSWORD.value,  # Sử dụng giá trị enum trực tiếp
            submitted_code=reset_pw_data.otp_code
        )

        if not is_valid:
            raise Unauthorized("Invalid or expired OTP code.")

        # Get user by email
        user = await user_repo.get_by_email(str(reset_pw_data.email))
        if not user or not user.is_active:
            raise NotFound("User account not found.")

        # Hash the new password
        hashed_new_password = hash_password(reset_pw_data.new_password.get_secret_value())

        # Update the user's password
        await user_repo.update_password(
            cast(UUID, user.id),
            str(hashed_new_password)
        )

        # Delete the OTP from Redis after successful verification
        await otp_service.delete_otp(reset_pw_data.email, OtpAction.RESET_PASSWORD.value)

        # Optionally revoke all existing tokens for security
        await redis_service.remove_session_from_allowlist(str(user.id))
        await redis_service.revoke_all_tokens_for_user(str(user.id))

        return True
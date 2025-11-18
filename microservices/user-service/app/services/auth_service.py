# microservices/user-service/app/services/auth_service.py
from typing import Tuple
from pydantic import EmailStr, ValidationError
from sqlalchemy import func

from shopping_shared.exceptions import Unauthorized, Forbidden, Conflict, NotFound, CacheError

from app.constants import OtpAction
from app.repositories.user_repository import UserRepository
from app.utils.password_utils import verify_password, hash_password
from app.utils.jwt_utils import jwt_handler, TokenData
from app.services.otp_service import otp_service
from app.services.redis_service import RedisService, redis_service
from app.services.kafka_service import kafka_service

from app.schemas import (
    UserCreateSchema,
    LoginRequestSchema,
    RegisterRequestSchema,
    AccessTokenSchema,
    OTPVerifyRequestSchema,
    OTPRequestSchema,
    ResetPasswordRequestSchema
)


class AuthService:

    @classmethod
    async def register_account(
        cls,
        reg_data: RegisterRequestSchema,
        user_repo: UserRepository
    ):
        """Handles the first step of registration: creating an inactive user and sending a verification OTP."""
        existing_user = await user_repo.get_by_username(reg_data.username)
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
        otp_request_data = OTPRequestSchema(email=reg_data.email, action=OtpAction.REGISTER)
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

        try:
            EmailStr(user_identifier)
            is_email = True
        except ValidationError:
            is_email = False

        if is_email:
            user = await user_repo.get_by_email(user_identifier)
        else:
            user = await user_repo.get_by_username(user_identifier)

        if not user or not verify_password(login_data.password.get_secret_value(), user.password_hash):
            raise Unauthorized("Invalid username or password")

        if not user.is_active:
            raise Forbidden("Account is not active. Please verify your email.")

        # Generate new tokens
        token_data = jwt_handler.create_tokens(
            user_id=str(user.id),
            user_role=user.system_role.value
        )

        access_token = AccessTokenSchema(
            access_token=token_data.access_token,
            token_type=token_data.token_type,
            expires_in_minutes=token_data.expires_in_minutes
        )

        refresh_token_str = token_data.refresh_token

        # Cập nhật refresh token JTI cho user để thực hiện single session
        try:
            await RedisService.add_session_to_allowlist(
                user_id=user.id,
                new_refresh_jti=token_data.refresh_jti,
                ttl_seconds=token_data.rt_ttl_seconds
            )
        except CacheError:
            raise CacheError("Could not get a new refresh token.")

        user.last_login = func.now()
        await user_repo.update(user)

        return access_token, refresh_token_str

    @classmethod
    async def logout_account(
            cls,
            user_id: str,
            access_token_jti: str,
            remaining_ttl_seconds: int  # ← ĐỔI TÊN: access_token_exp_timestamp → remaining_ttl_seconds
    ) -> None:
        """Logs out a user by removing their session and blocking the access token."""

        # 1. Xoá session khỏi allowlist để vô hiệu hoá refresh token
        await RedisService.remove_session_from_allowlist(user_id=user_id)

        # 2. Thêm access token vào blocklist nếu nó vẫn còn hạn
        if remaining_ttl_seconds > 0:
            await RedisService.add_token_to_blocklist(
                access_token_jti=access_token_jti,
                remaining_ttl_seconds=remaining_ttl_seconds
            )


    @classmethod
    async def refresh_tokens(
            cls,
            old_refresh_token: str,
            user_repo: UserRepository,
    ) -> TokenData:
        """
        Xử lý token refresh với rotation, sử dụng Redis Allowlist.
        Endpoint này phải tự xác thực không tin tưởng Kong Gateway.
        """

        # Giải mã Stateless
        try:
            # Bạn cần một hàm trong jwt_handler chỉ giải mã,
            # không kiểm tra stateful (blocklist/allowlist)
            payload = await jwt_handler.decode_token_stateless(
                token=old_refresh_token,
                token_type="refresh"
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
            user_role=user.system_role.value
        )

        return token_data


    @classmethod
    async def request_otp(
        cls,
        otp_data: OTPRequestSchema,
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

        if otp_data.action.value == OtpAction.REGISTER:
            await kafka_service.publish_user_registration_otp(
                email=otp_data.email,
                otp_code=otp_code
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
            action=OtpAction.RESET_PASSWORD.value,
            submitted_code=reset_pw_data.otp_code
        )

        if not is_valid:
            raise Unauthorized("Invalid or expired OTP code.")

        # Get user by email
        user = await user_repo.get_by_email(reset_pw_data.email)
        if not user or not user.is_active:
            raise NotFound("User account not found.")

        # Hash the new password
        hashed_new_password = hash_password(reset_pw_data.new_password.get_secret_value())

        # Update the user's password
        await user_repo.update_password(user.id, hashed_new_password)

        # Delete the OTP from Redis after successful verification
        await otp_service.delete_otp(reset_pw_data.email, OtpAction.RESET_PASSWORD.value)

        # Optionally revoke all existing tokens for security
        await redis_service.remove_session_from_allowlist(user.id)
        await redis_service.revoke_all_tokens_for_user(user.id)

        return True
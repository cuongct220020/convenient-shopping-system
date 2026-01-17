# user-service/app/services/auth_service.py
from typing import Tuple, cast
from uuid import UUID

from sqlalchemy import func

from app.enums import OtpAction
from app.repositories.user_repository import UserRepository
from app.utils.password_utils import verify_password, hash_password
from app.utils.jwt_utils import JWTHandler, TokenData
from app.services.otp_service import otp_service
from app.services.redis_service import RedisService, redis_service
from app.services.kafka_service import kafka_service
from app.models.user import User
from app.schemas.otp_schema import OTPVerifyRequestSchema, OTPRequestSchema
from app.schemas.auth_schema import (
    LoginRequestSchema,
    RegisterRequestSchema,
    ResetPasswordRequestSchema,
    ConfirmEmailChangeRequestSchema,
    AccessTokenResponseSchema
)

from shopping_shared.exceptions import Unauthorized, Forbidden, Conflict, NotFound, CacheError


class AuthService:

    @classmethod
    async def register_account(
        cls,
        reg_data: RegisterRequestSchema,
        user_repo: UserRepository
    ) -> User:

        conflict_users = await user_repo.get_user_for_registration_check(
            username=reg_data.username,
            email=reg_data.email,
            phone_num=reg_data.phone_num
        )

        if conflict_users["username_match"] and conflict_users["username_match"].is_active:
            raise Conflict("An account with this username already exists.")
        if conflict_users["email_match"] and conflict_users["email_match"].is_active:
            raise Conflict("An account with this email already exists.")
        if (reg_data.phone_num and
            conflict_users["phone_match"] and
            conflict_users["phone_match"].is_active):
            raise Conflict("An account with this phone number already exists.")

        user = (
            conflict_users["username_match"] or
            conflict_users["email_match"] or
            conflict_users["phone_match"]
        )

        if not user:
            hashed_password = hash_password(reg_data.password.get_secret_value())

            user_data_dict = {
                "username": reg_data.username,
                "email": reg_data.email,
                "password_hash": hashed_password,
                "first_name": reg_data.first_name,
                "last_name": reg_data.last_name,
                "phone_num": reg_data.phone_num,
                "is_active": False,
            }

            try:
                user = await user_repo.create_user_with_dict(user_data_dict)
            except Exception as e:
                # Handle database constraint violations
                from sqlalchemy.exc import IntegrityError
                if isinstance(e, IntegrityError):
                    # Check which constraint was violated
                    error_msg = str(e.orig).lower() if hasattr(e, 'orig') and e.orig else str(e).lower()
                    if 'uq_users_email' in error_msg or 'email' in error_msg:
                        raise Conflict("An account with this email already exists.")
                    elif 'uq_users_username' in error_msg or 'username' in error_msg:
                        raise Conflict("An account with this username already exists.")
                    elif 'uq_users_phone_num' in error_msg or 'phone' in error_msg:
                        raise Conflict("An account with this phone number already exists.")
                    else:
                        raise Conflict("Account creation failed due to a constraint violation.")
                else:
                    raise Conflict("Account creation failed due to a system error.")

        # Proceed to send OTP for the new or existing inactive user
        otp_request_data = OTPRequestSchema(email=reg_data.email, action=OtpAction.REGISTER)
        await cls.request_otp(otp_request_data, user_repo)

        return user


    @classmethod
    async def login_account(
        cls,
        login_data: LoginRequestSchema,
        user_repo: UserRepository
    ) -> Tuple[AccessTokenResponseSchema, str]:
        """
        Handles user login, creates JWTs, and saves the refresh token JTI
        to enforce a single session.
        """
        user_identifier = login_data.identifier

        user = await user_repo.get_by_identifier(user_identifier)

        if not user or not await verify_password(login_data.password, str(user.password_hash)):
            raise Unauthorized("Invalid username or password")

        if not user.is_active:
            raise Forbidden("Account is not active. Please verify your email.")

        # Generate new tokens
        jwt_handler = JWTHandler.get_instance()
        token_data = jwt_handler.create_tokens(
            user_id=str(user.id),
            user_role=str(user.system_role.value) if hasattr(user.system_role, "value") else str(user.system_role),
            username=str(user.username),
            email=str(user.email)
        )

        access_token = AccessTokenResponseSchema(
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
            # Don't raise the exception to allow the logout to continue

        try:
            # 2. Thêm access token vào blocklist nếu nó vẫn còn hạn
            if remaining_ttl_seconds > 0:
                await RedisService.add_token_to_blocklist(
                    access_token_jti=access_token_jti,
                    remaining_ttl_seconds=remaining_ttl_seconds
                )
        except Exception as e:
            # Don't raise the exception to allow the logout to complete
            pass

        await kafka_service.publish_user_logout_message(user_id=user_id, jti=access_token_jti)


    @classmethod
    async def refresh_tokens(
        cls,
        old_refresh_token: str,
        user_repo: UserRepository
    ) -> tuple[TokenData, bool]:  # Returns (token_data, is_active)
        """
        Xử lý token refresh với rotation, sử dụng Redis Allowlist.
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
            user_role=str(user.system_role.value) if hasattr(user.system_role, "value") else str(user.system_role),
            # Include identity fields so Kong can forward X-User-Username / X-User-Email consistently
            username=str(user.username),
            email=str(user.email),
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
    ) -> str:
        """Handles the business logic for requesting an OTP using Redis."""
        if otp_data.action == OtpAction.RESET_PASSWORD:
            # For reset password, the user must exist
            user = await user_repo.get_by_email(str(otp_data.email))
            if not user:
                raise NotFound("No account found with this email address.")
        elif otp_data.action == OtpAction.CHANGE_EMAIL:
            # For change email, the NEW email must NOT be in use
            user = await user_repo.get_by_email(str(otp_data.email))
            if user:
                raise Conflict("This email address is already in use.")
        elif otp_data.action == OtpAction.REGISTER:
            # For registration, user might not exist yet or be inactive.
            # The OTP is sent regardless, but the user creation happens in register_user.
            pass

        otp_code = await otp_service.generate_and_store_otp(str(otp_data.email), str(otp_data.action))

        await kafka_service.publish_otp_message(
            email=str(otp_data.email),
            otp_code=str(otp_code),
            action=str(otp_data.action)
        )

        return otp_code

    @classmethod
    async def activate_account_with_otp(
        cls,
        verify_data: OTPVerifyRequestSchema,
        user_repo: UserRepository
    ) -> bool:
        """
        Activates a newly registered account after verifying the OTP.
        Strictly for Action: REGISTER.
        """
        is_valid = await otp_service.verify_otp(
            email=verify_data.email,
            action=OtpAction.REGISTER.value,
            submitted_code=verify_data.otp_code
        )

        if not is_valid:
            raise Unauthorized("Invalid or expired OTP code.")

        user = await user_repo.get_by_email(str(verify_data.email))
        if not user:
             raise NotFound("User account not found.")
        
        if not user.is_active:
            await user_repo.activate_user(cast(UUID, user.id))
            
        return True

    @classmethod
    async def reset_password_with_otp(
        cls,
        reset_pw_data: ResetPasswordRequestSchema,
        user_repo: UserRepository
    ) -> bool:
        """
        Reset user password after validating OTP in an atomic operation.
        1. Verify OTP
        2. Update Password
        3. Revoke Tokens
        """
        # 1. Verify the OTP
        is_valid = await otp_service.verify_otp(
            email=reset_pw_data.email,
            action=OtpAction.RESET_PASSWORD.value,
            submitted_code=reset_pw_data.otp_code
        )

        if not is_valid:
            raise Unauthorized("Invalid or expired OTP code.")

        # 2. Get user & Check status
        user = await user_repo.get_by_email(str(reset_pw_data.email))
        if not user or not user.is_active:
            raise NotFound("User account not found.")

        # 3. Hash the new password and update
        hashed_new_password = hash_password(reset_pw_data.new_password.get_secret_value())
        await user_repo.update_password(
            cast(UUID, user.id),
            str(hashed_new_password)
        )

        # 4. Security Cleanup
        # Delete the OTP is handled by verify_otp if successful.
        # Revoke all existing sessions to enforce security.
        await redis_service.remove_session_from_allowlist(str(user.id))
        await redis_service.revoke_all_tokens_for_user(str(user.id))

        return True

    @classmethod
    async def change_email_with_otp(
        cls,
        user_id: str,
        change_data: ConfirmEmailChangeRequestSchema,
        user_repo: UserRepository
    ) -> bool:
        """
        Change user email after validating OTP sent to the NEW email.
        Atomic operation.
        """
        # 1. Verify OTP (sent to new email)
        is_valid = await otp_service.verify_otp(
            email=change_data.new_email,
            action=OtpAction.CHANGE_EMAIL.value,
            submitted_code=change_data.otp_code
        )

        if not is_valid:
            raise Unauthorized("Invalid or expired OTP code.")
        
        # 2. Check conflict (is new email already taken?)
        existing_user = await user_repo.get_by_email(str(change_data.new_email))
        if existing_user:
             raise Conflict("This email address is already in use by another account.")

        # 3. Update Email
        await user_repo.update_field(UUID(user_id), "email", change_data.new_email)
        
        # 4. Security Cleanup
        # Revoke sessions as email is a key identity field.
        await redis_service.remove_session_from_allowlist(user_id)
        
        return True

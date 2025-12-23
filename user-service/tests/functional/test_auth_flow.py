import pytest
from unittest.mock import patch
from app.models.user import User
from app.enums import UserRole


# 1. Test API Đăng ký (Register)
@pytest.mark.asyncio
async def test_register_success(test_client):
    """
    Test luồng đăng ký:
    - Input hợp lệ.
    - DB lưu user với is_active=False.
    - Kafka service được gọi để gửi OTP.
    """
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "StrongPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }

    # Mock KafkaService để không gửi message thật ra Kafka broker
    with patch("app.services.kafka_service.KafkaService.publish_user_registration_otp") as mock_kafka:
        # Giả lập hàm này chạy thành công (trả về None)
        mock_kafka.return_value = None

        # Gọi API
        request, response = await test_client.post("/api/v1/user-service/auth/register", json=payload)

        # Kiểm tra Response
        assert response.status == 201
        assert response.json["status"] == "success"

        # Kiểm tra Kafka Service đã được gọi đúng tham số chưa
        mock_kafka.assert_called_once()
        call_args = mock_kafka.call_args[1]  # Lấy kwargs
        assert call_args["email"] == "test@example.com"
        # otp_code là random nên chỉ kiểm tra nó tồn tại
        assert "otp_code" in call_args

    # 2. Test API Xác thực OTP (Verify OTP)


@pytest.mark.asyncio
async def test_verify_otp_success(test_client, db_session):
    """
    Test xác thực OTP:
    - Setup: Tạo sẵn user inactive và set OTP trong Redis (Mock Redis hoặc dùng Redis thật nếu cấu hình test cho phép).
    - Ở đây ta sẽ Mock luôn AuthService.verify_submitted_otp để đơn giản hóa việc test View.
    """
    # Setup: Tạo user trong DB trước
    user = User(
        username="verify_user",
        email="verify@example.com",
        password_hash="hashed_pass",
        first_name="Verify",
        last_name="User",
        system_role=UserRole.USER,
        is_active=False  # Chưa kích hoạt
    )
    db_session.add(user)
    await db_session.commit()

    payload = {
        "email": "verify@example.com",
        "otp": "123456",
        "action": "register"
    }

    # Mock tầng Service (Logic nghiệp vụ) để test tầng View (HTTP response)
    with patch("app.services.auth_service.AuthService.verify_submitted_otp") as mock_verify:
        mock_verify.return_value = True  # Giả lập verify thành công

        request, response = await test_client.post("/api/v1/user-service/auth/otp/verify", json=payload)

        assert response.status == 200
        assert response.json["message"] == "OTP verified successfully and action performed."


# 3. Test API Đăng nhập (Login)
@pytest.mark.asyncio
async def test_login_success(test_client, db_session):
    """
    Test đăng nhập:
    - Setup: Tạo user active, mock password hash.
    - Kiểm tra trả về Access Token và Cookie Refresh Token.
    """
    from app.utils.password_utils import hash_password

    password_raw = "Mypassword123"
    hashed = hash_password(password_raw)

    # Tạo user đã active
    user = User(
        username="login_user",
        email="login@example.com",
        password_hash=hashed,
        first_name="Login",
        last_name="User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    payload = {
        "identifier": "login@example.com",
        "password": password_raw
    }

    # Vì Login có gọi Redis để lưu session, nếu test env chưa setup Redis, bạn cần mock RedisService
    with patch("app.services.redis_service.RedisService.add_session_to_allowlist") as mock_redis:
        mock_redis.return_value = None

        request, response = await test_client.post("/api/v1/user-service/auth/login", json=payload)

        assert response.status == 200
        assert "access_token" in response.json["data"]

        # Kiểm tra Cookie (Sanic test client trả về cookies trong response)
        assert "refresh_token" in response.cookies
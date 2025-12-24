import pytest
from unittest.mock import patch
from sqlalchemy import select
from app.models.user import User

@pytest.mark.asyncio
async def test_full_registration_happy_path(test_client, db_session):
    """
    Functional Test: Kiểm tra trọn vẹn luồng đăng ký người dùng mới (Happy Path).
    1. Register -> 2. Verify OTP -> 3. Login
    """
    
    # === Bước 1: Đăng ký (Register) ===
    email_test = "functional@example.com"
    reg_payload = {
        "username": "functional_user",
        "email": email_test,
        "password": "StrongPassword123!",
        "first_name": "Func",
        "last_name": "Test"
    }

    # Mock Kafka và OTP Generation để kiểm soát dữ liệu test
    with patch("app.services.kafka_service.KafkaService.publish_user_registration_otp") as mock_kafka:
        # Giả lập sinh ra mã OTP cố định là '123456' để dễ verify
        with patch("app.services.otp_service.OTPService.generate_and_store_otp", return_value="123456") as mock_gen_otp:
            
            request, response = await test_client.post("/api/v1/user-service/auth/register", json=reg_payload)
            
            # Assert Response API
            assert response.status == 201
            assert response.json["status"] == "success"
            assert response.json["data"]["email"] == email_test
            
            # Assert Side-effects (Kafka & OTP Service)
            # Kiểm tra kỹ nội dung tin nhắn gửi đi Kafka (Contract Testing)
            mock_kafka.assert_called_once()
            call_kwargs = mock_kafka.call_args.kwargs
            
            # Nếu hàm được gọi theo kiểu positional args, ta lấy từ args
            if not call_kwargs:
                 call_args_list = mock_kafka.call_args.args
                 assert call_args_list[0] == email_test # email
                 # otp_code là biến số 2
            else:
                 # Nếu gọi theo keyword arguments
                 assert call_kwargs["email"] == email_test
                 assert "otp_code" in call_kwargs
                 assert call_kwargs["otp_code"] == "123456" # Do ta đã mock generate_otp trả về 123456

            mock_gen_otp.assert_called_once()

    # === Bước 2: Xác thực OTP (Verify) ===
    verify_payload = {
        "email": email_test,
        "otp_code": "123456", 
        "action": "register"
    }

    # Mock hàm verify_otp để trả về thành công (bỏ qua check Redis thật để đơn giản hóa Functional Test)
    # Nếu muốn test kỹ hơn Integration, cần chạy Redis container và không mock hàm này.
    with patch("app.services.otp_service.OTPService.verify_otp", return_value={"otp_hash": "dummy_hash"}) as mock_verify_otp:
        
        request, response = await test_client.post("/api/v1/user-service/auth/otp/verify", json=verify_payload)
        
        assert response.status == 200
        assert response.json["status"] == "success"
        
        # QUAN TRỌNG: Kiểm tra DB xem User đã được Active chưa
        result = await db_session.execute(select(User).where(User.email == email_test))
        user_in_db = result.scalar_one_or_none()
        
        assert user_in_db is not None
        assert user_in_db.is_active is True
        assert user_in_db.username == "functional_user"

    # === Bước 3: Đăng nhập (Login) ===
    login_payload = {
        "identifier": "functional_user",
        "password": "StrongPassword123!"
    }

    # Mock Redis Session để bỏ qua bước lưu session vào Redis thật
    with patch("app.services.redis_service.RedisService.add_session_to_allowlist", return_value=None):
        request, response = await test_client.post("/api/v1/user-service/auth/login", json=login_payload)
        
        assert response.status == 200
        assert response.json["status"] == "success"
        
        # Kiểm tra Access Token
        data = response.json["data"]
        assert "access_token" in data
        assert data["token_type"] == "Bearer"
        
        # Kiểm tra Refresh Token Cookie
        assert "refresh_token" in response.cookies
        cookie = response.cookies["refresh_token"]
        assert cookie.value is not None
        assert cookie.httponly is True

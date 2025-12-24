import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.auth_service import AuthService
from app.schemas.auth_schema import RegisterRequestSchema
from app.models.user import User
from app.enums import OtpAction, SystemRole

@pytest.mark.asyncio
async def test_register_account_success(mocker):
    """
    Unit Test: Kiểm tra logic nghiệp vụ đăng ký tài khoản (cô lập).
    Không kết nối DB, không kết nối Kafka.
    """
    # 1. Chuẩn bị dữ liệu (Arrange)
    reg_data = RegisterRequestSchema(
        username="unit_test_user",
        email="unit@example.com",
        password="StrongPassword123!",
        first_name="Unit",
        last_name="Test"
    )

    # 2. Mock dependencies (Arrange)
    mock_user_repo = MagicMock()
    # Giả lập: chưa có user nào trùng username
    mock_user_repo.get_by_username = AsyncMock(return_value=None)
    
    # Giả lập: hàm create user trả về object User hợp lệ
    expected_user = User(
        id="123-uuid",
        username=reg_data.username,
        email=reg_data.email,
        system_role=SystemRole.USER,
        is_active=False
    )
    mock_user_repo.create = AsyncMock(return_value=expected_user)

    # Mock hàm request_otp (để không gọi OTP Service và Kafka thật)
    mock_request_otp = mocker.patch("app.services.auth_service.AuthService.request_otp", new_callable=AsyncMock)

    # 3. Thực thi (Act)
    result_user = await AuthService.register_account(reg_data, mock_user_repo)

    # 4. Kiểm tra (Assert)
    # 4.1. Kết quả trả về
    assert result_user.username == "unit_test_user"
    assert result_user.email == "unit@example.com"
    assert result_user.is_active is False
    
    # 4.2. Repository được gọi đúng
    mock_user_repo.get_by_username.assert_called_once_with("unit_test_user")
    mock_user_repo.create.assert_called_once()
    
    # 4.3. Hàm gửi OTP được gọi tiếp theo
    mock_request_otp.assert_called_once()
    call_args_list = mock_request_otp.call_args.args
    actual_otp_data = call_args_list[0]
    
    assert actual_otp_data.email == "unit@example.com"
    assert actual_otp_data.action == OtpAction.REGISTER

# user-service/app/apis/auth_bp.py
from sanic import Blueprint

from app.views.auth.register_view import RegisterView
from app.views.auth.login_view import LoginView
from app.views.auth.logout_view import LogoutView
from app.views.auth.refresh_view import RefreshView
from app.views.auth.reset_password_view import ResetPasswordView
from app.views.auth.otp_view import OTPRequestView, OTPVerificationView

auth_bp = Blueprint('auth_blueprint', url_prefix='/auth')

# POST /api/v1/user-service/auth/register
auth_bp.add_route(RegisterView.as_view(), '/register')


# POST /api/v1/user-service/auth/login
auth_bp.add_route(LoginView.as_view(), '/login')


# POST /api/v1/user-service/auth/logout (Protected: Yêu cầu Access Token)
auth_bp.add_route(LogoutView.as_view(), '/logout')


# POST /api/v1/user-service/auth/refresh (Public: Yêu cầu Refresh Token)
auth_bp.add_route(RefreshView.as_view(), '/refresh-token')


# POST /api/v1/user-service/auth/reset-password (Public: Đặt lại mật khẩu khi bị quên)
auth_bp.add_route(ResetPasswordView.as_view(), '/reset-password')


# POST /api/v1/auth/otp/send (Public: Gửi yêu cầu OTP cho 'register' hoặc 'reset_password')
auth_bp.add_route(OTPRequestView.as_view(), '/otp/send')


# POST /api/v1/user-service/auth/otp/verify
auth_bp.add_route(OTPVerificationView.as_view(), '/otp/verify')
# app/apis/user_bp.py
from sanic import Blueprint

from app.views.users.change_password_view import ChangePasswordView
from app.views.users.me_core_view import MeView
from app.views.users.me_change_password_view import MeChangePasswordView
from app.views.users.me_profiles_view import MeIdentityProfileView, MeHealthProfileView
from app.views.users.me_email_view import MeEmailRequestChangeView, MeEmailConfirmChangeView

user_bp = Blueprint('user_blueprint', url_prefix='/users')

user_bp.add_route(MeView.as_view(), '/me')
user_bp.add_route(MeChangePasswordView.as_view(), '/me/change-password')
user_bp.add_route(MeIdentityProfileView.as_view(), '/me/profile/identity')
user_bp.add_route(MeHealthProfileView.as_view(), '/me/profile/health')
user_bp.add_route(MeEmailRequestChangeViewView.as_view(), '/me/email/request-change')
user_bp.add_route(MeEmailConfirmChangeView.as_view(), '/me/email/confirm-change')

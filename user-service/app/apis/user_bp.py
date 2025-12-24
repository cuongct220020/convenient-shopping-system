# user-service/app/apis/user_bp.py
from sanic import Blueprint

from app.views.users.me_change_password_view import ChangePasswordView
from app.views.users.me_core_view import MeView
from app.views.users.me_profile_view import MeIdentityProfileView, MeHealthProfileView
from app.views.users.me_email_view import MeRequestChangeEmailView, MeConfirmChangeEmailView
from app.views.users.me_tag_view import MeTagsView, MeTagsDeleteView

user_bp = Blueprint('user_blueprint', url_prefix='/users')

# Core user info
user_bp.add_route(MeView.as_view(), '/me')

# Password & email
user_bp.add_route(ChangePasswordView.as_view(), '/me/change-password')
user_bp.add_route(MeRequestChangeEmailView.as_view(), '/me/email/request-change')
user_bp.add_route(MeConfirmChangeEmailView.as_view(), '/me/email/confirm-change')

# Profiles
user_bp.add_route(MeIdentityProfileView.as_view(), '/me/profile/identity')
user_bp.add_route(MeHealthProfileView.as_view(), '/me/profile/health')

# Tags
user_bp.add_route(MeTagsView.as_view(), '/me/tags')
user_bp.add_route(MeTagsDeleteView.as_view(), '/me/tags/delete')
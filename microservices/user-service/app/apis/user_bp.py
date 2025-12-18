# # app/apis/user_bp.py
# from sanic import Blueprint
#
# from app.views.users.me_change_password_view import ChangePasswordView
# from app.views.users.me_core_view import MeView
# from app.views.users.me_profile_view import MeIdentityProfileView, MeHealthProfileView
# from app.views.users.me_email_view import MeRequestChangeEmailView, MeConfirmChangeEmailView
#
# user_bp = Blueprint('user_blueprint', url_prefix='/users')
#
# user_bp.add_route(MeView.as_view(), '/me')
# user_bp.add_route(ChangePasswordView.as_view(), '/me/change-password')
# user_bp.add_route(MeIdentityProfileView.as_view(), '/me/profile/identity')
# user_bp.add_route(MeHealthProfileView.as_view(), '/me/profile/health')
# user_bp.add_route(MeRequestChangeEmailView.as_view(), '/me/email/request-change')
# user_bp.add_route(MeConfirmChangeEmailView.as_view(), '/me/email/confirm-change')

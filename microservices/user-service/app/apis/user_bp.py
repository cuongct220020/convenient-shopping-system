# app/apis/user_profile_bp.py
from sanic import Blueprint

from app.views.users.change_password_view import ChangePasswordView
from app.views.users.me_view import MeView

user_profile_bp = Blueprint('user_blueprint', url_prefix='/users')
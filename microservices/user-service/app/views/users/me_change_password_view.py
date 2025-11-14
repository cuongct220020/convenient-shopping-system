# app/views/auth/change_password_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas.auth.change_password_schema import ChangePasswordRequest
from shared.shopping_shared.schemas import GenericResponse
from app.services.user_service import UserService


class ChangePasswordView(HTTPMethodView):
    decorators = [validate_request(ChangePasswordRequest)]


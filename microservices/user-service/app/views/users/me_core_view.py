# app/views/users/me_core_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView
from sqlalchemy.ext.asyncio import AsyncSession

from app.decorators.auth import Auth
from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas.users.user_schema import UserRead, ProfileUpdateSchema
from app.services.user_service import UserService


class MeView(HTTPMethodView):
    async def get(self, request: Request, user_id: int):
        pass

    async def patch(self, request: Request, user_id: int):
        pass







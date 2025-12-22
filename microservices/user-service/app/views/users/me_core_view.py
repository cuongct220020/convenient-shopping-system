# app/views/users/me_core_view.py
from sanic.request import Request
from sanic.views import HTTPMethodView


class MeView(HTTPMethodView):
    async def get(self, request: Request, user_id: int):
        pass

    async def patch(self, request: Request, user_id: int):
        pass







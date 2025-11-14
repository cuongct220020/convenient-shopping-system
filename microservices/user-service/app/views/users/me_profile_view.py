from urllib.request import Request

from sanic.views import HTTPMethodView

class MeIdentityProfileView(HTTPMethodView):

    async def get(self, request: Request, user_id: int):
        pass

    async def patch(self, request: Request, user_id: int):
        pass


class MeHealthProfileView(HTTPMethodView):

    async def get(self, request: Request, user_id: int):
        pass

    async def patch(self, request: Request, user_id: int):
        pass
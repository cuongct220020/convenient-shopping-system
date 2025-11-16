from sanic import Request
from sanic.views import HTTPMethodView


class GroupView(HTTPMethodView):

    async def post(self, request: Request):
        pass
    async def delete(self, request: Request):
        pass

class GroupMemberView(HTTPMethodView):
    async def post(self, request: Request):
        pass

    async def delete(self, request: Request):
        pass

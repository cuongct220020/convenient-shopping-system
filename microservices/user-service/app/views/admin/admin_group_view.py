from sanic import Request
from sanic.views import HTTPMethodView


class AdminGroupsView(HTTPMethodView):
    async def post(self, request: Request):
        pass


class AdminGroupDetailView(HTTPMethodView):
    async def get(self, requset: Request, group_id: int):
        pass

    async def patch(self, request: Request, group_id: int):
        pass

    async def delete(self, request: Request, group_id: int):
        pass

class AdminGroupMembersView(HTTPMethodView):

    async def post(self, request: Request, group_id: int):
        pass

    async def delete(self, request: Request, group_id: int):
        pass

class AdminGroupMembersManageView(HTTPMethodView):

    async def delete(self, request: Request, group_id: int, user_id: int):
        pass

    async def patch(self, request: Request, group_id: int, user_id: int):
        pass


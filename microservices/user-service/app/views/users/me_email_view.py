from urllib.request import Request

from sanic.views import HTTPMethodView

class UserView(HTTPMethodView):
    async def get(self, request: Request):
        pass



class MeRequestChangeEmailView(HTTPMethodView):

    async def post(self, request: Request, user_id: int):
        pass


class MeConfirmChangeEmailView(HTTPMethodView):

    async def post(self, request: Request, user_id: int):
        pass
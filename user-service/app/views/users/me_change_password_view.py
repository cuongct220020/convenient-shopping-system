# user-service/app/views/me_change_password_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas import ChangePasswordRequestSchema
from shopping_shared.schemas.response_schema import GenericResponse
from app.services.user_service import UserService


class ChangePasswordView(HTTPMethodView):

    @validate_request(ChangePasswordRequestSchema)
    async def post(self, request: Request):
        """Handles changing the password for the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(session=request.ctx.db_session)
        user_service = UserService(user_repo=user_repo)

        await user_service.change_password(user_id=user_id, data=validated_data)

        response = GenericResponse(
            status="success",
            message="Password changed successfully. All sessions have been logged out."
        )

        return json(response.model_dump(mode="json"), status=200)
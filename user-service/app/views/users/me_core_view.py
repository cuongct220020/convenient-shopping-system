# app/views/users/me_core_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from shopping_shared.exceptions import NotFound
from shopping_shared.schemas.response_schema import GenericResponse

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user_schema import UserInfoSchema, UserInfoUpdateSchema


class MeView(HTTPMethodView):

    @staticmethod
    async def get(request: Request):
        """Get current user info."""
        user_id = request.ctx.auth_payload["sub"]
        
        repo = UserRepository(request.ctx.db_session)
        service = UserService(repo)
        
        user = await service.get(user_id)
        
        response = GenericResponse(
            status="success",
            data=UserInfoSchema.model_validate(user)
        )
        return json(response.model_dump(exclude_none=True), status=200)

    @validate_request(UserInfoUpdateSchema)
    async def patch(self, request: Request):
        """Update current user info."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data
        
        user_repo = UserRepository(session=request.ctx.db_session)
        service = UserService(user_repo=user_repo)
        
        updated_user = await service.update(user_id, validated_data)
        
        response = GenericResponse(
            status="success",
            message="User information updated.",
            data=UserInfoSchema.model_validate(updated_user)
        )
        return json(response.model_dump(exclude_none=True), status=200)







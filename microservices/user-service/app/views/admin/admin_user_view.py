# app/views/admin/admin_user_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView


from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas import (
    UserAdminUpdateSchema,
    UserAdminViewSchema
)
from app.services.user_service import UserService
from shopping_shared.exceptions import Forbidden


class AdminUsersView(HTTPMethodView):
    async def get(self, request: Request):
        pass


    async def post(self, request: Request):
        """Creates a new user account."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo)

        new_user = await user_service.create_user_by_admin(request.ctx.validated_data)

        response = UserAdminViewResponse(
            data=UserAdminViewSchema.model_validate(new_user)
        )
        return json(response.model_dump(by_alias=True), status=201)


class AdminUserDetailView(HTTPMethodView):

    async def get(self, request: Request, user_id: int):
        """Retrieves details of a specific user."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo)

        user = await user_service.get_user_details_by_admin(user_id)

        response = UserAdminViewResponse(
            data=UserAdminViewSchema.model_validate(user)
        )
        return json(response.model_dump(by_alias=True), status=200)

    @validate_request(UserAdminUpdateSchema)
    async def patch(self, request: Request, user_id: int):
        """Updates information for a specific user."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo)

        updated_user = await user_service.update_user_by_admin(user_id, request.ctx.validated_data)

        response = UserAdminViewResponse(
            data=UserAdminViewSchema.model_validate(updated_user)
        )
        return json(response.model_dump(by_alias=True), status=200)


    async def delete(self, request: Request, user_id: int):
        """Soft deletes a specific user and revokes their sessions."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo)

        await user_service.delete_user_by_admin(user_id)

        response = SuccessResponse(
            message="User deactivated and sessions revoked successfully."
        )
        return json(response.model_dump(), status=200)
# app/views/admin/admin_user_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas import (
    UserAdminUpdateSchema,
    UserAdminViewSchema,
    RegisterRequestSchema
)
from app.services.user_service import UserService
from shopping_shared.exceptions import Forbidden, BadRequest
from shopping_shared.schemas.response_schema import GenericResponse, PaginationResponse


class AdminUsersView(HTTPMethodView):

    @staticmethod
    async def get(request: Request):
        """Lists all users with pagination for admin purposes."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

        # Parse pagination params
        try:
            page = int(request.args.get("page", 1))
            page_size = int(request.args.get("page_size", 20))
        except ValueError:
            raise BadRequest("Invalid pagination parameters.")

        repo = UserRepository(request.ctx.db_session)
        service = UserService(repo)

        # BaseService.get_all returns PaginationResult object
        paginated_result = await service.get_all(page=page, page_size=page_size)

        response = PaginationResponse(
            status="success",
            data=[UserAdminViewSchema.model_validate(u) for u in paginated_result.items],
            page=paginated_result.current_page,
            page_size=paginated_result.page_size,
            total_items=paginated_result.total_items,
            total_pages=paginated_result.total_pages
        )
        return json(response.model_dump(exclude_none=True), status=200)


    @validate_request(RegisterRequestSchema)
    async def post(self, request: Request):
        """Creates a new user account by admin."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo)

        # Convert RegisterRequestSchema to UserAdminCreateSchema format if needed,
        # or update create_user_by_admin to accept RegisterRequestSchema.
        # Assuming we can pass the validated data directly or map it.
        # Here we rely on the service to handle the creation logic.
        new_user = await user_service.create_user_by_admin(request.ctx.validated_data)

        response = GenericResponse(
            status="success",
            message="User created successfully.",
            data=UserAdminViewSchema.model_validate(new_user)
        )

        return json(response.model_dump(exclude_none=True), status=201)


class AdminUserDetailView(HTTPMethodView):

    async def get(self, request: Request, user_id: int):
        """Retrieves details of a specific user."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo)

        user = await user_service.get(user_id)

        response = GenericResponse(
            status="success",
            data=UserAdminViewSchema.model_validate(user)
        )
        return json(response.model_dump(exclude_none=True), status=200)

    @validate_request(UserAdminUpdateSchema)
    async def patch(self, request: Request, user_id: int):
        """Updates information for a specific user."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo)

        updated_user = await user_service.update_user_by_admin(user_id, request.ctx.validated_data)

        response = GenericResponse(
            status="success",
            message="User updated successfully.",
            data=UserAdminViewSchema.model_validate(updated_user)
        )
        return json(response.model_dump(exclude_none=True), status=200)


    async def delete(self, request: Request, user_id: int):
        """Soft deletes a specific user and revokes their sessions."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo)

        await user_service.delete_user_by_admin(user_id)

        response = GenericResponse(
            status="success",
            message="User deactivated and sessions revoked successfully."
        )
        return json(response.model_dump(), status=200)
# app/views/admin/admin_user_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_ext import openapi
from sanic_ext.extensions.openapi.types import Schema

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas import (
    UserAdminCreateSchema,
    UserAdminUpdateSchema,
    UserAdminViewSchema,
    UserAdminViewPaginatedResponse,
    UserAdminViewResponse,
    SuccessResponse,
)
from app.services.user_service import UserService
from shared.shopping_shared import Forbidden


class AdminUserListView(HTTPMethodView):
    # The 'protected' decorator has been removed.
    # Auth is handled by the global middleware 'request_auth'.
    # Role checks are now performed inside each method.

    @openapi.definition(
        summary="List all users (Admin only).",
        description="Retrieves a paginated list of all user accounts in the system.",
        response=Schema(UserAdminViewPaginatedResponse),
        tag="Admin"
    )
    async def get(self, request: Request):
        """Lists all users with pagination."""
        if getattr(request.ctx, 'role', None) != 'admin':
            raise Forbidden("You do not have permission to access this resource.")

        user_repo = UserRepository(request.ctx.db_session)
        user_service = UserService(user_repo)

        try:
            page = int(request.args.get("page", 1))
            page_size = int(request.args.get("page_size", 10))
        except (ValueError, TypeError):
            page = 1
            page_size = 10

        paginated_result = await user_service.list_all_users(page=page, page_size=page_size)

        # The paginated response schema is already structured, just pass the data
        return json(paginated_result.model_dump(by_alias=True), status=200)

    @openapi.definition(
        summary="Create a new user (Admin only).",
        description="Allows an admin to create a new user account with specified details.",
        body=Schema(UserAdminCreateSchema),
        response=Schema(UserAdminViewResponse),
        tag="Admin"
    )
    @validate_request(UserAdminCreateSchema)
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
    # The 'protected' decorator has been removed.
    # Auth is handled by the global middleware 'request_auth'.
    # Role checks are now performed inside each method.

    @openapi.definition(
        summary="Get user details by ID (Admin only).",
        description="Retrieves detailed information for a specific user account.",
        response=Schema(UserAdminViewResponse),
        tag="Admin"
    )
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

    @openapi.definition(
        summary="Update user information by ID (Admin only).",
        description="Allows an admin to update specific fields of a user account.",
        body=Schema(UserAdminUpdateSchema),
        response=Schema(UserAdminViewResponse),
        tag="Admin"
    )
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

    @openapi.definition(
        summary="Soft delete a user by ID (Admin only).",
        description="Deactivates a user account and revokes all their sessions.",
        response=Schema(SuccessResponse),
        tag="Admin"
    )
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
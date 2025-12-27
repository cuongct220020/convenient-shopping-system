# user-service/app/views/admin/admin_user_view.py
from uuid import UUID
from sanic.request import Request
from sanic_ext import openapi

from app.decorators import validate_request, require_system_role
from app.views.base_view import BaseAPIView
from app.enums import SystemRole
from app.repositories.user_repository import UserRepository
from app.schemas.user_admin_schema import (
    UserAdminCreateSchema,
    UserAdminUpdateSchema,
    UserAdminViewSchema
)
from app.services.admin_service import AdminUserService
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Admin User View")


class AdminUsersView(BaseAPIView):
    """
    Admin endpoints for managing users.
    All methods require ADMIN role.
    """
    decorators = [
        require_system_role(SystemRole.ADMIN),
        openapi.tag("Admin - User Management"),
        openapi.secured("bearerAuth")
    ]

    @staticmethod
    def _get_service(request: Request) -> AdminUserService:
        user_repo = UserRepository(session=request.ctx.db_session)
        return AdminUserService(user_repo)

    @openapi.summary("List all users (Admin)")
    @openapi.description("Lists all users in the system with pagination. Requires ADMIN role.")
    @openapi.response(200, UserAdminViewSchema)
    async def get(self, request: Request):
        """List all users with pagination."""
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))

        service = self._get_service(request)

        try:
            users, total = await service.get_all_users_paginated(page=page, page_size=page_size)

            # Use helper method from base class
            return self.success_response(
                data={
                    "items": [UserAdminViewSchema.model_validate(user).model_dump() for user in users],
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                },
                message="Users listed successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to list users", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to list users",
                status_code=500
            )

    @openapi.summary("Create a new user (Admin)")
    @openapi.description("Creates a new user account. Requires ADMIN role.")
    @openapi.body(UserAdminCreateSchema)
    @openapi.response(201, UserAdminViewSchema)
    @validate_request(UserAdminCreateSchema)
    async def post(self, request: Request):
        """Create a new user."""
        validated_data = request.ctx.validated_data
        service = self._get_service(request)

        try:
            user = await service.create_user(validated_data)

            # Use helper method from base class
            return self.success_response(
                data=UserAdminViewSchema.model_validate(user),
                message="User created successfully",
                status_code=201
            )
        except Exception as e:
            logger.error("Failed to create user", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to create user",
                status_code=500
            )


class AdminUserDetailView(BaseAPIView):
    """Admin endpoints for managing a specific user."""
    decorators = [
        require_system_role(SystemRole.ADMIN),
        openapi.tag("Admin - User Management"),
        openapi.secured("bearerAuth")
    ]

    @staticmethod
    def _get_service(request: Request) -> AdminUserService:
        user_repo = UserRepository(session=request.ctx.db_session)
        return AdminUserService(user_repo)

    @openapi.summary("Get user by ID (Admin)")
    @openapi.description("Retrieves a specific user by their ID. Requires ADMIN role.")
    @openapi.response(200, UserAdminViewSchema)
    async def get(self, request: Request, user_id: UUID):
        """Get a specific user by ID."""
        service = self._get_service(request)

        try:
            user = await service.get_user(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserAdminViewSchema.model_validate(user),
                message="User retrieved successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to get user", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve user",
                status_code=500
            )

    @openapi.summary("Update user by ID (Admin)")
    @openapi.description("Updates a specific user by their ID. Requires ADMIN role.")
    @openapi.body(UserAdminUpdateSchema)
    @openapi.response(200, UserAdminViewSchema)
    @validate_request(UserAdminUpdateSchema)
    async def put(self, request: Request, user_id: UUID):
        """Update a specific user by ID."""
        validated_data = request.ctx.validated_data
        service = self._get_service(request)

        try:
            user = await service.update_user(user_id, validated_data)

            # Use helper method from base class
            return self.success_response(
                data=UserAdminViewSchema.model_validate(user),
                message="User updated successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to update user", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to update user",
                status_code=500
            )

    @openapi.summary("Delete user by ID (Admin)")
    @openapi.description("Deletes a specific user by their ID. Requires ADMIN role.")
    @openapi.response(200, GenericResponse)
    async def delete(self, request: Request, user_id: UUID):
        """Delete a specific user by ID."""
        service = self._get_service(request)

        try:
            await service.delete_user(user_id)

            # Use helper method from base class
            return self.success_response(
                message="User deleted successfully",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to delete user", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to delete user",
                status_code=500
            )
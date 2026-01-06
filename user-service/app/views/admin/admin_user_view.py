# user-service/app/views/admin/admin_user_view.py
from uuid import UUID
from sanic.request import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request, require_system_role
from app.decorators.cache_response import cache_response
from app.views.base_view import BaseAPIView
from app.enums import SystemRole
from app.repositories.user_repository import UserRepository
from app.schemas.user_admin_schema import (
    UserAdminCreateSchema,
    UserAdminUpdateSchema,
    UserAdminViewSchema,
    PaginatedUserAdminViewResponseSchema
)
from app.services.admin_service import AdminUserService

from shopping_shared.exceptions import Conflict, NotFound
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body
from shopping_shared.caching.redis_keys import RedisKeys

logger = get_logger("Admin User View")


class BaseAdminUserView(BaseAPIView):
    @staticmethod
    def _get_service(request: Request) -> AdminUserService:
        user_repo = UserRepository(session=request.ctx.db_session)
        return AdminUserService(user_repo)


class AdminUsersView(BaseAdminUserView):
    """
    Admin endpoints for managing users. All methods require ADMIN role.
    """

    @openapi.definition(
        summary="List all users (Admin)",
        description="Lists all users in the system with pagination. Available only to ADMIN users. Returns comprehensive user details including status, roles, and creation date.",
        tag=["Admin Users Management"],
        secured={"bearerAuth": []},
        parameter=[
            {
                "name": "page",
                "in": "query",
                "required": False,
                "description": "Page number for pagination (default: 1)",
                "schema": {"type": "integer", "default": 1, "minimum": 1}
            },
            {
                "name": "page_size",
                "in": "query",
                "required": False,
                "description": "Number of items per page (default: 10, max: 100)",
                "schema": {"type": "integer", "default": 10, "minimum": 1, "maximum": 100}
            }
        ],
        response=[
            Response(
                content=get_openapi_body(PaginatedUserAdminViewResponseSchema),
                status=200,
                description="List all users in the system with pagination by admin.",
            )
        ]
    )
    @require_system_role(SystemRole.ADMIN)
    @cache_response(key_pattern=RedisKeys.ADMIN_USERS_LIST, ttl=60, page="1", page_size="10")
    async def get(self, request: Request):
        """
        List all users with pagination.
        GET api/v1/user-service/admin/users
        """
        try:
            # Validate and convert query parameters with proper error handling
            page_param = request.args.get("page", "1")
            page_size_param = request.args.get("page_size", "10")

            # Validate that parameters are numeric
            try:
                page = int(page_param)
                page_size = int(page_size_param)
            except ValueError:
                return self.error_response(
                    message="Page and page_size must be valid integers",
                    status_code=400
                )

            # Validate positive values
            if page < 1:
                return self.error_response(
                    message="Page must be a positive integer",
                    status_code=400
                )

            if page_size < 1:
                return self.error_response(
                    message="Page size must be a positive integer",
                    status_code=400
                )

            # Validate maximum page size
            if page_size > 100:
                return self.error_response(
                    message="Page size cannot exceed 100",
                    status_code=400
                )

            service = self._get_service(request)
            users, total = await service.get_all_users_paginated(page=page, page_size=page_size)

            paginated_response = PaginatedUserAdminViewResponseSchema(
                data=[UserAdminViewSchema.model_validate(user) for user in users],
                page=page,
                page_size=page_size,
                total_items=total,
                total_pages=(total + page_size - 1) // page_size
            )

            # Use helper method from base class
            return self.success_response(
                data=paginated_response,
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


    @openapi.definition(
        summary="Create a new user account (Admin)",
        description="Creates a new user account by an administrator. This endpoint allows admins to create user accounts with specified details without requiring the user to register themselves.",
        body=get_openapi_body(UserAdminCreateSchema),
        tag=["Admin Users Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserAdminViewSchema),
                status=201,
                description="User account created successfully by admin.",
            )
        ]
    )
    @validate_request(UserAdminCreateSchema)
    @require_system_role(SystemRole.ADMIN)
    async def post(self, request: Request):
        """
        Create a new user.
        POST api/v1/user-service/admin/users
        """
        validated_data = request.ctx.validated_data
        service = self._get_service(request)

        try:
            user = await service.create_user_by_admin(validated_data)

            # Use helper method from base class
            return self.success_response(
                data=UserAdminViewSchema.model_validate(user),
                message="User created successfully",
                status_code=201
            )
        except Conflict as e:
            return self.error_response(message=str(e), status_code=409)
        except Exception as e:
            logger.error("Failed to create user", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to create user",
                status_code=500
            )



class AdminUserDetailView(BaseAdminUserView):
    """Admin endpoints for managing a specific user."""


    @openapi.definition(
        summary="Retrieve user details by ID (Admin)",
        description="Retrieves comprehensive details for a specific user by their unique identifier. This endpoint is accessible only to administrators for user management purposes.",
        tag=["Admin Users Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserAdminViewSchema),
                status=200,
                description="User details retrieved successfully.",
            )
        ]
    )
    @require_system_role(SystemRole.ADMIN)
    @cache_response(key_pattern=RedisKeys.ADMIN_USER_DETAIL, ttl=300)
    async def get(self, request: Request, user_id: UUID):
        """
        Get a specific user by ID.
        GET api/v1/user-service/admin/users/{user_id}
        """
        service = self._get_service(request)

        try:
            user = await service.get_user_by_admin(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserAdminViewSchema.model_validate(user),
                message="User retrieved successfully",
                status_code=200
            )
        except NotFound as e:
            return self.error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error("Failed to get user", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to retrieve user",
                status_code=500
            )



    @openapi.definition(
        summary="Update user details by ID (Admin)",
        description="Updates the details of a specific user by their unique identifier. This endpoint allows administrators to modify user information such as status, roles, and personal details.",
        body=get_openapi_body(UserAdminUpdateSchema),
        tag=["Admin Users Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserAdminViewSchema),
                status=200,
                description="User details updated successfully.",
            )
        ]
    )
    @validate_request(UserAdminUpdateSchema)
    @require_system_role(SystemRole.ADMIN)
    async def put(self, request: Request, user_id: UUID):
        """
        Update a specific user by ID.
        PUT api/v1/user-service/admin/users/{user_id}
        """
        validated_data = request.ctx.validated_data
        service = self._get_service(request)

        try:
            user = await service.update_user_by_admin(user_id, validated_data)

            # Use helper method from base class
            return self.success_response(
                data=UserAdminViewSchema.model_validate(user),
                message="User updated successfully",
                status_code=200
            )
        except NotFound as e:
            return self.error_response(message=str(e), status_code=404)
        except Conflict as e:
            return self.error_response(message=str(e), status_code=409)
        except Exception as e:
            logger.error("Failed to update user", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to update user",
                status_code=500
            )


    @openapi.definition(
        summary="Delete user account by ID (Admin)",
        description="Permanently deletes a specific user account by their unique identifier. This action is irreversible and should be used with caution as it removes all user data from the system.",
        tag=["Admin Users Management"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(GenericResponse),
                status=200,
                description="User account deleted successfully.",
            )
        ]
    )
    @require_system_role(SystemRole.ADMIN)
    async def delete(self, request: Request, user_id: UUID):
        """
        Delete a specific user by ID.
        DELETE api/v1/user-service/admin/users/{user_id}
        """
        service = self._get_service(request)

        try:
            await service.delete_user_by_admin(user_id)

            # Use helper method from base class
            return self.success_response(
                message="User deleted successfully",
                status_code=200
            )
        except NotFound as e:
            return self.error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error("Failed to delete user", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to delete user",
                status_code=500
            )
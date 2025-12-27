# user-service/app/decorators/require_system_role.py
"""
Decorator để kiểm tra system-level role (ADMIN, USER).
Được áp dụng SAU khi auth_middleware đã inject request.ctx.auth_payload.
"""

from functools import wraps
from typing import Callable

from app.enums import SystemRole
from shopping_shared.exceptions import Forbidden
from sanic_ext import openapi
from shopping_shared.schemas.response_schema import GenericResponse


def require_system_role(*allowed_roles: SystemRole, auto_document: bool = True) -> Callable:
    """
    Check System Role of the user. Must be applied AFTER auth_middleware.

    Usage:
        @require_system_role(SystemRole.ADMIN)
        async def admin_only(request):
            ...

        @require_system_role(SystemRole.ADMIN, SystemRole.USER)
        async def any_authenticated_user(request):
            ...

    Args:
        *allowed_roles: One or more SystemRole values allowed
        auto_document: Whether to automatically document OpenAPI responses (default: True)
    """
    def decorator(func: Callable) -> Callable:
        if auto_document:
            # Automatically document the possible authentication/authorization error responses
            func = openapi.response(401, GenericResponse, "Unauthorized - Missing or invalid authentication")(func)
            func = openapi.response(403, GenericResponse, "Forbidden - Insufficient permissions")(func)

        @wraps(func)
        async def wrapper(self_or_request, *args, **kwargs):
            # Handle cả HTTPMethodView (self, request) và function view (request)
            if hasattr(self_or_request, 'ctx'):
                request = self_or_request
            else:
                # HTTPMethodView: self_or_request là self, args[0] là request
                request = args[0]
                args = args[1:]

            # Lấy role từ auth_payload (đã được inject bởi auth_middleware)
            auth_payload = getattr(request.ctx, 'auth_payload', None)
            if not auth_payload:
                raise Forbidden("Authentication required.")

            user_role_str = auth_payload.get("role")
            if not user_role_str:
                raise Forbidden("User role not found in token.")

            try:
                user_role = SystemRole(user_role_str)
            except ValueError:
                raise Forbidden(f"Invalid role: {user_role_str}")

            if user_role not in allowed_roles:
                allowed_str = ", ".join([r.value for r in allowed_roles])
                raise Forbidden(f"Access denied. Required roles: {allowed_str}")

            # Call original function
            if hasattr(self_or_request, 'ctx'):
                return await func(request, *args, **kwargs)
            else:
                return await func(self_or_request, request, *args, **kwargs)

        return wrapper
    return decorator
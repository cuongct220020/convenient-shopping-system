# user-service/app/decorators/require_group_role.py
"""
Decorator để kiểm tra role của user trong một Family Group cụ thể.
Được áp dụng SAU khi auth_middleware đã inject request.ctx.auth_payload.

Role Hierarchy:
    HEAD_CHEF > MEMBER

    HEAD_CHEF: Chủ nhóm, có toàn quyền quản lý
    MEMBER: Thành viên, chỉ có quyền xem và rời nhóm
"""
from functools import wraps
from typing import Callable
from uuid import UUID

from app.enums import GroupRole
from app.repositories.family_group_repository import GroupMembershipRepository
from shopping_shared.exceptions import Forbidden, NotFound
from sanic_ext import openapi
from shopping_shared.sanic.schemas import DocGenericResponse


def require_group_role(*allowed_roles: GroupRole, group_id_param: str = "group_id", auto_document: bool = True) -> Callable:
    """
    Check Group Role of the user within a specific family group. Must be applied AFTER auth_middleware.

    Usage:
        @require_group_role(GroupRole.HEAD_CHEF)
        async def head_chef_only(request, group_id: UUID):
            # Chỉ HEAD_CHEF mới vào được
            ...

        @require_group_role(GroupRole.HEAD_CHEF, GroupRole.MEMBER)
        async def all_members(request, group_id: UUID):
            # Tất cả thành viên đều vào được
            ...

    Args:
        *allowed_roles: One or more GroupRole values allowed
        group_id_param: Name of the parameter containing the group ID (default: "group_id")
        auto_document: Whether to automatically document OpenAPI responses (default: True)
    """
    def decorator(func: Callable) -> Callable:
        if auto_document:
            # Automatically document the possible authentication/authorization error responses
            func = openapi.response(401, DocGenericResponse, "Unauthorized - Missing or invalid authentication")(func)
            func = openapi.response(403, DocGenericResponse, "Forbidden - Insufficient permissions")(func)
            func = openapi.response(404, DocGenericResponse, "Not Found - Group not found or user not member")(func)

        @wraps(func)
        async def wrapper(self_or_request, *args, **kwargs):
            # Handle cả HTTPMethodView (self, request) và function view (request)
            if hasattr(self_or_request, 'ctx'):
                request = self_or_request
            else:
                # HTTPMethodView: self_or_request là self, args[0] là request
                request = args[0]
                args = args[1:]

            # Lấy user_id từ auth_payload
            auth_payload = getattr(request.ctx, 'auth_payload', None)
            if not auth_payload:
                raise Forbidden("Authentication required.")

            user_id = auth_payload.get("sub")
            if not user_id:
                raise Forbidden("User ID not found in token.")

            # Convert user_id to UUID if string
            if isinstance(user_id, str):
                try:
                    user_id = UUID(user_id)
                except ValueError:
                    raise Forbidden("Invalid user ID format.")

            # Lấy group_id từ kwargs
            group_id = kwargs.get(group_id_param)
            if not group_id:
                raise Forbidden(f"Group ID parameter '{group_id_param}' not found.")

            # Convert group_id to UUID if string
            if isinstance(group_id, str):
                try:
                    group_id = UUID(group_id)
                except ValueError:
                    raise Forbidden("Invalid group ID format.")

            # Query database để check membership và role
            db_session = getattr(request.ctx, 'db_session', None)
            if not db_session:
                raise Forbidden("Database session not available.")

            membership_repo = GroupMembershipRepository(db_session)
            membership = await membership_repo.get_membership(user_id, group_id)

            if not membership:
                raise NotFound("You are not a member of this group.")

            # Check role hierarchy: OWNER > HEAD_CHEF > MEMBER
            if membership.role not in allowed_roles:
                allowed_str = ", ".join([r.value for r in allowed_roles])
                raise Forbidden(f"Access denied. Required group roles: {allowed_str}")

            # Inject membership vào request context để view có thể sử dụng
            request.ctx.group_membership = membership

            # Call original function
            if hasattr(self_or_request, 'ctx'):
                return await func(request, *args, **kwargs)
            else:
                return await func(self_or_request, request, *args, **kwargs)

        return wrapper
    return decorator

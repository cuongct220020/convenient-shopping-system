# app/decorators/require_group_role.py
from functools import wraps

from app.repositories.family_group_repository import FamilyGroupRepository
from shopping_shared.exceptions import Forbidden


def require_group_role(group_id_param: str, *allowed_roles: GroupRole):
    """Check quyền trong nhóm gia đình"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            group_id = kwargs[group_id_param]
            user_id = request.ctx.user["user_id"]

            # Query database để check role
            member = await FamilyGroupRepository.get(
                group_id=group_id,
                user_id=user_id
            )

            if member.role not in allowed_roles:
                raise Forbidden(
                    f"Required role: {', '.join(allowed_roles)}"
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

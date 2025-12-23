# user-service/app/decorators/require_role.py

from functools import wraps
from shopping_shared.exceptions import Forbidden


def require_role(*allowed_roles: UserRole):
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Kong đã forward role vào header
            user_role = request.headers.get("X-User-Role")

            if UserRole(user_role) not in allowed_roles:
                raise Forbidden(
                    f"Required roles: {', '.join([r.value for r in allowed_roles])}"
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
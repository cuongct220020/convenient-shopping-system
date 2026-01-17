from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
from shopping_shared.middleware.fastapi_auth import get_current_user
from shopping_shared.exceptions import Unauthorized


class AdminMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ("GET", "OPTIONS"):
            return await call_next(request)
        
        # Skip authentication for recipe flattened endpoint
        if request.url.path == "/v2/recipes/flattened":
            return await call_next(request)
        
        try:
            auth_payload = await get_current_user(request)
            user_role = auth_payload.get("role")

            if user_role != "admin":
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "Admin role required for this operation",
                        "required_role": "admin",
                        "current_role": user_role
                    }
                )

            return await call_next(request)
            
        except Unauthorized as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)}
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error during authentication"}
            )


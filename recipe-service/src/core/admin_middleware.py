from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
from shopping_shared.middleware.auth_utils import extract_kong_headers
from shopping_shared.exceptions import Unauthorized
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("AdminMiddleware")


class AdminMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ("GET", "OPTIONS"):
            return await call_next(request)
        
        try:
            auth_payload = extract_kong_headers(dict(request.headers))
            user_role = auth_payload.get("role")

            if user_role != "admin":
                logger.warning(
                    f"Non-admin user attempted {request.method} {request.url.path}. "
                    f"User role: {user_role}, User ID: {auth_payload.get('sub')}"
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "Admin role required for this operation",
                        "required_role": "admin",
                        "current_role": user_role
                    }
                )

            logger.debug(
                f"Admin access granted for {request.method} {request.url.path}. "
                f"User ID: {auth_payload.get('sub')}"
            )
            return await call_next(request)
            
        except Unauthorized as e:
            logger.warning(f"Unauthorized request: {request.method} {request.url.path} - {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)}
            )
        except Exception as e:
            logger.exception(f"Error in admin middleware: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error during authentication"}
            )


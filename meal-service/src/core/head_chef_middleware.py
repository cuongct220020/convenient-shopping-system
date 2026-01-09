import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
import httpx
from shopping_shared.middleware.auth_utils import extract_kong_headers
from shopping_shared.exceptions import Unauthorized
from shopping_shared.utils.logger_utils import get_logger
from core.config import settings

logger = get_logger("HeadChefMiddleware")


class HeadChefMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "POST":
            return await call_next(request)

        path = request.url.path

        is_command = path.endswith("/v1/meals/command")
        is_transition = "/v1/meals/" in path and path.split("/")[-1] in ["cancel", "reopen", "finish"]
        
        if not (is_command or is_transition):
            return await call_next(request)

        try:
            auth_payload = extract_kong_headers(dict(request.headers))
            user_id_str = auth_payload.get("sub")
            
            if not user_id_str:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Missing user identity"}
                )

            query_params = dict(request.query_params)
            group_id_str = query_params.get("group_id")
            
            if not group_id_str:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "group_id query parameter is required"}
                )

            try:
                user_id = uuid.UUID(user_id_str)
                group_id = uuid.UUID(group_id_str)
            except (ValueError, TypeError):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid UUID format for user_id or group_id"}
                )

            is_head_chef = await self._check_head_chef(user_id, group_id)
            if not is_head_chef:
                logger.warning(
                    f"Non-head-chef user attempted meal operation. "
                    f"Path: {path}, User ID: {user_id}, Group ID: {group_id}"
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "Head chef role required for meal operations",
                        "required_role": "head_chef"
                    }
                )
            
            logger.debug(
                f"Head chef access granted. "
                f"Path: {path}, User ID: {user_id}, Group ID: {group_id}"
            )
            return await call_next(request)
            
        except Unauthorized as e:
            logger.warning(f"Unauthorized request: {path} - {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)}
            )
        except Exception as e:
            logger.exception(f"Error in head chef middleware: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error during authorization check"}
            )
    
    async def _check_head_chef(self, user_id: uuid.UUID, group_id: uuid.UUID) -> bool:
        # Construct URL with the correct prefix for user-service
        # Assuming USER_SERVICE_URL is http://user-service:8000
        url = f"{settings.USER_SERVICE_URL}/api/v1/user-service/groups/internal/{group_id}/members/{user_id}/access-check"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    json={"check_head_chef": True},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        result_data = data.get("data", {})
                        return result_data.get("authorized", False) and result_data.get("is_head_chef", False)
                    return False
                elif response.status_code == 403:
                    # User is member but not head chef
                    return False
                elif response.status_code == 404:
                    # User is not a member or group not found
                    return False
                else:
                    logger.error(
                        f"Unexpected response from user-service: {response.status_code} - {response.text}"
                    )
                    # Fail closed for unexpected errors
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout when calling user-service to check head chef: {url}")
            # Fail closed on timeout
            return False
        except httpx.RequestError as e:
            logger.error(f"Error calling user-service to check head chef: {e}")
            # Fail closed on request errors
            return False
        except Exception as e:
            logger.exception(f"Unexpected error checking head chef: {e}")
            # Fail closed on unexpected errors
            return False


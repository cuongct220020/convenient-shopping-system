# notification-service/app/apis/ws_bp.py

"""
WebSocket Endpoints for Convenient Shopping System

1. /notifications/users/<user_id> - Personal Notifications
   This endpoint is for individual user-specific notifications. These would be personalized alerts based on the user's own activities and preferences:
   - Expiration reminders: Personal alerts about food items in their refrigerator approaching expiration.
   - Shopping list updates: Personal reminders about items on their individual shopping lists.
   - Recipe suggestions: Personalized recipe recommendations based on their preferences and available ingredients
   - Account-specific notifications: Login alerts, security notifications, account updates
   - Personal meal plan updates: Notifications about their personal meal plans and cooking schedules
   - Purchase history notifications: Receipt confirmations, order status updates
   - Personalized food waste reports: Individual statistics about their food consumption and waste

Each endpoint serves a different scope of communication within the Convenient Shopping System, allowing for efficient and targeted notification delivery
based on the relevance to individual users or family groups.
"""
from sanic import Blueprint
from sanic import Websocket
from app.websocket.websocket_manager import websocket_manager
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.middleware.auth_utils import extract_kong_headers, validate_token_state
from shopping_shared.exceptions import Unauthorized

logger = get_logger("Websocket Blueprint")

# Tạo Blueprint cho WebSocket
ws_bp = Blueprint("websocket", url_prefix="/v1/notification-service/notifications")


@ws_bp.websocket("/users/<user_id>")
async def ws_user_notifications(request, ws: Websocket, user_id: str):

    # Mẹo: Đợi một chút để handshake hoàn tất hoàn toàn ở tầng protocol
    import asyncio
    await asyncio.sleep(0.1)
    
    try:
        # 1. Trích xuất payload (Truy cập headers trực tiếp, không qua dict())
        auth_payload = extract_kong_headers(request.headers)

        # 2. Verify token state
        redis_client = getattr(request.ctx, "redis_client", None)
        await validate_token_state(
            user_id=auth_payload["sub"],
            jti=auth_payload["jti"],
            iat=auth_payload["iat"],
            redis_client=redis_client,
            check_blocklist=True
        )

        request.ctx.auth_payload = auth_payload
        requesting_user_id = auth_payload.get("sub")

        if requesting_user_id != user_id:
            logger.warning(f"User {requesting_user_id} tried to access notifications for user {user_id}")
            await ws.close(code=1008, reason="Forbidden")
            return

        logger.info(f"User {requesting_user_id} connected to personal channel {user_id}")

    except Unauthorized as e:
        logger.warning(f"WebSocket auth denied: {e}")
        await ws.close(code=1008, reason="Unauthorized")
        return
    except Exception as e:
        logger.error(f"FATAL: Error during WS setup for {user_id}: {type(e).__name__}: {e}", exc_info=True)
        await ws.close(code=1011, reason="Internal Error")
        return

    await websocket_manager.connect_to_user(ws, user_id)

    try:
        logger.debug(f"Entering message loop for user {user_id}")
        async for message in ws:
            logger.info(f"Received from {user_id}: {message}")
        logger.debug(f"Loop ended normally for {user_id}")
    except Exception as e:
        logger.error(f"DEBUG: Loop exception for {user_id}: {e}")
    finally:
        logger.debug(f"DEBUG: Cleaning up connection for {user_id}")
        await websocket_manager.disconnect_from_user(ws, user_id)


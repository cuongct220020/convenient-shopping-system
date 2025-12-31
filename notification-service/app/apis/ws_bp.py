# notification-service/app/apis/ws_bp.py

"""
WebSocket Endpoints for Convenient Shopping System

1. /notifications/groups/<group_id> - Group Notifications
   This endpoint is for family/group-specific notifications. Since the system supports family groups sharing shopping lists and coordinating tasks,
   these notifications would include:
   - Family shopping list updates: When a family member adds/removes items from shared shopping lists
   - Task assignments: Notifications about assigned shopping duties or cooking responsibilities
   - Inventory updates: When a family member updates the refrigerator inventory
   - Meal plan changes: Updates to shared weekly meal plans
   - Group activity notifications: Reminders about group activities, shared expenses
   - Collaborative recipe sharing: When family members share new recipes or cooking experiences

2. /notifications/users/<user_id> - Personal Notifications
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
from uuid import UUID

from sanic import Blueprint
from sanic import Websocket
from app.websocket.websocket_manager import websocket_manager
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Websocket Blueprint")

# Tạo Blueprint cho WebSocket
ws_bp = Blueprint("websocket", url_prefix="/api/v1/notification-service/ws")


@ws_bp.websocket("/notifications/groups/<group_id: UUID>")
async def ws_group_notifications(request, ws: Websocket, group_id: UUID):
    """WebSocket cho thông báo nhóm - người dùng kết nối đến nhóm cụ thể"""
    user_id = request.ctx.auth_payload.get("sub") if hasattr(request.ctx, 'auth_payload') else "anonymous"

    # Có thể thêm xác thực người dùng có quyền truy cập nhóm hay không
    await websocket_manager.connect_to_group(ws, group_id)

    try:
        async for message in ws:
            # Xử lý tin nhắn từ client nếu cần
            logger.info(f"Received message from group {group_id}: {message}")
            pass
    except Exception as e:
        logger.error(f"WebSocket error for group {group_id}: {e}", exc_info=True)
    finally:
        await websocket_manager.disconnect_from_group(ws, group_id)


@ws_bp.websocket("/notifications/users/<user_id: UUID>")
async def ws_user_notifications(request, ws: Websocket, user_id: UUID):
    """WebSocket cho thông báo cá nhân - người dùng kết nối đến kênh riêng"""
    # Xác thực người dùng có quyền truy cập kênh này hay không
    requesting_user_id = request.ctx.auth_payload.get("sub") if hasattr(request.ctx, 'auth_payload') else "anonymous"

    if requesting_user_id != user_id:
        logger.warning(f"User {requesting_user_id} tried to access notifications for user {user_id}")
        await ws.close()
        return

    await websocket_manager.connect_to_user(ws, user_id)

    try:
        async for message in ws:
            # Xử lý tin nhắn từ client nếu cần
            logger.info(f"Received message for user {user_id}: {message}")
            pass
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}", exc_info=True)
    finally:
        await websocket_manager.disconnect_from_user(ws, user_id)


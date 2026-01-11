# notification-service/app/consumers/handlers/daily_meal_handler.py
from uuid import UUID

from app.consumers.handlers.base_handler import BaseMessageHandler
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification_schema import NotificationCreateSchema, NotificationResponseSchema
from app.templates.notification_templates import DailyMealNotificationTemplate
from app.utils.get_group_info import get_group_info
from app.websocket.websocket_manager import websocket_manager
from shopping_shared.databases.database_manager import database_manager as postgres_db
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Daily Meal Handler")


class DailyMealHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the DAILY_MEAL notification.
        Expected message format:
        {
          "event_type": "daily_meal",
          "group_id": "uuid_string",
          "receivers": ["uuid_string"],  # optional
          "data": {
            "group_name": str,
            "breakfast": list[str],
            "lunch": list[str],
            "dinner": list[str]
          }
        }
        """
        event_type = message.get("event_type")
        group_id_raw = message.get("group_id")
        raw_data = message.get("data") or {}

        if not event_type or not group_id_raw or not isinstance(raw_data, dict):
            logger.warning(f"Invalid message format: {message}")
            return

        # 1) Render template title/content
        try:
            rendered = DailyMealNotificationTemplate.render(raw_data)
        except Exception as e:
            logger.error(f"Failed to render template for message: {message}. Error: {e}", exc_info=True)
            return

        try:
            group_id = UUID(str(group_id_raw))
        except Exception:
            logger.warning(f"Invalid group_id: {group_id_raw}")
            return

        # 2) Get group info + resolve receivers
        if app is None:
            logger.error("App context is required to resolve group info / DB config")
            return

        group_name_from_service, members, head_chef = await get_group_info(group_id, app.config)

        has_receivers_field = "receivers" in message
        receivers = message.get("receivers") if has_receivers_field else None

        if not has_receivers_field:
            receiver_is_head_chef = bool(message.get("receiver_is_head_chef", False))
            if receiver_is_head_chef:
                head_chef_id = None
                if isinstance(head_chef, dict):
                    head_chef_id = head_chef.get("user_id") or head_chef.get("userId")
                    if head_chef_id is None and isinstance(head_chef.get("user"), dict):
                        head_chef_id = head_chef["user"].get("user_id") or head_chef["user"].get("id")
                receivers = [head_chef_id] if head_chef_id else []
            else:
                receivers = []
                for m in members or []:
                    if not isinstance(m, dict):
                        continue
                    member_id = m.get("user_id") or m.get("userId")
                    if member_id is None and isinstance(m.get("user"), dict):
                        member_id = m["user"].get("user_id") or m["user"].get("id")
                    if member_id:
                        receivers.append(member_id)

        final_group_name = group_name_from_service or raw_data.get("group_name")
        if not final_group_name:
            logger.error(f"Missing group_name for group {group_id}. message={message}")
            return

        # Ensure DB is initialized for consumer context (learn from user-service: setup_db listener)
        if postgres_db.engine is None:
            logger.error("Database is not initialized. Ensure setup_db is registered in app listeners.")
            return

        created_for_ws: list[tuple[str, dict]] = []

        # 3) Insert one row per receiver
        try:
            async with postgres_db.get_session() as session:
                repo = NotificationRepository(session)
                for r in receivers or []:
                    try:
                        receiver_uuid = UUID(str(r))
                    except Exception:
                        logger.warning(f"Invalid receiver id: {r}")
                        continue

                    created = await repo.create(NotificationCreateSchema(
                        receiver=receiver_uuid,
                        group_id=group_id,
                        group_name=final_group_name,
                        template_code=DailyMealNotificationTemplate.template_code,
                        title=rendered["title"],
                        content=rendered["content"],
                        raw_data=raw_data,
                        is_read=False,
                    ))
                    created_for_ws.append(
                        (str(receiver_uuid), NotificationResponseSchema.model_validate(created).model_dump(mode="json"))
                    )
        except Exception as e:
            logger.error(f"Failed to persist notifications for message: {message}. Error: {e}", exc_info=True)
            return

        # 4) Push created rows to websocket
        for user_id, payload in created_for_ws:
            await websocket_manager.send_to_user(user_id, {"event_type": event_type, "data": payload})


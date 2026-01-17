# notification-service/app/consumers/handlers/add_user_group_handler.py
from uuid import UUID

from app.consumers.handlers.base_handler import BaseMessageHandler
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification_schema import NotificationCreateSchema, NotificationResponseSchema
from app.templates.notification_templates import GroupUserAddedNotificationTemplate
from app.utils.get_group_info import get_group_info
from app.websocket.websocket_manager import websocket_manager

from shopping_shared.databases.database_manager import database_manager as postgres_db


class AddUserGroupHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the group_user_added notification.
        Expected message format:
        {
          "event_type": "group_user_added",
          "group_id": "uuid_string",
          "receivers": ["uuid_string"],  # optional
          "data": {
            "requester_username": str
          }
        }
        """
        event_type = message.get("event_type")
        group_id_raw = message.get("group_id")
        raw_data = message.get("data") or {}

        if not event_type or not group_id_raw or not isinstance(raw_data, dict):
            return

        try:
            group_id = UUID(str(group_id_raw))
        except Exception:
            return

        # 1) Get group info first (to inject group_name into data)
        if app is None:
            return

        group_name_from_service, members, head_chef = await get_group_info(group_id, app.config)

        if not group_name_from_service:
            return

        raw_data["group_name"] = group_name_from_service

        # 2) Render template title/content (after group_name injection)
        try:
            rendered = GroupUserAddedNotificationTemplate.render(raw_data)
        except Exception as e:
            return

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

        # Ensure DB is initialized for consumer context (learn from user-service: setup_db listener)
        if postgres_db.engine is None:
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
                        continue

                    created = await repo.create(NotificationCreateSchema(
                        receiver=receiver_uuid,
                        group_id=group_id,
                        group_name=group_name_from_service,
                        template_code=GroupUserAddedNotificationTemplate.template_code,
                        title=rendered["title"],
                        content=rendered["content"],
                        raw_data=raw_data,
                        is_read=False,
                    ))
                    created_for_ws.append(
                        (str(receiver_uuid), NotificationResponseSchema.model_validate(created).model_dump(mode="json"))
                    )
        except Exception as e:
            return

        # 4) Push created rows to websocket
        for user_id, payload in created_for_ws:
            await websocket_manager.send_to_user(user_id, {"event_type": event_type, "data": payload})
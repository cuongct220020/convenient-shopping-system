# notification-service/app/consumers/handlers/update_head_chef_role_handler.py
from app.consumers.handlers.base_handler import BaseMessageHandler
from app.services.websocket_notification_service import websocket_notification_service
from app.utils.get_current_timestamp import get_current_timestamp
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("Update Head Chef Role Handler")


class UpdateHeadChefRoleHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the UPDATE_HEADCHEF_ROLE_EVENTS_TOPIC message.
        Expected message format:
        {
          "event_type": "group_head_chef_updated",
          "requester_id": "uuid_string",
          "requester_username": "string",
          "group_id": "uuid_string",
          "group_name": "string",
          "old_head_chef_id": "uuid_string", // Can be null
          "old_head_chef_identifier": "string", // Can be null
          "new_head_chef_id": "uuid_string",
          "new_head_chef_identifier": "string",
          "timestamp": "iso8601_string"
        }
        """
        try:
            event_type = message.get("event_type")
            requester_id = message.get("requester_id")
            requester_username = message.get("requester_username")
            group_id = message.get("group_id")
            group_name = message.get("group_name")
            old_head_chef_id = message.get("old_head_chef_id")
            old_head_chef_identifier = message.get("old_head_chef_identifier")
            new_head_chef_id = message.get("new_head_chef_id")
            new_head_chef_identifier = message.get("new_head_chef_identifier")
            timestamp = message.get("timestamp")

            # Validate required fields (allowing old_head_chef fields to be null)
            if not all([event_type, requester_id, requester_username, group_id, group_name, new_head_chef_id, new_head_chef_identifier, timestamp]):
                logger.error(f"Missing required fields in message: {message}")
                return

            # Log the received message for debugging
            logger.info(
                f"Processing head chef role update event: "
                f"requester_id={requester_id}, "
                f"group_id={group_id}, "
                f"old_head_chef_id={old_head_chef_id}, "
                f"new_head_chef_id={new_head_chef_id}"
            )

            # Send notification to all group members (group notification)
            await websocket_notification_service.send_group_update_head_chef_role_notification(
                event_type=event_type,
                requester_id=requester_id,
                requester_username=requester_username,
                group_id=group_id,
                group_name=group_name,
                old_head_chef_id=old_head_chef_id,
                old_head_chef_identifier=old_head_chef_identifier,
                new_head_chef_id=new_head_chef_id,
                new_head_chef_identifier=new_head_chef_identifier,
                timestamp=timestamp if timestamp else get_current_timestamp(),
            )

            logger.info(f"Successfully processed head chef role update event for group {group_id}")

        except Exception as e:
            logger.error(f"Error processing head chef role update message: {e}", exc_info=True)
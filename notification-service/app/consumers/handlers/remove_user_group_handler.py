# notification-service/app/consumers/handlers/remove_user_group_handler.py
from app.consumers.handlers.base_handler import BaseMessageHandler
from app.services.websocket_notification_service import websocket_notification_service
from app.utils.get_current_timestamp import get_current_timestamp

from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("Remove User Group Handler")


class RemoveUserGroupHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the REMOVE_USERS_GROUP_EVENTS_TOPIC message.
        Expected message format:
        {
          "event_type": "group_user_removed",
          "requester_id": "uuid_string",
          "requester_username": "string",
          "requester_user_role": "string",
          "group_id": "uuid_string",
          "group_name": "string",
          "user_to_remove_id": "uuid_string",
          "user_to_remove_identifier": "string",
          "timestamp": "iso8601_string"
        }
        """
        try:
            event_type = message.get("event_type")
            requester_id = message.get("requester_id")
            requester_username = message.get("requester_username")
            requester_user_role = message.get("requester_user_role")
            group_id = message.get("group_id")
            group_name = message.get("group_name")
            user_to_remove_id = message.get("user_to_remove_id")
            user_to_remove_identifier = message.get("user_to_remove_identifier")
            timestamp = message.get("timestamp")

            # Validate required fields
            if not all([event_type, requester_id, requester_username, group_id, group_name, user_to_remove_id, user_to_remove_identifier, timestamp]):
                logger.error(f"Missing required fields in message: {message}")
                return

            # Log the received message for debugging
            logger.info(
                f"Processing remove user from group event: "
                f"requester_id={requester_id}, "
                f"group_id={group_id}, "
                f"user_to_remove_id={user_to_remove_id}, "
                f"user_to_remove_identifier={user_to_remove_identifier}"
            )



            await websocket_notification_service.send_group_user_removed_notification(
                event_type=event_type,
                requester_id=requester_id,
                requester_username=requester_username,
                requester_user_role=requester_user_role,
                group_id=group_id,
                group_name=group_name,
                user_to_remove_id=user_to_remove_id,
                user_to_remove_identifier=user_to_remove_identifier,
                timestamp=timestamp if timestamp else get_current_timestamp(),
            )

            logger.info(f"Successfully processed remove user from group event for user {user_to_remove_identifier}")

        except Exception as e:
            logger.error(f"Error processing remove user group message: {e}", exc_info=True)

# notification-service/app/consumers/handlers/user_leave_group_handler.py
from app.consumers.handlers.base_handler import BaseMessageHandler
from app.services.websocket_notification_service import websocket_notification_service
from app.utils.get_current_timestamp import get_current_timestamp
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("User Leave Group Handler")


class UserLeaveGroupHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the LEAVE_GROUP_EVENTS_TOPIC message.
        Expected message format:
        {
          "event_type": "group_user_left",
          "user_id": "uuid_string",
          "user_identifier": "string",
          "group_id": "uuid_string",
          "group_name": "string",
          "timestamp": "iso8601_string"
        }
        """
        try:
            event_type = message.get("event_type")
            user_id = message.get("user_id")
            user_identifier = message.get("user_identifier")
            group_id = message.get("group_id")
            group_name = message.get("group_name")
            timestamp = message.get("timestamp")

            # Validate required fields
            if not all([event_type, user_id, user_identifier, group_id, group_name, timestamp]):
                logger.error(f"Missing required fields in message: {message}")
                return

            # Log the received message for debugging
            logger.info(
                f"Processing leave group event: "
                f"user_id={user_id}, "
                f"group_id={group_id}, "
                f"user_identifier={user_identifier}"
            )


            # Send notification to all remaining group members (group notification)
            await websocket_notification_service.send_group_user_leaved_notification(
                event_type=event_type,
                user_id=user_id,
                user_identifier=user_identifier,
                group_id=group_id,
                group_name=group_name,
                timestamp=timestamp if timestamp else get_current_timestamp()
            )

            logger.info(f"Successfully processed leave group event for user {user_identifier}")

        except Exception as e:
            logger.error(f"Error processing leave group message: {e}", exc_info=True)
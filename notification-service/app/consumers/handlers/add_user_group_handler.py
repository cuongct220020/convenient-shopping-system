# notification-service/app/consumers/handlers/add_user_group_handler.py
from app.consumers.handlers.base_handler import BaseMessageHandler
from app.services.websocket_notification_service import websocket_notification_service
from app.utils.get_current_timestamp import get_current_timestamp
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("Add User Group Handler")


class AddUserGroupHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the ADD_USERS_GROUP_EVENTS_TOPIC message.
        Expected message format:
        {
          "event_type": "group_user_added",
          "requester_id": "uuid_string",
          "requester_username": "string",
          "group_id": "uuid_string",
          "group_name": "string",
          "group_members_ids": [uuid_string],
          "user_to_add_id": "uuid_string",
          "user_to_add_identifier": "string",
          "timestamp": "iso8601_string"
        }
        """
        try:
            event_type = message.get("event_type")
            requester_id = message.get("requester_id")
            requester_username = message.get("requester_username")
            group_id = message.get("group_id")
            group_name = message.get("group_name")
            group_members_ids = message.get("group_members_ids")
            user_to_add_id = message.get("user_to_add_id")
            user_to_add_identifier = message.get("user_to_add_identifier")
            timestamp = message.get("timestamp")

            # Validate required fields
            if not all([event_type, requester_id, group_id, group_name, user_to_add_id, user_to_add_identifier, timestamp]):
                logger.error(f"Missing required fields in message: {message}")
                return

            # Log the received message for debugging
            logger.info(
                f"Processing add user to group event: "
                f"requester_id={requester_id}, "
                f"group_id={group_id}, "
                f"user_to_add_id={user_to_add_id}, "
                f"user_to_add_identifier={user_to_add_identifier}"
            )

            # Send notification to the user being added (personal notification)
            await websocket_notification_service.send_group_user_added_notification(
                event_type=event_type,
                requester_id=requester_id,
                requester_username=requester_username,
                group_id=group_id,
                group_name=group_name,
                group_member_ids=group_members_ids,
                user_to_add_id=user_to_add_id,
                user_to_add_identifier=user_to_add_identifier,
                timestamp=timestamp if timestamp else get_current_timestamp(),
            )

        except Exception as e:
            logger.error(f"Error processing add user group message: {e}", exc_info=True)
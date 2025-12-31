from app.consumers.handlers.base_handler import BaseMessageHandler
from app.services.websocket_notification_service import websocket_notification_service
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("AddUserGroupHandler")


class AddUserGroupHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the ADD_USER_GROUP_EVENTS_TOPIC message.
        """
        try:
            requester_id = message.get("requester_id")
            group_id = message.get("group_id")
            user_to_add_id = message.get("user_to_add_id")
            user_to_add_identifier = message.get("user_to_add_identifier")
            group_member_ids = message.get("group_member_ids", [])

            # Validate required fields
            if not all([requester_id, group_id, user_to_add_id, user_to_add_identifier, group_member_ids]):
                logger.error(f"Missing required fields in message: {message}")
                return

            # Initialize the websocket notification service with the app if provided
            if app and websocket_notification_service.app is None:
                websocket_notification_service.init_app(app)

            # Log the received message for debugging
            logger.info(
                f"Processing add user to group event: "
                f"requester_id={requester_id}, "
                f"group_id={group_id}, "
                f"user_to_add_id={user_to_add_id}, "
                f"user_to_add_identifier={user_to_add_identifier}, "
                f"total_group_members={len(group_member_ids)}"
            )

            # Send notification to all group members (including the user being added)
            await websocket_notification_service.send_group_user_added_notification(
                requester_id=requester_id,
                group_id=group_id,
                user_to_add_id=user_to_add_id,
                user_to_add_identifier=user_to_add_identifier,
                group_member_ids=group_member_ids
            )

            logger.info(f"Successfully processed add user to group event for user {user_to_add_identifier}")

        except Exception as e:
            logger.error(f"Error processing add user group message: {e}", exc_info=True)

    @staticmethod
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat() + "Z"

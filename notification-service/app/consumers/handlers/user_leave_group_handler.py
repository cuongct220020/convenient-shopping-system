from app.consumers.handlers.base_handler import BaseMessageHandler
from app.services.websocket_notification_service import websocket_notification_service
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("LeaveGroupHandler")


class UserLeaveGroupHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the LEAVE_GROUP_EVENTS_TOPIC message.
        
        Expected message format:
        {
            "user_id": "98cbaaea-0c03-4ac6-bdca-d835e86bbb6f",
            "group_id": "f412d17c-f141-4589-bd06-f074f02a1f8b",
            "user_identifier": "user@example.com",
            "group_member_ids": ["user1_id", "user2_id", ...]  # All remaining members in the group
        }
        """
        try:
            user_id = message.get("user_id")
            group_id = message.get("group_id")
            user_identifier = message.get("user_identifier")
            group_member_ids = message.get("group_member_ids", [])

            # Validate required fields
            if not all([user_id, group_id, user_identifier, group_member_ids]):
                logger.error(f"Missing required fields in message: {message}")
                return

            # Initialize the websocket notification service with the app if provided
            if app and websocket_notification_service.app is None:
                websocket_notification_service.init_app(app)

            # Log the received message for debugging
            logger.info(
                f"Processing leave group event: "
                f"user_id={user_id}, "
                f"group_id={group_id}, "
                f"user_identifier={user_identifier}, "
                f"total_group_members={len(group_member_ids)}"
            )

            # Send notification to all remaining group members
            await websocket_notification_service.send_group_member_left_notification(
                user_id=user_id,
                group_id=group_id,
                user_identifier=user_identifier,
                group_member_ids=group_member_ids
            )

            logger.info(f"Successfully processed leave group event for user {user_identifier}")
            
        except Exception as e:
            logger.error(f"Error processing leave group message: {e}", exc_info=True)

    @staticmethod
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat() + "Z"
from app.consumers.handlers.base_handler import BaseMessageHandler
from app.services.websocket_notification_service import websocket_notification_service
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("RemoveUserGroupHandler")


class RemoveUserGroupHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the REMOVE_USERS_GROUP_EVENTS_TOPIC message.
        
        Expected message format:
        {
            "requester_id": "98cbaaea-0c03-4ac6-bdca-d835e86bbb6f",
            "group_id": "f412d17c-f141-4589-bd06-f074f02a1f8b",
            "user_to_remove_id": "04f83499-7b7f-46e4-a454-a9e39b2615c4",
            "user_to_remove_identifier": "member_b_90084@test.com",
            "group_member_ids": ["user1_id", "user2_id", ...]  # All remaining members in the group
        }
        """
        try:
            requester_id = message.get("requester_id")
            group_id = message.get("group_id")
            user_to_remove_id = message.get("user_to_remove_id")
            user_to_remove_identifier = message.get("user_to_remove_identifier")
            group_member_ids = message.get("group_member_ids", [])

            # Validate required fields
            if not all([requester_id, group_id, user_to_remove_id, user_to_remove_identifier, group_member_ids]):
                logger.error(f"Missing required fields in message: {message}")
                return

            # Initialize the websocket notification service with the app if provided
            if app and websocket_notification_service.app is None:
                websocket_notification_service.init_app(app)

            # Log the received message for debugging
            logger.info(
                f"Processing remove user from group event: "
                f"requester_id={requester_id}, "
                f"group_id={group_id}, "
                f"user_to_remove_id={user_to_remove_id}, "
                f"user_to_remove_identifier={user_to_remove_identifier}, "
                f"total_group_members={len(group_member_ids)}"
            )

            # Send notification to all remaining group members
            await websocket_notification_service.send_group_user_removed_notification(
                requester_id=requester_id,
                group_id=group_id,
                user_to_remove_id=user_to_remove_id,
                user_to_remove_identifier=user_to_remove_identifier,
                group_member_ids=group_member_ids
            )

            logger.info(f"Successfully processed remove user from group event for user {user_to_remove_identifier}")
            
        except Exception as e:
            logger.error(f"Error processing remove user group message: {e}", exc_info=True)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat() + "Z"
from app.consumers.handlers.base_handler import BaseMessageHandler
from app.services.websocket_notification_service import websocket_notification_service
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("UpdateHeadChefRoleHandler")


class UpdateHeadChefRoleHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the UPDATE_HEADCHEF_ROLE_EVENTS_TOPIC message.
        
        Expected message format:
        {
            "requester_id": "98cbaaea-0c03-4ac6-bdca-d835e86bbb6f",
            "group_id": "f412d17c-f141-4589-bd06-f074f02a1f8b",
            "old_head_chef_id": "04f83499-7b7f-46e4-a454-a9e39b2615c4",
            "new_head_chef_id": "12345678-7b7f-46e4-a454-a9e39b261234",
            "old_head_chef_identifier": "old_head@example.com",
            "new_head_chef_identifier": "new_head@example.com",
            "group_member_ids": ["user1_id", "user2_id", ...]  # All members in the group
        }
        """
        try:
            requester_id = message.get("requester_id")
            group_id = message.get("group_id")
            old_head_chef_id = message.get("old_head_chef_id")
            new_head_chef_id = message.get("new_head_chef_id")
            old_head_chef_identifier = message.get("old_head_chef_identifier")
            new_head_chef_identifier = message.get("new_head_chef_identifier")
            group_member_ids = message.get("group_member_ids", [])

            # Validate required fields
            if not all([requester_id, group_id, old_head_chef_id, new_head_chef_id, 
                       old_head_chef_identifier, new_head_chef_identifier, group_member_ids]):
                logger.error(f"Missing required fields in message: {message}")
                return

            # Initialize the websocket notification service with the app if provided
            if app and websocket_notification_service.app is None:
                websocket_notification_service.init_app(app)

            # Log the received message for debugging
            logger.info(
                f"Processing head chef role update event: "
                f"requester_id={requester_id}, "
                f"group_id={group_id}, "
                f"old_head_chef_id={old_head_chef_id}, "
                f"new_head_chef_id={new_head_chef_id}, "
                f"total_group_members={len(group_member_ids)}"
            )

            # Send notification to all group members
            await websocket_notification_service.send_head_chef_role_updated_notification(
                requester_id=requester_id,
                group_id=group_id,
                old_head_chef_id=old_head_chef_id,
                new_head_chef_id=new_head_chef_id,
                old_head_chef_identifier=old_head_chef_identifier,
                new_head_chef_identifier=new_head_chef_identifier,
                group_member_ids=group_member_ids
            )

            logger.info(f"Successfully processed head chef role update event for group {group_id}")
            
        except Exception as e:
            logger.error(f"Error processing head chef role update message: {e}", exc_info=True)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat() + "Z"
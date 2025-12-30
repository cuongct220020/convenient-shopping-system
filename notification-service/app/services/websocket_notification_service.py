import json
from typing import Dict, List
from uuid import UUID
from sanic import Sanic
from shopping_shared.utils.logger_utils import get_logger
from app.websocket.websocket_manager import websocket_manager


logger = get_logger("WebSocket Notification Service")


class WebSocketNotificationService:
    """
    Service to handle WebSocket notifications for various events.
    """
    
    def __init__(self, app: Sanic = None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app: Sanic):
        self.app = app
        logger.info("WebSocket NotificationService initialized.")
    
    async def send_group_user_added_notification(
        self, 
        requester_id: str, 
        group_id: str, 
        user_to_add_id: str, 
        user_to_add_identifier: str
    ):
        """
        Send notification to the user being added and all other members in the group.
        
        Args:
            requester_id: ID of the user who requested the addition
            group_id: ID of the group where user is being added
            user_to_add_id: ID of the user being added to the group
            user_to_add_identifier: Email or username of the user being added
        """
        try:
            # Prepare the notification message
            message = {
                "event_type": "GROUP_USER_ADDED",
                "data": {
                    "requester_id": requester_id,
                    "group_id": group_id,
                    "user_to_add_id": user_to_add_id,
                    "user_to_add_identifier": user_to_add_identifier,
                    "timestamp": self._get_current_timestamp()
                }
            }
            
            # Send notification to the user being added
            await websocket_manager.send_to_user(user_to_add_id, message)
            logger.info(f"Sent group user added notification to user {user_to_add_id}")
            
            # Get other group members and send them the notification
            # This requires integration with user-service to get group members
            # For now, I'll implement the logic assuming we have a method to get group members
            other_member_ids = await self._get_group_member_ids(group_id, exclude_user_ids=[user_to_add_id])
            
            for member_id in other_member_ids:
                await websocket_manager.send_to_user(member_id, message)
                logger.info(f"Sent group user added notification to member {member_id}")
                
        except Exception as e:
            logger.error(f"Error sending group user added notification: {e}", exc_info=True)
    
    async def _get_group_member_ids(self, group_id: str, exclude_user_ids: List[str] = None) -> List[str]:
        """
        Get all member IDs for a group, excluding specified user IDs.
        This method would typically call the user-service to get group members.
        For now, returning an empty list as placeholder.
        """
        # In a real implementation, this would call the user-service API
        # to get all members of the group
        # For now, returning empty list as placeholder
        # This will be implemented when we integrate with user-service
        return []
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now(UTC).isoformat() + "Z"


# Global instance
websocket_notification_service = WebSocketNotificationService()
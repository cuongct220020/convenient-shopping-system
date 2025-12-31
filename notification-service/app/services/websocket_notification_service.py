import json
from typing import Dict, List
from uuid import UUID
from sanic import Sanic
from shopping_shared.utils.logger_utils import get_logger
from app.websocket.websocket_manager import websocket_manager
from app.services.notification_service import notification_service


logger = get_logger("WebSocket Notification Service")


class WebSocketNotificationService:
    """
    Service to handle WebSocket notifications for various events.
    """

    def __init__(self):
        # Dependencies are managed globally or injected where needed
        pass
        
    # No explicit init_app needed as it relies on global services that are initialized elsewhere

    async def send_group_user_added_notification(
        self,
        requester_id: str,
        group_id: str,
        user_to_add_id: str,
        user_to_add_identifier: str,
        group_member_ids: List[str]
    ):
        """
        Send notification to the user being added and all other members in the group.

        Args:
            requester_id: ID of the user who requested the addition
            group_id: ID of the group where user is being added
            user_to_add_id: ID of the user being added to the group
            user_to_add_identifier: Email or username of the user being added
            group_member_ids: List of all member IDs in the group
        """
        try:
            # Create notifications in the database
            created_notifications = await notification_service.create_group_user_added_notification(
                user_ids=group_member_ids,
                group_id=group_id,
                requester_id=requester_id,
                user_to_add_id=user_to_add_id,
                user_to_add_identifier=user_to_add_identifier
            )

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

            # Send WebSocket notification to all group members
            for member_id in group_member_ids:
                try:
                    await websocket_manager.send_to_user(member_id, message)

                    # Log successful delivery
                    notification = next((n for n in created_notifications if str(n.user_id) == member_id), None)
                    if notification:
                        await notification_service.log_notification_delivery(
                            str(notification.id),
                            "WEBSOCKET",
                            True
                        )

                    logger.info(f"Sent group user added notification to member {member_id}")
                except Exception as e:
                    logger.error(f"Failed to send WebSocket notification to member {member_id}: {e}")

                    # Log failed delivery
                    notification = next((n for n in created_notifications if str(n.user_id) == member_id), None)
                    if notification:
                        await notification_service.log_notification_delivery(
                            str(notification.id),
                            "WEBSOCKET",
                            False,
                            str(e)
                        )

        except Exception as e:
            logger.error(f"Error sending group user added notification: {e}", exc_info=True)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat() + "Z"


# Global instance
websocket_notification_service = WebSocketNotificationService()
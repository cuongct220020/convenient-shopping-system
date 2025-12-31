from datetime import datetime
from typing import List

from app.websocket.websocket_manager import websocket_manager
from app.utils.get_current_timestamp import get_current_timestamp

from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("WebSocket Notification Service")


class WebSocketNotificationService:
    """
    Service to handle WebSocket notifications for various events.
    """

    @staticmethod
    async def send_group_user_added_notification(
        event_type: str,
        requester_id: str,
        requester_username: str,
        group_id: str,
        group_name: str,
        group_member_ids: List[str],
        user_to_add_id: str,
        user_to_add_identifier: str,
        timestamp: datetime,
    ):
        """
        Send notification to the user being added and all other members in the group.
        """

        try:
            # Prepare the notification message for WebSocket
            message = {
                "event_type": event_type,
                "data": {
                    "requester_id": requester_id,
                    "requester_username": requester_username,
                    "group_id": group_id,
                    "group_name": group_name,
                    "group_member_ids": group_member_ids,
                    "user_to_add_id": user_to_add_id,
                    "user_to_add_identifier": user_to_add_identifier,
                    "timestamp": timestamp if timestamp else get_current_timestamp()
                }
            }

            # Send notification to all existing group members using broadcast
            await websocket_manager.broadcast_to_group(group_id, message)
            logger.info(f"Broadcasted group user added notification to group {group_id}")

            # Send notification to the user being added
            try:
                await websocket_manager.send_to_user(user_to_add_id, message)
                logger.info(f"Sent group user added notification to user being added: {user_to_add_id}")
            except Exception as e:
                logger.error(f"Failed to send WebSocket notification to user being added {user_to_add_id}: {e}")

            # Add the new user to the group WebSocket connections
            await websocket_manager.add_user_to_group(user_to_add_id, group_id)
            logger.info(f"Successfully added user {user_to_add_id} to WebSocket group {group_id}")

        except Exception as e:
            logger.error(f"Error sending group user added notification: {e}", exc_info=True)

        logger.info(f"Successfully processed add user to group event for user {user_to_add_identifier}")


    @staticmethod
    async def send_group_user_removed_notification(
        event_type: str,
        requester_id: str,
        requester_username: str,
        group_id: str,
        group_name: str,
        user_to_remove_id: str,
        user_to_remove_identifier: str,
        timestamp: datetime,
    ):
        """
        Send notification to all remaining members in the group and the user being removed.
        Then remove the user from the group WebSocket connections.
        """
        try:
            # Prepare the notification message for WebSocket
            message = {
                "event_type": event_type,
                "data": {
                    "requester_id": requester_id,
                    "requester_username": requester_username,
                    "group_id": group_id,
                    "group_name": group_name,
                    "user_to_remove_id": user_to_remove_id,
                    "user_to_remove_identifier": user_to_remove_identifier,
                    "timestamp": timestamp if timestamp else get_current_timestamp()
                }
            }

            # Send notification to all remaining group members using broadcast
            await websocket_manager.broadcast_to_group(group_id, message)
            logger.info(f"Broadcasted group user removed notification to group {group_id}")

            # Send notification to the user being removed
            try:
                await websocket_manager.send_to_user(user_to_remove_id, message)
                logger.info(f"Sent group user removed notification to user being removed: {user_to_remove_id}")
            except Exception as e:
                logger.error(f"Failed to send WebSocket notification to user being removed {user_to_remove_id}: {e}")

            # Remove the user from the group WebSocket connections
            await websocket_manager.remove_user_from_group(user_to_remove_id, group_id)
            logger.info(f"Successfully removed user {user_to_remove_id} from WebSocket group {group_id}")

        except Exception as e:
            logger.error(f"Error sending group user removed notification: {e}", exc_info=True)

        logger.info(f"Successfully processed remove user from group event for user {user_to_remove_identifier}")



    @staticmethod
    async def send_group_update_head_chef_role_notification(
        event_type: str,
        requester_id: str,
        requester_username: str,
        group_id: str,
        group_name: str,
        old_head_chef_id: str,
        old_head_chef_identifier: str,
        new_head_chef_id: str,
        new_head_chef_identifier: str,
        timestamp: datetime,
    ):
        """
        Send notification to all group members about head chef role update.
        """
        try:
            message = {
                "event_type": event_type,
                "data": {
                    "requester_id": requester_id,
                    "requester_username": requester_username,
                    "group_id": group_id,
                    "group_name": group_name,
                    "old_head_chef_id": old_head_chef_id,
                    "old_head_chef_identifier": old_head_chef_identifier,
                    "new_head_chef_id": new_head_chef_id,
                    "new_head_chef_identifier": new_head_chef_identifier,
                    "timestamp": timestamp if timestamp else get_current_timestamp()
                }
            }

            await websocket_manager.broadcast_to_group(group_id, message)
            logger.info(f"Broadcasted head chef role update notification to group {group_id}")

        except Exception as e:
            logger.error(f"Error sending head chef role update notification: {e}", exc_info=True)

        logger.info(f"Successfully processed head chef role update event for group {group_id}")



    @staticmethod
    async def send_group_user_leaved_notification(
        event_type: str,
        user_id: str,
        user_identifier: str,
        group_id: str,
        group_name: str,
        timestamp: datetime,
    ):
        """
        Send notification to all remaining members in the group about user leaving.
        Then remove the user from the group WebSocket connections.
        """
        try:
            # Prepare the notification message for WebSocket
            message = {
                "event_type": event_type,
                "data": {
                    "user_id": user_id,
                    "user_identifier": user_identifier,
                    "group_id": group_id,
                    "group_name": group_name,
                    "timestamp": timestamp if timestamp else get_current_timestamp()
                }
            }

            # Send notification to all remaining group members using broadcast
            await websocket_manager.broadcast_to_group(group_id, message)
            logger.info(f"Broadcasted group user left notification to group {group_id}")

            # Remove the user from the group WebSocket connections
            await websocket_manager.remove_user_from_group(user_id, group_id)
            logger.info(f"Successfully removed user {user_id} from WebSocket group {group_id}")

        except Exception as e:
            logger.error(f"Error sending group user left notification: {e}", exc_info=True)

        logger.info(f"Successfully processed user left group event for user {user_identifier}")




# Global instance
websocket_notification_service = WebSocketNotificationService()
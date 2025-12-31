# notification-service/app/consumers/handlers/user_logout_handler.py
from app.consumers.handlers.base_handler import BaseMessageHandler
from app.websocket.websocket_manager import websocket_manager
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("User Logout Handler")


class UserLogoutHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the LOGOUT_EVENTS_TOPIC message.
        Expected message format:
        {
          "event_type": "account_logged_out",
          "user_id": "uuid_string",
          "access_token_id": "uuid_string",
          "timestamp": "iso8601_string",
        }
        """
        try:
            event_type = message.get("event_type")
            user_id = message.get("user_id")
            access_token_id = message.get("access_token_id")
            timestamp = message.get("timestamp")

            # Validate required fields
            if not all([event_type, user_id, access_token_id, timestamp]):
                logger.error(f"Missing required fields in message: {message}")
                return

            # Log the received message for debugging
            logger.info(f"Processing logout event for user: {user_id}")

            # Handle user logout by disconnecting all WebSocket connections for the user
            await websocket_manager.disconnect_user_all_connections(user_id)

            logger.info(f"Successfully disconnected all WebSocket connections for user {user_id}")

        except Exception as e:
            logger.error(f"Error processing logout message: {e}", exc_info=True)
# notification-service/app/consumers/handlers/user_logout_handler.py
from app.consumers.handlers.base_handler import BaseMessageHandler
from app.websocket.websocket_manager import websocket_manager


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
                return

            # Handle user logout by disconnecting all WebSocket connections for the user
            await websocket_manager.disconnect_user_all_connections(user_id)

        except Exception as e:
            pass
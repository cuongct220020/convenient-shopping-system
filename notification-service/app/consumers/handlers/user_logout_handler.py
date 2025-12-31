from app.consumers.handlers.base_handler import BaseMessageHandler
from app.services.websocket_notification_service import websocket_notification_service
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("LogoutUserHandler")


class UserLogoutHandler(BaseMessageHandler):
    async def handle(self, message: dict, app=None):
        """
        Handle the LOGOUT_EVENTS_TOPIC message.
        
        Expected message format:
        {
            "user_id": "98cbaaea-0c03-4ac6-bdca-d835e86bbb6f",
            "timestamp": "2023-01-01T00:00:00Z"
        }
        """
        try:
            event_type = message.get("event_type")
            user_id = message.get("user_id")
            access_token_id = message.get("access_token_id")
            timestamp = message.get("timestamp")


            # Validate required fields
            if not user_id:
                logger.error(f"Missing required fields in message: {message}")
                return

            # Initialize the websocket notification service with the app if provided
            if app and websocket_notification_service.app is None:
                websocket_notification_service.init_app(app)

            # Log the received message for debugging
            logger.info(
                f"Processing logout event for user: {user_id}"
            )

            # Send notification to the user who logged out
            # Prepare the notification message
            notification_message = {
                "event_type": event_type,
                "data": {
                    "user_id": user_id,
                    "timestamp": timestamp if not None else self._get_current_timestamp()
                }
            }

            # Send WebSocket notification to the user
            await websocket_notification_service.send_logout_notification(
                user_id=user_id,
                message=notification_message
            )

            logger.info(f"Successfully processed logout event for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing logout message: {e}", exc_info=True)

    @staticmethod
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat() + "Z"
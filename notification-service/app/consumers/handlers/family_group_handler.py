from app.consumers.handlers.base_handler import BaseMessageHandler
from app.services.websocket_notification_service import websocket_notification_service
from app.websocket.websocket_manager import websocket_manager
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("Add User Group Handler")

class AddUserGroupHandler(BaseMessageHandler):
    async def handler(self, message: dict, app = None):
        try:
            request_id = message.get("request_id")
            group_id = message.get("group_id")
            user_to_add_id = message.get("user_to_add_id")
            user_to_add_identifier = message.get("user_to_add_identifier")
            group_member_ids = message.get("group_member_ids")

            if not all([request_id, group_id, user_to_add_id, user_to_add_identifier, group_member_ids]):
                logger.error(f"Missing required fields in message: {message}")

            if app and websocket_notification_service is None:
                websocket_notification_service.init_app(app)

    #         for member_id in group_member_ids:
    #             notification_message = {
    #                 "event_type": "ADD_USERS_GROUP_EVENT",
    #             }
    #
    #
    # def _get_current_timestamp(self) -> str:

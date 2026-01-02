# # notification-service/app/services/noti_service.py
# from typing import List, Optional
# from uuid import UUID
# from sanic import Sanic
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import sessionmaker
#
# from app.models import Notification, NotificationType
# from app.repositories.notification_repository import (
#     NotificationRepository,
#     NotificationTypeRepository,
#     NotificationDeliveryLogRepository
# )
# from shopping_shared.utils.logger_utils import get_logger
#
#
# logger = get_logger("Notification Service")
#
#
# class NotificationService:
#     """
#     Service to handle database operations for notifications.
#     """
#
#     def __init__(self, engine=None):
#         self.engine = engine
#         if engine:
#             logger.info("NotificationService initialized.")
#
#     def set_engine(self, engine):
#         """Set database engine explicitly."""
#         self.engine = engine
#         logger.info("NotificationService engine set.")
#
#     def _get_session(self) -> AsyncSession:
#         """Get a new database session."""
#         if not self.engine:
#             raise RuntimeError("Database engine not initialized in NotificationService")
#         return sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)()
#
#     async def create_group_user_added_notification(
#         self,
#         user_ids: List[str],
#         group_id: str,
#         requester_id: str,
#         user_to_add_id: str,
#         user_to_add_identifier: str
#     ) -> List[Notification]:
#         """
#         Create notifications in the database for group user added event.
#
#         Args:
#             user_ids: List of user IDs to send notification to
#             group_id: ID of the group
#             requester_id: ID of the user who requested the addition
#             user_to_add_id: ID of the user being added
#             user_to_add_identifier: Email or username of the user being added
#
#         Returns:
#             List of created Notification objects
#         """
#         async with self._get_session() as session:
#             notification_repo = NotificationRepository(session)
#             type_repo = NotificationTypeRepository(session)
#
#             # Get or create the notification type
#             notification_type = await type_repo.get_by_code("GROUP_USER_ADDED")
#             if not notification_type:
#                 # Create default notification types
#                 await type_repo.create_default_types()
#                 notification_type = await type_repo.get_by_code("GROUP_USER_ADDED")
#
#             if not notification_type:
#                 logger.error("Could not find or create GROUP_USER_ADDED notification type")
#                 return []
#
#             created_notifications = []
#
#             # Create a notification for each user
#             for user_id in user_ids:
#                 try:
#                     # Prepare payload with relevant data
#                     payload = {
#                         "event_type": "GROUP_USER_ADDED",
#                         "requester_id": requester_id,
#                         "group_id": group_id,
#                         "user_to_add_id": user_to_add_id,
#                         "user_to_add_identifier": user_to_add_identifier,
#                         "timestamp": self._get_current_timestamp()
#                     }
#
#                     # Create the notification
#                     notification = Notification(
#                         user_id=UUID(user_id),
#                         group_id=UUID(group_id) if self._is_valid_uuid(group_id) else None,
#                         type_code=notification_type.code,
#                         payload=payload,
#                         is_read=False
#                     )
#
#                     session.add(notification)
#                     await session.flush()  # Get the ID of the notification
#                     created_notifications.append(notification)
#
#                     logger.debug(f"Created notification for user {user_id}")
#
#                 except Exception as e:
#                     logger.error(f"Error creating notification for user {user_id}: {e}", exc_info=True)
#
#             # Commit all notifications
#             await session.commit()
#
#             logger.info(f"Created {len(created_notifications)} notifications for group user added event")
#             return created_notifications
#
#     async def log_notification_delivery(
#         self,
#         notification_id: str,
#         delivery_method: str,
#         success: bool,
#         error_message: Optional[str] = None
#     ):
#         """
#         Log the delivery attempt of a notification.
#         """
#         async with self._get_session() as session:
#             log_repo = NotificationDeliveryLogRepository(session)
#
#             try:
#                 await log_repo.log_delivery_attempt(
#                     notification_id=UUID(notification_id),
#                     delivery_method=delivery_method,
#                     success=success,
#                     error_message=error_message
#                 )
#                 await session.commit()
#
#                 logger.info(f"Logged delivery attempt for notification {notification_id}, "
#                            f"method: {delivery_method}, success: {success}")
#             except Exception as e:
#                 logger.error(f"Error logging notification delivery for {notification_id}: {e}", exc_info=True)
#                 await session.rollback()
#
#     def _get_current_timestamp(self) -> str:
#         """Get current timestamp in ISO format."""
#         from datetime import datetime
#         return datetime.utcnow().isoformat() + "Z"
#
#     def _is_valid_uuid(self, uuid_str: str) -> bool:
#         """Check if a string is a valid UUID."""
#         try:
#             UUID(uuid_str)
#             return True
#         except ValueError:
#             return False
#
#
# # Global instance
# notification_service = NotificationService()
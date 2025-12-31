# # notification-service/app/repositories/notification_repository.py
# from typing import Optional, List
# from uuid import UUID
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import selectinload
#
# from app.models import Notification, NotificationType, NotificationDeliveryLog
# from shopping_shared.databases.base_repository import BaseRepository
# from app.schemas.notification_schema import (
#     NotificationCreateSchema,
#     NotificationUpdateSchema,
#     NotificationTypeCreateSchema,
#     NotificationTypeUpdateSchema,
#     NotificationDeliveryLogCreateSchema
# )
#
#
# class NotificationRepository(
#     BaseRepository[
#         Notification,
#         NotificationCreateSchema,
#         NotificationUpdateSchema
#     ]
# ):
#     """
#     Repository for Notification model with specialized methods.
#     """
#     def __init__(self, session: AsyncSession):
#         super().__init__(Notification, session)
#
#     async def get_by_user_id(self, user_id: UUID) -> List[Notification]:
#         """Get all notifications for a specific user."""
#         stmt = (
#             select(Notification)
#             .where(Notification.user_id == user_id)
#             .options(selectinload(Notification.notification_type))
#         )
#         result = await self.session.execute(stmt)
#         return result.scalars().all()
#
#     async def get_unread_by_user_id(self, user_id: UUID) -> List[Notification]:
#         """Get all unread notifications for a specific user."""
#         stmt = (
#             select(Notification)
#             .where(
#                 Notification.user_id == user_id,
#                 Notification.is_read == False
#             )
#             .options(selectinload(Notification.notification_type))
#         )
#         result = await self.session.execute(stmt)
#         return result.scalars().all()
#
#     async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
#         """Mark a notification as read."""
#         return await self.update_field(notification_id, "is_read", True)
#
#     async def mark_all_as_read(self, user_id: UUID) -> int:
#         """Mark all notifications for a user as read."""
#         stmt = (
#             select(Notification)
#             .where(Notification.user_id == user_id)
#             .where(Notification.is_read == False)
#         )
#         result = await self.session.execute(stmt)
#         notifications = result.scalars().all()
#
#         for notification in notifications:
#             notification.is_read = True
#
#         await self.session.flush()
#         return len(notifications)
#
#
# class NotificationTypeRepository:
#     """
#     Repository for NotificationType model (doesn't use BaseRepository due to different schema requirements).
#     """
#     def __init__(self, session: AsyncSession):
#         self.session = session
#         self.model = NotificationType
#
#     async def get_by_code(self, code: str) -> Optional[NotificationType]:
#         """Get notification type by its code."""
#         stmt = select(NotificationType).where(NotificationType.code == code)
#         result = await self.session.execute(stmt)
#         return result.scalars().first()
#
#     async def create(self, data: NotificationTypeCreateSchema) -> NotificationType:
#         """Create a new notification type."""
#         notification_type = NotificationType(**data.model_dump())
#         self.session.add(notification_type)
#         await self.session.flush()
#         await self.session.refresh(notification_type)
#         return notification_type
#
#     async def update(self, code: str, data: NotificationTypeUpdateSchema) -> Optional[NotificationType]:
#         """Update an existing notification type."""
#         notification_type = await self.get_by_code(code)
#         if notification_type:
#             update_data = data.model_dump(exclude_unset=True)
#             for key, value in update_data.items():
#                 setattr(notification_type, key, value)
#             await self.session.flush()
#             await self.session.refresh(notification_type)
#         return notification_type
#
#     async def create_default_types(self):
#         """Create default notification types if they don't exist."""
#         from app.enums.notification_priority import NotificationPriority
#
#         default_types = [
#             {
#                 "code": "GROUP_USER_ADDED",
#                 "template_body": "User {user_to_add_identifier} has been added to the group by {requester_id}",
#                 "priority_level": NotificationPriority.MEDIUM
#             },
#             {
#                 "code": "GROUP_USER_REMOVED",
#                 "template_body": "User has been removed from the group",
#                 "priority_level": NotificationPriority.MEDIUM
#             },
#             {
#                 "code": "GROUP_INVITATION",
#                 "template_body": "You have been invited to join a group",
#                 "priority_level": NotificationPriority.HIGH
#             },
#             {
#                 "code": "SYSTEM_ALERT",
#                 "template_body": "System alert: {message}",
#                 "priority_level": NotificationPriority.HIGH
#             }
#         ]
#
#         for type_data in default_types:
#             existing = await self.get_by_code(type_data["code"])
#             if not existing:
#                 notification_type = NotificationType(**type_data)
#                 self.session.add(notification_type)
#
#         await self.session.flush()
#
#
# class NotificationDeliveryLogRepository:
#     """
#     Repository for NotificationDeliveryLog model (doesn't use BaseRepository due to different schema requirements).
#     """
#     def __init__(self, session: AsyncSession):
#         self.session = session
#         self.model = NotificationDeliveryLog
#
#     async def create(self, data: NotificationDeliveryLogCreateSchema) -> NotificationDeliveryLog:
#         """Create a new notification delivery log entry."""
#         log_entry = NotificationDeliveryLog(**data.model_dump())
#         self.session.add(log_entry)
#         await self.session.flush()
#         await self.session.refresh(log_entry)
#         return log_entry
#
#     async def log_delivery_attempt(
#         self,
#         notification_id: UUID,
#         delivery_method: str,
#         success: bool,
#         error_message: Optional[str] = None
#     ) -> NotificationDeliveryLog:
#         """Log a notification delivery attempt."""
#         log_entry = NotificationDeliveryLog(
#             notification_id=notification_id,
#             delivery_method=delivery_method,
#             success=success,
#             error_message=error_message
#         )
#         self.session.add(log_entry)
#         await self.session.flush()
#         return log_entry
# notification-service/app/services/notification_service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification_schema import NotificationResponseSchema, NotificationCreateSchema
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Notification Service")


class NotificationService:
    """
    Service to handle database operations for notifications.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = NotificationRepository(session)

    async def create_notification(self, notification_data: NotificationCreateSchema) -> NotificationResponseSchema:
        """
        Create a new notification.
        
        Args:
            notification_data: NotificationCreateSchema containing notification data
        
        Returns:
            NotificationResponseSchema of the created notification
        """
        notification = await self.repository.create(notification_data)
        return NotificationResponseSchema.model_validate(notification)

    async def get_notifications_by_user_id(self, user_id: UUID) -> List[NotificationResponseSchema]:
        """
        Get all notifications for a specific user.
        
        Args:
            user_id: UUID of the user (receiver)
        
        Returns:
            List of NotificationResponseSchema
        """
        notifications = await self.repository.get_by_receiver(user_id)
        return [NotificationResponseSchema.model_validate(notif) for notif in notifications]

    async def delete_notification(self, notification_id: int, user_id: UUID) -> bool:
        """
        Delete a notification. Only allows deletion of notifications owned by the user.
        
        Args:
            notification_id: ID of the notification
            user_id: UUID of the user (receiver) - for authorization check
        
        Returns:
            True if deleted, False if not found or not authorized
        """
        notification = await self.repository.get_by_id(notification_id)
        if not notification:
            return False
        
        # Check authorization: user can only delete their own notifications
        if notification.receiver != user_id:
            logger.warning(f"User {user_id} attempted to delete notification {notification_id} owned by {notification.receiver}")
            return False
        
        return await self.repository.delete(notification_id)

    async def mark_notification_as_read(self, notification_id: int, user_id: UUID) -> bool:
        """
        Mark a notification as read. Only allows marking notifications owned by the user.
        
        Args:
            notification_id: ID of the notification
            user_id: UUID of the user (receiver) - for authorization check
        
        Returns:
            True if successful, False if not found or not authorized
        """
        return await self.repository.mark_as_read(notification_id, user_id)


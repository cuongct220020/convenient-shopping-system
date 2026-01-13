# notification-service/app/repositories/notification_repository.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.notifications import Notification
from app.schemas.notification_schema import NotificationCreateSchema, NotificationUpdateSchema
from shopping_shared.databases.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification, NotificationCreateSchema, NotificationUpdateSchema]):
    """
    Repository for Notification model with specialized methods.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def get_by_receiver(self, receiver_id: UUID) -> List[Notification]:
        """Get all notifications for a specific receiver."""
        stmt = (
            select(Notification)
            .where(Notification.receiver == receiver_id)
            .order_by(Notification.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: int, receiver_id: UUID) -> Optional[Notification]:
        """Mark a notification as read. Only allows marking notifications owned by the receiver."""
        notification = await self.get_by_id(notification_id)
        if notification and notification.receiver == receiver_id:
            notification.is_read = True
            await self.session.flush()
            await self.session.refresh(notification)
            return notification
        return None

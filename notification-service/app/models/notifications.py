from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import Enum as SQLEnum
from uuid import UUID, uuid4
from shopping_shared.databases.base_model import Base
from app.enums.notification_priority import NotificationPriority


class NotificationType(Base):
    __tablename__ = "notification_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    template_body: Mapped[str] = mapped_column(Text, nullable=False)
    priority_level: Mapped[NotificationPriority] = mapped_column(
        SQLEnum(NotificationPriority), nullable=False
    )

    # Relationship to notifications
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="notification_type"
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    group_id: Mapped[UUID] = mapped_column(ForeignKey("family_groups.id"), nullable=True, index=True)
    type_code: Mapped[str] = mapped_column(String(50), ForeignKey("notification_types.code"), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)  # Stores dynamic data
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationship to notification type
    notification_type: Mapped["NotificationType"] = relationship(
        "NotificationType", back_populates="notifications"
    )


class NotificationDeliveryLog(Base):
    __tablename__ = "notification_delivery_logs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    notification_id: Mapped[UUID] = mapped_column(ForeignKey("notifications.id"), nullable=False)
    delivery_method: Mapped[str] = mapped_column(String(20), nullable=False)  # WEBSOCKET, EMAIL, PUSH
    delivered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

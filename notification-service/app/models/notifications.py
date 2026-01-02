from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql.json import JSONB
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
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # Display name (e.g., "Expiry Warning")
    template_title: Mapped[str] = mapped_column(String(200), nullable=True)  # Template for title
    template_body: Mapped[str] = mapped_column(Text, nullable=False)
    priority_level: Mapped[NotificationPriority] = mapped_column(
        SQLEnum(NotificationPriority), default=NotificationPriority.LOW, nullable=False
    )

    # Relationship to notifications
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="notification_type"
    )
    
    # Relationship to settings
    user_settings: Mapped[list["UserNotificationSetting"]] = relationship(
        "UserNotificationSetting", back_populates="notification_type"
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Logical Reference Only (No ForeignKey to external services)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    group_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    type_code: Mapped[str] = mapped_column(String(50), ForeignKey("notification_types.code"), nullable=False)
    
    # Content Snapshot (Stored at creation time for history integrity & fast access)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    action_link: Mapped[str] = mapped_column(String(500), nullable=True)
    
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Stores dynamic data
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationship to notification type
    notification_type: Mapped["NotificationType"] = relationship(
        "NotificationType", back_populates="notifications"
    )

    # Relationship to logs
    delivery_logs: Mapped[list["NotificationDeliveryLog"]] = relationship(
        "NotificationDeliveryLog", back_populates="notification"
    )


class UserNotificationSetting(Base):
    __tablename__ = "user_notification_settings"
    
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    notification_type_code: Mapped[str] = mapped_column(String(50), ForeignKey("notification_types.code"), primary_key=True)
    
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_email: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_push: Mapped[bool] = mapped_column(Boolean, default=True)
    
    notification_type: Mapped["NotificationType"] = relationship(
        "NotificationType", back_populates="user_settings"
    )


class NotificationDeliveryLog(Base):
    __tablename__ = "notification_delivery_logs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    notification_id: Mapped[UUID] = mapped_column(ForeignKey("notifications.id"), nullable=False)
    delivery_method: Mapped[str] = mapped_column(String(20), nullable=False)  # WEBSOCKET, EMAIL, PUSH
    delivered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    notification: Mapped["Notification"] = relationship(
        "Notification", back_populates="delivery_logs"
    )
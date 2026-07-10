from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.enums.notification_priority import NotificationPriority


class NotificationCreateSchema(BaseModel):
    """Schema for creating a new notification."""
    receiver: UUID
    group_id: UUID
    group_name: str
    template_code: str
    title: str
    content: str
    raw_data: Optional[Dict[str, Any]] = None
    is_read: bool = False


class NotificationUpdateSchema(BaseModel):
    """Schema for updating an existing notification."""
    is_read: Optional[bool] = None
    payload: Optional[Dict[str, Any]] = None


class NotificationTypeCreateSchema(BaseModel):
    """Schema for creating a new notification type."""
    code: str = Field(..., max_length=50)
    template_body: str
    priority_level: NotificationPriority


class NotificationTypeUpdateSchema(BaseModel):
    """Schema for updating an existing notification type."""
    template_body: Optional[str] = None
    priority_level: Optional[NotificationPriority] = None


class NotificationResponseSchema(BaseModel):
    """Schema for notification response."""
    id: int
    group_id: UUID
    group_name: str
    receiver: UUID
    created_at: datetime
    template_code: str
    raw_data: Optional[Dict[str, Any]] = None
    is_read: bool
    title: str
    content: str

    class Config:
        from_attributes = True


class NotificationDeliveryLogCreateSchema(BaseModel):
    """Schema for creating a notification delivery log."""
    notification_id: UUID
    delivery_method: str
    success: bool
    error_message: Optional[str] = None
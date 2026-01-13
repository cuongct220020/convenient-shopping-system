from sqlalchemy import Integer, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from uuid import UUID
from datetime import datetime
from shopping_shared.databases.base_model import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    group_name: Mapped[str] = mapped_column(String(255), nullable=False)
    receiver: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    template_code: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
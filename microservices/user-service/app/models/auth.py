from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shopping_shared.databases.base_model import Base


class AuthRefreshToken(Base):
    __tablename__ = "auth_refresh_tokens"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
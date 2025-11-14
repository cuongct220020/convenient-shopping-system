from typing import List, Optional
from uuid import UUID

from sqlalchemy import String, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.shopping_shared.databases.base_model import Base

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tag_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tag_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # --- Relationships ---
    # N-M to User (via user_tags table)
    users: Mapped[List["User"]] = relationship(
        secondary="user_tags", back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag {self.tag_name}>"


class UserTag(Base):
    __tablename__ = "user_tags"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=True
    )
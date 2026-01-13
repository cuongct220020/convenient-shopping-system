# user-service/app/models/user_tag.py
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import String, BigInteger, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shopping_shared.databases.base_model import Base


class Tag(Base):
    """
    Tag master table - stores all available tags.
    Tags are pre-populated from Enums (AgeTag, MedicalConditionTag, etc.)

    Structure:
        - tag_value: 4-digit code (e.g., '0212' for DIABETES)
        - tag_category: age, medical, allergy, diet, taste
        - tag_name: Human-readable name (e.g., 'DIABETES')
        - description: Optional description
    """
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    tag_value: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index=True,
        comment="4-digit tag code (e.g., '0212')"
    )

    tag_category: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Category: age, medical, allergy, diet, taste"
    )

    tag_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Enum name (e.g., 'DIABETES')"
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Human-readable description"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When this tag was defined in the system"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="When this tag definition was last updated"
    )

    # Relationships - Many-to-Many with User via user_tags
    users: Mapped[List["User"]] = relationship(
        secondary="user_tags",
        back_populates="tags",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Tag({self.tag_value}: {self.tag_name})>"


class UserTag(Base):
    __tablename__ = "user_tags"

    # Composite Primary Key
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )

    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )

    # Timestamp
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<UserTag(user_id={self.user_id}, tag_id={self.tag_id})>"

    # Add composite index for common queries
    __table_args__ = (
        # Composite index for getting user tags: WHERE user_id = ? AND tag_id = ?
        # Also efficient for listing tags by user: WHERE user_id = ?
        Index('ix_user_tags_user_id_tag_id', 'user_id', 'tag_id'),
    )
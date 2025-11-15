from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum

from app.models import User
from shopping_shared.databases.base_model import Base
from app.constants import GroupRole


class FamilyGroup(Base):
    __tablename__ = "family_groups"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    group_name: Mapped[str] = mapped_column(String(255), nullable=False)
    group_avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # --- Relationships ---
    creator: Mapped[Optional["User"]] = relationship(
        foreign_keys=[created_by_user_id], back_populates="created_groups"
    )

    # N-M tới User (qua bảng group_memberships)
    members: Mapped[List["User"]] = relationship(
        secondary="group_memberships", back_populates="groups"
    )

    def __repr__(self) -> str:
        return f"<FamilyGroup {self.group_name}>"


class GroupMembership(Base):
    __tablename__ = "group_memberships"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("family_groups.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[GroupRole] = mapped_column(
        SQLEnum(GroupRole), nullable=False, default=GroupRole.MEMBER
    )

    added_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    jointed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
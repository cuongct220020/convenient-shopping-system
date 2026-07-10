# user-service/app/models/family_group.py
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum

from shopping_shared.databases.base_model import Base
from app.enums import GroupRole


class FamilyGroup(Base):
    __tablename__ = "family_groups"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    group_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    group_avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # --- Relationships ---
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="created_groups"
    )

    # N-M to User via group_memberships table
    members: Mapped[List["User"]] = relationship(
        "User",
        secondary="group_memberships",
        primaryjoin="FamilyGroup.id == GroupMembership.group_id",
        secondaryjoin="GroupMembership.user_id == User.id",
        back_populates="groups",
        viewonly=True
    )

    # Additional relationship
    group_memberships: Mapped[List["GroupMembership"]] = relationship(
        "GroupMembership",
        foreign_keys="GroupMembership.group_id",
        back_populates="group",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<FamilyGroup {self.group_name}>"


class GroupMembership(Base):
    __tablename__ = "group_memberships"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("family_groups.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    role: Mapped[GroupRole] = mapped_column(
        SQLEnum(GroupRole), nullable=False, default=GroupRole.MEMBER, index=True
    )

    added_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        comment="ID of the user who added the member to the group"
    )

    jointed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys="GroupMembership.user_id",
        back_populates="group_memberships"
    )
    group: Mapped["FamilyGroup"] = relationship(
        "FamilyGroup",
        foreign_keys="GroupMembership.group_id",
        back_populates="group_memberships"
    )
    added_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys="GroupMembership.added_by_user_id",
        back_populates="added_group_memberships"
    )

    # Add composite indexes for common queries
    __table_args__ = (
        # Composite index for checking membership: WHERE user_id = ? AND group_id = ?
        # This is more efficient than individual indexes when querying both fields
        Index('ix_group_memberships_user_id_group_id', 'user_id', 'group_id'),
        Index('ix_group_memberships_group_id_user_id', 'group_id', 'user_id'),
    )
# user-service/app/models/user.py
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum

from app.enums import SystemRole
from shopping_shared.databases.base_model import Base

if TYPE_CHECKING:
    from app.models.family_group import FamilyGroup
    from app.models.user_profile import UserIdentityProfile, UserHealthProfile
    from app.models.user_tag import Tag


class User(Base):
    """
    User model representing system users.

    Handles authentication, authorization and user profile data.
    """
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    system_role: Mapped[SystemRole] = mapped_column(
        SQLEnum(SystemRole), nullable=False, default=SystemRole.USER
    )

    phone_num: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # --- Relationships ---
    # 1-1 to UserIdentityProfile
    identity_profile: Mapped[Optional["UserIdentityProfile"]] = relationship(
        "UserIdentityProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )

    # 1-1 to UserHealthProfile
    health_profile: Mapped[Optional["UserHealthProfile"]] = relationship(
        "UserHealthProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )

    # N-M to Tag (via user_tags table)
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="user_tags",
        back_populates="users"
    )

    # N-M to FamilyGroup (via group_memberships table)
    groups: Mapped[List["FamilyGroup"]] = relationship(
        "FamilyGroup",
        secondary="group_memberships",
        primaryjoin="User.id == GroupMembership.user_id",
        secondaryjoin="GroupMembership.group_id == FamilyGroup.id",
        back_populates="members",
        viewonly=True
    )

    # 1-N to FamilyGroup (as creator)
    created_groups: Mapped[List["FamilyGroup"]] = relationship(
        "FamilyGroup",
        foreign_keys="FamilyGroup.created_by_user_id",
        back_populates="creator"
    )

    # Additional relationships for GroupMembership
    group_memberships: Mapped[List["GroupMembership"]] = relationship(
        "GroupMembership",
        foreign_keys="GroupMembership.user_id",
        back_populates="user"
    )
    added_group_memberships: Mapped[List["GroupMembership"]] = relationship(
        "GroupMembership",
        foreign_keys="GroupMembership.added_by_user_id",
        back_populates="added_by_user"
    )

    def __repr__(self) -> str:
        return f"<User username={self.username}, email={self.email}>"
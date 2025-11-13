from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum

from .base import Base
from .constants import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    system_role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), nullable=False, default=UserRole.FAMILY_MEMBER
    )

    phone_num: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # --- Relationships ---

    # 1-1 tới UserIdentityProfile
    identity_profile: Mapped["UserIdentityProfile"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # 1-1 tới UserHealthProfile
    health_profile: Mapped["UserHealthProfile"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # 1-N tới AuthRefreshToken
    refresh_tokens: Mapped[List["AuthRefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # N-M tới Tag (qua bảng user_tags)
    tags: Mapped[List["Tag"]] = relationship(
        secondary="user_tags", back_populates="users"
    )

    # N-M tới FamilyGroup (qua bảng group_memberships)
    groups: Mapped[List["FamilyGroup"]] = relationship(
        secondary="group_memberships", back_populates="members"
    )

    # 1-N tới FamilyGroup (với tư cách người tạo)
    created_groups: Mapped[List["FamilyGroup"]] = relationship(
        foreign_keys="FamilyGroup.created_by_user_id", back_populates="creator"
    )

    # 1-N tới FamilyGroup (với tư cách headchef)
    headchef_of_groups: Mapped[List["FamilyGroup"]] = relationship(
        foreign_keys="FamilyGroup.headchef_user_id", back_populates="headchef"
    )

    def __repr__(self) -> str:
        return f"<User user_name={self.user_name}, email={self.email}>"
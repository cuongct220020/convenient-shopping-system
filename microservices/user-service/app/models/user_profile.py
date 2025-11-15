from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    String, Date, DateTime, ForeignKey, SmallInteger, Numeric, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum

from app.models import Address, User
from shopping_shared.databases.base_model import Base
from app.constants import UserGender, ActivityLevel, HealthCondition, HealthGoal


class UserIdentityProfile(Base):
    __tablename__ = "user_identity_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    gender: Mapped[UserGender] = mapped_column(
        SQLEnum(UserGender), nullable=False, default=UserGender.OTHER
    )
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    address_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("addresses.id"), nullable=True
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # --- Relationships ---
    # 1-1 to User (reverse 1-1 relationship)
    user: Mapped["User"] = relationship(back_populates="identity_profile")

    # N-1 to Address
    address: Mapped[Optional["Address"]] = relationship(back_populates="user_profiles")


class UserHealthProfile(Base):
    __tablename__ = "user_health_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    height_cm: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)

    activity_level: Mapped[Optional[ActivityLevel]] = mapped_column(
        SQLEnum(ActivityLevel), nullable=True, default=ActivityLevel.MODERATE
    )
    curr_condition: Mapped[Optional[HealthCondition]] = mapped_column(
        SQLEnum(HealthCondition), nullable=True, default=HealthCondition.NORMAL
    )
    health_goal: Mapped[Optional[HealthGoal]] = mapped_column(
        SQLEnum(HealthGoal), nullable=True, default=HealthGoal.MAINTAIN
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # --- Relationships ---
    # 1-1 to User (reverse 1-1 relationship)
    user: Mapped["User"] = relationship(back_populates="health_profile")
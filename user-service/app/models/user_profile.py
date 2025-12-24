# user-service/app/models/user_profile.py
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, SmallInteger, Numeric, func
from sqlalchemy.sql.sqltypes import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import UserGender, ActivityLevel, HealthCondition, HealthGoal
from shopping_shared.databases.base_model import Base

class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ward: Mapped[str] = mapped_column(String(100), nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)

    # --- Relationships ---
    user_profiles: Mapped[List["UserIdentityProfile"]] = relationship(back_populates="address")

    def __repr__(self) -> str:
        return f"<Address id={self.id}, {self.district}, {self.city}>"


class UserIdentityProfile(Base):
    __tablename__ = "user_identity_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
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
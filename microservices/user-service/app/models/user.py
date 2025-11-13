# app/models/user_constants.py
from datetime import datetime, UTC
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum
from app.constants.user_role_constants import UserRole

from .base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.FAMILY_MEMBER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    last_login: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=True
    )
    active_refresh_jti: Mapped[str] = mapped_column(String, nullable=True, index=True)

    def __repr__(self) -> str:
        return f"<User username={self.username}, role={self.user_role}>"


class UserIdentityProfile(Base):
    __tablename__ = "user_identity_profiles"

    pass

class UserHealthProfile(Base):
    __tablename__ = "user_health_profiles"

    pass


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ward: Mapped[str] = mapped_column(String(100), nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)


    def __repr__(self) -> str:
        return f"<Address id={self.address_id}, {self.district}, {self.province_city}>"
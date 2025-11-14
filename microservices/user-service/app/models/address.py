from typing import List
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.shopping_shared.databases.base_model import Base

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

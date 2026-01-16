import uuid
from datetime import date
from sqlalchemy import Integer, String, Date, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from enums.meal_type import MealType
from enums.meal_status import MealStatus


class Meal(Base):
    __tablename__ = "meals"

    meal_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType), nullable=False, index=True)
    meal_status: Mapped[MealStatus] = mapped_column(Enum(MealStatus), nullable=False, default=MealStatus.CREATED, index=True)

    __table_args__ = (
        UniqueConstraint("date", "meal_type", "group_id", name="unique_meal_date_group_type"),
    )

    recipe_list: Mapped[list["RecipeList"]] = relationship(
        back_populates="meal",
        cascade="all, delete-orphan"
    )


class RecipeList(Base):
    __tablename__ = "recipe_lists"

    recipe_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.meal_id"), primary_key=True, index=True)
    recipe_name: Mapped[str] = mapped_column(String, nullable=False)
    servings: Mapped[int] = mapped_column(Integer, nullable=False)

    meal: Mapped["Meal"] = relationship(
        back_populates="recipe_list",
        foreign_keys=[meal_id]
    )

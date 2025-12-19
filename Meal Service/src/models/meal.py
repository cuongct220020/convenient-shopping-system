from datetime import date
from sqlalchemy import Integer, Float, String, Date, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from enums.meal_type import MealType


class Meal(Base):
    __tablename__ = "meals"

    meal_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType), nullable=False)

    __table_args__ = (
        UniqueConstraint("date", "meal_type", name="unique_meal_date_type"),
    )

    recipe_list: Mapped[list["RecipeList"]] = relationship(
        back_populates="meal",
        cascade="all, delete-orphan"
    )
    storable_unit_list: Mapped[list["StorableUnitList"]] = relationship(
        back_populates="meal",
        cascade="all, delete-orphan"
    )


class RecipeList(Base):
    __tablename__ = "recipe_lists"

    recipe_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.meal_id"), primary_key=True)
    recipe_name: Mapped[str] = mapped_column(String, nullable=False)
    servings: Mapped[int] = mapped_column(Integer, nullable=False)

    meal: Mapped["Meal"] = relationship(
        back_populates="recipe_list",
        foreign_keys=[meal_id]
    )


class StorableUnitList(Base):
    __tablename__ = "storable_unit_lists"

    unit_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.meal_id"), primary_key=True)
    unit_name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)

    meal: Mapped["Meal"] = relationship(
        back_populates="storable_unit_list",
        foreign_keys=[meal_id]
    )


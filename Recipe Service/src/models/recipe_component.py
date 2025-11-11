from sqlalchemy import Integer, String, Float, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enums.c_measurement_unit import CMeasurementUnit
from enums.uc_measurement_unit import UCMeasurementUnit
from core.database import Base

class RecipeComponent(Base):
    __tablename__ = "recipe_components"

    component_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    component_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String, nullable=False, index=True)

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "component",
    }


class Ingredient(RecipeComponent):
    __tablename__ = "ingredients"

    component_id: Mapped[int] = mapped_column(ForeignKey("recipe_components.component_id"), primary_key=True)
    estimated_shelf_life: Mapped[int] = mapped_column(Integer, nullable=True)
    protein: Mapped[float] = mapped_column(Float, nullable=True)
    fat: Mapped[float] = mapped_column(Float, nullable=True)
    carb: Mapped[float] = mapped_column(Float, nullable=True)
    fiber: Mapped[float] = mapped_column(Float, nullable=True)
    calories: Mapped[float] = mapped_column(Float, nullable=True)
    estimated_price: Mapped[int] = mapped_column(Integer, nullable=True)
    ingredient_tag_list: Mapped[list[int]] = mapped_column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "ingredient",
        "with_polymorphic": "*"
    }


class CountableIngredient(Ingredient):
    __tablename__ = "countable_ingredients"

    component_id: Mapped[int] = mapped_column(ForeignKey("ingredients.component_id"), primary_key=True)
    c_measurement_unit: Mapped[CMeasurementUnit] = mapped_column(Enum(CMeasurementUnit))

    __mapper_args__ = {
        "polymorphic_identity": "countable_ingredient"
    }


class UncountableIngredient(Ingredient):
    __tablename__ = "uncountable_ingredients"

    component_id: Mapped[int] = mapped_column(ForeignKey("ingredients.component_id"), primary_key=True)
    uc_measurement_unit: Mapped[UCMeasurementUnit] = mapped_column(Enum(UCMeasurementUnit))

    __mapper_args__ = {
        "polymorphic_identity": "uncountable_ingredient",
    }


class BulkIngredient(UncountableIngredient):
    __tablename__ = "bulk_ingredients"

    component_id: Mapped[int] = mapped_column(ForeignKey("uncountable_ingredients.component_id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "bulk_ingredient"
    }


class ComponentList(Base):
    __tablename__ = "component_lists"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.component_id"),primary_key=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("recipe_components.component_id"),primary_key=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=True)

    recipe: Mapped["Recipe"] = relationship(
        back_populates="component_list",
        foreign_keys=[recipe_id]
    )
    component: Mapped["RecipeComponent"] = relationship(
        foreign_keys=[component_id]
    )


class Recipe(RecipeComponent):
    __tablename__ = "recipes"

    component_id: Mapped[int] = mapped_column(ForeignKey("recipe_components.component_id"),primary_key=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    prep_time: Mapped[int] = mapped_column(Integer, nullable=True)
    cook_time: Mapped[int] = mapped_column(Integer, nullable=True)
    default_servings: Mapped[int] = mapped_column(Integer, default=1)
    description: Mapped[str] = mapped_column(String, nullable=True)
    instructions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    component_list: Mapped[list["ComponentList"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": "recipe"
    }

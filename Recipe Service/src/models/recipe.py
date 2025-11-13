from enums.measurement_unit import MeasurementUnit
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from core.database import Base

class RecipeCountableIngredient(Base):
    __tablename__ = "recipe_countable_ingredient"

    recipe_id = Column(Integer, ForeignKey("recipe.recipe_id"), primary_key=True)
    ingredient_id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)

class RecipeUncountableIngredient(Base):
    __tablename__ = "recipe_uncountable_ingredient"

    recipe_id = Column(Integer, ForeignKey("recipe.recipe_id"), primary_key=True)
    ingredient_id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    unit = Column(Enum(MeasurementUnit), nullable=False)

class Recipe(Base):
    __tablename__ = "recipe"

    recipe_id = Column(Integer, primary_key=True)
    recipe_name = Column(String, nullable=False, unique=True)
    default_servings = Column(Integer, nullable=False)
    instructions = Column(Text, nullable=False)

    countable_ingredients = relationship("RecipeCountableIngredient", backref="recipe", cascade="all, delete-orphan")

    uncountable_ingredients = relationship("RecipeUncountableIngredient", backref="recipe", cascade="all, delete-orphan")

    @property
    def countable_ingredient_list(self):
        return [
            {
                "ingredient_id": ci.ingredient_id,
                "quantity": ci.quantity
            }
            for ci in self.countable_ingredients
        ]

    @property
    def uncountable_ingredient_list(self):
        return [
            {
                "ingredient_id": ui.ingredient_id,
                "quantity": ui.quantity,
                "unit": ui.unit.value
            }
            for ui in self.uncountable_ingredients
        ]



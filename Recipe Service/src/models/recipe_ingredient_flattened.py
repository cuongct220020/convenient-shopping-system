from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, JSON
from core.database import Base

class RecipeIngredientFlattened(Base):
    __tablename__ = "recipe_ingredient_flattened"
    __table_args__ = {'info': {'is_view': True}}

    recipe_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_name: Mapped[str] = mapped_column(String, nullable=False)
    all_ingredients: Mapped[list[dict]] = mapped_column(JSON, nullable=False)

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, select, String
from typing import Sequence, Optional
from .crud_base import CRUDBase
from models.recipe_component import Recipe, ComponentList
from models.recipe_ingredient_flattened import RecipeIngredientFlattened
from schemas.recipe import RecipeCreate, RecipeUpdate

"""
    Method for RecipeDetailResponse
"""

class RecipeCRUD(CRUDBase[Recipe, RecipeCreate, RecipeUpdate]):
    def get_detail(self, db: Session, id: int) -> Optional[Recipe]:
        return db.execute(
            select(Recipe)
            .options(
                selectinload(Recipe.component_list)
                .selectinload(ComponentList.component)
            )
            .where(Recipe.component_id == id)
        ).scalars().first()

    def get_flattened(self, db: Session, id: int) -> Optional[RecipeIngredientFlattened]:
        return db.get(RecipeIngredientFlattened, id)

    def search(self, db: Session, keyword: str, limit: int = 10)  -> Sequence[Recipe]:
        return db.execute(
            select(Recipe)
            .where(
                Recipe.component_id.in_(
                    select(RecipeIngredientFlattened.recipe_id)
                    .where(
                        or_(
                            RecipeIngredientFlattened.recipe_name.ilike(f"%{keyword}%"),
                            RecipeIngredientFlattened.all_ingredients.cast(String).ilike(f"%{keyword}%")
                        )
                    )
                )
            )
            .limit(limit)
        ).scalars().all()

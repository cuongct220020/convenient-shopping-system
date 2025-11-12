from sqlalchemy.orm import Session, selectinload
from .crud_base import CRUDBase
from models.recipe_component import Recipe, ComponentList
from models.recipe_ingredient_flattened import RecipeIngredientFlattened
from schemas.recipe import RecipeCreate, RecipeUpdate

"""
    Method for RecipeDetailResponse
"""

class RecipeCRUD(CRUDBase[Recipe, RecipeCreate, RecipeUpdate]):
    def get_detail(self, db: Session, id: int):
        return (
            db.query(Recipe)
            .options(
                selectinload(Recipe.component_list)
                .selectinload(ComponentList.component)
            )
            .filter(Recipe.component_id == id)
            .first()
        )

    def get_flattened(self, db: Session, id: int):
        return db.get(RecipeIngredientFlattened, id)
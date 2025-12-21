from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, select, String
from typing import Sequence
from schemas.recipe_flattened_schemas import RecipeFlattenedResponse
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.recipe_component import Recipe, ComponentList
from models.recipe_ingredient_flattened import RecipeIngredientFlattened
from schemas.recipe_schemas import RecipeCreate, RecipeUpdate
from utils.custom_mapping import recipe_flattened_aggregated_mapping

"""
    Method for RecipeDetailResponse
"""

class RecipeCRUD(CRUDBase[Recipe, RecipeCreate, RecipeUpdate]):
    def get_detail(self, db: Session, ids: list[int]) -> Sequence[Recipe]:
        return db.execute(
            select(Recipe)
            .options(
                selectinload(Recipe.component_list)
                .selectinload(ComponentList.component),
                selectinload(Recipe.component_list)
                .selectinload(ComponentList.component.of_type(Recipe))
                .selectinload(Recipe.component_list)
                .selectinload(ComponentList.component),
            )
            .where(Recipe.component_id.in_(ids))
        ).scalars().all()

    def get_flattened(self, db: Session, ids: list[int]) -> Sequence[RecipeFlattenedResponse]:
        db_recipes = self.get_detail(db, ids)
        if len(db_recipes) != len(ids):
            missing_ids = set(ids) - {r.component_id for r in db_recipes}
            raise HTTPException(status_code=404, detail=f"Recipes with ids={missing_ids} not found")

        results = []
        recipe_map = {r.component_id: r for r in db_recipes}
        for id in ids:
            recipe = recipe_map[id]
            results.append(RecipeFlattenedResponse(
                recipe_id=id,
                all_ingredients=recipe_flattened_aggregated_mapping(recipe)
            ))
        return results

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

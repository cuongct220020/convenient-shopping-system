from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, select, String
from typing import Sequence, Optional
import httpx
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.recipe_component import Recipe, ComponentList
from models.recipe_ingredient_flattened import RecipeIngredientFlattened
from schemas.recipe_schemas import RecipeCreate, RecipeUpdate
from schemas.recipe_flattened_schemas import RecipeQuantityInput
from schemas.ingredient_schemas import IngredientResponse
from utils.custom_mapping import recipes_flattened_aggregated_mapping

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

    async def get_flattened(
        self,
        recipes_with_quantity: list[RecipeQuantityInput],
        group_id: Optional[int],
        check_existence: bool,
        db: Session
    ) -> list[tuple[float, IngredientResponse, Optional[list]]]:
        recipe_ids = [r.recipe_id for r in recipes_with_quantity]
        db_recipes = self.get_detail(db, recipe_ids)

        if len(db_recipes) != len(recipe_ids):
            missing_ids = set(recipe_ids) - {r.component_id for r in db_recipes}
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Recipes with ids={missing_ids} not found")

        recipe_map = {r.component_id: r for r in db_recipes}
        db_recipes_with_quantity = [(r.quantity, recipe_map[r.recipe_id]) for r in recipes_with_quantity]
        aggregated_ingredients = recipes_flattened_aggregated_mapping(db_recipes_with_quantity)

        result: list[tuple[float, IngredientResponse, Optional[list]]] = []
        if check_existence:
            component_names = [ingredient.component_name for quantity, ingredient in aggregated_ingredients.values()]
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:8002/v1/storable_units/filter",
                    params={
                        "group_id": group_id,
                        "unit_name": component_names
                    }
                )
                response.raise_for_status()
                data = response.json().get("data", [])
                units_name_map: dict[str, list] = {}
                for item in data:
                    units_name_map.setdefault(item["unit_name"], []).append(item)
                for quantity, ingredient in aggregated_ingredients.all_ingredients.values():
                    result.append((quantity, ingredient, units_name_map.get(ingredient.component_name, [])))
        else:
            for quantity, ingredient in aggregated_ingredients.all_ingredients.values():
                result.append((quantity, ingredient, None))

        return result

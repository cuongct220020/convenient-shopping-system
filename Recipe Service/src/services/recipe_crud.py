from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, select, String
from typing import Sequence, Optional
import httpx
import asyncio
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.recipe_component import Recipe, ComponentList
from models.recipe_ingredient_flattened import RecipeIngredientFlattened
from schemas.recipe_schemas import RecipeCreate, RecipeUpdate
from schemas.recipe_flattened_schemas import RecipeQuantityInput
from schemas.ingredient_schemas import IngredientResponse
from utils.custom_mapping import recipes_flattened_aggregated_mapping
from messaging.producers.recipe_producer import publish_recipe_event
from core.es import get_es

"""
    Method for RecipeDetailResponse
"""

class RecipeCRUD(CRUDBase[Recipe, RecipeCreate, RecipeUpdate]):
    def create(self, db: Session, obj_in: RecipeCreate) -> Recipe:
        db_obj = super().create(db, obj_in)
        db.refresh(db_obj)
        if db_obj.component_list:
            for cl in db_obj.component_list:
                db.refresh(cl)
                if cl.component:
                    db.refresh(cl.component)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(publish_recipe_event("recipe_created", db_obj))
        else:
            loop.run_until_complete(publish_recipe_event("recipe_created", db_obj))
        return db_obj

    def update(self, db: Session, obj_in: RecipeUpdate, db_obj: Recipe) -> Recipe:
        result = super().update(db, obj_in, db_obj)
        db.refresh(result)
        if result.component_list:
            for cl in result.component_list:
                db.refresh(cl)
                if cl.component:
                    db.refresh(cl.component)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(publish_recipe_event("recipe_updated", result))
        else:
            loop.run_until_complete(publish_recipe_event("recipe_updated", result))
        return result

    def delete(self, db: Session, id: int) -> Recipe:
        obj = db.get(Recipe, id)
        if obj is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Recipe with id={id} not found")
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(publish_recipe_event("recipe_deleted", id))
        else:
            loop.run_until_complete(publish_recipe_event("recipe_deleted", id))
        return super().delete(db, id)

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

    async def search(self, db: Session, keyword: str, limit: int = 10) -> Sequence[Recipe]:
        es = get_es()
        query = {
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["component_name", "component_list"]
                }
            },
            "size": 1000
        }
        response = await es.search(index="recipes", body=query)
        component_ids = [int(hit["_id"]) for hit in response["hits"]["hits"]]
        
        if not component_ids:
            return []
        
        return db.execute(
            select(Recipe)
            .where(Recipe.component_id.in_(component_ids))
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

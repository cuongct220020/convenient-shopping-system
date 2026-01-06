from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, or_, cast
from sqlalchemy.dialects.postgresql import JSONB
from typing import Sequence, Optional
from shopping_shared.crud.crud_base import CRUDBase
from models.recipe_component import Recipe, ComponentList
from models.component_existence import ComponentExistence
from schemas.recipe_schemas import RecipeCreate, RecipeUpdate
from schemas.recipe_flattened_schemas import RecipeQuantityInput
from schemas.ingredient_schemas import IngredientResponse
from utils.custom_mapping import recipes_flattened_aggregated_mapping

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
        return db_obj

    def update(self, db: Session, obj_in: RecipeUpdate, db_obj: Recipe) -> Recipe:
        result = super().update(db, obj_in, db_obj)
        db.refresh(result)
        if result.component_list:
            for cl in result.component_list:
                db.refresh(cl)
                if cl.component:
                    db.refresh(cl.component)
        return result

    def delete(self, db: Session, id: int) -> Recipe:
        obj = db.get(Recipe, id)
        if obj is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Recipe with id={id} not found")
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

    def search(self, db: Session, keyword: str, cursor: Optional[int] = None, limit: int = 100) -> Sequence[Recipe]:
        keyword_lower = keyword.lower()
        stmt = select(Recipe).where(
            or_(
                Recipe.component_name.ilike(f"%{keyword}%"),
                Recipe.keywords.contains([keyword_lower])
            )
        )
        if cursor is not None:
            stmt = stmt.where(Recipe.component_id < cursor)
        stmt = stmt.order_by(Recipe.component_id.desc()).limit(limit)
        return db.execute(stmt).scalars().all()

    async def get_flattened(
        self,
        recipes_with_quantity: list[RecipeQuantityInput],
        group_id: Optional[int],
        check_existence: bool,
        db: Session
    ) -> list[tuple[float, IngredientResponse, Optional[bool]]]:
        recipe_ids = [r.recipe_id for r in recipes_with_quantity]
        db_recipes = self.get_detail(db, recipe_ids)

        if len(db_recipes) != len(recipe_ids):
            missing_ids = set(recipe_ids) - {r.component_id for r in db_recipes}
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Recipes with ids={missing_ids} not found")

        recipe_map = {r.component_id: r for r in db_recipes}
        db_recipes_with_quantity = [(r.quantity, recipe_map[r.recipe_id]) for r in recipes_with_quantity]
        aggregated_ingredients = recipes_flattened_aggregated_mapping(db_recipes_with_quantity)

        result: list[tuple[float, IngredientResponse, Optional[bool]]] = []
        if check_existence:
            component_existence = db.query(ComponentExistence).filter(ComponentExistence.group_id == group_id).first()
            component_name_list = component_existence.component_name_list if component_existence else []

            for quantity, ingredient in aggregated_ingredients.all_ingredients.values():
                available = ingredient.component_name in component_name_list
                result.append((quantity, ingredient, available))
        else:
            for quantity, ingredient in aggregated_ingredients.all_ingredients.values():
                result.append((quantity, ingredient, None))

        return result

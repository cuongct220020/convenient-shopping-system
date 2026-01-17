import uuid
import json
from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, or_
from typing import Sequence, Optional
from shopping_shared.crud.crud_base import CRUDBase
from models.recipe_component import Recipe, ComponentList, RecipesFlattened
from models.component_existence import ComponentExistence
from schemas.recipe_schemas import RecipeCreate, RecipeUpdate
from schemas.recipe_flattened_schemas import RecipeQuantityInput
from schemas.ingredient_schemas import IngredientResponse
from utils.custom_mapping import recipes_flattened_aggregated_mapping

"""
    Method for RecipeDetailResponse
"""

class RecipeCRUD(CRUDBase[Recipe, RecipeCreate, RecipeUpdate]):
    def _update_recipes_flattened(self, db: Session, recipe: Recipe) -> None:
        try:
            aggregated = recipes_flattened_aggregated_mapping([(recipe.default_servings, recipe)])

            all_ingredients_list = []
            for component_id, (quantity, ingredient) in aggregated.all_ingredients.items():
                ingredient_dict = ingredient.model_dump(mode='json')
                all_ingredients_list.append({
                    'component_id': component_id,
                    'quantity': quantity,
                    'ingredient': ingredient_dict
                })

            recipes_flattened = db.query(RecipesFlattened).filter(
                RecipesFlattened.component_id == recipe.component_id
            ).first()
            
            if recipes_flattened:
                recipes_flattened.component_name = recipe.component_name
                recipes_flattened.all_ingredients = all_ingredients_list
            else:
                recipes_flattened = RecipesFlattened(
                    component_id=recipe.component_id,
                    component_name=recipe.component_name,
                    all_ingredients=all_ingredients_list
                )
                db.add(recipes_flattened)
            
            db.flush()
        except Exception as e:
            pass

    def create(self, db: Session, obj_in: RecipeCreate) -> Recipe:
        try:
            db_obj = super().create(db, obj_in)
            db.refresh(db_obj)
            if db_obj.component_list:
                for cl in db_obj.component_list:
                    db.refresh(cl)
                    if cl.component:
                        db.refresh(cl.component)

            self._update_recipes_flattened(db, db_obj)
            
            return db_obj
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error creating recipe")

    def update(self, db: Session, obj_in: RecipeUpdate, db_obj: Recipe) -> Recipe:
        try:
            result = super().update(db, obj_in, db_obj)
            db.refresh(result)
            if result.component_list:
                for cl in result.component_list:
                    db.refresh(cl)
                    if cl.component:
                        db.refresh(cl.component)

            self._update_recipes_flattened(db, result)
            
            return result
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error updating recipe")


    def get_detail(self, db: Session, ids: list[int]) -> Sequence[Recipe]:
        try:
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
        except Exception as e:
            raise

    def search(self, db: Session, keyword: str, cursor: Optional[int] = None, limit: int = 100) -> Sequence[Recipe]:
        keyword_lower = keyword.lower()
        stmt = (
            select(Recipe)
            .options(selectinload(Recipe.component_list))
            .where(
                or_(
                    Recipe.component_name.ilike(f"%{keyword}%"),
                    Recipe.keywords.contains([keyword_lower])
                )
            )
        )
        if cursor is not None:
            stmt = stmt.where(Recipe.component_id < cursor)
        stmt = stmt.order_by(Recipe.component_id.desc()).limit(limit)
        return db.execute(stmt).scalars().all()

    def get_flattened(
        self,
        recipes_with_quantity: list[RecipeQuantityInput],
        group_id: Optional[uuid.UUID],
        check_existence: bool,
        db: Session
    ) -> list[tuple[float, dict, Optional[bool]]]:
        try:
            recipe_ids = [r.recipe_id for r in recipes_with_quantity]

            recipes_flattened_records = db.query(RecipesFlattened).filter(
                RecipesFlattened.component_id.in_(recipe_ids)
            ).all()
            recipes_map = {r.component_id: r for r in db.query(Recipe).filter(Recipe.component_id.in_(recipe_ids)).all()}

            if len(recipes_flattened_records) != len(recipe_ids):
                found_ids = {rf.component_id for rf in recipes_flattened_records}
                missing_ids = set(recipe_ids) - found_ids
                raise HTTPException(status_code=404, detail=f"Recipes with ids={missing_ids} not found in recipes_flattened")

            aggregated: dict[int, tuple[float, dict]] = {}
            
            for recipe_input in recipes_with_quantity:
                recipe_id = recipe_input.recipe_id
                requested_quantity = recipe_input.quantity
                
                recipes_flattened = next((rf for rf in recipes_flattened_records if rf.component_id == recipe_id), None)
                recipe = recipes_map.get(recipe_id)
                
                if not recipes_flattened:
                    continue
                if not recipe:
                    continue

                default_servings = recipe.default_servings
                scale_factor = requested_quantity / default_servings if default_servings > 0 else 1.0

                for ingredient_data in recipes_flattened.all_ingredients:
                    component_id = ingredient_data['component_id']
                    base_quantity = ingredient_data['quantity']
                    scaled_quantity = base_quantity * scale_factor
                    ingredient_dict = ingredient_data['ingredient']

                    if component_id in aggregated:
                        existing_quantity, _ = aggregated[component_id]
                        aggregated[component_id] = (existing_quantity + scaled_quantity, ingredient_dict)
                    else:
                        aggregated[component_id] = (scaled_quantity, ingredient_dict)

            result: list[tuple[float, dict, Optional[bool]]] = []
            if check_existence:
                component_existence = db.query(ComponentExistence).filter(ComponentExistence.group_id == group_id).first()
                component_name_list = component_existence.component_name_list if component_existence else []

                for quantity, ingredient_dict in aggregated.values():
                    available = ingredient_dict['component_name'] in component_name_list
                    result.append((quantity, ingredient_dict, available))
            else:
                for quantity, ingredient_dict in aggregated.values():
                    result.append((quantity, ingredient_dict, None))

            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error processing flattened recipes")

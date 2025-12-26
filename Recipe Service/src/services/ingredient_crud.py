from sqlalchemy.orm import Session, with_polymorphic
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from shared.shopping_shared.crud.crud_base import CRUDBase
from typing import Optional, Sequence
from fastapi import HTTPException
from models.recipe_component import Ingredient, CountableIngredient, UncountableIngredient
from schemas.ingredient_schemas import IngredientCreate, IngredientUpdate
from enums.category import Category
from messaging.producers.ingredient_producer import publish_ingredient_event
from core.es import get_es
import asyncio

class IngredientCRUD(CRUDBase[Ingredient, IngredientCreate, IngredientUpdate]):
    model_map = {
        "countable_ingredient": CountableIngredient,
        "uncountable_ingredient": UncountableIngredient,
    }

    def create(self, db: Session, obj_in: IngredientCreate) -> Ingredient:
        model_class = self.model_map[obj_in.type]
        if not model_class:
            raise ValueError(f"Unknown ingredient type: {obj_in.type}")
        db_obj = model_class(**obj_in.model_dump())
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(publish_ingredient_event("ingredient_created", db_obj))
            else:
                loop.run_until_complete(publish_ingredient_event("ingredient_created", db_obj))
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
        return db_obj

    def update(self, db: Session, obj_in: IngredientUpdate, db_obj: Ingredient) -> Ingredient:
        if obj_in.type and obj_in.type != db_obj.type:
            raise ValueError("Ingredient type mismatch")
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"type"})
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(publish_ingredient_event("ingredient_updated", db_obj))
            else:
                loop.run_until_complete(publish_ingredient_event("ingredient_updated", db_obj))
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
        return db_obj

    def delete(self, db: Session, id: int) -> Ingredient:
        obj = db.get(Ingredient, id)
        if obj is None:
            raise HTTPException(status_code=404, detail=f"Ingredient with id={id} not found")

        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(publish_ingredient_event("ingredient_deleted", obj))
        else:
            loop.run_until_complete(publish_ingredient_event("ingredient_deleted", obj))

        return super().delete(db, id)

    async def search(self, db: Session, keyword: str, cursor: Optional[int] = None, limit: int = 100) -> Sequence[Ingredient]:
        es = get_es()
        query = {
            "query": {
                "match": {
                    "component_name": keyword
                }
            },
            "size": 1000
        }
        response = await es.search(index="ingredients", body=query)
        component_ids = [int(hit["_id"]) for hit in response["hits"]["hits"]]
        
        if not component_ids:
            return []
        
        IngredientPoly = with_polymorphic(Ingredient, "*")
        stmt = select(IngredientPoly).where(IngredientPoly.component_id.in_(component_ids))
        if cursor is not None:
            stmt = stmt.where(IngredientPoly.component_id < cursor)
        stmt = stmt.order_by(IngredientPoly.component_id.desc()).limit(limit)
        return db.execute(stmt).scalars().all()

    def filter(self, db: Session, category: Category, cursor: Optional[int] = None, limit: int = 100) -> Sequence[Ingredient]:
        IngredientPoly = with_polymorphic(Ingredient, "*")
        stmt = select(IngredientPoly).where(IngredientPoly.category == category.value)      # type: ignore
        if cursor is not None:
            stmt = stmt.where(IngredientPoly.component_id < cursor)
        stmt = stmt.order_by(IngredientPoly.component_id.desc()).limit(limit)
        return db.execute(stmt).scalars().all()

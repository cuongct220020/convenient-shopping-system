from sqlalchemy.orm import Session, with_polymorphic
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from shared.shopping_shared.crud.crud_base import CRUDBase
from typing import List, Optional, Sequence
from fastapi import HTTPException
from models.recipe_component import Ingredient, CountableIngredient, UncountableIngredient
from schemas.ingredient_schemas import IngredientCreate, IngredientUpdate
from enums.category import Category

"""
    Override create and update methods to allow flexibility in ingredient types
"""

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
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
        return db_obj

    def search(self, db: Session, keyword: str, cursor: Optional[int] = None, limit: int = 100) -> Sequence[Ingredient]:
        countable_stmt = select(CountableIngredient).where(
            CountableIngredient.component_name.ilike(f"%{keyword}%")
        )
        if cursor is not None:
            countable_stmt = countable_stmt.where(CountableIngredient.component_id < cursor)
        countable_stmt = countable_stmt.order_by(CountableIngredient.component_id.desc()).limit(limit)
        countable_results = db.execute(countable_stmt).scalars().all()

        uncountable_stmt = select(UncountableIngredient).where(
            UncountableIngredient.component_name.ilike(f"%{keyword}%")
        )
        if cursor is not None:
            uncountable_stmt = uncountable_stmt.where(UncountableIngredient.component_id < cursor)
        uncountable_stmt = uncountable_stmt.order_by(UncountableIngredient.component_id.desc()).limit(limit)
        uncountable_results = db.execute(uncountable_stmt).scalars().all()

        all_results = countable_results + uncountable_results
        all_results.sort(key=lambda x: x.component_id, reverse=True)

        return all_results[:limit]

    def filter(self, db: Session, category: Category, cursor: Optional[int] = None, limit: int = 100) -> Sequence[Ingredient]:
        IngredientPoly = with_polymorphic(Ingredient, "*")
        stmt = select(IngredientPoly).where(IngredientPoly.category == category.value)      # type: ignore
        if cursor is not None:
            stmt = stmt.where(IngredientPoly.component_id < cursor)
        stmt = stmt.order_by(IngredientPoly.component_id.desc()).limit(limit)
        return db.execute(stmt).scalars().all()

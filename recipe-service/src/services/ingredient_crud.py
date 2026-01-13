from sqlalchemy.orm import Session, with_polymorphic
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from shopping_shared.crud.crud_base import CRUDBase
from typing import Optional, Sequence
from fastapi import HTTPException
from models.recipe_component import Ingredient, CountableIngredient, UncountableIngredient
from schemas.ingredient_schemas import IngredientCreate, IngredientUpdate
from enums.category import Category
from sqlalchemy import or_

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
        IngredientPoly = with_polymorphic(Ingredient, "*")
        stmt = select(IngredientPoly).where(
            or_(
                CountableIngredient.component_name.ilike(f"%{keyword}%"),
                UncountableIngredient.component_name.ilike(f"%{keyword}%")
            )
        )
        if cursor is not None:
            stmt = stmt.where(IngredientPoly.component_id < cursor)
        stmt = stmt.order_by(IngredientPoly.component_id.desc()).limit(limit)
        return db.execute(stmt).scalars().all()

    def filter(self, db: Session, category: list[Category], cursor: Optional[int] = None, limit: int = 100) -> Sequence[Ingredient]:
        IngredientPoly = with_polymorphic(Ingredient, "*")
        stmt = select(IngredientPoly).where(IngredientPoly.category.in_([c.value for c in category]))      # type: ignore
        if cursor is not None:
            stmt = stmt.where(IngredientPoly.component_id < cursor)
        stmt = stmt.order_by(IngredientPoly.component_id.desc()).limit(limit)
        return db.execute(stmt).scalars().all()

from sqlalchemy.orm import Session
from .crud_base import CRUDBase
from models.recipe_component import Ingredient, CountableIngredient, UncountableIngredient, BulkIngredient
from schemas.ingredient import IngredientCreate, IngredientUpdate

"""
    Override create and update methods to allow flexibility in ingredient types
"""

class IngredientCRUD(CRUDBase[Ingredient, IngredientCreate, IngredientUpdate]):
    model_map = {
        "countable_ingredient": CountableIngredient,
        "uncountable_ingredient": UncountableIngredient,
        "bulk_ingredient": BulkIngredient,
    }

    def create(self, db: Session, obj_in: IngredientCreate) -> Ingredient:
        model_class = self.model_map[obj_in.type]
        if not model_class:
            raise ValueError(f"Unknown ingredient type: {obj_in.type}")
        db_obj = model_class(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, obj_in: IngredientUpdate, db_obj: Ingredient) -> Ingredient:
        if obj_in.type and obj_in.type != db_obj.type:
            raise ValueError("Ingredient type mismatch")
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"type"})
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

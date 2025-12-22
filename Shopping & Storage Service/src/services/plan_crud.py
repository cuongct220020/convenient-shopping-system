from sqlalchemy.orm import Session
from fastapi import HTTPException
from .crud_base import CRUDBase
from models.shopping_plan import ShoppingPlan
from schemas.plan_schemas import PlanCreate, PlanUpdate

class PLanCRUD(CRUDBase[ShoppingPlan, PlanCreate, PlanUpdate]):
    def update(self, db: Session, obj_in: PlanUpdate, db_obj: ShoppingPlan) -> ShoppingPlan:
        if not db_obj.plan_status.is_active():
            raise HTTPException(status_code=400, detail="Cannot update plan: plan is not active")
        return super().update(db, obj_in, db_obj)
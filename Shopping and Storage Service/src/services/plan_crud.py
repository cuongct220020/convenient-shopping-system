from sqlalchemy.orm import Session
from fastapi import HTTPException
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.shopping_plan import ShoppingPlan
from schemas.plan_schemas import PlanCreate, PlanUpdate
from enums.plan_status import PlanStatus

class PLanCRUD(CRUDBase[ShoppingPlan, PlanCreate, PlanUpdate]):
    def update(self, db: Session, obj_in: PlanUpdate, db_obj: ShoppingPlan) -> ShoppingPlan:
        if db_obj.plan_status not in [PlanStatus.CREATED, PlanStatus.IN_PROGRESS]:
            raise HTTPException(status_code=400, detail="Cannot update plan: plan is not active")
        return super().update(db, obj_in, db_obj)
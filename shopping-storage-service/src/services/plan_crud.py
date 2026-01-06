from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from fastapi import HTTPException
from shopping_shared.crud.crud_base import CRUDBase
from models.shopping_plan import ShoppingPlan
from schemas.plan_schemas import PlanCreate, PlanUpdate
from enums.plan_status import PlanStatus

class PLanCRUD(CRUDBase[ShoppingPlan, PlanCreate, PlanUpdate]):
    def update(self, db: Session, obj_in: PlanUpdate, db_obj: ShoppingPlan) -> ShoppingPlan:
        if db_obj.plan_status not in [PlanStatus.CREATED, PlanStatus.IN_PROGRESS]:
            raise HTTPException(status_code=400, detail="Cannot update plan: plan is not active")
        return super().update(db, obj_in, db_obj)

    def filter(
        self,
        db: Session,
        group_id: Optional[int] = None,
        plan_status: Optional[PlanStatus] = None,
        sort_by: str = "last_modified",
        order: str = "desc",
        cursor: Optional[int] = None,
        limit: int = 100
    ):
        stmt = select(ShoppingPlan)
        if sort_by == "last_modified":
            sort_column = ShoppingPlan.last_modified
        else:
            sort_column = ShoppingPlan.deadline

        if group_id is not None:
            stmt = stmt.where(ShoppingPlan.group_id == group_id)

        if plan_status is not None:
            stmt = stmt.where(ShoppingPlan.plan_status == plan_status)

        if order == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        if cursor is not None:
            if order == "asc":
                stmt = stmt.where(ShoppingPlan.plan_id > cursor)
            else:
                stmt = stmt.where(ShoppingPlan.plan_id < cursor)

        stmt = stmt.limit(limit)
        return db.execute(stmt).scalars().all()

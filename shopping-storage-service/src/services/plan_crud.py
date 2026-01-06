from datetime import datetime, time, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from fastapi import HTTPException
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.shopping_plan import ShoppingPlan
from schemas.plan_schemas import PlanCreate, PlanUpdate
from enums.plan_status import PlanStatus

class PlanCRUD(CRUDBase[ShoppingPlan, PlanCreate, PlanUpdate]):
    def update(self, db: Session, obj_in: PlanUpdate, db_obj: ShoppingPlan) -> ShoppingPlan:
        if db_obj.plan_status not in [PlanStatus.CREATED, PlanStatus.IN_PROGRESS]:
            raise HTTPException(status_code=400, detail="Cannot update plan: plan is not active")
        return super().update(db, obj_in, db_obj)

    def filter(
        self,
        db: Session,
        group_id: Optional[UUID] = None,
        plan_status: Optional[PlanStatus] = None,
        deadline: Optional[datetime] = None,
        cursor: Optional[int] = None,
        limit: int = 100
    ):
        stmt = select(ShoppingPlan)

        if group_id is not None:
            stmt = stmt.where(ShoppingPlan.group_id == group_id)

        if plan_status is not None:
            stmt = stmt.where(ShoppingPlan.plan_status == plan_status)

        if deadline is not None:
            # Filter by deadline day (ignore time portion)
            day = deadline.date()
            start = datetime.combine(day, time.min)
            if deadline.tzinfo is not None:
                start = start.replace(tzinfo=deadline.tzinfo)
            end = start + timedelta(days=1)
            stmt = stmt.where(ShoppingPlan.deadline >= start, ShoppingPlan.deadline < end)

        # Use stable ordering for cursor pagination
        stmt = stmt.order_by(desc(ShoppingPlan.plan_id))

        if cursor is not None:
            stmt = stmt.where(ShoppingPlan.plan_id < cursor)

        stmt = stmt.limit(limit)
        return db.execute(stmt).scalars().all()

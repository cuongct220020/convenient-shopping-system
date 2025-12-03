from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from enums.plan_status import PlanStatus
from models.shopping_plan import ShoppingPlan

class PlanTransition:
    def assign(self, db: Session, id: int, assignee_id: int):
        with db.begin():
            plan = db.execute(
                select(ShoppingPlan)
                .where(ShoppingPlan.plan_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            if plan is None:
                raise HTTPException(status_code=404, detail=f"ShoppingPlan with id={id} not found")

            if plan.plan_status != PlanStatus.CREATED:
                raise HTTPException(status_code=400, detail=f"Cannot assign plan: plan status must be CREATED, got {plan.plan_status}")

            plan.assignee_id = assignee_id
            plan.plan_status = PlanStatus.IN_PROGRESS

    def unassign(self):
        return 1

    def cancel(self):
        return 1

    def report(self):

    def reopen(self):

    def expire(self):
from typing import Literal, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from enums.plan_status import PlanStatus
from models.shopping_plan import ShoppingPlan

class PlanTransition:
    def _preconditions_check(self, plan: Optional[ShoppingPlan], allowed_status: PlanStatus | Literal["active"]):
        if plan is None:
            raise HTTPException(status_code=404, detail=f"ShoppingPlan not found")
        if allowed_status == "active":
            if not plan.plan_status.is_active():
                raise HTTPException(status_code=400, detail="Operation not allowed: plan is not active")
        else:
            if plan.plan_status != allowed_status:
                raise HTTPException(status_code=400,
                                    detail=f"Operation not allowed: plan status must be {allowed_status}, got {plan.plan_status}")

    def assign(self, db: Session, id: int, assignee_id: int) -> ShoppingPlan:
        with db.begin():
            plan = db.execute(
                select(ShoppingPlan)
                .where(ShoppingPlan.plan_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(plan, PlanStatus.CREATED)

            plan.assignee_id = assignee_id
            plan.plan_status = PlanStatus.IN_PROGRESS
            
            db.refresh(plan)
            return plan

    def unassign(self, db: Session, id: int, assignee_id: int) -> ShoppingPlan:
        with db.begin():
            plan = db.execute(
                select(ShoppingPlan)
                .where(ShoppingPlan.plan_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(plan, PlanStatus.IN_PROGRESS)

            if plan.assignee_id != assignee_id:
                raise HTTPException(status_code=403, detail=f"Operation not allowed: user {assignee_id} is not the current assignee of this plan")

            plan.assignee_id = None
            plan.plan_status = PlanStatus.CREATED
            
            db.refresh(plan)
            return plan

    def cancel(self, db: Session, id: int, assigner_id: int) -> ShoppingPlan:
        with db.begin():
            plan = db.execute(
                select(ShoppingPlan)
                .where(ShoppingPlan.plan_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(plan, "active")

            if plan.assignee_id != assigner_id:
                raise HTTPException(status_code=403,
                                    detail=f"Operation not allowed: user {assigner_id} is not the assigner of this plan")

            plan.assignee_id = None
            plan.plan_status = PlanStatus.CANCELLED
            
            db.refresh(plan)
            return plan

    def report(self, db: Session, id: int, assignee_id: int) -> ShoppingPlan:
        with db.begin():
            plan = db.execute(
                select(ShoppingPlan)
                .where(ShoppingPlan.plan_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(plan, PlanStatus.IN_PROGRESS)

            if plan.assignee_id != assignee_id:
                raise HTTPException(status_code=403,
                                    detail=f"Operation not allowed: user {assignee_id} is not the current assignee of this plan")

            plan.plan_status = PlanStatus.COMPLETED
            
            db.refresh(plan)
            return plan

    def reopen(self, db: Session, id: int, assigner_id: int) -> ShoppingPlan:
        with db.begin():
            plan = db.execute(
                select(ShoppingPlan)
                .where(ShoppingPlan.plan_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(plan, PlanStatus.CANCELLED)

            if plan.assignee_id != assigner_id:
                raise HTTPException(status_code=403,
                                    detail=f"Operation not allowed: user {assigner_id} is not the assigner of this plan")

            plan.plan_status = PlanStatus.CREATED
            
            db.refresh(plan)
            return plan

    def expire(self, db: Session, id: int) -> ShoppingPlan:
        with db.begin():
            plan = db.execute(
                select(ShoppingPlan)
                .where(ShoppingPlan.plan_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(plan, "active")

            plan.plan_status = PlanStatus.EXPIRED
            
            db.refresh(plan)
            return plan
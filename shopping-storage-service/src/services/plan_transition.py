from typing import Optional, Any, List
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from enums.plan_status import PlanStatus
from models.shopping_plan import ShoppingPlan
from schemas.plan_schemas import PlanReport, PlanResponse

class PlanTransition:
    def _preconditions_check(self, plan: Optional[ShoppingPlan], allowed_status: PlanStatus | List[PlanStatus]):
        if plan is None:
            raise HTTPException(status_code=404, detail=f"ShoppingPlan not found")
        if isinstance(allowed_status, list):
            if plan.plan_status not in allowed_status:
                raise HTTPException(status_code=400,
                                    detail=f"Operation not allowed: plan status must be one of {allowed_status}, got {plan.plan_status}")
        else:
            if plan.plan_status != allowed_status:
                raise HTTPException(status_code=400,
                                    detail=f"Operation not allowed: plan status must be {allowed_status}, got {plan.plan_status}")

    def assign(self, db: Session, id: int, assignee_id: UUID) -> PlanResponse:
        with db.begin():
            plan = db.execute(
                select(ShoppingPlan)
                .where(ShoppingPlan.plan_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(plan, PlanStatus.CREATED)

            plan.assignee_id = assignee_id
            plan.plan_status = PlanStatus.IN_PROGRESS

            return PlanResponse.model_validate(plan)

    def unassign(self, db: Session, id: int, assignee_id: UUID) -> PlanResponse:
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

            return PlanResponse.model_validate(plan)

    def cancel(self, db: Session, id: int, assigner_id: UUID) -> PlanResponse:
        with db.begin():
            plan = db.execute(
                select(ShoppingPlan)
                .where(ShoppingPlan.plan_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(plan, [PlanStatus.CREATED, PlanStatus.IN_PROGRESS])

            if plan.assigner_id != assigner_id:
                raise HTTPException(status_code=403,
                                    detail=f"Operation not allowed: user {assigner_id} is not the assigner of this plan")

            plan.assignee_id = None
            plan.plan_status = PlanStatus.CANCELLED

            return PlanResponse.model_validate(plan)

    def check_completion(self, plan: ShoppingPlan, report: PlanReport):
        shopping_list = plan.shopping_list if isinstance(plan.shopping_list, list) else []

        required_quantities = {}
        for item in shopping_list:
            if isinstance(item, dict) and 'component_id' in item and 'quantity' in item:
                component_id = item['component_id']
                quantity = item['quantity']
                if component_id in required_quantities:
                    required_quantities[component_id] += quantity
                else:
                    required_quantities[component_id] = quantity

        reported_quantities = {}
        for item in report.report_content:
            if item.component_id is not None:
                component_id = item.component_id
                if item.content_quantity is not None:
                    item_quantity = item.package_quantity * item.content_quantity
                else:
                    item_quantity = item.package_quantity

                if component_id in reported_quantities:
                    reported_quantities[component_id] += item_quantity
                else:
                    reported_quantities[component_id] = item_quantity

        missing_quantities = []
        for item in plan.shopping_list:
            component_id = item.get('component_id')
            required_quantity = required_quantities.get(component_id, 0)
            reported_quantity = reported_quantities.get(component_id, 0)

            if reported_quantity < required_quantity:
                missing_quantities.append({
                    'component_id': component_id,
                    'component_name': item['component_name'],
                    'missing_quantity': required_quantity - reported_quantity
                })
        is_complete = len(missing_quantities) == 0
        return is_complete, missing_quantities

    def report(self, db: Session, id: int, assignee_id: UUID, report: PlanReport, confirm: bool = True) -> tuple[bool, str, Any]:
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

            if not confirm:
                is_complete, missing_quantities = self.check_completion(plan, report)
                if not is_complete:
                    return False, "Report incomplete", {"missing_items": missing_quantities}

            plan.plan_status = PlanStatus.COMPLETED
            validated_plan = PlanResponse.model_validate(plan)

            return True, "Report accepted and plan completed", validated_plan

    def reopen(self, db: Session, id: int, assigner_id: UUID) -> PlanResponse:
        with db.begin():
            plan = db.execute(
                select(ShoppingPlan)
                .where(ShoppingPlan.plan_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(plan, PlanStatus.CANCELLED)

            if plan.assigner_id != assigner_id:
                raise HTTPException(status_code=403,
                                    detail=f"Operation not allowed: user {assigner_id} is not the assigner of this plan")

            plan.plan_status = PlanStatus.CREATED

            return PlanResponse.model_validate(plan)
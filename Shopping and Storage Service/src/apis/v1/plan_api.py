from fastapi import APIRouter, status, Depends, Body, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Any
from services.plan_crud import PLanCRUD
from services.plan_transition import PlanTransition
from services.report_process import report_process
from schemas.plan_schemas import PlanCreate, PlanUpdate, PlanResponse, PlanReport
from models.shopping_plan import ShoppingPlan
from shared.shopping_shared.schemas.response_schema import GenericResponse
from .crud_router_base import create_crud_router
from database import get_db

plan_crud = PLanCRUD(ShoppingPlan)
plan_transition = PlanTransition()

plan_router = APIRouter(
    prefix="/v1/shopping_plans",
    tags=["shopping_plans"]
)

crud_router = create_crud_router(
    model=ShoppingPlan,
    crud_base=plan_crud,
    create_schema=PlanCreate,
    update_schema=PlanUpdate,
    response_schema=PlanResponse
)

plan_router.include_router(crud_router)


@plan_router.post(
    "/{id}/assign",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Assign a shopping plan to an assignee. "
        "The plan status must be CREATED. "
        "After assignment, the plan status will be IN_PROGRESS."
    )
)
def assign_plan(id: int, assignee_id: int = Body(..., gt=0), db: Session = Depends(get_db)):
    return plan_transition.assign(db, id, assignee_id)


@plan_router.post(
    "/{id}/unassign",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Unassign a shopping plan from the current assignee. "
        "The plan status must be IN_PROGRESS and the assignee_id must match. "
        "After unassignment, the plan status will be CREATED."
    )
)
def unassign_plan(id: int, assignee_id: int = Body(..., gt=0), db: Session = Depends(get_db)):
    return plan_transition.unassign(db, id, assignee_id)


@plan_router.post(
    "/{id}/cancel",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Cancel an active shopping plan. "
        "The plan must be active and the assigner_id must match. "
        "After cancellation, the plan status will be CANCELLED."
    )
)
def cancel_plan(id: int, assigner_id: int = Body(..., gt=0), db: Session = Depends(get_db)):
    return plan_transition.cancel(db, id, assigner_id)


@plan_router.post(
    "/{id}/report",
    response_model=GenericResponse[Any],
    status_code=status.HTTP_200_OK,
    description=(
        "Report completion of a shopping plan. "
        "The plan status must be IN_PROGRESS and the assignee_id must match. "
        "If confirm=False, will validate the report content against the shopping list and complete the plan only if all required items are reported. "
        "If confirm=True, immediately complete the plan without validation. The plan status will be COMPLETED. "
        "After successful report, items from report_content will be added to their respective storages as StorableUnits."
    )
)
def report_plan(
    id: int, 
    report: PlanReport, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    assignee_id: int = Body(..., gt=0), 
    confirm: bool = Body(True)
):
    is_completed, message, data = plan_transition.report(db, id, assignee_id, report, confirm)
    if is_completed:
        background_tasks.add_task(report_process, report)
    return GenericResponse(message=message, data=data)

@plan_router.post(
    "/{id}/reopen",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Reopen a cancelled shopping plan. "
        "The plan status must be CANCELLED and the assigner_id must match. "
        "After reopening, the plan status will be CREATED."
    )
)
def reopen_plan(id: int, assigner_id: int = Body(..., gt=0), db: Session = Depends(get_db)):
    return plan_transition.reopen(db, id, assigner_id)

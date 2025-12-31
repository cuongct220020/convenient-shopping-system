from fastapi import APIRouter, status, Depends, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import Any, Optional
from services.plan_crud import PLanCRUD
from services.plan_transition import PlanTransition
from services.report_process import report_process
from schemas.plan_schemas import PlanCreate, PlanUpdate, PlanResponse, PlanReport
from models.shopping_plan import ShoppingPlan
from enums.plan_status import PlanStatus
from shared.shopping_shared.schemas.response_schema import GenericResponse, PaginationResponse
from .crud_router_base import create_crud_router
from core.database import get_db

plan_crud = PLanCRUD(ShoppingPlan)
plan_transition = PlanTransition()

plan_router = APIRouter(
    prefix="/v1/shopping_plans",
    tags=["shopping_plans"]
)

@plan_router.get(
    "/filter",
    response_model=PaginationResponse[PlanResponse],
    status_code=status.HTTP_200_OK,
    description="Filter shopping plans by group_id and/or plan_status. Supports sorting by last_modified or deadline, and pagination with cursor and limit."
)
def filter_plans(
    group_id: Optional[int] = Query(None, gt=0),
    plan_status: Optional[PlanStatus] = Query(None),
    sort_by: str = Query("last_modified", regex="^(last_modified|deadline)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    cursor: Optional[int] = Query(None, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db)
):
    plans = plan_crud.filter(
        db,
        group_id=group_id,
        plan_status=plan_status,
        sort_by=sort_by,
        order=order,
        cursor=cursor,
        limit=limit
    )
    pk = inspect(ShoppingPlan).primary_key[0]
    next_cursor = getattr(plans[-1], pk.name) if plans and len(plans) == limit else None
    return PaginationResponse(
        data=[PlanResponse.model_validate(plan) for plan in plans],
        next_cursor=next_cursor,
        size=len(plans),
        has_more=len(plans) == limit
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
def assign_plan(id: int, assignee_id: int = Query(..., gt=0), db: Session = Depends(get_db)):
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
def unassign_plan(id: int, assignee_id: int = Query(..., gt=0), db: Session = Depends(get_db)):
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
def cancel_plan(id: int, assigner_id: int = Query(..., gt=0), db: Session = Depends(get_db)):
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
async def report_plan(
    id: int, 
    report: PlanReport, 
    db: Session = Depends(get_db),
    assignee_id: int = Query(..., gt=0),
    confirm: bool = Query(True)
):
    is_completed, message, data = plan_transition.report(db, id, assignee_id, report, confirm)
    if is_completed:
        await report_process(report, db)
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
def reopen_plan(id: int, assigner_id: int = Query(..., gt=0), db: Session = Depends(get_db)):
    return plan_transition.reopen(db, id, assigner_id)



from datetime import datetime
from fastapi import APIRouter, status, Depends, Body, BackgroundTasks, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import Any, Optional
from uuid import UUID
from services.plan_crud import PlanCRUD
from services.plan_transition import PlanTransition
from services.report_process import report_process
from schemas.plan_schemas import PlanCreate, PlanUpdate, PlanResponse, PlanReport
from models.shopping_plan import ShoppingPlan
from enums.plan_status import PlanStatus
from shared.shopping_shared.schemas.cursor_pagination_schema import GenericResponse, CursorPaginationResponse
from .crud_router_base import create_crud_router
from core.database import get_db

plan_crud = PlanCRUD(ShoppingPlan)
plan_transition = PlanTransition()

plan_router = APIRouter(
    prefix="/v1/shopping_plans",
    tags=["shopping_plans"]
)

@plan_router.get(
    "/filter",
    response_model=CursorPaginationResponse[PlanResponse],
    status_code=status.HTTP_200_OK,
    description=(
        "Filter shopping plans by group_id and/or plan_status and/or deadline (by day). "
        "Supports pagination with cursor and limit."
    )
)
def filter_plans(
    group_id: Optional[UUID] = Query(None, description="Filter by group ID"),
    plan_status: Optional[PlanStatus] = Query(None, description="Filter by plan status", examples=[PlanStatus.CREATED, PlanStatus.IN_PROGRESS]),
    deadline: Optional[datetime] = Query(
        None,
        description="Filter by deadline day (datetime format; only the date portion is used)",
        examples=["2025-12-31T00:00:00"]
    ),
    cursor: Optional[int] = Query(None, ge=0, description="Cursor for pagination (ID of the last item from previous page)"),
    limit: int = Query(100, ge=1, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    plans = plan_crud.filter(
        db,
        group_id=group_id,
        plan_status=plan_status,
        deadline=deadline,
        cursor=cursor,
        limit=limit
    )
    pk = inspect(ShoppingPlan).primary_key[0]
    next_cursor = getattr(plans[-1], pk.name) if plans and len(plans) == limit else None
    return CursorPaginationResponse(
        data=[PlanResponse.model_validate(plan) for plan in plans],
        next_cursor=next_cursor,
        size=len(plans),
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
def assign_plan(
    id: int = Path(..., ge=1),
    assignee_id: UUID = Query(..., description="The UUID of the user to assign the plan to"),
    db: Session = Depends(get_db)
):
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
def unassign_plan(
    id: int = Path(..., ge=1),
    assignee_id: UUID = Query(..., description="The UUID of the user to unassign from the plan"),
    db: Session = Depends(get_db)
):
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
def cancel_plan(
    id: int = Path(..., ge=1),
    assigner_id: UUID = Query(..., description="The UUID of the user who created the plan"),
    db: Session = Depends(get_db)
):
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
    background_tasks: BackgroundTasks,
    id: int = Path(..., ge=1),
    report: PlanReport = Body(..., description="Report data containing the items purchased"),
    db: Session = Depends(get_db),
    assignee_id: UUID = Query(..., description="The UUID of the user reporting the plan completion"),
    confirm: bool = Query(True, description="If True, immediately complete without validation. If False, validate report content first")
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
def reopen_plan(
    id: int = Path(..., ge=1),
    assigner_id: UUID = Query(..., description="The UUID of the user who created the plan"),
    db: Session = Depends(get_db)
):
    return plan_transition.reopen(db, id, assigner_id)



from fastapi import APIRouter, status, Depends, Body
from sqlalchemy.orm import Session
from services.plan_crud import PLanCRUD
from services.plan_transition import PlanTransition
from schemas.plan_schemas import PlanCreate, PlanUpdate, PlanResponse
from models.shopping_plan import ShoppingPlan
from shared.shopping_shared.crud.crud_router_base import create_crud_router
from shared.shopping_shared.databases.fastapi_database import get_db
from shared.shopping_shared.schemas.response_schema import GenericResponse

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
    response_model=GenericResponse[PlanResponse],
    status_code=status.HTTP_200_OK,
    description=(
        "Assign a shopping plan to an assignee. "
        "The plan status must be CREATED. "
        "After assignment, the plan status will be IN_PROGRESS."
    )
)
def assign_plan(id: int, assignee_id: int = Body(..., gt=0), db: Session = Depends(get_db)):
    plan_transition.assign(db, id, assignee_id)
    plan = plan_crud.get(db, id)
    return GenericResponse(
        message="Plan assigned successfully",
        data=PlanResponse.model_validate(plan)
    )


@plan_router.post(
    "/{id}/unassign",
    response_model=GenericResponse[PlanResponse],
    status_code=status.HTTP_200_OK,
    description=(
        "Unassign a shopping plan from the current assignee. "
        "The plan status must be IN_PROGRESS and the assignee_id must match. "
        "After unassignment, the plan status will be CREATED."
    )
)
def unassign_plan(id: int, assignee_id: int = Body(..., gt=0), db: Session = Depends(get_db)):
    plan_transition.unassign(db, id, assignee_id)
    plan = plan_crud.get(db, id)
    return GenericResponse(
        message="Plan unassigned successfully",
        data=PlanResponse.model_validate(plan)
    )


@plan_router.post(
    "/{id}/cancel",
    response_model=GenericResponse[PlanResponse],
    status_code=status.HTTP_200_OK,
    description=(
        "Cancel an active shopping plan. "
        "The plan must be active and the assigner_id must match. "
        "After cancellation, the plan status will be CANCELLED."
    )
)
def cancel_plan(id: int, assigner_id: int = Body(..., gt=0), db: Session = Depends(get_db)):
    plan_transition.cancel(db, id, assigner_id)
    plan = plan_crud.get(db, id)
    return GenericResponse(
        message="Plan cancelled successfully",
        data=PlanResponse.model_validate(plan)
    )


@plan_router.post(
    "/{id}/report",
    response_model=GenericResponse[PlanResponse],
    status_code=status.HTTP_200_OK,
    description=(
        "Report completion of a shopping plan. "
        "The plan status must be IN_PROGRESS and the assignee_id must match. "
        "After reporting, the plan status will be COMPLETED."
    )
)
def report_plan(id: int, assignee_id: int = Body(..., gt=0), db: Session = Depends(get_db)):
    plan_transition.report(db, id, assignee_id)
    plan = plan_crud.get(db, id)
    return GenericResponse(
        message="Plan reported as completed successfully",
        data=PlanResponse.model_validate(plan)
    )


@plan_router.post(
    "/{id}/reopen",
    response_model=GenericResponse[PlanResponse],
    status_code=status.HTTP_200_OK,
    description=(
        "Reopen a cancelled shopping plan. "
        "The plan status must be CANCELLED and the assigner_id must match. "
        "After reopening, the plan status will be CREATED."
    )
)
def reopen_plan(id: int, assigner_id: int = Body(..., gt=0), db: Session = Depends(get_db)):
    plan_transition.reopen(db, id, assigner_id)
    plan = plan_crud.get(db, id)
    return GenericResponse(
        message="Plan reopened successfully",
        data=PlanResponse.model_validate(plan)
    )


@plan_router.post(
    "/{id}/expire",
    response_model=GenericResponse[PlanResponse],
    status_code=status.HTTP_200_OK,
    description=(
        "Expire an active shopping plan. "
        "The plan must be active. "
        "After expiration, the plan status will be EXPIRED."
    )
)
def expire_plan(id: int, db: Session = Depends(get_db)):
    plan_transition.expire(db, id)
    plan = plan_crud.get(db, id)
    return GenericResponse(
        message="Plan expired successfully",
        data=PlanResponse.model_validate(plan)
    )

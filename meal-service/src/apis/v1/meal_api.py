from fastapi import APIRouter, Depends, Query, status, Path, Body
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from services.meal_command_handler import MealCommandHandler
from services.meal_transition import MealTransition
from schemas.meal_schemas import DailyMealsCommand, MealResponse, MealMissingResponse
from enums.meal_type import MealType
from core.database import get_db

meal_command_handler = MealCommandHandler()
meal_transition = MealTransition()

meal_router = APIRouter(
    prefix="/v1/meals",
    tags=["meals"]
)

@meal_router.get(
    "/",
    response_model=list[MealResponse | MealMissingResponse],
    status_code=status.HTTP_200_OK,
    description="Get meals by date, group_id and optionally by meal_type. If meal_type is not provided, returns all meals (breakfast, lunch, dinner) for that date and group_id."
)
def get_meals(
    meal_date: date = Query(..., description="The date to get meals for"),
    group_id: int = Query(..., ge=1, description="Group ID to get meals for"),
    meal_type: Optional[MealType] = Query(None, description="Filter by meal type (breakfast, lunch, dinner). If not provided, returns all meals for the date", examples=[MealType.BREAKFAST, MealType.LUNCH]),
    db: Session = Depends(get_db)
):
    return meal_command_handler.get(db, meal_date, group_id, meal_type)

@meal_router.post(
    "/command",
    response_model=list[MealResponse | MealMissingResponse],
    status_code=status.HTTP_200_OK,
    description="Process daily meal commands for upserting, deleting, or skipping meals."
)
def process_daily_meal_command(daily_command: DailyMealsCommand = Body(..., description="Daily meal commands for upserting, deleting, or skipping meals"), db: Session = Depends(get_db)):
    responses = meal_command_handler.handle(db, daily_command)
    return responses

@meal_router.post(
    "/{id}/cancel",
    response_model=MealResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Cancel a meal. "
        "The meal status must be CREATED. "
        "After cancellation, the meal status will be CANCELLED."
    )
)
def cancel_meal(id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    return meal_transition.cancel(db, id)


@meal_router.post(
    "/{id}/reopen",
    response_model=MealResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Reopen a cancelled meal. "
        "The meal status must be CANCELLED. "
        "After reopening, the meal status will be CREATED."
    )
)
def reopen_meal(id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    return meal_transition.reopen(db, id)


@meal_router.post(
    "/{id}/finish",
    response_model=MealResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Finish a meal. "
        "The meal status must be CREATED. "
        "After finishing, the meal status will be DONE."
    )
)
def finish_meal(id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    return meal_transition.finish(db, id)


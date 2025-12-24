from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from services.meal_command_handler import MealCommandHandler
from services.meal_transition import MealTransition
from schemas.meal_schemas import DailyMealsCommand, MealResponse
from enums.meal_type import MealType
from database import get_db

meal_command_handler = MealCommandHandler()
meal_transition = MealTransition()

meal_router = APIRouter(
    prefix="/v1/meals",
    tags=["meals"]
)

@meal_router.get(
    "/",
    response_model=list[MealResponse],
    status_code=status.HTTP_200_OK,
    description="Get meals by date and optionally by meal_type. If meal_type is not provided, returns all meals for that date."
)
def get_meals(meal_date: date, meal_type: Optional[MealType], db: Session = Depends(get_db)):
    return meal_command_handler.get(db, meal_date, meal_type)

@meal_router.post(
    "/command",
    response_model=list[MealResponse | str],
    status_code=status.HTTP_200_OK,
    description="Process daily meal commands for upserting, deleting, or skipping meals."
)
async def process_daily_meal_command(daily_command: DailyMealsCommand, db: Session = Depends(get_db)):
    responses = await meal_command_handler.handle(db, daily_command)
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
def cancel_meal(id: int, db: Session = Depends(get_db)):
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
def reopen_meal(id: int, db: Session = Depends(get_db)):
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
def finish_meal(id: int, db: Session = Depends(get_db)):
    return meal_transition.finish(db, id)


import uuid
from fastapi import APIRouter, Depends, Query, status, HTTPException
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
def get_meals(meal_date: date, group_id: uuid.UUID = Query(...), meal_type: Optional[MealType] = None, db: Session = Depends(get_db)):
    return meal_command_handler.get(db, meal_date, group_id, meal_type)

@meal_router.post(
    "/command",
    response_model=list[MealResponse | MealMissingResponse],
    status_code=status.HTTP_200_OK,
    description="Process daily meal commands for upserting, deleting, or skipping meals."
)
def process_daily_meal_command(
    daily_command: DailyMealsCommand, 
    group_id: uuid.UUID = Query(..., description="Group ID for authorization check"),
    db: Session = Depends(get_db)
):
    # Validate that group_id in query matches group_id in body
    if daily_command.group_id != group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="group_id in query parameter must match group_id in request body"
        )
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
def cancel_meal(
    id: int, 
    group_id: uuid.UUID = Query(..., description="Group ID for authorization check"),
    db: Session = Depends(get_db)
):
    return meal_transition.cancel(db, id, group_id)


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
def reopen_meal(
    id: int, 
    group_id: uuid.UUID = Query(..., description="Group ID for authorization check"),
    db: Session = Depends(get_db)
):
    return meal_transition.reopen(db, id, group_id)


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
def finish_meal(
    id: int, 
    group_id: uuid.UUID = Query(..., description="Group ID for authorization check"),
    db: Session = Depends(get_db)
):
    return meal_transition.finish(db, id, group_id)


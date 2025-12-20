from fastapi import APIRouter, Depends, Query, status, HTTPException, BackgroundTasks
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from services.meal_crud import MealCRUD, MealCommandHandler
from schemas.meal_schemas import DailyMealsCommand, MealResponse
from models.meal import Meal
from messaging.producers.meal_content_updated_producer import produce_meal_content_updated
from database import get_db
from shared.shopping_shared.schemas.response_schema import PaginationResponse

meal_crud = MealCRUD(Meal)
meal_command_handler = MealCommandHandler()

meal_router = APIRouter(
    prefix="/v1/meals",
    tags=["meals"]
)

@meal_router.get(
    "/{id}",
    response_model=MealResponse,
    status_code=status.HTTP_200_OK,
    description="Retrieve a Meal by its unique ID. Returns 404 if the Meal does not exist."
)
def get_meal(id: int, db: Session = Depends(get_db)):
    meal = meal_crud.get(db, id)
    if meal is None:
        raise HTTPException(status_code=404, detail=f"Meal with id={id} not found")
    return meal

@meal_router.get(
    "/",
    response_model=PaginationResponse[MealResponse],
    status_code=status.HTTP_200_OK,
    description="Retrieve a list of Meals. Supports pagination with cursor and limit."
)
def get_many_meals(Cursor: Optional[int] = Query(None, ge=0), limit: int = Query(100, ge=1), db: Session = Depends(get_db)):
    meals = meal_crud.get_many(db, cursor=Cursor, limit=limit)
    pk = inspect(Meal).primary_key[0]
    next_cursor = getattr(meals[-1], pk.name) if meals and len(meals) == limit else None
    return PaginationResponse(
        data=list(meals),
        next_cursor=next_cursor,
        size=len(meals),
        has_more=len(meals) == limit
    )

@meal_router.post(
    "/command",
    response_model=list[MealResponse | str],
    status_code=status.HTTP_200_OK,
    description="Process daily meal commands for upserting, deleting, or skipping meals."
)
def process_daily_meal_command(daily_command: DailyMealsCommand, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    responses, events =  meal_command_handler.handle(db, daily_command)
    for event in events:
        background_tasks.add_task(produce_meal_content_updated, event)
    return responses


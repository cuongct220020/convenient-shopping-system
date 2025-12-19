from fastapi import APIRouter
from services.meal_crud import MealCRUD
from schemas.meal_schemas import MealCreate, MealUpdate, MealResponse
from models.meal import Meal
from .crud_router_base import create_crud_router
from database import get_db

meal_crud = MealCRUD(Meal)

meal_router = APIRouter(
    prefix="/v1/meals",
    tags=["meals"]
)

crud_router = create_crud_router(
    model=Meal,
    crud_base=meal_crud,
    create_schema=MealCreate,
    update_schema=MealUpdate,
    response_schema=MealResponse
)

meal_router.include_router(crud_router)


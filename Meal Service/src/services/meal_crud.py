import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from datetime import date
from enums.meal_type import MealType
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.meal import Meal, RecipeList
from schemas.meal_schemas import MealCommand, DailyMealsCommand
from utils.list_diff import list_diff

class MealCRUD(CRUDBase[Meal, MealCommand, MealCommand]):
    pass

class MealCommandHandler:
    def handle(self, db: Session, daily_command: DailyMealsCommand) -> tuple[list[Meal], list[dict]]:
        responses = []
        events = []
        for meal_type, meal_command in [(MealType.BREAKFAST, daily_command.breakfast),
                                        (MealType.LUNCH, daily_command.lunch),
                                        (MealType.DINNER, daily_command.dinner)]:
            if meal_command.action == "upsert":
                response, event = self.upsert(db, daily_command.date, daily_command.group_id, meal_type, meal_command)
            elif meal_command.action == "delete":
                response, event = self.delete(db, daily_command.date, daily_command.group_id, meal_type)
            elif meal_command.action == "skip":
                continue
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action {meal_command.action} for meal {meal_type}")
            responses.append(response)
            events.append(event)
        return responses, events

    def upsert(self, db: Session, date: date, group_id: int, meal_type: MealType, meal_command: MealCommand):
        meal: Meal | None = db.execute(
            select(Meal).where(Meal.date == date, Meal.group_id == group_id, Meal.meal_type == meal_type)
        ).scalars().first()
        if not meal:
            meal = Meal(date=date, group_id=group_id, meal_type=meal_type)
            db.add(meal)
        old_recipe_list = meal.recipe_list if meal.recipe_list else []
        if meal_command.recipe_list is not None:
            meal.recipe_list = [RecipeList(recipe_id=recipe.recipe_id,
                                           recipe_name=recipe.recipe_name,
                                           servings=recipe.servings)
                                for recipe in meal_command.recipe_list]

        try:
            with httpx.Client(timeout=30) as client:
                payload = [
                    {
                        "recipe_id": recipe.recipe_id,
                        "servings": recipe.servings
                    }
                    for recipe in meal_command.recipe_list
                ]
                response = client.post(
                    "http://localhost:8001/v2/recipes/flattened",
                    json=payload
                )
                response.raise_for_status()
                meal.all_ingredients = response.json().get("all_ingredients", [])
        except httpx.HTTPError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to fetch all_ingredients: {str(e)}")

        event = {
            "event_type": "meal_upserted",
            "data": {
                "meal_id": meal.meal_id,
                "date": str(meal.date),
                "meal_type": {MealType.BREAKFAST: 1, MealType.LUNCH: 2, MealType.DINNER: 3}[meal.meal_type],                # type: ignore
                "recipe_diff": list_diff(old_recipe_list, meal.recipe_list, "recipe_id", "servings")
            }
        }

        try:
            db.commit()
            db.refresh(meal)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")

        return meal, event

    def delete(self, db: Session, date: date, group_id: int, meal_type: MealType):
        meal: Meal | None = db.execute(
            select(Meal).where(Meal.date == date, Meal.group_id == group_id, Meal.meal_type == meal_type)
        ).scalars().first()
        if not meal:
            raise HTTPException(status_code=404, detail=f"Meal {meal_type} on {date} for group {group_id} not found")

        event = {
            "event_type": "meal_deleted",
            "data": {
                "meal_id": meal.meal_id,
                "date": str(meal.date),
                "meal_type": {MealType.BREAKFAST: 1, MealType.LUNCH: 2, MealType.DINNER: 3}[meal.meal_type]
            }
        }

        db.delete(meal)
        db.commit()
        return "Deleted", event



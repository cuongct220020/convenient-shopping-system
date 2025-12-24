from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from datetime import date
from typing import Optional, Sequence
from enums.meal_type import MealType
from models.meal import Meal, RecipeList
from schemas.meal_schemas import MealCommand, DailyMealsCommand

class MealCommandHandler:
    async def handle(self, db: Session, daily_command: DailyMealsCommand) -> list[Meal | str]:
        responses = []
        for meal_type, meal_command in [(MealType.BREAKFAST, daily_command.breakfast),
                                        (MealType.LUNCH, daily_command.lunch),
                                        (MealType.DINNER, daily_command.dinner)]:
            if meal_command.action == "upsert":
                response = await self.upsert(db, daily_command.date, daily_command.group_id, meal_type, meal_command)
            elif meal_command.action == "delete":
                response = self.delete(db, daily_command.date, daily_command.group_id, meal_type)
            elif meal_command.action == "skip":
                continue
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action {meal_command.action} for meal {meal_type}")
            responses.append(response)
        return responses

    async def upsert(self, db: Session, date: date, group_id: int, meal_type: MealType, meal_command: MealCommand):
        meal: Meal | None = db.execute(
            select(Meal).where(Meal.date == date, Meal.group_id == group_id, Meal.meal_type == meal_type)
        ).scalars().first()
        if not meal:
            meal = Meal(date=date, group_id=group_id, meal_type=meal_type)
            db.add(meal)
        if meal_command.recipe_list is not None:
            meal.recipe_list = [RecipeList(recipe_id=recipe.recipe_id,
                                           recipe_name=recipe.recipe_name,
                                           servings=recipe.servings)
                                for recipe in meal_command.recipe_list]

        try:
            db.commit()
            db.refresh(meal)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")

        return meal

    def delete(self, db: Session, date: date, group_id: int, meal_type: MealType):
        meal: Meal | None = db.execute(
            select(Meal).where(Meal.date == date, Meal.group_id == group_id, Meal.meal_type == meal_type)
        ).scalars().first()
        if not meal:
            raise HTTPException(status_code=404, detail=f"Meal {meal_type} on {date} for group {group_id} not found")

        db.delete(meal)
        db.commit()
        return "Deleted"

    def get(self, db: Session, date: date, meal_type: Optional[MealType] = None) -> Sequence[Meal]:
        stmt = select(Meal).where(Meal.date == date)

        if meal_type is not None:
            stmt = stmt.where(Meal.meal_type == meal_type)

        return db.execute(stmt).scalars().all()



from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from datetime import date
from typing import Optional, Sequence
from enums.meal_type import MealType
from models.meal import Meal, RecipeList
from schemas.meal_schemas import MealCommand, DailyMealsCommand, MealResponse, MealMissingResponse

class MealCommandHandler:
    def handle(self, db: Session, daily_command: DailyMealsCommand) -> list[Meal | MealMissingResponse]:
        responses = []
        for meal_type, meal_command in [(MealType.BREAKFAST, daily_command.breakfast),
                                        (MealType.LUNCH, daily_command.lunch),
                                        (MealType.DINNER, daily_command.dinner)]:
            if meal_command.action == "upsert":
                response = self.upsert(db, daily_command.date, daily_command.group_id, meal_type, meal_command)
                responses.append(response)
            elif meal_command.action == "delete":
                response = self.delete(db, daily_command.date, daily_command.group_id, meal_type)
                responses.append(response)
            elif meal_command.action == "skip":
                response = self.get(db, daily_command.date, daily_command.group_id, meal_type)[0]
                responses.append(response)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action {meal_command.action} for meal {meal_type}")
        return responses

    def upsert(self, db: Session, date: date, group_id: int, meal_type: MealType, meal_command: MealCommand):
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

    def delete(self, db: Session, date: date, group_id: int, meal_type: MealType) -> MealMissingResponse:
        meal: Meal | None = db.execute(
            select(Meal).where(Meal.date == date, Meal.group_id == group_id, Meal.meal_type == meal_type)
        ).scalars().first()
        if meal:
            db.delete(meal)
            db.commit()
        return MealMissingResponse(
            date=date,
            group_id=group_id,
            meal_type=meal_type,
            detail="Meal deleted"
        )

    def get(self, db: Session, date: date, group_id: int, meal_type: Optional[MealType] = None) -> Sequence[MealResponse | MealMissingResponse]:
        stmt = select(Meal).where(Meal.date == date, Meal.group_id == group_id)

        if meal_type is not None:
            stmt = stmt.where(Meal.meal_type == meal_type)
            meal = db.execute(stmt).scalars().one_or_none()
            if meal:
                return [MealResponse.model_validate(meal)]
            else:
                return [MealMissingResponse(
                    date=date,
                    group_id=group_id,
                    meal_type=meal_type,
                    detail="Meal has not been planned yet"
                )]
        else:
            meals = db.execute(stmt).scalars().all()
            meal_map = {meal.meal_type: meal for meal in meals}
            return [
                MealResponse.model_validate(meal) if (meal := meal_map.get(meal_type)) else MealMissingResponse(
                    date=date,
                    group_id=group_id,
                    meal_type=meal_type,
                    detail="Meal has not been planned yet"
                )
                for meal_type in [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]
            ]



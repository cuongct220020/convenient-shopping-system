from typing import Literal, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from enums.meal_status import MealStatus
from models.meal import Meal


class MealTransition:
    def _preconditions_check(self, meal: Optional[Meal], allowed_status: MealStatus):
        if meal is None:
            raise HTTPException(status_code=404, detail=f"Meal not found")
        if meal.status != allowed_status:
            raise HTTPException(status_code=400, detail=f"Operation not allowed: meal status must be {allowed_status}, got {meal.status}")

    def cancel(self, db: Session, id: int) -> Meal:
        with db.begin():
            meal = db.execute(
                select(Meal)
                .where(Meal.meal_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(meal, MealStatus.CREATED)

            meal.status = MealStatus.CANCELLED

            db.refresh(meal)
            return meal

    def reopen(self, db: Session, id: int) -> Meal:
        with db.begin():
            meal = db.execute(
                select(Meal)
                .where(Meal.meal_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(meal, MealStatus.CANCELLED)

            meal.status = MealStatus.CREATED

            db.refresh(meal)
            return meal

    def finish(self, db: Session, id: int) -> Meal:
        with db.begin():
            meal = db.execute(
                select(Meal)
                .where(Meal.meal_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(meal, MealStatus.CREATED)

            meal.status = MealStatus.DONE

            db.refresh(meal)
            return meal


import uuid
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from enums.meal_status import MealStatus
from models.meal import Meal
from schemas.meal_schemas import MealResponse


class MealTransition:
    def _preconditions_check(self, meal: Optional[Meal], allowed_status: MealStatus, group_id: uuid.UUID):
        if meal is None:
            raise HTTPException(status_code=404, detail=f"Meal not found")
        if meal.group_id != group_id:
            raise HTTPException(status_code=403, detail=f"Meal does not belong to the specified group")
        if meal.meal_status != allowed_status:
            raise HTTPException(status_code=400, detail=f"Operation not allowed: meal status must be {allowed_status}, got {meal.meal_status}")

    def cancel(self, db: Session, id: int, group_id: uuid.UUID) -> MealResponse:
        with db.begin():
            meal = db.execute(
                select(Meal)
                .where(Meal.meal_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(meal, MealStatus.CREATED, group_id)

            meal.meal_status = MealStatus.CANCELLED

            return MealResponse.model_validate(meal)

    def reopen(self, db: Session, id: int, group_id: uuid.UUID) -> MealResponse:
        with db.begin():
            meal = db.execute(
                select(Meal)
                .where(Meal.meal_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(meal, MealStatus.CANCELLED, group_id)

            meal.meal_status = MealStatus.CREATED

            return MealResponse.model_validate(meal)

    def finish(self, db: Session, id: int, group_id: uuid.UUID) -> MealResponse:
        with db.begin():
            meal = db.execute(
                select(Meal)
                .where(Meal.meal_id == id)
                .with_for_update()
            ).scalar_one_or_none()

            self._preconditions_check(meal, MealStatus.CREATED, group_id)

            meal.meal_status = MealStatus.DONE

            return MealResponse.model_validate(meal)
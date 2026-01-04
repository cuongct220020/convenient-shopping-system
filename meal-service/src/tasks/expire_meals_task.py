from datetime import date
from sqlalchemy import update
from enums.meal_status import MealStatus
from models.meal import Meal
from core.database import get_db

def expire_meals():
    db = next(get_db())
    today = date.today()

    with db.begin():
        db.execute(
            update(Meal)
            .where(Meal.meal_status == MealStatus.CREATED, Meal.date < today)
            .values(meal_status=MealStatus.EXPIRED)
        )

    db.close()
from sqlalchemy import update
from database import get_db
from enums.meal_status import MealStatus
from models.meal import Meal

def handle_unit_allocated(data: list):
    db = next(get_db())
    try:
        meal_ids = [item["meal_id"] for item in data]
        db.execute(
            update(Meal)
            .where(Meal.meal_id.in_(meal_ids))
            .values(meal_status=MealStatus.RESERVED)
        )
        db.commit()

    except:
        db.rollback()
        raise
    finally:
        db.close()

def handle_unit_shortage(data: list):
    db = next(get_db())
    try:
        meal_ids = [item["meal_id"] for item in data]
        db.execute(
            update(Meal)
            .where(Meal.meal_id.in_(meal_ids))
            .values(meal_status=MealStatus.BACKORDERED)
        )
        db.commit()

    except:
        db.rollback()
        raise
    finally:
        db.close()
from sqlalchemy import update
from database import get_db
from models.meal import Meal

def sufficiency_updated_handler(data: list):
    db = next(get_db())
    try:
        for item in data:
            db.execute(
                update(Meal).
                where(Meal.meal_id == item["meal_id"])
                .values(is_sufficient=item["is_sufficient"])
            )
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
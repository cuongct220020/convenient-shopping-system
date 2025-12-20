from database import get_db
from models.storage import MealReservation

def handle_meal_upserted(data: dict):
    db = next(get_db())
    try:

from shared.shopping_shared.crud.crud_base import CRUDBase
from models.meal import Meal
from schemas.meal_schemas import MealCreate, MealUpdate

class MealCRUD(CRUDBase[Meal, MealCreate, MealUpdate]):
    pass


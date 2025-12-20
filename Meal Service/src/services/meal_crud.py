from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date
from enums.meal_type import MealType
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.meal import Meal, RecipeList, StorableUnitList
from schemas.meal_schemas import MealCommand, DailyMealsCommand, MealResponse

class MealCRUD(CRUDBase[Meal, MealCommand, MealCommand]):
    pass

class MealCommandHandler:
    def handle(self, db: Session, daily_command: DailyMealsCommand) -> list[Meal]:
        responses = []
        for meal_type, meal_command in [(MealType.BREAKFAST, daily_command.breakfast),
                                        (MealType.LUNCH, daily_command.lunch),
                                        (MealType.DINNER, daily_command.dinner)]:
            if meal_command.action == "upsert":
                response = self.upsert(db, daily_command.date, daily_command.group_id, meal_type, meal_command)
            elif meal_command.action == "delete":
                response = self.delete(db, daily_command.date, daily_command.group_id, meal_type)
            elif meal_command.action == "skip":
                continue
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action {meal_command.action} for meal {meal_type}")
            responses.append(response)
        return responses

    def upsert(self, db: Session, date: date, group_id: int, meal_type: MealType, meal_command: MealCommand) -> Meal:
        meal: Meal | None = db.query(Meal).filter_by(date=date, group_id=group_id, meal_type=meal_type).first()
        if not meal:
            meal = Meal(date=date, group_id=group_id, meal_type=meal_type)
            db.add(meal)
        if meal_command.recipe_list is not None:
            meal.recipe_list = [RecipeList(recipe_id=recipe.recipe_id,
                                           recipe_name=recipe.recipe_name,
                                           servings=recipe.servings)
                                for recipe in meal_command.recipe_list]
        if meal_command.storable_unit_list is not None:
            meal.storable_unit_list = [StorableUnitList(unit_id=unit.unit_id,
                                                       unit_name=unit.unit_name,
                                                       quantity=unit.quantity)
                                       for unit in meal_command.storable_unit_list]
        try:
            db.commit()
            db.refresh(meal)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
        return meal

    def delete(self, db: Session, date: date, group_id: int, meal_type: MealType):
        meal: Meal | None = db.query(Meal).filter_by(date=date, group_id=group_id, meal_type=meal_type).first()
        if not meal:
            raise HTTPException(status_code=404, detail=f"Meal {meal_type} on {date} for group {group_id} not found")
        db.delete(meal)
        db.commit()
        return "Deleted"



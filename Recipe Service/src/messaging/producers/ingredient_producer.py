from typing import Literal
from shared.shopping_shared.messaging.kafka_manager import kafka_manager
from shared.shopping_shared.messaging.topics import INGREDIENT_EVENTS_TOPIC
from models.recipe_component import Ingredient, CountableIngredient, UncountableIngredient

async def publish_ingredient_event(
    event_type: Literal["ingredient_created", "ingredient_updated", "ingredient_deleted"],
    ingredient: Ingredient
) -> None:
    unit = None
    if isinstance(ingredient, CountableIngredient):
        unit = str(ingredient.c_measurement_unit.value)
    elif isinstance(ingredient, UncountableIngredient):
        unit = str(ingredient.uc_measurement_unit.value)
    
    payload = {
        "event_type": event_type,
        "data": {
            "component_id": ingredient.component_id,
            "component_name": ingredient.component_name,
            "type": ingredient.type,
            "unit": unit
        }
    }

    producer = await kafka_manager.get_producer()
    await producer.send(INGREDIENT_EVENTS_TOPIC, value=payload)

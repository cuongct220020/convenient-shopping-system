from typing import Literal
from shared.shopping_shared.messaging.kafka_manager import kafka_manager
from shared.shopping_shared.messaging.topics import RECIPE_EVENTS_TOPIC
from models.recipe_component import Recipe, CountableIngredient, UncountableIngredient


async def publish_recipe_event(
    event_type: Literal["recipe_created", "recipe_updated", "recipe_deleted"],
    recipe: Recipe
) -> None:
    component_list = []
    for cl in recipe.component_list:
        component = cl.component
        if isinstance(component, Recipe):
            component_list.append(component.component_name)
        elif isinstance(component, (CountableIngredient, UncountableIngredient)):
            component_list.append(component.component_name)
    
    payload = {
        "event_type": event_type,
        "data": {
            "component_id": recipe.component_id,
            "component_name": recipe.component_name,
            "component_list": component_list
        }
    }

    producer = await kafka_manager.get_producer()
    await producer.send(RECIPE_EVENTS_TOPIC, value=payload)


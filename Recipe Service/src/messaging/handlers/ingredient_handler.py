from typing import Dict, Any
from core.es import get_es

INGREDIENT_INDEX = "ingredients"


async def handle_ingredient_upsert(data: Dict[str, Any]):
    es = get_es()
    component_id = data.get("component_id")
    
    document = {
        "component_id": component_id,
        "component_name": data.get("component_name"),
        "type": data.get("type"),
        "unit": data.get("unit")
    }
    
    await es.index(
        index=INGREDIENT_INDEX,
        id=str(component_id),
        document=document
    )


async def handle_ingredient_deleted(data: Dict[str, Any]):
    es = get_es()
    component_id = data.get("component_id")
    
    await es.delete(
        index=INGREDIENT_INDEX,
        id=str(component_id),
        ignore=[404]
    )

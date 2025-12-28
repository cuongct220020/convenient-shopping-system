from typing import Dict, Any
from core.es import get_es

async def handle_recipe_upsert(data: Dict[str, Any]):
    es = get_es()
    component_id = data.get("component_id")
    
    document = {
        "component_id": component_id,
        "component_name": data.get("component_name"),
        "component_list": data.get("component_list", [])
    }
    
    await es.index(
        index="recipes",
        id=str(component_id),
        document=document
    )


async def handle_recipe_deleted(data: Dict[str, Any]):
    es = get_es()
    component_id = data.get("component_id")
    
    await es.delete(
        index="recipes",
        id=str(component_id),
        ignore=[404]
    )


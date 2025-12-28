from typing import Dict, Any
from core.database import get_db
from models.component_existence import ComponentExistence


async def handle_component_existence_update(data: Dict[str, Any]):
    db = next(get_db())
    group_id = data.get("group_id")
    unit_names = data.get("unit_names", [])

    with db.begin():
        if not unit_names:
            db.query(ComponentExistence).filter(ComponentExistence.group_id == group_id).delete()
        else:
            existing = db.query(ComponentExistence).filter(ComponentExistence.group_id == group_id).first()
            if existing:
                existing.component_name_list = unit_names
            else:
                db_obj = ComponentExistence(
                    group_id=group_id,
                    component_name_list=unit_names
                )
                db.add(db_obj)

    db.close()


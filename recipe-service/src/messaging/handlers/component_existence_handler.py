import uuid
from typing import Dict, Any
from core.database import SessionLocal
from models.component_existence import ComponentExistence

def handle_component_existence_update(data: Dict[str, Any]):
    db = SessionLocal()
    try:
        group_id_raw = data.get("group_id")
        group_id = uuid.UUID(group_id_raw) if isinstance(group_id_raw, str) else group_id_raw
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
        
    except Exception as e:
        raise
    finally:
        db.close()


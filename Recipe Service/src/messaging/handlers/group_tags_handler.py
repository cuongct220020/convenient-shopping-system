from typing import Dict, Any
from core.database import get_db
from models.group_preference import GroupPreference


async def handle_group_tags_update(data: Dict[str, Any]):
    db = next(get_db())
    group_id = data.get("group_id")
    group_tag_list = data.get("group_tag_list", [])

    with db.begin():
        if not group_tag_list:
            db.query(GroupPreference).filter(GroupPreference.group_id == group_id).delete()
        else:
            existing = db.query(GroupPreference).filter(GroupPreference.group_id == group_id).first()
            if existing:
                existing.group_tag_list = group_tag_list
            else:
                db_obj = GroupPreference(
                    group_id=group_id,
                    group_tag_list=group_tag_list
                )
                db.add(db_obj)

    db.close()


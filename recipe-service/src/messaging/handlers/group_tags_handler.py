import uuid
from typing import Dict, Any
from core.database import get_db
from models.group_preference import GroupPreference


def handle_group_tags_update(data: Dict[str, Any]):
    db = next(get_db())
    try:
        user_id_raw = data.get("user_id")
        user_id = uuid.UUID(user_id_raw) if isinstance(user_id_raw, str) else user_id_raw
        if user_id is None:
            return

        user_tag_list = data.get("user_tag_list", [])

        user_group_ids: set[uuid.UUID] = set()
        raw_groups = data.get("user_group_list", [])
        if isinstance(raw_groups, list):
            for g in raw_groups:
                if isinstance(g, uuid.UUID):
                    user_group_ids.add(g)
                elif isinstance(g, str):
                    try:
                        user_group_ids.add(uuid.UUID(g))
                    except ValueError:
                        continue

        with db.begin():
            db.query(GroupPreference).filter(GroupPreference.user_id == user_id).delete()
            for group_id in user_group_ids:
                db.add(
                    GroupPreference(
                        user_id=user_id,
                        group_id=group_id,
                        user_tag_list=user_tag_list,
                    )
                )
    finally:
        db.close()
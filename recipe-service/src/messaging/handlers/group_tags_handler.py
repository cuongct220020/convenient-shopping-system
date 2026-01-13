import uuid
import json
import ast
from typing import Dict, Any, List
from sqlalchemy import select, delete
from core.database import get_db
from models.group_preference import GroupPreference
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("GroupTagsHandler")


def handle_group_tags_update(event: Dict[str, Any]):
    db = next(get_db())
    try:
        user_id = uuid.UUID(event.get("user_id")) if isinstance(event.get("user_id"), str) else event.get("user_id")
        tags = event.get("tags", [])
        list_group_ids_raw = event.get("list_group_ids", [])
        
        # Parse list_group_ids
        if isinstance(list_group_ids_raw, str):
            try:
                list_group_ids = json.loads(list_group_ids_raw)
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to parse list_group_ids as JSON: {list_group_ids_raw}, error: {e}")
                try:
                    list_group_ids = ast.literal_eval(list_group_ids_raw)
                except (ValueError, SyntaxError) as e:
                    logger.warning(f"Failed to parse list_group_ids as literal: {list_group_ids_raw}, error: {e}")
                    list_group_ids = []
        else:
            list_group_ids = list_group_ids_raw if isinstance(list_group_ids_raw, list) else []
            if not isinstance(list_group_ids_raw, list):
                logger.warning(f"list_group_ids is not a string or list: {type(list_group_ids_raw)}")

        # Convert group IDs to UUIDs
        group_ids: List[uuid.UUID] = []
        for group_id_str in list_group_ids:
            try:
                if isinstance(group_id_str, uuid.UUID):
                    group_ids.append(group_id_str)
                elif isinstance(group_id_str, str):
                    group_ids.append(uuid.UUID(group_id_str))
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to convert group_id to UUID: {group_id_str}, error: {e}")
                continue

        # Get existing preferences for this user
        stmt = select(GroupPreference).where(GroupPreference.user_id == user_id)
        existing_preferences = {
            pref.group_id: pref 
            for pref in db.execute(stmt).scalars().all()
        }

        with db.begin():
            for group_id in group_ids:
                if group_id in existing_preferences:
                    existing_preferences[group_id].user_tag_list = tags
                else:
                    db.add(
                        GroupPreference(
                            user_id=user_id,
                            group_id=group_id,
                            user_tag_list=tags,
                        )
                    )
            
            # Delete preferences for groups that are no longer in the list
            existing_group_ids = set(existing_preferences.keys())
            current_group_ids = set(group_ids)
            groups_to_delete = existing_group_ids - current_group_ids
            
            if groups_to_delete:
                delete_stmt = delete(GroupPreference).where(
                    GroupPreference.user_id == user_id,
                    GroupPreference.group_id.in_(groups_to_delete)
                )
                db.execute(delete_stmt)
        
        logger.info(f"Successfully processed group tags update: user_id={user_id}, groups={len(group_ids)}, tags={len(tags)}")
    except Exception as e:
        logger.error(f"Error processing group tags update: user_id={event.get('user_id')}, error={str(e)}", exc_info=True)
        raise
    finally:
        db.close()
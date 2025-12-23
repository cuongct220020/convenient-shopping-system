# user-service/app/services/user_tag_service.py
from typing import List, Dict
from uuid import UUID

from shopping_shared.exceptions import NotFound, BadRequest
from shopping_shared.utils.logger_utils import get_logger

from app.repositories.user_tag_repository import UserTagRepository
from app.schemas.user_tag_schema import (
    UserTagBulkAddSchema,
    UserTagDeleteSchema,
    UserTagUpdateByCategorySchema,
    UserTagsByCategoryResponseSchema
)

logger = get_logger("User Tag Service")


class UserTagService:
    """Service for handling user tags business logic."""

    def __init__(self, user_tag_repo: UserTagRepository):
        self.repository = user_tag_repo

    async def get_user_tags_grouped(
        self,
        user_id: UUID
    ) -> UserTagsByCategoryResponseSchema:
        """
        Get user's tags grouped by category.

        Returns:
            UserTagsByCategoryResponseSchema with tags grouped by category
        """
        grouped_dict = await self.repository.get_tags_grouped_by_category(user_id)

        response = UserTagsByCategoryResponseSchema(
            age=grouped_dict.get('age', []),
            medical=grouped_dict.get('medical', []),
            allergy=grouped_dict.get('allergy', []),
            diet=grouped_dict.get('diet', []),
            taste=grouped_dict.get('taste', [])
        )

        logger.info(f"Retrieved tags grouped by category for user {user_id}")
        return response

    async def add_tags(
        self,
        user_id: UUID,
        data: UserTagBulkAddSchema
    ) -> Dict[str, int]:
        """
        Add tags to user.

        Returns:
            Dict with 'added_count' key
        """
        added_count = await self.repository.add_tags(user_id, data.tag_values)

        logger.info(
            f"Added {added_count}/{len(data.tag_values)} tags to user {user_id}"
        )

        return {"added_count": added_count}

    async def remove_tags(
        self,
        user_id: UUID,
        data: UserTagDeleteSchema
    ) -> Dict[str, int]:
        """
        Remove tags from user.

        Returns:
            Dict with 'deleted_count' key
        """
        deleted_count = await self.repository.remove_tags(user_id, data.tag_values)

        if deleted_count == 0:
            logger.warning(f"No tags were deleted for user {user_id}")
        else:
            logger.info(f"Deleted {deleted_count} tags from user {user_id}")

        return {"deleted_count": deleted_count}

    async def update_tags_by_category(
        self,
        user_id: UUID,
        data: UserTagUpdateByCategorySchema
    ) -> Dict[str, any]:
        """
        Replace all tags in a specific category.

        Returns:
            Dict with 'category' and 'updated_count' keys
        """
        updated_count = await self.repository.replace_tags_by_category(
            user_id,
            data.category,
            data.tag_values
        )

        logger.info(
            f"Replaced {updated_count} tags in category '{data.category}' "
            f"for user {user_id}"
        )

        return {
            "category": data.category,
            "updated_count": updated_count
        }


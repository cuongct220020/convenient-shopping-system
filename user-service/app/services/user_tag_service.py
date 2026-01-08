# user-service/app/services/user_tag_service.py
from typing import Dict, List
from uuid import UUID

from app.models.user_tag import Tag
from app.repositories.user_tag_repository import UserTagRepository
from app.services.redis_service import redis_service
from app.schemas.user_tag_schema import (
    UserTagBulkAddSchema,
    UserTagDeleteSchema,
    UserTagsByCategorySchema,
    UserTagSchema,
    UserTagsResponseSchema
)

from shopping_shared.caching.redis_keys import RedisKeys
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("User Tag Service")


class UserTagService:
    def __init__(self, user_tag_repo: UserTagRepository):
        self.user_tag_repo = user_tag_repo

    async def get_user_tags_grouped(self, user_id: UUID) -> UserTagsResponseSchema:
        """Get user tags grouped by category with counts."""
        grouped_tags = await self.user_tag_repo.get_user_tags_by_category(user_id)
        
        # Convert to response schema
        age_tags = [self._tag_to_schema(tag) for tag in grouped_tags.get('age', [])]
        medical_tags = [self._tag_to_schema(tag) for tag in grouped_tags.get('medical', [])]
        allergy_tags = [self._tag_to_schema(tag) for tag in grouped_tags.get('allergy', [])]
        diet_tags = [self._tag_to_schema(tag) for tag in grouped_tags.get('diet', [])]
        taste_tags = [self._tag_to_schema(tag) for tag in grouped_tags.get('taste', [])]

        total_tags = sum(len(tags) for tags in grouped_tags.values())
        categories_count = {cat: len(tags) for cat, tags in grouped_tags.items()}

        return UserTagsResponseSchema(
            data=UserTagsByCategorySchema(
                age=age_tags,
                medical=medical_tags,
                allergy=allergy_tags,
                diet=diet_tags,
                taste=taste_tags
            ),
            total_tags=total_tags,
            categories_count=categories_count
        )

    async def get_user_tags_detailed(self, user_id: UUID) -> List[UserTagSchema]:
        """Get all user tags with detailed information."""
        tags = await self.user_tag_repo.get_user_tags_detailed(user_id)
        return [self._tag_to_schema(tag) for tag in tags]

    async def add_tags(self, user_id: UUID, data: UserTagBulkAddSchema) -> Dict[str, int]:
        """Add multiple tags to user."""
        count = await self.user_tag_repo.add_tags_to_user(user_id, data.tag_values)
        logger.info(f"Added {count} tags to user {user_id}")

        await redis_service.delete_key(RedisKeys.user_tags_key(str(user_id)))

        return {"added_count": count}

    async def remove_tags(self, user_id: UUID, data: UserTagDeleteSchema) -> Dict[str, int]:
        """Remove multiple tags from user."""
        count = await self.user_tag_repo.remove_tags_from_user(user_id, data.tag_values)
        logger.info(f"Removed {count} tags from user {user_id}")

        await redis_service.delete_key(RedisKeys.user_tags_key(str(user_id)))

        return {"removed_count": count}

    async def update_category_tags(self, user_id: UUID, category: str, tag_values: List[str]) -> Dict[str, int]:
        """Update all tags in a specific category."""
        count = await self.user_tag_repo.replace_category_tags(user_id, category, tag_values)
        logger.info(f"Updated {count} tags in category {category} for user {user_id}")

        await redis_service.delete_key(RedisKeys.user_tags_key(str(user_id)))

        return {"updated_count": count}

    @staticmethod
    def _tag_to_schema(tag: Tag) -> UserTagSchema:
        """Convert Tag model to UserTagSchema."""
        return UserTagSchema(
            id=tag.id,
            tag_value=tag.tag_value,
            tag_category=tag.tag_category,
            tag_name=tag.tag_name,
            description=tag.description,
            created_at=tag.created_at.isoformat() if tag.created_at else None
        )
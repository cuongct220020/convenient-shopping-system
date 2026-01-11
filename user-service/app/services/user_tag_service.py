# user-service/app/services/user_tag_service.py
from typing import Dict, List
from uuid import UUID
from datetime import datetime

from app.models.user_tag import Tag
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.repositories.user_tag_repository import UserTagRepository
from app.services.redis_service import redis_service
from app.schemas.user_tag_schema import (
    UserTagBulkAddSchema,
    UserTagDeleteSchema,
    UserTagsByCategorySchema,
    UserTagSchema,
    UserTagsResponseSchema
)
from app.services.kafka_service import kafka_service

from shopping_shared.caching.redis_keys import RedisKeys
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("User Tag Service")


class UserTagService:
    def __init__(self, user_tag_repo: UserTagRepository, group_membership_repo: GroupMembershipRepository):
        self.user_tag_repo = user_tag_repo
        self.group_membership_repo = group_membership_repo

    async def get_user_tags_grouped(self, user_id: UUID) -> UserTagsResponseSchema:
        """Get user tags grouped by category with counts."""
        grouped_tags = await self.user_tag_repo.get_user_tags_by_category(user_id)
        
        def process_tags(items):
            return [self._tag_to_schema(tag, updated_at) for tag, updated_at in items]

        # Convert to response schema
        age_tags = process_tags(grouped_tags.get('age', []))
        medical_tags = process_tags(grouped_tags.get('medical', []))
        allergy_tags = process_tags(grouped_tags.get('allergy', []))
        diet_tags = process_tags(grouped_tags.get('diet', []))
        taste_tags = process_tags(grouped_tags.get('taste', []))

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

    async def add_tags(
        self,
        user_id: UUID,
        username: str,
        email: str,
        data: UserTagBulkAddSchema
    ) -> Dict[str, int]:
        """Add multiple tags to user."""
        count = await self.user_tag_repo.add_tags_to_user(user_id, data.tag_values)
        logger.info(f"Added {count} tags to user {user_id}")

        await self._publish_tag_update(user_id, username, email)

        await redis_service.delete_key(RedisKeys.user_tags_key(str(user_id)))

        return {"added_count": count}


    async def remove_tags(
        self, 
        user_id: UUID, 
        username: str,
        email: str,
        data: UserTagDeleteSchema
    ) -> Dict[str, int]:
        """Remove multiple tags from user."""
        count = await self.user_tag_repo.remove_tags_from_user(user_id, data.tag_values)
        logger.info(f"Removed {count} tags from user {user_id}")

        await self._publish_tag_update(user_id, username, email)

        await redis_service.delete_key(RedisKeys.user_tags_key(str(user_id)))

        return {"removed_count": count}


    async def update_category_tags(
        self, 
        user_id: UUID, 
        username: str,
        email: str,
        category: str, 
        tag_values: List[str]
    ) -> Dict[str, int]:
        """Update all tags in a specific category."""
        count = await self.user_tag_repo.replace_category_tags(user_id, category, tag_values)
        logger.info(f"Updated {count} tags in category {category} for user {user_id}")

        await self._publish_tag_update(user_id, username, email)

        await redis_service.delete_key(RedisKeys.user_tags_key(str(user_id)))

        return {"updated_count": count}


    async def _publish_tag_update(self, user_id: UUID, username: str, email: str) -> None:
        """Helper to fetch updated data and publish Kafka message."""
        try:
            # 1. Get current tags (values only)
            tags = await self.user_tag_repo.get_user_tag_values(user_id)

            # 2. Get user groups
            groups = await self.group_membership_repo.get_user_groups(user_id)
            group_ids = [str(group.group_id) for group, _ in groups]

            # 3. Publish message
            await kafka_service.publish_user_update_tag_message(
                user_id=str(user_id),
                username=username,
                email=email,
                tags=tags,
                list_group_ids=group_ids
            )
        except Exception as e:
            logger.error(f"Failed to publish tag update event for user {user_id}: {e}")
            # Non-blocking: We don't want to fail the API request if Kafka fails,
            # but we should log it. Ideally we might want a retry mechanism or transactional outbox.

    @staticmethod
    def _tag_to_schema(tag: Tag, user_tag_updated_at: datetime = None) -> UserTagSchema:
        """Convert Tag model to UserTagSchema."""
        return UserTagSchema(
            id=tag.id,
            tag_value=tag.tag_value,
            tag_category=tag.tag_category,
            tag_name=tag.tag_name,
            description=tag.description,
            updated_at=user_tag_updated_at.isoformat() if user_tag_updated_at else None
        )
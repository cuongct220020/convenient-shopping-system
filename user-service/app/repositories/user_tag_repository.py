# user-service/app/repositories/user_tag_repository.py
from typing import List, Dict
from uuid import UUID
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shopping_shared.databases.base_repository import BaseRepository
from app.models.user_tag import Tag, UserTag
from app.models.user import User


class TagRepository(BaseRepository[Tag, None, None]):
    """Repository for Tag master table."""

    def __init__(self, session: AsyncSession):
        super().__init__(Tag, session)

    async def get_by_tag_value(self, tag_value: str) -> Tag | None:
        """Get tag by its value (e.g., '0212')."""
        query = select(Tag).where(Tag.tag_value == tag_value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_tag_values(self, tag_values: List[str]) -> List[Tag]:
        """Get multiple tags by their values."""
        query = select(Tag).where(Tag.tag_value.in_(tag_values))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> List[Tag]:
        """Get all tags in a specific category."""
        query = select(Tag).where(Tag.tag_category == category).order_by(Tag.tag_value)
        result = await self.session.execute(query)
        return list(result.scalars().all())


class UserTagRepository:
    """
    Repository for managing User ←→ Tag Many-to-Many relationship.
    Uses junction table user_tags.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.tag_repo = TagRepository(session)

    async def get_user_tags(self, user_id: UUID) -> List[Tag]:
        """
        Get all tags for a user.
        Returns Tag objects, not UserTag junction records.
        """
        query = (
            select(Tag)
            .join(UserTag, UserTag.tag_id == Tag.id)
            .where(UserTag.user_id == user_id)
            .order_by(Tag.tag_category, Tag.tag_value)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_tags_by_category(self, user_id: UUID, category: str) -> List[Tag]:
        """Get user's tags filtered by category."""
        query = (
            select(Tag)
            .join(UserTag, UserTag.tag_id == Tag.id)
            .where(
                and_(
                    UserTag.user_id == user_id,
                    Tag.tag_category == category
                )
            )
            .order_by(Tag.tag_value)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_tags_grouped_by_category(self, user_id: UUID) -> Dict[str, List[str]]:
        """
        Get user's tags grouped by category.
        Returns dict: {'age': ['0102'], 'medical': ['0212', '0201'], ...}
        """
        tags = await self.get_user_tags(user_id)

        grouped = {
            'age': [],
            'medical': [],
            'allergy': [],
            'diet': [],
            'taste': []
        }

        for tag in tags:
            if tag.tag_category in grouped:
                grouped[tag.tag_category].append(tag.tag_value)

        return grouped

    async def add_tags(self, user_id: UUID, tag_values: List[str]) -> int:
        """
        Add tags to user.

        Args:
            user_id: User ID
            tag_values: List of tag codes (e.g., ['0212', '0300'])

        Returns:
            Number of tags actually added (skips duplicates)
        """
        # Get Tag objects by values
        tags = await self.tag_repo.get_by_tag_values(tag_values)

        if not tags:
            return 0

        # Get existing UserTag associations
        existing_query = select(UserTag.tag_id).where(UserTag.user_id == user_id)
        existing_result = await self.session.execute(existing_query)
        existing_tag_ids = {row[0] for row in existing_result.all()}

        # Add only new associations
        added_count = 0
        for tag in tags:
            if tag.id not in existing_tag_ids:
                user_tag = UserTag(user_id=user_id, tag_id=tag.id)
                self.session.add(user_tag)
                added_count += 1

        if added_count > 0:
            await self.session.flush()

        return added_count

    async def remove_tags(self, user_id: UUID, tag_values: List[str]) -> int:
        """
        Remove tags from user.

        Returns:
            Number of tags actually removed
        """
        # Get Tag IDs by values
        tags = await self.tag_repo.get_by_tag_values(tag_values)
        tag_ids = [tag.id for tag in tags]

        if not tag_ids:
            return 0

        # Delete UserTag associations
        query = delete(UserTag).where(
            and_(
                UserTag.user_id == user_id,
                UserTag.tag_id.in_(tag_ids)
            )
        )
        result = await self.session.execute(query)
        await self.session.flush()

        return result.rowcount

    async def remove_all_tags(self, user_id: UUID) -> int:
        """Remove all tags for a user."""
        query = delete(UserTag).where(UserTag.user_id == user_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount

    async def replace_tags_by_category(
        self,
        user_id: UUID,
        category: str,
        new_tag_values: List[str]
    ) -> int:
        """
        Replace all tags in a specific category with new ones.

        Args:
            user_id: User ID
            category: Category to replace
            new_tag_values: New tag values for this category

        Returns:
            Number of tags in the category after replacement
        """
        # Get all tags in category (from Tag table)
        category_tags = await self.tag_repo.get_by_category(category)
        category_tag_ids = [tag.id for tag in category_tags]

        # Delete existing UserTag associations for this category
        if category_tag_ids:
            await self.session.execute(
                delete(UserTag).where(
                    and_(
                        UserTag.user_id == user_id,
                        UserTag.tag_id.in_(category_tag_ids)
                    )
                )
            )
            await self.session.flush()

        # Add new tags
        if new_tag_values:
            await self.add_tags(user_id, new_tag_values)

        return len(new_tag_values)


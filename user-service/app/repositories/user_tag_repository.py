# user-service/app/repositories/user_tag_repository.py
from datetime import datetime
from typing import List, Dict, Optional, Sequence
from uuid import UUID
from sqlalchemy import select, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_tag import Tag, UserTag

from shopping_shared.databases.base_repository import BaseRepository


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
    Repository for managing User ←→ Tag Many-to-Many relationship. Uses junction table user_tags.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.tag_repo = TagRepository(session)

    async def get_user_tags_by_category(self, user_id: UUID) -> Dict[str, List[tuple[Tag, datetime]]]:
        """Get all user tags grouped by category with optimized query."""
        from datetime import datetime
        stmt = (
            select(Tag, UserTag.updated_at)
            .join(UserTag)
            .where(UserTag.user_id == user_id)
            .order_by(Tag.tag_category, Tag.tag_value)
        )
        result = await self.session.execute(stmt)
        # Result contains tuples of (Tag, updated_at)
        rows = result.all()

        # Group tags by category
        grouped_tags: Dict[str, List[tuple[Tag, datetime]]] = {
            'age': [],
            'medical': [],
            'allergy': [],
            'diet': [],
            'taste': []
        }

        for tag, updated_at in rows:
            if tag.tag_category in grouped_tags:
                grouped_tags[tag.tag_category].append((tag, updated_at))

        return grouped_tags

    async def get_user_tags_detailed(self, user_id: UUID) -> Sequence[Tag]:
        """Get all user tags with detailed information."""
        stmt = (
            select(Tag)
            .join(UserTag)
            .where(UserTag.user_id == user_id)
            .order_by(Tag.tag_category, Tag.tag_name)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_tag_values(self, user_id: UUID) -> List[str]:
        """Get only tag values for a user - optimized for validation."""
        stmt = (
            select(Tag.tag_value)
            .join(UserTag)
            .where(UserTag.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def add_tags_to_user(self, user_id: UUID, tag_values: List[str]) -> int:
        """Add multiple tags to user with validation."""
        # Get existing tags to avoid duplicates
        existing_values = await self.get_user_tag_values(user_id)
        new_values = [v for v in tag_values if v not in existing_values]

        if not new_values:
            return 0

        # Get tag IDs for the values
        tag_stmt = select(Tag.id).where(Tag.tag_value.in_(new_values))
        result = await self.session.execute(tag_stmt)
        tag_ids = [row[0] for row in result.all()]

        # Create UserTag associations
        # Use Core insert to avoid SQLAlchemy insert many values issue with composite PK + UUID
        from sqlalchemy import insert
        insert_data = [
            {"user_id": user_id, "tag_id": tag_id}
            for tag_id in tag_ids
        ]

        if insert_data:
            stmt = insert(UserTag).values(insert_data)
            await self.session.execute(stmt)
            await self.session.flush()

        return len(insert_data)

    async def remove_tags_from_user(self, user_id: UUID, tag_values: List[str]) -> int:
        """Remove multiple tags from user."""
        # Get tag IDs for the values
        tag_stmt = select(Tag.id).where(Tag.tag_value.in_(tag_values))
        result = await self.session.execute(tag_stmt)
        tag_ids = [row[0] for row in result.all()]

        if not tag_ids:
            return 0

        # Delete UserTag associations
        delete_stmt = (
            delete(UserTag)
            .where(
                and_(
                    UserTag.user_id == user_id,
                    UserTag.tag_id.in_(tag_ids)
                )
            )
        )
        result = await self.session.execute(delete_stmt)
        await self.session.flush()

        return result.rowcount

    async def replace_category_tags(self, user_id: UUID, category: str, tag_values: List[str]) -> int:
        """Replace all tags in a specific category."""
        # First, remove all tags in this category
        existing_category_tags_stmt = (
            select(Tag.id)
            .join(UserTag)
            .where(
                and_(
                    UserTag.user_id == user_id,
                    Tag.tag_category == category
                )
            )
        )
        result = await self.session.execute(existing_category_tags_stmt)
        existing_category_tag_ids = [row[0] for row in result.all()]

        if existing_category_tag_ids:
            delete_stmt = (
                delete(UserTag)
                .where(
                    and_(
                        UserTag.user_id == user_id,
                        UserTag.tag_id.in_(existing_category_tag_ids)
                    )
                )
            )
            await self.session.execute(delete_stmt)

        # Add new tags if provided
        if tag_values:
            new_tag_ids_stmt = select(Tag.id).where(Tag.tag_value.in_(tag_values))
            result = await self.session.execute(new_tag_ids_stmt)
            new_tag_ids = [row[0] for row in result.all()]

            # Create new associations
            # Use Core insert
            from sqlalchemy import insert
            insert_data = [
                {"user_id": user_id, "tag_id": tag_id}
                for tag_id in new_tag_ids
            ]

            if insert_data:
                stmt = insert(UserTag).values(insert_data)
                await self.session.execute(stmt)

        await self.session.flush()
        return len(tag_values) if tag_values else 0

    async def get_available_tags_by_category(self, category: Optional[str] = None) -> Sequence[Tag]:
        """Get available tags, optionally filtered by category."""
        stmt = select(Tag)
        if category:
            stmt = stmt.where(Tag.tag_category == category)
        stmt = stmt.order_by(Tag.tag_category, Tag.tag_name)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_tags_count(self, user_id: UUID) -> int:
        """Get total count of user's tags."""
        stmt = (
            select(func.count(UserTag.user_id))
            .where(UserTag.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

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
#!/usr/bin/env python3
"""
Script to seed initial tags into the database.

This script populates the 'tags' table with data from the Enums defined in 
app.enums.tags (AgeTag, MedicalConditionTag, AllergyTag, etc.).
It checks if a tag exists before inserting to prevent duplicates.
"""

import asyncio
import sys
from pathlib import Path

# Add the shared module to the path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.models.user_tag import Tag
from app.enums.tags import (
    AgeTag,
    MedicalConditionTag,
    AllergyTag,
    SpecialDietTag,
    TastePreferenceTag
)
from shopping_shared.databases.database_manager import database_manager as postgres_db
from app.config import Config


# Mapping of Enum classes to their category names and descriptions
TAG_CATEGORIES = {
    'age': AgeTag,
    'medical': MedicalConditionTag,
    'allergy': AllergyTag,
    'diet': SpecialDietTag,
    'taste': TastePreferenceTag
}

# Helper mapping for human-readable descriptions (Optional: You could also add this to the Enum itself)
# For now, we generate a simple description based on the name.
def get_tag_description(tag_name: str, category: str) -> str:
    return f"{tag_name.replace('_', ' ').title()} ({category})"


async def seed_tags():
    """
    Seed tags from Enums into the database.
    """
    # Get database URI from config
    db_uri = Config.POSTGRESQL.DATABASE_URI
    
    # Setup database connection
    await postgres_db.setup(database_uri=db_uri, debug=Config.RUN_SETTING.get('debug', True))
    
    async with postgres_db.get_session() as session:
        print(f"🌱 Starting Tag Seeding...")
        
        total_added = 0
        total_skipped = 0
        
        for category, enum_class in TAG_CATEGORIES.items():
            print(f"\nProcessing category: {category.upper()}")
            
            for tag_enum in enum_class:
                tag_value = tag_enum.value
                tag_name = tag_enum.name
                description = get_tag_description(tag_name, category)
                
                # Check if tag already exists
                stmt = select(Tag).where(Tag.tag_value == tag_value)
                result = await session.execute(stmt)
                existing_tag = result.scalar_one_or_none()
                
                if existing_tag:
                    print(f"  ⏭️  Skipped {tag_name} ({tag_value}) - Already exists")
                    total_skipped += 1
                else:
                    new_tag = Tag(
                        tag_value=tag_value,
                        tag_category=category,
                        tag_name=tag_name,
                        description=description
                    )
                    session.add(new_tag)
                    print(f"  ✅ Added {tag_name} ({tag_value})")
                    total_added += 1
        
        try:
            await session.commit()
            print("\n" + "="*50)
            print(f"🎉 Tag Seeding Completed!")
            print(f"   Added: {total_added}")
            print(f"   Skipped: {total_skipped}")
            print("="*50)
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error seeding tags: {str(e)}")


def main():
    asyncio.run(seed_tags())


if __name__ == "__main__":
    main()

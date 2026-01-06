"""add indexes

Revision ID: 2486565d29d7
Revises: 025c38f150d8
Create Date: 2026-01-06 17:17:05.892342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2486565d29d7'
down_revision: Union[str, Sequence[str], None] = '025c38f150d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Meals: common filters in MealCommandHandler + expire job
    op.create_index("ix_meals_date", "meals", ["date"], unique=False)
    op.create_index("ix_meals_group_id", "meals", ["group_id"], unique=False)
    op.create_index("ix_meals_meal_type", "meals", ["meal_type"], unique=False)
    op.create_index("ix_meals_meal_status", "meals", ["meal_status"], unique=False)

    # RecipeList: often need all recipes by meal_id
    op.create_index("ix_recipe_lists_meal_id", "recipe_lists", ["meal_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_recipe_lists_meal_id", table_name="recipe_lists")
    op.drop_index("ix_meals_meal_status", table_name="meals")
    op.drop_index("ix_meals_meal_type", table_name="meals")
    op.drop_index("ix_meals_group_id", table_name="meals")
    op.drop_index("ix_meals_date", table_name="meals")

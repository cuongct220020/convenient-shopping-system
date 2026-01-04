"""add category

Revision ID: eeb5dd7e0970
Revises: cd3e7c8f4548
Create Date: 2025-11-26 08:31:11.660832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eeb5dd7e0970'
down_revision: Union[str, Sequence[str], None] = 'cd3e7c8f4548'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    category_enum = sa.Enum(
        'alcoholic_beverages', 'beverages', 'cakes', 'candies', 'cereals_grains',
        'cold_cuts', 'dried_fruits', 'fresh_fruits', 'fresh_meat', 'fruit_jams',
        'grains_staples', 'icecream_cheese', 'instant_foods', 'milk', 'others',
        'seafood_fishballs', 'seasonings', 'snacks', 'vegetables', 'yogurt',
        name='category'
    )
    category_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'ingredients',
        sa.Column('category', category_enum, nullable=False, server_default='others')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('ingredients', 'category')

    category_enum = sa.Enum(
        'alcoholic_beverages', 'beverages', 'cakes', 'candies', 'cereals_grains',
        'cold_cuts', 'dried_fruits', 'fresh_fruits', 'fresh_meat', 'fruit_jams',
        'grains_staples', 'icecream_cheese', 'instant_foods', 'milk', 'others',
        'seafood_fishballs', 'seasonings', 'snacks', 'vegetables', 'yogurt',
        name='category'
    )
    category_enum.drop(op.get_bind(), checkfirst=True)


"""add indexes

Revision ID: 661e3740eabb
Revises: 6c175f4c9cab
Create Date: 2026-01-06 16:53:10.740528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '661e3740eabb'
down_revision: Union[str, Sequence[str], None] = '6c175f4c9cab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NOTE:
    # - Using Postgres-specific indexes because we rely on:
    #   - ILIKE '%keyword%' searches -> pg_trgm + GIN trigram ops
    #   - JSONB contains -> GIN JSONB
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Ingredient filtering
    op.create_index(
        "ix_ingredients_category",
        "ingredients",
        ["category"],
        unique=False,
    )

    # ILIKE searches on component_name (fuzzy substring)
    op.create_index(
        "ix_countable_ingredients_component_name_trgm",
        "countable_ingredients",
        ["component_name"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"component_name": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_uncountable_ingredients_component_name_trgm",
        "uncountable_ingredients",
        ["component_name"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"component_name": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_recipes_component_name_trgm",
        "recipes",
        ["component_name"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"component_name": "gin_trgm_ops"},
    )

    # JSONB containment searches on keywords
    op.create_index(
        "ix_recipes_keywords_gin",
        "recipes",
        ["keywords"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_recipes_keywords_gin", table_name="recipes")
    op.drop_index("ix_recipes_component_name_trgm", table_name="recipes")
    op.drop_index("ix_uncountable_ingredients_component_name_trgm", table_name="uncountable_ingredients")
    op.drop_index("ix_countable_ingredients_component_name_trgm", table_name="countable_ingredients")
    op.drop_index("ix_ingredients_category", table_name="ingredients")

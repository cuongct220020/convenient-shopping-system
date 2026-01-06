"""add indexes

Revision ID: 12ff2489bf9b
Revises: 6da8e0492236
Create Date: 2026-01-06 17:12:43.407115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12ff2489bf9b'
down_revision: Union[str, Sequence[str], None] = '6da8e0492236'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Shopping plans: common filters + sorting fields
    op.create_index("ix_shopping_plans_group_id", "shopping_plans", ["group_id"], unique=False)
    op.create_index("ix_shopping_plans_plan_status", "shopping_plans", ["plan_status"], unique=False)
    op.create_index("ix_shopping_plans_last_modified", "shopping_plans", ["last_modified"], unique=False)
    op.create_index("ix_shopping_plans_deadline", "shopping_plans", ["deadline"], unique=False)

    # Storages: join/filter via group_id
    op.create_index("ix_storages_group_id", "storages", ["group_id"], unique=False)

    # Storable units: common filters / joins
    op.create_index("ix_storable_units_storage_id", "storable_units", ["storage_id"], unique=False)
    op.create_index("ix_storable_units_unit_name", "storable_units", ["unit_name"], unique=False)
    op.create_index("ix_storable_units_component_id", "storable_units", ["component_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_storable_units_component_id", table_name="storable_units")
    op.drop_index("ix_storable_units_unit_name", table_name="storable_units")
    op.drop_index("ix_storable_units_storage_id", table_name="storable_units")
    op.drop_index("ix_storages_group_id", table_name="storages")
    op.drop_index("ix_shopping_plans_deadline", table_name="shopping_plans")
    op.drop_index("ix_shopping_plans_last_modified", table_name="shopping_plans")
    op.drop_index("ix_shopping_plans_plan_status", table_name="shopping_plans")
    op.drop_index("ix_shopping_plans_group_id", table_name="shopping_plans")

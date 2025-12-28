"""drop recipe_ingredient_flattened materialized view

Revision ID: 88b0157da878
Revises: a1268fb19b84
Create Date: 2025-12-19 00:27:24.227878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88b0157da878'
down_revision: Union[str, Sequence[str], None] = 'a1268fb19b84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
            DROP MATERIALIZED VIEW IF EXISTS recipe_ingredient_flattened CASCADE;
        """)


def downgrade() -> None:
    """Downgrade schema."""
    pass

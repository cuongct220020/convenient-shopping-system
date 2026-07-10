"""even more countable unit

Revision ID: 5d4d44b2f032
Revises: 661e3740eabb
Create Date: 2026-01-06 18:17:23.749446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d4d44b2f032'
down_revision: Union[str, Sequence[str], None] = '661e3740eabb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE cmeasurementunit ADD VALUE 'LA'")
    op.execute("ALTER TYPE cmeasurementunit ADD VALUE 'HOP'")
    op.execute("ALTER TYPE cmeasurementunit ADD VALUE 'CAI'")

def downgrade() -> None:
    """Downgrade schema."""
    pass

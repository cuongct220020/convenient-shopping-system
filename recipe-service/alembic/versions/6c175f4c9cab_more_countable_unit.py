"""more countable unit

Revision ID: 6c175f4c9cab
Revises: 3c9be40ccf27
Create Date: 2025-12-31 08:41:32.762854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c175f4c9cab'
down_revision: Union[str, Sequence[str], None] = '3c9be40ccf27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute("ALTER TYPE cmeasurementunit ADD VALUE 'CON'")
    op.execute("ALTER TYPE cmeasurementunit ADD VALUE 'VIEN'")
    op.execute("ALTER TYPE cmeasurementunit ADD VALUE 'TUI'")
    op.execute("ALTER TYPE cmeasurementunit ADD VALUE 'CAY'")
    op.execute("ALTER TYPE cmeasurementunit ADD VALUE 'LAT'")
    op.execute("ALTER TYPE cmeasurementunit ADD VALUE 'KHUC'")

def downgrade():
    pass

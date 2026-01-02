"""remove description, add level

Revision ID: a1268fb19b84
Revises: eeb5dd7e0970
Create Date: 2025-12-03 19:08:12.780689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1268fb19b84'
down_revision: Union[str, Sequence[str], None] = 'eeb5dd7e0970'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    level_enum = sa.Enum('EASY', 'MEDIUM', 'HARD', name='level')
    level_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('recipes', sa.Column('level', level_enum, nullable=True))
    op.drop_column('recipes', 'description')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('recipes', sa.Column('description', sa.VARCHAR(), nullable=True))
    op.drop_column('recipes', 'level')
    level_enum = sa.Enum('EASY', 'MEDIUM', 'HARD', name='level')
    level_enum.drop(op.get_bind(), checkfirst=True)

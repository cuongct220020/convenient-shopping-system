"""make user names nullable

Revision ID: aba394e8ae7f
Revises: 2935629a1caa
Create Date: 2025-12-28 11:33:22.820396+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aba394e8ae7f'
down_revision: Union[str, Sequence[str], None] = '2935629a1caa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'first_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('users', 'last_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'last_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('users', 'first_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
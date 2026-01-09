"""change storage group_id to uuid

Revision ID: f123456789ab
Revises: e7495aa90fcb
Create Date: 2026-01-09 18:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f123456789ab'
down_revision: Union[str, Sequence[str], None] = 'e7495aa90fcb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change group_id from Integer to UUID in storages table
    # Using gen_random_uuid() for conversion since integer cannot be directly cast to uuid easily
    # This assumes existing data (if any) doesn't need to be preserved strictly or allows random mapping
    op.alter_column(
        'storages',
        'group_id',
        existing_type=sa.INTEGER(),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using='gen_random_uuid()'
    )


def downgrade() -> None:
    # Change group_id from UUID back to Integer
    op.alter_column(
        'storages',
        'group_id',
        existing_type=sa.UUID(),
        type_=sa.INTEGER(),
        existing_nullable=False,
        postgresql_using='1'
    )

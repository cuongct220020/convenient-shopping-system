"""change group_id from int to uuid

Revision ID: 938918bf7c02
Revises: 5d4d44b2f032
Create Date: 2026-01-06 22:19:07.381968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '938918bf7c02'
down_revision: Union[str, Sequence[str], None] = '5d4d44b2f032'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change group_id from Integer to UUID in component_existence table
    op.alter_column(
        'component_existence',
        'group_id',
        existing_type=sa.INTEGER(),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using='gen_random_uuid()'
    )

    # Change group_id from Integer to UUID in group_preferences table
    op.alter_column(
        'group_preferences',
        'group_id',
        existing_type=sa.INTEGER(),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using='gen_random_uuid()'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Change group_id from UUID back to Integer in component_existence table
    op.alter_column(
        'component_existence',
        'group_id',
        existing_type=sa.UUID(),
        type_=sa.INTEGER(),
        existing_nullable=False,
        postgresql_using='1'
    )

    # Change group_id from UUID back to Integer in group_preferences table
    op.alter_column(
        'group_preferences',
        'group_id',
        existing_type=sa.UUID(),
        type_=sa.INTEGER(),
        existing_nullable=False,
        postgresql_using='1'
    )

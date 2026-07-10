"""change group_id assigner_id assignee_id from int to uuid

Revision ID: e7495aa90fcb
Revises: 12ff2489bf9b
Create Date: 2026-01-06 22:29:19.307431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e7495aa90fcb'
down_revision: Union[str, Sequence[str], None] = '12ff2489bf9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change group_id from Integer to UUID
    op.alter_column('shopping_plans', 'group_id',
               existing_type=sa.Integer(),
               type_=postgresql.UUID(as_uuid=True),
               existing_nullable=False,
                postgresql_using='gen_random_uuid()')
    
    # Change assigner_id from Integer to UUID
    op.alter_column('shopping_plans', 'assigner_id',
               existing_type=sa.Integer(),
               type_=postgresql.UUID(as_uuid=True),
               existing_nullable=False,
                postgresql_using='gen_random_uuid()')
    
    # Change assignee_id from Integer to UUID
    op.alter_column('shopping_plans', 'assignee_id',
               existing_type=sa.Integer(),
               type_=postgresql.UUID(as_uuid=True),
               existing_nullable=True,
                postgresql_using='gen_random_uuid()')


def downgrade() -> None:
    """Downgrade schema."""
    # Change assignee_id back from UUID to Integer
    op.alter_column('shopping_plans', 'assignee_id',
               existing_type=postgresql.UUID(as_uuid=True),
               type_=sa.Integer(),
               existing_nullable=True,
                postgresql_using='1')
    
    # Change assigner_id back from UUID to Integer
    op.alter_column('shopping_plans', 'assigner_id',
               existing_type=postgresql.UUID(as_uuid=True),
               type_=sa.Integer(),
               existing_nullable=False,
                postgresql_using='1')
    
    # Change group_id back from UUID to Integer
    op.alter_column('shopping_plans', 'group_id',
               existing_type=postgresql.UUID(as_uuid=True),
               type_=sa.Integer(),
               existing_nullable=False,
                postgresql_using='1')

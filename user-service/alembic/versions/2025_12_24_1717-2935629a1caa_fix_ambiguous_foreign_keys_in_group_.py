"""fix_ambiguous_foreign_keys_in_group_memberships

Revision ID: 2935629a1caa
Revises: cffbc8170d44
Create Date: 2025-12-24 17:17:01.753161+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2935629a1caa'
down_revision: Union[str, Sequence[str], None] = 'cffbc8170d44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # No schema changes needed - only relationship updates in SQLAlchemy models
    # The database structure remains the same, only the ORM mappings are updated
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # No schema changes to revert - only relationship updates in SQLAlchemy models
    pass

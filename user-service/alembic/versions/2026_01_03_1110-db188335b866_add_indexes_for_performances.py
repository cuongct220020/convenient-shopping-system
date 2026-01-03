"""add_indexes_for_performances

Revision ID: db188335b866
Revises: aba394e8ae7f
Create Date: 2026-01-03 11:10:13.409100+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db188335b866'
down_revision: Union[str, Sequence[str], None] = 'aba394e8ae7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add single-column indexes based on current models
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_system_role', 'users', ['system_role'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    op.create_index('ix_family_groups_group_name', 'family_groups', ['group_name'])
    op.create_index('ix_family_groups_created_by_user_id', 'family_groups', ['created_by_user_id'])
    op.create_index('ix_family_groups_created_at', 'family_groups', ['created_at'])

    op.create_index('ix_user_identity_profiles_user_id', 'user_identity_profiles', ['user_id'])
    op.create_index('ix_user_health_profiles_user_id', 'user_health_profiles', ['user_id'])

    op.create_index('ix_group_memberships_user_id', 'group_memberships', ['user_id'])
    op.create_index('ix_group_memberships_group_id', 'group_memberships', ['group_id'])
    op.create_index('ix_group_memberships_role', 'group_memberships', ['role'])

    op.create_index('ix_user_tags_user_id', 'user_tags', ['user_id'])
    op.create_index('ix_user_tags_tag_id', 'user_tags', ['tag_id'])

    op.create_index('ix_tags_tag_category', 'tags', ['tag_category'])

    # Add composite indexes based on current models
    op.create_index('ix_group_memberships_user_id_group_id', 'group_memberships', ['user_id', 'group_id'])
    op.create_index('ix_group_memberships_group_id_user_id', 'group_memberships', ['group_id', 'user_id'])
    op.create_index('ix_user_tags_user_id_tag_id', 'user_tags', ['user_id', 'tag_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop composite indexes
    op.drop_index('ix_user_tags_user_id_tag_id', table_name='user_tags')
    op.drop_index('ix_group_memberships_group_id_user_id', table_name='group_memberships')
    op.drop_index('ix_group_memberships_user_id_group_id', table_name='group_memberships')

    # Drop single-column indexes
    op.drop_index('ix_tags_tag_category', table_name='tags')
    op.drop_index('ix_user_tags_tag_id', table_name='user_tags')
    op.drop_index('ix_user_tags_user_id', table_name='user_tags')
    op.drop_index('ix_group_memberships_role', table_name='group_memberships')
    op.drop_index('ix_group_memberships_group_id', table_name='group_memberships')
    op.drop_index('ix_group_memberships_user_id', table_name='group_memberships')
    op.drop_index('ix_user_health_profiles_user_id', table_name='user_health_profiles')
    op.drop_index('ix_user_identity_profiles_user_id', table_name='user_identity_profiles')
    op.drop_index('ix_family_groups_created_at', table_name='family_groups')
    op.drop_index('ix_family_groups_created_by_user_id', table_name='family_groups')
    op.drop_index('ix_family_groups_group_name', table_name='family_groups')
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_system_role', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')

"""admin account activation flag

Revision ID: 0003_admin_is_active
Revises: 0002_roles_approval_map
Create Date: 2026-08-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_admin_is_active"
down_revision: Union[str, None] = "0002_roles_approval_map"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("admin_users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    op.drop_column("admin_users", "is_active")

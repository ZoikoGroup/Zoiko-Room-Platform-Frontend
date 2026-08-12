"""admin roles, listing ownership/approval, map coordinates

Revision ID: 0002_roles_approval_map
Revises: 0001_initial
Create Date: 2026-08-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_roles_approval_map"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("admin_users", sa.Column("role", sa.String(20), nullable=False, server_default=sa.text("'admin'")))

    op.add_column("listings", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("listings", sa.Column("longitude", sa.Float(), nullable=True))
    op.add_column("listings", sa.Column("approval_status", sa.String(20), nullable=False, server_default=sa.text("'pending'")))
    # Nullable at first so existing rows can backfill, then tightened to NOT NULL.
    op.add_column("listings", sa.Column("owner_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True))
    op.execute(
        "UPDATE listings SET owner_id = (SELECT id FROM admin_users ORDER BY id LIMIT 1), approval_status = 'approved'"
    )
    op.alter_column("listings", "owner_id", nullable=False)


def downgrade() -> None:
    op.drop_column("listings", "owner_id")
    op.drop_column("listings", "approval_status")
    op.drop_column("listings", "longitude")
    op.drop_column("listings", "latitude")
    op.drop_column("admin_users", "role")

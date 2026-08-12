"""admin self-registration approval status

Revision ID: 0004_admin_approval_status
Revises: 0003_admin_is_active
Create Date: 2026-08-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_admin_approval_status"
down_revision: Union[str, None] = "0003_admin_is_active"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing accounts were all created directly by a super admin, so they're
    # already trusted -- default them to 'approved' rather than 'pending'.
    op.add_column(
        "admin_users", sa.Column("approval_status", sa.String(20), nullable=False, server_default=sa.text("'approved'"))
    )


def downgrade() -> None:
    op.drop_column("admin_users", "approval_status")

"""add listing rejection_reason

Revision ID: 022bda4d123a
Revises: 12173435b59e
Create Date: 2026-09-01 08:19:57.263184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '022bda4d123a'
down_revision: Union[str, None] = '12173435b59e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "listings",
        sa.Column("rejection_reason", sa.String(1000), nullable=False, server_default=sa.text("''")),
    )


def downgrade() -> None:
    op.drop_column("listings", "rejection_reason")

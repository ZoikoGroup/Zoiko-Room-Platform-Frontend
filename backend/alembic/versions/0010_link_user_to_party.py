"""link user_accounts to parties (one-to-many)

Revision ID: 0010_link_user_to_party
Revises: 0009_user_account_table
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010_link_user_to_party"
down_revision: Union[str, None] = "0009_user_account_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # user_accounts table already has party_id FK from 0009, so no changes needed here
    # This migration is a placeholder to maintain proper revision order
    pass


def downgrade() -> None:
    # No changes to revert
    pass

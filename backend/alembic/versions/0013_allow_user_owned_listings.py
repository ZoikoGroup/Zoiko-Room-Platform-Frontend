"""allow party-owned listings without an admin owner

Revision ID: 0013_allow_user_owned_listings
Revises: 0012_sublet_model
Create Date: 2026-08-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013_allow_user_owned_listings"
down_revision: Union[str, None] = "0012_sublet_model"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing admin-owned listings retain their owner_id; USER-hosted listings
    # are represented by party_id without creating an AdminUser.
    op.alter_column("listings", "owner_id", existing_type=sa.Integer(), existing_nullable=False, nullable=True)


def downgrade() -> None:
    op.alter_column("listings", "owner_id", existing_type=sa.Integer(), existing_nullable=True, nullable=False)

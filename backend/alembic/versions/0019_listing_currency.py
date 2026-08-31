"""add currency to listings

Revision ID: 0019_listing_currency
Revises: 0018_notifications
Create Date: 2026-08-27

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0019_listing_currency"
down_revision: Union[str, None] = "0018_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Additive, defaulted column -- every existing listing gets 'INR' automatically,
    # no existing row's price_per_night (or anything else) is touched.
    op.add_column(
        "listings",
        sa.Column("currency", sa.String(3), nullable=False, server_default=sa.text("'INR'")),
    )


def downgrade() -> None:
    op.drop_column("listings", "currency")

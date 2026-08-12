"""listing contact info: optional per-listing override of the owner's name/phone/email

Revision ID: 0006_listing_contact_info
Revises: 0005_marketplace_foundation
Create Date: 2026-08-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_listing_contact_info"
down_revision: Union[str, None] = "0005_marketplace_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("listings", sa.Column("contact_name", sa.String(255), nullable=False, server_default=sa.text("''")))
    op.add_column("listings", sa.Column("contact_phone", sa.String(50), nullable=False, server_default=sa.text("''")))
    op.add_column("listings", sa.Column("contact_email", sa.String(255), nullable=False, server_default=sa.text("''")))


def downgrade() -> None:
    op.drop_column("listings", "contact_email")
    op.drop_column("listings", "contact_phone")
    op.drop_column("listings", "contact_name")

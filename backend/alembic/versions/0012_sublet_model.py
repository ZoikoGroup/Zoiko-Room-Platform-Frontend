"""add sublet_requests table

Revision ID: 0012_sublet_model
Revises: 0011_refactor_listing_ownership
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012_sublet_model"
down_revision: Union[str, None] = "0011_refactor_listing_ownership"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if table already exists to handle idempotent migrations
    if not op.get_context().dialect.has_table(op.get_context().connection, "sublet_requests"):
        op.create_table(
            "sublet_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("current_occupancy_id", sa.Integer(), sa.ForeignKey("occupancies.id", ondelete="CASCADE"), unique=True, nullable=False),
            sa.Column("proposed_renter_party_id", sa.Integer(), sa.ForeignKey("parties.id", ondelete="CASCADE"), nullable=False),
            sa.Column("status", sa.String(30), nullable=False, server_default=sa.text("'pending_verification'")),
            sa.Column("authority_evidence_ref", sa.String(1024), nullable=False, server_default=sa.text("''")),
            sa.Column("admin_decision", sa.String(20), nullable=False, server_default=sa.text("''")),
            sa.Column("admin_notes", sa.String(2000), nullable=False, server_default=sa.text("''")),
            sa.Column("decided_by_admin_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("ix_sublet_requests_status", "sublet_requests", ["status"])


def downgrade() -> None:
    op.drop_table("sublet_requests")

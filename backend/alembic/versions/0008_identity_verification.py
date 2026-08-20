"""identity verification table

Revision ID: 0008_identity_verification
Revises: 0007_leasing_occupancy_finance
Create Date: 2026-08-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_identity_verification"
down_revision: Union[str, None] = "0007_leasing_occupancy_finance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "identity_verifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("party_id", sa.Integer(), sa.ForeignKey("parties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("encrypted_reference", sa.String(1024), nullable=False),
        sa.Column("evidence_ref", sa.String(1024), nullable=False, server_default=sa.text("''")),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verifier_admin_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("identity_verifications")

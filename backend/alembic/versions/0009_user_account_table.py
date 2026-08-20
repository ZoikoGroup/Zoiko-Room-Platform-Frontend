"""add user_accounts table

Revision ID: 0009_user_account_table
Revises: 0008_identity_verification
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_user_account_table"
down_revision: Union[str, None] = "0008_identity_verification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if table already exists to handle idempotent migrations
    if not op.get_context().dialect.has_table(op.get_context().connection, "user_accounts"):
        op.create_table(
            "user_accounts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
            sa.Column("hashed_password", sa.String(255), nullable=False),
            sa.Column("full_name", sa.String(255), nullable=False),
            sa.Column("phone", sa.String(50), nullable=False, server_default=sa.text("''")),
            sa.Column("party_id", sa.Integer(), sa.ForeignKey("parties.id", ondelete="SET NULL"), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        # Note: index=True in email column above automatically creates the index
        # No need for explicit op.create_index() call


def downgrade() -> None:
    op.drop_table("user_accounts")

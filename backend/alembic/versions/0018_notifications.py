"""persistent notification system

Revision ID: 0018_notifications
Revises: a7ae7d50c8e3
Create Date: 2026-08-27

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0018_notifications"
down_revision: Union[str, None] = "a7ae7d50c8e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipient_type", sa.String(10), nullable=False),
        sa.Column("recipient_user_id", sa.Integer(), sa.ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=True),
        sa.Column("recipient_admin_id", sa.Integer(), sa.ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=True),
        # Non-nullable "user:<id>" / "admin:<id>" computed at insert time, purely so
        # the dedupe constraint below has no nullable column to slip past --
        # Postgres unique constraints never treat two NULLs as equal, so a
        # constraint built directly on the two nullable recipient_*_id columns
        # would never actually fire.
        sa.Column("recipient_key", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.String(2000), nullable=False, server_default=sa.text("''")),
        sa.Column("notification_type", sa.String(100), nullable=False),
        sa.Column("related_entity_type", sa.String(50), nullable=False, server_default=sa.text("''")),
        sa.Column("related_entity_id", sa.String(50), nullable=False, server_default=sa.text("''")),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "notification_type", "related_entity_type", "related_entity_id", "recipient_key",
            name="uq_notifications_dedupe",
        ),
    )
    op.create_index("ix_notifications_recipient_user", "notifications", ["recipient_user_id", "is_read"])
    op.create_index("ix_notifications_recipient_admin", "notifications", ["recipient_admin_id", "is_read"])


def downgrade() -> None:
    op.drop_index("ix_notifications_recipient_admin", table_name="notifications")
    op.drop_index("ix_notifications_recipient_user", table_name="notifications")
    op.drop_table("notifications")

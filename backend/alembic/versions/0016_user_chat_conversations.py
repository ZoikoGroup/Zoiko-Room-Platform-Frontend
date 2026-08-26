"""add user_id to chat_conversations for user-side chatbot

Revision ID: 0016_user_chat_conversations
Revises: 0015_identity_verification_docs
Create Date: 2026-08-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0016_user_chat_conversations"
down_revision: Union[str, None] = "0014_chat_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chat_conversations",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_chat_conversations_user_id"),
        "chat_conversations",
        ["user_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_chat_conversations_user_id",
        "chat_conversations",
        "user_accounts",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_chat_conversations_user_id", "chat_conversations", type_="foreignkey")
    op.drop_index(op.f("ix_chat_conversations_user_id"), table_name="chat_conversations")
    op.drop_column("chat_conversations", "user_id")

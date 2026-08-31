"""add CHECK constraint: exactly one of (admin_id, user_id) must be non-null

Revision ID: 0018_chat_conv_check
Revises: 0098d369823b
Create Date: 2026-08-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0018_chat_conv_check"
down_revision: Union[str, None] = "0098d369823b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_chat_conversations_one_actor",
        "chat_conversations",
        # Exactly one of admin_id or user_id must be set, never both, never neither.
        sa.text(
            "(admin_id IS NOT NULL AND user_id IS NULL) OR "
            "(admin_id IS NULL AND user_id IS NOT NULL)"
        ),
    )


def downgrade() -> None:
    op.drop_constraint("ck_chat_conversations_one_actor", "chat_conversations", type_="check")

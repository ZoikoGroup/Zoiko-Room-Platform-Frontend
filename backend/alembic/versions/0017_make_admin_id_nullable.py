"""make admin_id nullable in chat_conversations for dual-use table

Revision ID: 0017_make_admin_id_nullable
Revises: 0016_user_chat_conversations
Create Date: 2026-08-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0017_make_admin_id_nullable"
down_revision: Union[str, None] = "0016_user_chat_conversations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "chat_conversations",
        "admin_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "chat_conversations",
        "admin_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

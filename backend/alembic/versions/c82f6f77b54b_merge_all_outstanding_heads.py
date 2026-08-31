"""merge all outstanding heads

Revision ID: c82f6f77b54b
Revises: 0018_chat_conv_check, 0018_notifications, 6128f86ddead, 7fc7c3a5c88a
Create Date: 2026-08-31 03:50:44.327343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c82f6f77b54b'
down_revision: Union[str, None] = ('0018_chat_conv_check', '0018_notifications', '6128f86ddead', '7fc7c3a5c88a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

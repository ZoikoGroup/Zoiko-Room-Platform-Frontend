"""merge listing currency and outstanding heads

Revision ID: 12173435b59e
Revises: 0019_listing_currency, c82f6f77b54b
Create Date: 2026-08-31 14:09:04.076692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12173435b59e'
down_revision: Union[str, None] = ('0019_listing_currency', 'c82f6f77b54b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

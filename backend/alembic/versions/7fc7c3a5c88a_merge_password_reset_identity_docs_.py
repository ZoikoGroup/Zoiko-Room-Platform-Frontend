"""merge password-reset/identity-docs branch with chat-tables branch

Revision ID: 7fc7c3a5c88a
Revises: 0017_make_admin_id_nullable, 5c3ae3ab4c67
Create Date: 2026-08-26 05:32:37.100034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fc7c3a5c88a'
down_revision: Union[str, None] = ('0017_make_admin_id_nullable', '5c3ae3ab4c67')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

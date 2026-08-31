"""merge chat and identity migration heads

Revision ID: a7ae7d50c8e3
Revises: 5c3ae3ab4c67, 0017_make_admin_id_nullable
Create Date: 2026-08-26 11:46:36.093025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7ae7d50c8e3'
down_revision: Union[str, None] = ('5c3ae3ab4c67', '0017_make_admin_id_nullable')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

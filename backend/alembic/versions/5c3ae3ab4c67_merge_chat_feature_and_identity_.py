"""merge chat feature and identity-verification/password-reset branches

Revision ID: 5c3ae3ab4c67
Revises: 0014_chat_tables, 0015_identity_verification_docs
Create Date: 2026-08-25 16:57:53.946166

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c3ae3ab4c67'
down_revision: Union[str, None] = ('0014_chat_tables', '0015_identity_verification_docs')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

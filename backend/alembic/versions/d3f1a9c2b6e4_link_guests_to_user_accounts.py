"""link_guests_to_user_accounts

Revision ID: d3f1a9c2b6e4
Revises: 022bda4d123a
Create Date: 2026-09-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3f1a9c2b6e4'
down_revision: Union[str, None] = '022bda4d123a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('guests', sa.Column('user_account_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_guests_user_account_id', 'guests', 'user_accounts',
        ['user_account_id'], ['id'], ondelete='SET NULL',
    )
    op.create_unique_constraint('uq_guests_user_account_id', 'guests', ['user_account_id'])

    # Backfill: link every existing Guest to the UserAccount that already
    # matches it by email -- the same matching rule the application code used
    # everywhere before this migration (Guest.email == UserAccount.email) --
    # so historical data isn't disconnected from the new FK on day one. Both
    # guests.email and user_accounts.email are unique, so this join can never
    # assign the same user_account_id to two different guest rows.
    op.execute(
        """
        UPDATE guests
        SET user_account_id = user_accounts.id
        FROM user_accounts
        WHERE guests.email = user_accounts.email
          AND guests.user_account_id IS NULL
        """
    )


def downgrade() -> None:
    op.drop_constraint('uq_guests_user_account_id', 'guests', type_='unique')
    op.drop_constraint('fk_guests_user_account_id', 'guests', type_='foreignkey')
    op.drop_column('guests', 'user_account_id')

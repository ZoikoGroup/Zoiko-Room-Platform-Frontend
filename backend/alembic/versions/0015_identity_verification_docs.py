"""expand identity verification document types + secure document upload

Revision ID: 0015_identity_verification_docs
Revises: 0014_user_password_reset
Create Date: 2026-08-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015_identity_verification_docs"
down_revision: Union[str, None] = "0014_user_password_reset"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The document number/reference becomes optional now that a real uploaded
    # file is the primary evidence.
    op.alter_column("identity_verifications", "encrypted_reference", existing_type=sa.String(1024), nullable=True)

    op.add_column(
        "identity_verifications",
        sa.Column("document_category", sa.String(20), nullable=False, server_default=sa.text("'identity'")),
    )
    op.add_column(
        "identity_verifications",
        sa.Column("custom_document_name", sa.String(255), nullable=False, server_default=sa.text("''")),
    )
    op.add_column(
        "identity_verifications",
        sa.Column("verifier_notes", sa.String(2000), nullable=False, server_default=sa.text("''")),
    )
    op.add_column("identity_verifications", sa.Column("document_file_path", sa.String(1024), nullable=True))
    op.add_column(
        "identity_verifications",
        sa.Column("document_file_original_name", sa.String(255), nullable=False, server_default=sa.text("''")),
    )
    op.add_column(
        "identity_verifications",
        sa.Column("document_file_content_type", sa.String(100), nullable=False, server_default=sa.text("''")),
    )
    op.add_column("identity_verifications", sa.Column("document_file_size", sa.Integer(), nullable=True))

    # Every pre-existing row predates this feature and was one of the three
    # original identity documents.
    op.execute(
        "UPDATE identity_verifications SET document_category = 'identity' "
        "WHERE document_type IN ('aadhaar', 'passport', 'driving_license')"
    )


def downgrade() -> None:
    op.drop_column("identity_verifications", "document_file_size")
    op.drop_column("identity_verifications", "document_file_content_type")
    op.drop_column("identity_verifications", "document_file_original_name")
    op.drop_column("identity_verifications", "document_file_path")
    op.drop_column("identity_verifications", "verifier_notes")
    op.drop_column("identity_verifications", "custom_document_name")
    op.drop_column("identity_verifications", "document_category")
    op.alter_column("identity_verifications", "encrypted_reference", existing_type=sa.String(1024), nullable=False)

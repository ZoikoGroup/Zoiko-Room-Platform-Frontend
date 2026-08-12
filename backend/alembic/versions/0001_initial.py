"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-06

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False, server_default=sa.text("'Zoiko Admin'")),
        sa.Column("phone", sa.String(50), nullable=False, server_default=sa.text("''")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_admin_users_email", "admin_users", ["email"])

    op.create_table(
        "admin_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_user_id", sa.Integer(), sa.ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("logo_url", sa.String(1024), nullable=False, server_default=sa.text("''")),
        sa.Column("notify_new_booking", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notify_payments", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notify_reviews", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("notify_marketing", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "listings",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("property_type", sa.String(20), nullable=False),
        sa.Column("room_type", sa.String(255), nullable=False),
        sa.Column("city", sa.String(255), nullable=False),
        sa.Column("location", sa.String(500), nullable=False),
        sa.Column("price_per_night", sa.Float(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False, server_default="4.5"),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("guests", sa.Integer(), nullable=False),
        sa.Column("bedrooms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bathrooms", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("images", postgresql.ARRAY(sa.String()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("amenities", postgresql.ARRAY(sa.String()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("description", sa.String(2000), nullable=False, server_default=sa.text("''")),
        sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("available", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_listings_slug", "listings", ["slug"])

    op.create_table(
        "guests",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(50), nullable=False, server_default=sa.text("''")),
        sa.Column("avatar", sa.String(1024), nullable=False, server_default=sa.text("''")),
        sa.Column("location", sa.String(255), nullable=False, server_default=sa.text("''")),
        sa.Column("joined_at", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'")),
    )
    op.create_index("ix_guests_email", "guests", ["email"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("listing_id", sa.String(20), sa.ForeignKey("listings.id"), nullable=False),
        sa.Column("guest_id", sa.String(20), sa.ForeignKey("guests.id"), nullable=False),
        sa.Column("check_in", sa.Date(), nullable=False),
        sa.Column("check_out", sa.Date(), nullable=False),
        sa.Column("guests", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("payment_status", sa.String(20), nullable=False, server_default=sa.text("'unpaid'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("booking_id", sa.String(20), sa.ForeignKey("bookings.id"), nullable=False, unique=True),
        sa.Column("method", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("listing_id", sa.String(20), sa.ForeignKey("listings.id"), nullable=False),
        sa.Column("guest_id", sa.String(20), sa.ForeignKey("guests.id"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.String(2000), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("payments")
    op.drop_table("bookings")
    op.drop_index("ix_guests_email", table_name="guests")
    op.drop_table("guests")
    op.drop_index("ix_listings_slug", table_name="listings")
    op.drop_table("listings")
    op.drop_table("admin_settings")
    op.drop_index("ix_admin_users_email", table_name="admin_users")
    op.drop_table("admin_users")

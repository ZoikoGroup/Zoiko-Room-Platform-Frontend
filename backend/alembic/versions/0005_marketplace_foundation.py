"""marketplace foundation: party/membership/market-release/property/room/authority/
room-passport/occupancy-classification/audit/domain-event, listing state machine

Revision ID: 0005_marketplace_foundation
Revises: 0004_admin_approval_status
Create Date: 2026-08-08

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_marketplace_foundation"
down_revision: Union[str, None] = "0004_admin_approval_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "parties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("party_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("jurisdiction", sa.String(50), nullable=False, server_default=sa.text("'IN'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "memberships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_user_id", sa.Integer(), sa.ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("party_id", sa.Integer(), sa.ForeignKey("parties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "market_releases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("jurisdiction", sa.String(50), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("min_stay_nights", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by_admin_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_party_id", sa.Integer(), sa.ForeignKey("parties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("city", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("room_type", sa.String(30), nullable=False, server_default=sa.text("'private_room'")),
        sa.Column("size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("has_ensuite", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "authority_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("party_id", sa.Integer(), sa.ForeignKey("parties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("authority_type", sa.String(50), nullable=False),
        sa.Column("evidence_ref", sa.String(1024), nullable=False, server_default=sa.text("''")),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verifier_admin_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'not_started'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "room_passport_claims",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("claim_type", sa.String(100), nullable=False),
        sa.Column("value", sa.String(1000), nullable=False),
        sa.Column("evidence_tier", sa.String(30), nullable=False, server_default=sa.text("'self_attested'")),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "room_passport_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("hash", sa.String(64), nullable=False),
        sa.Column("captured_claims", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "occupancy_classifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("classification", sa.String(100), nullable=False, server_default=sa.text("''")),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("evidence_ref", sa.String(1024), nullable=False, server_default=sa.text("''")),
        sa.Column("jurisdiction", sa.String(50), nullable=False, server_default=sa.text("'IN'")),
        sa.Column("rule_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("review_state", sa.String(20), nullable=False, server_default=sa.text("'UNKNOWN'")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_admin_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("role", sa.String(30), nullable=False, server_default=sa.text("''")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(50), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False, server_default=sa.text("''")),
        sa.Column("correlation_id", sa.String(64), nullable=False, server_default=sa.text("''")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "domain_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(50), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("delivery_state", sa.String(20), nullable=False, server_default=sa.text("'pending'")),
    )

    # --- Listing state machine migration ---
    op.add_column("listings", sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id"), nullable=True))
    op.add_column("listings", sa.Column("market_release_id", sa.Integer(), sa.ForeignKey("market_releases.id"), nullable=True))
    op.add_column("listings", sa.Column("min_stay_nights", sa.Integer(), nullable=False, server_default="30"))
    op.add_column("listings", sa.Column("state", sa.String(20), nullable=False, server_default=sa.text("'DRAFT'")))
    op.drop_column("listings", "approval_status")
    op.drop_column("listings", "available")
    op.alter_column("listings", "property_type", server_default=sa.text("'private_room'"))


def downgrade() -> None:
    op.alter_column("listings", "property_type", server_default=None)
    op.add_column("listings", sa.Column("available", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("listings", sa.Column("approval_status", sa.String(20), nullable=False, server_default=sa.text("'pending'")))
    op.drop_column("listings", "state")
    op.drop_column("listings", "min_stay_nights")
    op.drop_column("listings", "market_release_id")
    op.drop_column("listings", "room_id")

    op.drop_table("domain_events")
    op.drop_table("audit_events")
    op.drop_table("occupancy_classifications")
    op.drop_table("room_passport_snapshots")
    op.drop_table("room_passport_claims")
    op.drop_table("authority_records")
    op.drop_table("rooms")
    op.drop_table("properties")
    op.drop_table("market_releases")
    op.drop_table("memberships")
    op.drop_table("parties")

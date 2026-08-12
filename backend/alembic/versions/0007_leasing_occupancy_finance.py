"""leasing/occupancy/finance: application/offer/agreement pipeline, active occupancy,
simulated payment ledger with obligations/allocations/deposits/payouts/refunds/
disputes/reconciliation (steps 7-20 of the marketplace standard)

Revision ID: 0007_leasing_occupancy_finance
Revises: 0006_listing_contact_info
Create Date: 2026-08-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_leasing_occupancy_finance"
down_revision: Union[str, None] = "0006_listing_contact_info"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("listing_id", sa.String(20), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("guest_id", sa.String(20), sa.ForeignKey("guests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'SUBMITTED'")),
        sa.Column("message", sa.String(2000), nullable=False, server_default=sa.text("''")),
        sa.Column("desired_move_in", sa.Date(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "application_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("reason_code", sa.String(50), nullable=False, server_default=sa.text("''")),
        sa.Column("note", sa.String(2000), nullable=False, server_default=sa.text("''")),
        sa.Column("decided_by_admin_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("listing_id", sa.String(20), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("guest_id", sa.String(20), sa.ForeignKey("guests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "offer_terms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("offer_id", sa.Integer(), sa.ForeignKey("offers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("monthly_rent", sa.Numeric(12, 2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("term_months", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "agreements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("offer_id", sa.Integer(), sa.ForeignKey("offers.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("content_ref", sa.String(1024), nullable=False, server_default=sa.text("''")),
        sa.Column("signed_by_provider_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signed_by_renter_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signature_ref", sa.String(255), nullable=False, server_default=sa.text("''")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "occupancies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("offer_id", sa.Integer(), sa.ForeignKey("offers.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("listing_id", sa.String(20), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("guest_id", sa.String(20), sa.ForeignKey("guests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'PENDING_MOVE_IN'")),
        sa.Column("move_in_date", sa.Date(), nullable=True),
        sa.Column("expected_end_date", sa.Date(), nullable=True),
        sa.Column("move_out_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "payout_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("party_id", sa.Integer(), sa.ForeignKey("parties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period_key", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default=sa.text("'INR'")),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("hold_reason", sa.String(255), nullable=False, server_default=sa.text("''")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("party_id", "period_key", name="uq_payout_party_period"),
    )

    op.create_table(
        "obligations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("obligation_type", sa.String(20), nullable=False),
        sa.Column("money_plane", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default=sa.text("'INR'")),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("agreement_id", sa.Integer(), sa.ForeignKey("agreements.id", ondelete="CASCADE"), nullable=True),
        sa.Column("occupancy_id", sa.Integer(), sa.ForeignKey("occupancies.id", ondelete="CASCADE"), nullable=True),
        sa.Column("payout_id", sa.Integer(), sa.ForeignKey("payout_records.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "simulated_payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guest_id", sa.String(20), sa.ForeignKey("guests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default=sa.text("'INR'")),
        sa.Column("idempotency_key", sa.String(255), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "payment_allocations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("simulated_payments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("obligation_id", sa.Integer(), sa.ForeignKey("obligations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount_allocated", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "deposit_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("obligation_id", sa.Integer(), sa.ForeignKey("obligations.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'HELD'")),
        sa.Column("held_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("released_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(2000), nullable=False, server_default=sa.text("''")),
    )

    op.create_table(
        "refund_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("simulated_payments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("obligation_id", sa.Integer(), sa.ForeignKey("obligations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("reason", sa.String(2000), nullable=False, server_default=sa.text("''")),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'REQUESTED'")),
        sa.Column("requested_by_admin_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=False),
        sa.Column("decided_by_admin_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "dispute_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("simulated_payments.id", ondelete="CASCADE"), nullable=True),
        sa.Column("occupancy_id", sa.Integer(), sa.ForeignKey("occupancies.id", ondelete="CASCADE"), nullable=True),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False, server_default=sa.text("''")),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'OPEN'")),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_notes", sa.String(2000), nullable=False, server_default=sa.text("''")),
    )

    op.create_table(
        "reconciliation_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("totals", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("mismatches", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("status", sa.String(30), nullable=False, server_default=sa.text("'CLEAN'")),
    )


def downgrade() -> None:
    op.drop_table("reconciliation_runs")
    op.drop_table("dispute_cases")
    op.drop_table("refund_requests")
    op.drop_table("deposit_records")
    op.drop_table("payment_allocations")
    op.drop_table("simulated_payments")
    op.drop_table("obligations")
    op.drop_table("payout_records")
    op.drop_table("occupancies")
    op.drop_table("agreements")
    op.drop_table("offer_terms")
    op.drop_table("offers")
    op.drop_table("application_decisions")
    op.drop_table("applications")

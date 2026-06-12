"""create property fund request allocation tables

Revision ID: 20260612_0002
Revises: 20260612_0001
Create Date: 2026-06-12 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260612_0002"
down_revision: str | None = "20260612_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("total_units", sa.Integer(), nullable=False),
        sa.Column("manager_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "total_units >= 0",
            name="ck_properties_total_units_non_negative",
        ),
        sa.ForeignKeyConstraint(["manager_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_properties_code"), "properties", ["code"], unique=True)
    op.create_index(op.f("ix_properties_id"), "properties", ["id"], unique=False)
    op.create_index(op.f("ix_properties_manager_id"), "properties", ["manager_id"], unique=False)

    op.create_table(
        "property_funds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("annual_budget", sa.Numeric(14, 2), nullable=False),
        sa.Column("current_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("reserved_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "annual_budget >= 0",
            name="ck_property_funds_annual_budget_non_negative",
        ),
        sa.CheckConstraint(
            "current_balance >= 0",
            name="ck_property_funds_current_balance_non_negative",
        ),
        sa.CheckConstraint(
            "fiscal_year >= 2000",
            name="ck_property_funds_fiscal_year_valid",
        ),
        sa.CheckConstraint(
            "reserved_balance <= current_balance",
            name="ck_property_funds_reserved_not_above_current",
        ),
        sa.CheckConstraint(
            "reserved_balance >= 0",
            name="ck_property_funds_reserved_balance_non_negative",
        ),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("property_id", "fiscal_year", name="uq_property_funds_property_year"),
    )
    op.create_index(op.f("ix_property_funds_fiscal_year"), "property_funds", ["fiscal_year"], unique=False)
    op.create_index(op.f("ix_property_funds_id"), "property_funds", ["id"], unique=False)
    op.create_index(op.f("ix_property_funds_property_id"), "property_funds", ["property_id"], unique=False)

    op.create_table(
        "maintenance_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("submitted_by_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "priority",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="maintenancepriority"),
            nullable=False,
        ),
        sa.Column("priority_score", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "APPROVED",
                "ALLOCATED",
                "IN_PROGRESS",
                "COMPLETED",
                "REJECTED",
                "CANCELLED",
                name="maintenancerequeststatus",
            ),
            nullable=False,
        ),
        sa.Column("estimated_cost", sa.Numeric(14, 2), nullable=False),
        sa.Column("approved_cost", sa.Numeric(14, 2), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("required_by", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "approved_cost IS NULL OR approved_cost >= 0",
            name="ck_maintenance_requests_approved_cost_non_negative",
        ),
        sa.CheckConstraint(
            "estimated_cost >= 0",
            name="ck_maintenance_requests_estimated_cost_non_negative",
        ),
        sa.CheckConstraint(
            "priority_score BETWEEN 1 AND 100",
            name="ck_maintenance_requests_priority_score_range",
        ),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["submitted_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_maintenance_requests_id"), "maintenance_requests", ["id"], unique=False)
    op.create_index(op.f("ix_maintenance_requests_priority"), "maintenance_requests", ["priority"], unique=False)
    op.create_index(op.f("ix_maintenance_requests_property_id"), "maintenance_requests", ["property_id"], unique=False)
    op.create_index(op.f("ix_maintenance_requests_requested_at"), "maintenance_requests", ["requested_at"], unique=False)
    op.create_index(op.f("ix_maintenance_requests_status"), "maintenance_requests", ["status"], unique=False)
    op.create_index(op.f("ix_maintenance_requests_submitted_by_id"), "maintenance_requests", ["submitted_by_id"], unique=False)

    op.create_table(
        "allocations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("maintenance_request_id", sa.Integer(), nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=False),
        sa.Column("approved_by_id", sa.Integer(), nullable=True),
        sa.Column("amount_allocated", sa.Numeric(14, 2), nullable=False),
        sa.Column("amount_released", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "RESERVED",
                "RELEASED",
                "PARTIALLY_RELEASED",
                "CANCELLED",
                name="allocationstatus",
            ),
            nullable=False,
        ),
        sa.Column("decision_notes", sa.Text(), nullable=True),
        sa.Column("allocated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "amount_allocated > 0",
            name="ck_allocations_amount_allocated_positive",
        ),
        sa.CheckConstraint(
            "amount_released <= amount_allocated",
            name="ck_allocations_released_not_above_allocated",
        ),
        sa.CheckConstraint(
            "amount_released >= 0",
            name="ck_allocations_amount_released_non_negative",
        ),
        sa.ForeignKeyConstraint(["approved_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["fund_id"], ["property_funds.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["maintenance_request_id"],
            ["maintenance_requests.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_allocations_allocated_at"), "allocations", ["allocated_at"], unique=False)
    op.create_index(op.f("ix_allocations_approved_by_id"), "allocations", ["approved_by_id"], unique=False)
    op.create_index(op.f("ix_allocations_fund_id"), "allocations", ["fund_id"], unique=False)
    op.create_index(op.f("ix_allocations_id"), "allocations", ["id"], unique=False)
    op.create_index(op.f("ix_allocations_maintenance_request_id"), "allocations", ["maintenance_request_id"], unique=True)
    op.create_index(op.f("ix_allocations_status"), "allocations", ["status"], unique=False)

    op.create_table(
        "fund_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=False),
        sa.Column("allocation_id", sa.Integer(), nullable=True),
        sa.Column("performed_by_id", sa.Integer(), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum(
                "CREDIT",
                "DEBIT",
                "RESERVE",
                "RELEASE",
                "ADJUSTMENT",
                name="fundtransactiontype",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("balance_after", sa.Numeric(14, 2), nullable=False),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("transaction_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_fund_transactions_amount_positive",
        ),
        sa.CheckConstraint(
            "balance_after >= 0",
            name="ck_fund_transactions_balance_after_non_negative",
        ),
        sa.ForeignKeyConstraint(["allocation_id"], ["allocations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["fund_id"], ["property_funds.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performed_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fund_transactions_allocation_id"), "fund_transactions", ["allocation_id"], unique=True)
    op.create_index(op.f("ix_fund_transactions_fund_id"), "fund_transactions", ["fund_id"], unique=False)
    op.create_index(op.f("ix_fund_transactions_id"), "fund_transactions", ["id"], unique=False)
    op.create_index(op.f("ix_fund_transactions_performed_by_id"), "fund_transactions", ["performed_by_id"], unique=False)
    op.create_index(op.f("ix_fund_transactions_reference"), "fund_transactions", ["reference"], unique=False)
    op.create_index(op.f("ix_fund_transactions_transaction_date"), "fund_transactions", ["transaction_date"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_fund_transactions_transaction_date"), table_name="fund_transactions")
    op.drop_index(op.f("ix_fund_transactions_reference"), table_name="fund_transactions")
    op.drop_index(op.f("ix_fund_transactions_performed_by_id"), table_name="fund_transactions")
    op.drop_index(op.f("ix_fund_transactions_id"), table_name="fund_transactions")
    op.drop_index(op.f("ix_fund_transactions_fund_id"), table_name="fund_transactions")
    op.drop_index(op.f("ix_fund_transactions_allocation_id"), table_name="fund_transactions")
    op.drop_table("fund_transactions")

    op.drop_index(op.f("ix_allocations_status"), table_name="allocations")
    op.drop_index(op.f("ix_allocations_maintenance_request_id"), table_name="allocations")
    op.drop_index(op.f("ix_allocations_id"), table_name="allocations")
    op.drop_index(op.f("ix_allocations_fund_id"), table_name="allocations")
    op.drop_index(op.f("ix_allocations_approved_by_id"), table_name="allocations")
    op.drop_index(op.f("ix_allocations_allocated_at"), table_name="allocations")
    op.drop_table("allocations")

    op.drop_index(op.f("ix_maintenance_requests_submitted_by_id"), table_name="maintenance_requests")
    op.drop_index(op.f("ix_maintenance_requests_status"), table_name="maintenance_requests")
    op.drop_index(op.f("ix_maintenance_requests_requested_at"), table_name="maintenance_requests")
    op.drop_index(op.f("ix_maintenance_requests_property_id"), table_name="maintenance_requests")
    op.drop_index(op.f("ix_maintenance_requests_priority"), table_name="maintenance_requests")
    op.drop_index(op.f("ix_maintenance_requests_id"), table_name="maintenance_requests")
    op.drop_table("maintenance_requests")

    op.drop_index(op.f("ix_property_funds_property_id"), table_name="property_funds")
    op.drop_index(op.f("ix_property_funds_id"), table_name="property_funds")
    op.drop_index(op.f("ix_property_funds_fiscal_year"), table_name="property_funds")
    op.drop_table("property_funds")

    op.drop_index(op.f("ix_properties_manager_id"), table_name="properties")
    op.drop_index(op.f("ix_properties_id"), table_name="properties")
    op.drop_index(op.f("ix_properties_code"), table_name="properties")
    op.drop_table("properties")

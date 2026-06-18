"""create manager properties

Revision ID: 20260618_0003
Revises: 20260612_0002
Create Date: 2026-06-18 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260618_0003"
down_revision: str | None = "20260612_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "manager_properties",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("manager_id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["manager_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "manager_id",
            "property_id",
            name="uq_manager_properties_manager_property",
        ),
    )
    op.create_index(op.f("ix_manager_properties_id"), "manager_properties", ["id"], unique=False)
    op.create_index(
        op.f("ix_manager_properties_manager_id"),
        "manager_properties",
        ["manager_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_manager_properties_property_id"),
        "manager_properties",
        ["property_id"],
        unique=False,
    )

    op.execute(
        """
        INSERT INTO manager_properties (manager_id, property_id, assigned_at)
        SELECT manager_id, id, created_at
        FROM properties
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_manager_properties_property_id"), table_name="manager_properties")
    op.drop_index(op.f("ix_manager_properties_manager_id"), table_name="manager_properties")
    op.drop_index(op.f("ix_manager_properties_id"), table_name="manager_properties")
    op.drop_table("manager_properties")

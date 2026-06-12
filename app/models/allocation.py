import enum
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AllocationStatus(str, enum.Enum):
    RESERVED = "reserved"
    RELEASED = "released"
    PARTIALLY_RELEASED = "partially_released"
    CANCELLED = "cancelled"


class Allocation(Base):
    __tablename__ = "allocations"
    __table_args__ = (
        CheckConstraint("amount_allocated > 0", name="ck_allocations_amount_allocated_positive"),
        CheckConstraint("amount_released >= 0", name="ck_allocations_amount_released_non_negative"),
        CheckConstraint(
            "amount_released <= amount_allocated",
            name="ck_allocations_released_not_above_allocated",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    maintenance_request_id: Mapped[int] = mapped_column(
        ForeignKey("maintenance_requests.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    fund_id: Mapped[int] = mapped_column(
        ForeignKey("property_funds.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    approved_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    amount_allocated: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    amount_released: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    status: Mapped[AllocationStatus] = mapped_column(
        Enum(AllocationStatus),
        nullable=False,
        default=AllocationStatus.RESERVED,
        index=True,
    )
    decision_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    allocated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    maintenance_request: Mapped["MaintenanceRequest"] = relationship(
        "MaintenanceRequest",
        back_populates="allocation",
    )
    fund: Mapped["PropertyFund"] = relationship("PropertyFund", back_populates="allocations")
    approved_by: Mapped["User | None"] = relationship(
        "User",
        back_populates="approved_allocations",
        foreign_keys=[approved_by_id],
    )
    transaction: Mapped["FundTransaction | None"] = relationship(
        "FundTransaction",
        back_populates="allocation",
        uselist=False,
        foreign_keys="FundTransaction.allocation_id",
    )

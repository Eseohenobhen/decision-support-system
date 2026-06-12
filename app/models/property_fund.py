from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PropertyFund(Base):
    __tablename__ = "property_funds"
    __table_args__ = (
        UniqueConstraint("property_id", "fiscal_year", name="uq_property_funds_property_year"),
        CheckConstraint("fiscal_year >= 2000", name="ck_property_funds_fiscal_year_valid"),
        CheckConstraint("annual_budget >= 0", name="ck_property_funds_annual_budget_non_negative"),
        CheckConstraint("current_balance >= 0", name="ck_property_funds_current_balance_non_negative"),
        CheckConstraint("reserved_balance >= 0", name="ck_property_funds_reserved_balance_non_negative"),
        CheckConstraint(
            "reserved_balance <= current_balance",
            name="ck_property_funds_reserved_not_above_current",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    annual_budget: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    reserved_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="NGN")
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

    property: Mapped["Property"] = relationship("Property", back_populates="funds")
    transactions: Mapped[list["FundTransaction"]] = relationship(
        "FundTransaction",
        back_populates="fund",
        cascade="all, delete-orphan",
    )
    allocations: Mapped[list["Allocation"]] = relationship(
        "Allocation",
        back_populates="fund",
    )

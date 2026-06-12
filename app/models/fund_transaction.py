import enum
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class FundTransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    RESERVE = "reserve"
    RELEASE = "release"
    ADJUSTMENT = "adjustment"


class FundTransaction(Base):
    __tablename__ = "fund_transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_fund_transactions_amount_positive"),
        CheckConstraint("balance_after >= 0", name="ck_fund_transactions_balance_after_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fund_id: Mapped[int] = mapped_column(
        ForeignKey("property_funds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    allocation_id: Mapped[int | None] = mapped_column(
        ForeignKey("allocations.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )
    performed_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[FundTransactionType] = mapped_column(
        Enum(FundTransactionType),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    fund: Mapped["PropertyFund"] = relationship("PropertyFund", back_populates="transactions")
    allocation: Mapped["Allocation | None"] = relationship(
        "Allocation",
        back_populates="transaction",
        foreign_keys=[allocation_id],
    )
    performed_by: Mapped["User"] = relationship(
        "User",
        back_populates="fund_transactions",
        foreign_keys=[performed_by_id],
    )

import enum
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class MaintenancePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MaintenanceRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    ALLOCATED = "allocated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    __table_args__ = (
        CheckConstraint("estimated_cost >= 0", name="ck_maintenance_requests_estimated_cost_non_negative"),
        CheckConstraint("approved_cost IS NULL OR approved_cost >= 0", name="ck_maintenance_requests_approved_cost_non_negative"),
        CheckConstraint("priority_score BETWEEN 1 AND 100", name="ck_maintenance_requests_priority_score_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submitted_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[MaintenancePriority] = mapped_column(
        Enum(MaintenancePriority),
        nullable=False,
        default=MaintenancePriority.MEDIUM,
        index=True,
    )
    priority_score: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    status: Mapped[MaintenanceRequestStatus] = mapped_column(
        Enum(MaintenanceRequestStatus),
        nullable=False,
        default=MaintenanceRequestStatus.PENDING,
        index=True,
    )
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    approved_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
    required_by: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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

    property: Mapped["Property"] = relationship(
        "Property",
        back_populates="maintenance_requests",
    )
    submitted_by: Mapped["User"] = relationship(
        "User",
        back_populates="maintenance_requests",
        foreign_keys=[submitted_by_id],
    )
    allocation: Mapped["Allocation | None"] = relationship(
        "Allocation",
        back_populates="maintenance_request",
        cascade="all, delete-orphan",
        uselist=False,
    )

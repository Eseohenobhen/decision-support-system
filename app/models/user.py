import enum
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PROPERTY_MANAGER = "property_manager"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.PROPERTY_MANAGER,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
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

    managed_properties: Mapped[list["Property"]] = relationship(
        "Property",
        back_populates="manager",
        foreign_keys="Property.manager_id",
    )
    property_assignments: Mapped[list["ManagerProperty"]] = relationship(
        "ManagerProperty",
        back_populates="manager",
        cascade="all, delete-orphan",
    )
    fund_transactions: Mapped[list["FundTransaction"]] = relationship(
        "FundTransaction",
        back_populates="performed_by",
        foreign_keys="FundTransaction.performed_by_id",
    )
    maintenance_requests: Mapped[list["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest",
        back_populates="submitted_by",
        foreign_keys="MaintenanceRequest.submitted_by_id",
    )
    approved_allocations: Mapped[list["Allocation"]] = relationship(
        "Allocation",
        back_populates="approved_by",
        foreign_keys="Allocation.approved_by_id",
    )

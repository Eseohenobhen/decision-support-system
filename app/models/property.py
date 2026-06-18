from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Property(Base):
    __tablename__ = "properties"
    __table_args__ = (
        CheckConstraint("total_units >= 0", name="ck_properties_total_units_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Nigeria")
    total_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    manager_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
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

    manager: Mapped["User"] = relationship(
        "User",
        back_populates="managed_properties",
        foreign_keys=[manager_id],
    )
    funds: Mapped[list["PropertyFund"]] = relationship(
        "PropertyFund",
        back_populates="property",
        cascade="all, delete-orphan",
    )
    maintenance_requests: Mapped[list["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest",
        back_populates="property",
        cascade="all, delete-orphan",
    )
    manager_assignments: Mapped[list["ManagerProperty"]] = relationship(
        "ManagerProperty",
        back_populates="property",
        cascade="all, delete-orphan",
    )

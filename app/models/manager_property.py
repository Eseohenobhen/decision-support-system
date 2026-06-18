from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ManagerProperty(Base):
    __tablename__ = "manager_properties"
    __table_args__ = (
        UniqueConstraint("manager_id", "property_id", name="uq_manager_properties_manager_property"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    manager_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    manager: Mapped["User"] = relationship("User", back_populates="property_assignments")
    property: Mapped["Property"] = relationship("Property", back_populates="manager_assignments")

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.maintenance_request import MaintenancePriority, MaintenanceRequestStatus


class MaintenanceRequestBase(BaseModel):
    property_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    priority_score: int = Field(default=50, ge=1, le=100)
    estimated_cost: Decimal = Field(ge=0)
    required_by: datetime | None = None

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class MaintenanceRequestCreate(MaintenanceRequestBase):
    pass


class MaintenanceRequestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    priority: MaintenancePriority | None = None
    priority_score: int | None = Field(default=None, ge=1, le=100)
    status: MaintenanceRequestStatus | None = None
    estimated_cost: Decimal | None = Field(default=None, ge=0)
    approved_cost: Decimal | None = Field(default=None, ge=0)
    required_by: datetime | None = None
    completed_at: datetime | None = None

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value


class MaintenanceRequestRead(MaintenanceRequestBase):
    id: int
    submitted_by_id: int
    status: MaintenanceRequestStatus
    approved_cost: Decimal | None
    requested_at: datetime
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from decimal import Decimal

from pydantic import BaseModel, Field


class MaintenanceAllocationSummary(BaseModel):
    total_available_fund: Decimal
    total_estimated_maintenance_cost: Decimal
    high_priority_items: int
    recommendation: str


class MaintenanceItemInput(BaseModel):
    item_id: int = Field(gt=0)
    estimated_cost: Decimal = Field(ge=0)
    priority: int = Field(ge=1, le=5)


class AllocationRecommendationRequest(BaseModel):
    available_fund: Decimal = Field(ge=0)
    items: list[MaintenanceItemInput] = Field(default_factory=list)


class AllocationRecommendationResponse(BaseModel):
    available_fund: Decimal
    requested_total: Decimal
    recommended_total: Decimal
    selected_item_ids: list[int]
    deferred_item_ids: list[int]

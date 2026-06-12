from decimal import Decimal

from fastapi import APIRouter, Depends

from app.api.deps import get_current_property_manager
from app.models.user import User
from app.schemas.maintenance_allocation import (
    AllocationRecommendationRequest,
    AllocationRecommendationResponse,
    MaintenanceAllocationSummary,
)

router = APIRouter()


@router.get("/summary", response_model=MaintenanceAllocationSummary)
def get_allocation_summary(
    _: User = Depends(get_current_property_manager),
) -> MaintenanceAllocationSummary:
    return MaintenanceAllocationSummary(
        total_available_fund=Decimal("0.00"),
        total_estimated_maintenance_cost=Decimal("0.00"),
        high_priority_items=0,
        recommendation="No maintenance records have been submitted yet.",
    )


@router.post("/recommend", response_model=AllocationRecommendationResponse)
def recommend_allocation(
    request: AllocationRecommendationRequest,
    _: User = Depends(get_current_property_manager),
) -> AllocationRecommendationResponse:
    requested_total = sum(item.estimated_cost for item in request.items)
    approved_items = sorted(request.items, key=lambda item: item.priority, reverse=True)

    running_total = Decimal("0.00")
    selected_item_ids: list[int] = []
    for item in approved_items:
        if running_total + item.estimated_cost <= request.available_fund:
            selected_item_ids.append(item.item_id)
            running_total += item.estimated_cost

    return AllocationRecommendationResponse(
        available_fund=request.available_fund,
        requested_total=requested_total,
        recommended_total=running_total,
        selected_item_ids=selected_item_ids,
        deferred_item_ids=[
            item.item_id for item in request.items if item.item_id not in selected_item_ids
        ],
    )

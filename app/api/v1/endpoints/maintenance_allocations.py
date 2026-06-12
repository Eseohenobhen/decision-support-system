from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_property_manager, get_db
from app.models.user import User
from app.schemas.dss import DSSRankingRequest, DSSRankingResponse
from app.schemas.maintenance_allocation import (
    AllocationRecommendationRequest,
    AllocationRecommendationResponse,
    AutomaticAllocationRequest,
    AutomaticAllocationResponse,
    MaintenanceAllocationSummary,
)
from app.services.allocation_service import automatically_allocate_funds
from app.services.dss_engine import rank_recommendations

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


@router.post("/dss/rank", response_model=DSSRankingResponse)
def rank_maintenance_recommendations(
    request: DSSRankingRequest,
    _: User = Depends(get_current_property_manager),
) -> DSSRankingResponse:
    return DSSRankingResponse(
        formula="(U * 0.4) + (I * 0.3) + (A * 0.2) - (Cost Factor * 0.1)",
        items=rank_recommendations(request.items),
    )


@router.post("/auto-allocate", response_model=AutomaticAllocationResponse)
def auto_allocate_maintenance_funds(
    request: AutomaticAllocationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> AutomaticAllocationResponse:
    return automatically_allocate_funds(
        db,
        allocation_in=request,
        current_user=current_user,
    )

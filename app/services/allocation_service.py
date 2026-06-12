from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.allocation import Allocation, AllocationStatus
from app.models.fund_transaction import FundTransaction, FundTransactionType
from app.models.maintenance_request import MaintenanceRequest, MaintenanceRequestStatus
from app.models.property_fund import PropertyFund
from app.models.user import User
from app.schemas.maintenance_allocation import (
    AutomaticAllocationItem,
    AutomaticAllocationRequest,
    AutomaticAllocationResponse,
)
from app.services.property_service import get_accessible_property

ELIGIBLE_ALLOCATION_STATUSES = (
    MaintenanceRequestStatus.PENDING,
    MaintenanceRequestStatus.APPROVED,
)


def get_request_amount(request: MaintenanceRequest) -> Decimal:
    return request.approved_cost if request.approved_cost is not None else request.estimated_cost


def get_fund_available_balance(fund: PropertyFund) -> Decimal:
    return fund.current_balance - fund.reserved_balance


def automatically_allocate_funds(
    db: Session,
    allocation_in: AutomaticAllocationRequest,
    current_user: User,
) -> AutomaticAllocationResponse:
    get_accessible_property(db, allocation_in.property_id, current_user)

    fund = db.scalar(
        select(PropertyFund)
        .where(
            PropertyFund.property_id == allocation_in.property_id,
            PropertyFund.fiscal_year == allocation_in.fiscal_year,
        )
        .with_for_update()
    )
    if fund is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property fund not found for the selected fiscal year",
        )

    starting_available_fund = get_fund_available_balance(fund)
    if starting_available_fund <= 0:
        return AutomaticAllocationResponse(
            property_id=allocation_in.property_id,
            fund_id=fund.id,
            fiscal_year=fund.fiscal_year,
            starting_available_fund=starting_available_fund,
            ending_available_fund=starting_available_fund,
            total_allocated=Decimal("0.00"),
            allocations_created=0,
            allocations=[],
        )

    maintenance_requests = list(
        db.scalars(
            select(MaintenanceRequest)
            .where(
                MaintenanceRequest.property_id == allocation_in.property_id,
                MaintenanceRequest.status.in_(ELIGIBLE_ALLOCATION_STATUSES),
                ~MaintenanceRequest.allocation.has(),
            )
            .order_by(
                MaintenanceRequest.priority_score.desc(),
                MaintenanceRequest.requested_at.asc(),
            )
            .with_for_update()
        )
    )

    available_fund = starting_available_fund
    total_allocated = Decimal("0.00")
    allocation_items: list[AutomaticAllocationItem] = []

    for request in maintenance_requests:
        if available_fund <= 0:
            break

        requested_amount = get_request_amount(request)
        if requested_amount <= 0:
            continue

        allocated_amount = min(requested_amount, available_fund)
        allocation = Allocation(
            maintenance_request_id=request.id,
            fund_id=fund.id,
            approved_by_id=current_user.id,
            amount_allocated=allocated_amount,
            amount_released=Decimal("0.00"),
            status=AllocationStatus.RESERVED,
            decision_notes="Automatically allocated by DSS priority ranking.",
        )
        db.add(allocation)
        db.flush()

        fund.reserved_balance += allocated_amount
        available_fund -= allocated_amount
        total_allocated += allocated_amount
        request.status = MaintenanceRequestStatus.ALLOCATED

        db.add(
            FundTransaction(
                fund_id=fund.id,
                allocation_id=allocation.id,
                performed_by_id=current_user.id,
                transaction_type=FundTransactionType.RESERVE,
                amount=allocated_amount,
                balance_after=fund.current_balance,
                reference=f"AUTO-ALLOC-{allocation.id}",
                description=(
                    "Automatic reserve allocation for maintenance "
                    f"request #{request.id}."
                ),
            )
        )

        allocation_items.append(
            AutomaticAllocationItem(
                allocation_id=allocation.id,
                maintenance_request_id=request.id,
                priority_score=request.priority_score,
                requested_amount=requested_amount,
                allocated_amount=allocated_amount,
                fully_funded=allocated_amount == requested_amount,
            )
        )

    db.add(fund)
    db.commit()

    return AutomaticAllocationResponse(
        property_id=allocation_in.property_id,
        fund_id=fund.id,
        fiscal_year=fund.fiscal_year,
        starting_available_fund=starting_available_fund,
        ending_available_fund=get_fund_available_balance(fund),
        total_allocated=total_allocated,
        allocations_created=len(allocation_items),
        allocations=allocation_items,
    )

from decimal import Decimal

from app.models.allocation import AllocationStatus
from app.models.maintenance_request import MaintenanceRequest, MaintenanceRequestStatus
from app.services.allocation_service import automatically_allocate_funds, get_fund_available_balance
from app.schemas.maintenance_allocation import AutomaticAllocationRequest


def test_automatically_allocate_funds_allocates_requests(db_session, manager_user, property_with_fund):
    property_, fund = property_with_fund

    from app.models.maintenance_request import MaintenancePriority

    request_a = MaintenanceRequest(
        property_id=property_.id,
        submitted_by_id=manager_user.id,
        title="Fix roof",
        description="Roof repair",
        priority=MaintenancePriority.HIGH,
        priority_score=90,
        status=MaintenanceRequestStatus.PENDING,
        estimated_cost=Decimal("30000.00"),
        approved_cost=Decimal("25000.00"),
    )
    request_b = MaintenanceRequest(
        property_id=property_.id,
        submitted_by_id=manager_user.id,
        title="Paint walls",
        description="Exterior painting",
        priority=MaintenancePriority.MEDIUM,
        priority_score=50,
        status=MaintenanceRequestStatus.PENDING,
        estimated_cost=Decimal("10000.00"),
    )
    db_session.add_all([request_a, request_b])
    db_session.commit()

    allocation_in = AutomaticAllocationRequest(property_id=property_.id, fiscal_year=fund.fiscal_year)
    response = automatically_allocate_funds(db_session, allocation_in, manager_user)

    assert response.property_id == property_.id
    assert response.fund_id == fund.id
    assert response.total_allocated == Decimal("35000.00")
    assert response.allocations_created == 2
    assert fund.reserved_balance >= Decimal("10000.00")
    assert get_fund_available_balance(fund) == fund.current_balance - fund.reserved_balance
    assert response.ending_available_fund == get_fund_available_balance(fund)


def test_automatically_allocate_funds_returns_zero_when_no_fund(db_session, manager_user, property_with_fund):
    property_, fund = property_with_fund
    fund.current_balance = Decimal("0.00")
    fund.reserved_balance = Decimal("0.00")
    db_session.add(fund)
    db_session.commit()

    allocation_in = AutomaticAllocationRequest(property_id=property_.id, fiscal_year=fund.fiscal_year)
    response = automatically_allocate_funds(db_session, allocation_in, manager_user)

    assert response.total_allocated == Decimal("0.00")
    assert response.allocations_created == 0
    assert response.ending_available_fund == Decimal("0.00")

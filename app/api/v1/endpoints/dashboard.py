from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_property_manager, get_db
from app.models.user import User
from app.schemas.manager_property import ManagerFundsDashboard
from app.services.manager_property_service import get_manager_funds_dashboard

router = APIRouter()


@router.get(
    "/manager-funds",
    response_model=ManagerFundsDashboard,
    summary="Get manager funds dashboard",
    description=(
        "Returns manager details, total managed fund balance, assigned properties, "
        "and each property's current fund balance. Project managers can only view "
        "their own dashboard. Admins can view any project manager by passing manager_id."
    ),
    responses={
        200: {
            "description": "Manager fund dashboard",
            "content": {
                "application/json": {
                    "example": {
                        "manager": {
                            "id": 2,
                            "email": "manager@example.com",
                            "full_name": "Manager User",
                            "role": "property_manager",
                        },
                        "total_funds_managed": "175000.00",
                        "assigned_properties": [
                            {
                                "id": 10,
                                "code": "PROP-10",
                                "name": "Lekki Heights",
                                "address": "10 Admiralty Way",
                                "city": "Lagos",
                                "state": "Lagos",
                                "country": "Nigeria",
                                "total_units": 48,
                                "current_fund_balance": "175000.00",
                                "funds": [
                                    {
                                        "fund_id": 7,
                                        "fiscal_year": 2026,
                                        "current_balance": "175000.00",
                                        "reserved_balance": "25000.00",
                                        "available_balance": "150000.00",
                                        "currency": "NGN",
                                    }
                                ],
                            }
                        ],
                    }
                }
            },
        },
        400: {"description": "manager_id is required for admins"},
        403: {"description": "Project managers cannot view another manager's dashboard"},
        422: {"description": "manager_id must reference an active project manager"},
    },
)
def read_manager_funds_dashboard(
    manager_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> ManagerFundsDashboard:
    return get_manager_funds_dashboard(db, current_user=current_user, manager_id=manager_id)

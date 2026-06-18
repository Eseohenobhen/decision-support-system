from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole
from app.schemas.property import PropertyRead
from app.schemas.user import UserRead


class ManagerPropertyBase(BaseModel):
    manager_id: int = Field(gt=0, examples=[2])
    property_id: int = Field(gt=0, examples=[10])


class ManagerPropertyCreate(ManagerPropertyBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "manager_id": 2,
                "property_id": 10,
            }
        }
    )


class ManagerPropertyRead(ManagerPropertyBase):
    id: int
    assigned_at: datetime
    manager: UserRead | None = None
    property: PropertyRead | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "manager_id": 2,
                "property_id": 10,
                "assigned_at": "2026-06-18T12:00:00Z",
                "manager": {
                    "id": 2,
                    "email": "manager@example.com",
                    "full_name": "Manager User",
                    "role": "property_manager",
                    "is_active": True,
                    "created_at": "2026-06-18T10:00:00Z",
                    "updated_at": "2026-06-18T10:00:00Z",
                },
                "property": {
                    "id": 10,
                    "code": "PROP-10",
                    "name": "Lekki Heights",
                    "address": "10 Admiralty Way",
                    "city": "Lagos",
                    "state": "Lagos",
                    "country": "Nigeria",
                    "total_units": 48,
                    "manager_id": 2,
                    "created_at": "2026-06-18T10:00:00Z",
                    "updated_at": "2026-06-18T10:00:00Z",
                },
            }
        },
    )


class ManagerFundsManager(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class ManagerFundBalance(BaseModel):
    fund_id: int
    fiscal_year: int
    current_balance: Decimal
    reserved_balance: Decimal
    available_balance: Decimal
    currency: str


class ManagerFundProperty(BaseModel):
    id: int
    code: str
    name: str
    address: str
    city: str
    state: str
    country: str
    total_units: int
    current_fund_balance: Decimal
    funds: list[ManagerFundBalance]


class ManagerFundsDashboard(BaseModel):
    manager: ManagerFundsManager
    total_funds_managed: Decimal
    assigned_properties: list[ManagerFundProperty]

    model_config = ConfigDict(
        json_schema_extra={
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
    )

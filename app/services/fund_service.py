from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.property import Property
from app.models.property_fund import PropertyFund
from app.models.user import User, UserRole
from app.schemas.fund import PropertyFundCreate, PropertyFundUpdate
from app.services.manager_access import manager_property_access_filter
from app.services.property_service import get_accessible_property, get_property


def list_funds(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 100,
) -> list[PropertyFund]:
    stmt = select(PropertyFund).order_by(PropertyFund.fiscal_year.desc()).offset(skip).limit(limit)
    if current_user.role == UserRole.PROPERTY_MANAGER:
        stmt = stmt.join(Property).where(manager_property_access_filter(current_user.id))
    return list(db.scalars(stmt))


def get_fund(db: Session, fund_id: int) -> PropertyFund | None:
    return db.get(PropertyFund, fund_id)


def get_accessible_fund(
    db: Session,
    fund_id: int,
    current_user: User,
) -> PropertyFund:
    fund = get_fund(db, fund_id)
    if fund is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fund not found")

    if current_user.role == UserRole.PROPERTY_MANAGER:
        get_accessible_property(db, fund.property_id, current_user)

    return fund


def ensure_property_year_available(
    db: Session,
    property_id: int,
    fiscal_year: int,
    fund_id: int | None = None,
) -> None:
    existing = db.scalar(
        select(PropertyFund).where(
            PropertyFund.property_id == property_id,
            PropertyFund.fiscal_year == fiscal_year,
        )
    )
    if existing is not None and existing.id != fund_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A fund already exists for this property and fiscal year",
        )


def validate_balances(current_balance: Decimal, reserved_balance: Decimal) -> None:
    if reserved_balance > current_balance:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="reserved_balance cannot exceed current_balance",
        )


def create_fund(db: Session, fund_in: PropertyFundCreate) -> PropertyFund:
    if get_property(db, fund_in.property_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    ensure_property_year_available(db, fund_in.property_id, fund_in.fiscal_year)
    validate_balances(fund_in.current_balance, fund_in.reserved_balance)

    fund = PropertyFund(**fund_in.model_dump())
    db.add(fund)
    db.commit()
    db.refresh(fund)
    return fund


def update_fund(
    db: Session,
    fund: PropertyFund,
    fund_in: PropertyFundUpdate,
) -> PropertyFund:
    update_data = fund_in.model_dump(exclude_unset=True)

    fiscal_year = update_data.get("fiscal_year", fund.fiscal_year)
    ensure_property_year_available(db, fund.property_id, fiscal_year, fund.id)

    current_balance = update_data.get("current_balance", fund.current_balance)
    reserved_balance = update_data.get("reserved_balance", fund.reserved_balance)
    validate_balances(current_balance, reserved_balance)

    for field, value in update_data.items():
        setattr(fund, field, value)

    db.add(fund)
    db.commit()
    db.refresh(fund)
    return fund


def delete_fund(db: Session, fund: PropertyFund) -> None:
    db.delete(fund)
    db.commit()

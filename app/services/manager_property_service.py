from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.manager_property import ManagerProperty
from app.models.property import Property
from app.models.user import User, UserRole
from app.schemas.manager_property import (
    ManagerFundBalance,
    ManagerFundProperty,
    ManagerFundsDashboard,
    ManagerPropertyCreate,
)
from app.services.manager_access import manager_property_access_filter
from app.services.property_service import get_property, validate_property_manager


def list_manager_properties(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 100,
) -> list[ManagerProperty]:
    stmt = (
        select(ManagerProperty)
        .options(joinedload(ManagerProperty.manager), joinedload(ManagerProperty.property))
        .order_by(ManagerProperty.assigned_at.desc())
        .offset(skip)
        .limit(limit)
    )
    if current_user.role == UserRole.PROPERTY_MANAGER:
        stmt = stmt.where(ManagerProperty.manager_id == current_user.id)
    return list(db.scalars(stmt))


def create_manager_property(
    db: Session,
    assignment_in: ManagerPropertyCreate,
) -> ManagerProperty:
    validate_property_manager(db, assignment_in.manager_id)
    if get_property(db, assignment_in.property_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    existing = db.scalar(
        select(ManagerProperty).where(
            ManagerProperty.manager_id == assignment_in.manager_id,
            ManagerProperty.property_id == assignment_in.property_id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Manager is already assigned to this property",
        )

    assignment = ManagerProperty(**assignment_in.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return db.scalar(
        select(ManagerProperty)
        .options(joinedload(ManagerProperty.manager), joinedload(ManagerProperty.property))
        .where(ManagerProperty.id == assignment.id)
    )


def get_manager_property(db: Session, assignment_id: int) -> ManagerProperty:
    assignment = db.scalar(
        select(ManagerProperty)
        .options(joinedload(ManagerProperty.manager), joinedload(ManagerProperty.property))
        .where(ManagerProperty.id == assignment_id)
    )
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager property assignment not found",
        )
    return assignment


def delete_manager_property(db: Session, assignment: ManagerProperty) -> None:
    db.delete(assignment)
    db.commit()


def get_manager_funds_dashboard(
    db: Session,
    current_user: User,
    manager_id: int | None = None,
) -> ManagerFundsDashboard:
    if current_user.role == UserRole.PROPERTY_MANAGER:
        if manager_id is not None and manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project managers can only view their own fund dashboard",
            )
        manager = current_user
    else:
        if manager_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="manager_id is required when an admin views the manager funds dashboard",
            )
        manager = validate_property_manager(db, manager_id)

    stmt = (
        select(Property)
        .outerjoin(
            ManagerProperty,
            and_(
                ManagerProperty.property_id == Property.id,
                ManagerProperty.manager_id == manager.id,
            ),
        )
        .options(selectinload(Property.funds))
        .where(manager_property_access_filter(manager.id))
        .order_by(Property.name)
        .distinct()
    )
    properties = list(db.scalars(stmt))

    assigned_properties: list[ManagerFundProperty] = []
    total_funds_managed = Decimal("0.00")
    for property_ in properties:
        funds = [
            ManagerFundBalance(
                fund_id=fund.id,
                fiscal_year=fund.fiscal_year,
                current_balance=fund.current_balance,
                reserved_balance=fund.reserved_balance,
                available_balance=fund.current_balance - fund.reserved_balance,
                currency=fund.currency,
            )
            for fund in sorted(property_.funds, key=lambda item: item.fiscal_year, reverse=True)
        ]
        property_balance = sum((fund.current_balance for fund in property_.funds), Decimal("0.00"))
        total_funds_managed += property_balance
        assigned_properties.append(
            ManagerFundProperty(
                id=property_.id,
                code=property_.code,
                name=property_.name,
                address=property_.address,
                city=property_.city,
                state=property_.state,
                country=property_.country,
                total_units=property_.total_units,
                current_fund_balance=property_balance,
                funds=funds,
            )
        )

    return ManagerFundsDashboard(
        manager=manager,
        total_funds_managed=total_funds_managed,
        assigned_properties=assigned_properties,
    )

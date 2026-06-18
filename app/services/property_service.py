from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.property import Property
from app.models.user import User, UserRole
from app.schemas.property import PropertyCreate, PropertyUpdate
from app.services.manager_access import is_manager_assigned_to_property, manager_property_access_filter
from app.services.user_service import get_user_by_id


def list_properties(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 100,
) -> list[Property]:
    stmt = select(Property).order_by(Property.name).offset(skip).limit(limit)
    if current_user.role == UserRole.PROPERTY_MANAGER:
        stmt = stmt.where(manager_property_access_filter(current_user.id))
    return list(db.scalars(stmt))


def get_property(db: Session, property_id: int) -> Property | None:
    return db.get(Property, property_id)


def get_accessible_property(
    db: Session,
    property_id: int,
    current_user: User,
) -> Property:
    property_ = get_property(db, property_id)
    if property_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    if current_user.role == UserRole.PROPERTY_MANAGER and not is_manager_assigned_to_property(
        db,
        current_user.id,
        property_.id,
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    return property_


def validate_property_manager(db: Session, manager_id: int) -> User:
    manager = get_user_by_id(db, manager_id)
    if manager is None or not manager.is_active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="manager_id must reference an active user",
        )
    if manager.role != UserRole.PROPERTY_MANAGER:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="manager_id must reference a property manager",
        )
    return manager


def ensure_property_code_available(
    db: Session,
    code: str,
    property_id: int | None = None,
) -> None:
    existing = db.scalar(select(Property).where(Property.code == code))
    if existing is not None and existing.id != property_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A property with this code already exists",
        )


def create_property(db: Session, property_in: PropertyCreate) -> Property:
    validate_property_manager(db, property_in.manager_id)
    ensure_property_code_available(db, property_in.code)

    property_ = Property(**property_in.model_dump())
    db.add(property_)
    db.commit()
    db.refresh(property_)
    return property_


def update_property(
    db: Session,
    property_: Property,
    property_in: PropertyUpdate,
) -> Property:
    update_data = property_in.model_dump(exclude_unset=True)

    if "code" in update_data:
        ensure_property_code_available(db, update_data["code"], property_.id)
    if "manager_id" in update_data:
        validate_property_manager(db, update_data["manager_id"])

    for field, value in update_data.items():
        setattr(property_, field, value)

    db.add(property_)
    db.commit()
    db.refresh(property_)
    return property_


def delete_property(db: Session, property_: Property) -> None:
    db.delete(property_)
    db.commit()

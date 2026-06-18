from sqlalchemy import or_, select
from sqlalchemy.orm import Session, aliased

from app.models.manager_property import ManagerProperty
from app.models.property import Property


def manager_property_access_filter(manager_id: int):
    assignment = aliased(ManagerProperty)
    assignment_exists = (
        select(assignment.id)
        .where(
            assignment.property_id == Property.id,
            assignment.manager_id == manager_id,
        )
        .correlate(Property)
        .exists()
    )
    return or_(Property.manager_id == manager_id, assignment_exists)


def is_manager_assigned_to_property(db: Session, manager_id: int, property_id: int) -> bool:
    property_ = db.get(Property, property_id)
    if property_ is None:
        return False
    if property_.manager_id == manager_id:
        return True
    return db.scalar(
        select(ManagerProperty.id).where(
            ManagerProperty.manager_id == manager_id,
            ManagerProperty.property_id == property_id,
        )
    ) is not None

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.maintenance_request import MaintenanceRequest, MaintenanceRequestStatus
from app.models.property import Property
from app.models.user import User, UserRole
from app.schemas.maintenance_request_crud import (
    MaintenanceRequestCreate,
    MaintenanceRequestUpdate,
)
from app.services.property_service import get_accessible_property


def list_maintenance_requests(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 100,
    property_id: int | None = None,
    status_filter: MaintenanceRequestStatus | None = None,
) -> list[MaintenanceRequest]:
    stmt = select(MaintenanceRequest).order_by(MaintenanceRequest.requested_at.desc())

    if current_user.role == UserRole.PROPERTY_MANAGER:
        stmt = stmt.join(Property).where(Property.manager_id == current_user.id)

    if property_id is not None:
        if current_user.role == UserRole.PROPERTY_MANAGER:
            get_accessible_property(db, property_id, current_user)
        stmt = stmt.where(MaintenanceRequest.property_id == property_id)

    if status_filter is not None:
        stmt = stmt.where(MaintenanceRequest.status == status_filter)

    return list(db.scalars(stmt.offset(skip).limit(limit)))


def get_maintenance_request(
    db: Session,
    request_id: int,
) -> MaintenanceRequest | None:
    return db.get(MaintenanceRequest, request_id)


def get_accessible_maintenance_request(
    db: Session,
    request_id: int,
    current_user: User,
) -> MaintenanceRequest:
    request = get_maintenance_request(db, request_id)
    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance request not found",
        )

    if current_user.role == UserRole.PROPERTY_MANAGER:
        get_accessible_property(db, request.property_id, current_user)

    return request


def create_maintenance_request(
    db: Session,
    request_in: MaintenanceRequestCreate,
    submitted_by: User,
) -> MaintenanceRequest:
    get_accessible_property(db, request_in.property_id, submitted_by)

    request = MaintenanceRequest(
        **request_in.model_dump(),
        submitted_by_id=submitted_by.id,
        status=MaintenanceRequestStatus.PENDING,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def update_maintenance_request(
    db: Session,
    request: MaintenanceRequest,
    request_in: MaintenanceRequestUpdate,
) -> MaintenanceRequest:
    update_data = request_in.model_dump(exclude_unset=True)

    if (
        update_data.get("completed_at") is not None
        and update_data.get("status", request.status) != MaintenanceRequestStatus.COMPLETED
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="completed_at can only be set when status is completed",
        )

    for field, value in update_data.items():
        setattr(request, field, value)

    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def delete_maintenance_request(db: Session, request: MaintenanceRequest) -> None:
    db.delete(request)
    db.commit()

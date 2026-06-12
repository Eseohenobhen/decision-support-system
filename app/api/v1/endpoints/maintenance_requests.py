from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_property_manager, get_db
from app.models.maintenance_request import MaintenanceRequestStatus
from app.models.user import User
from app.schemas.maintenance_request_crud import (
    MaintenanceRequestCreate,
    MaintenanceRequestRead,
    MaintenanceRequestUpdate,
)
from app.services.maintenance_request_service import (
    create_maintenance_request,
    delete_maintenance_request,
    get_accessible_maintenance_request,
    list_maintenance_requests,
    update_maintenance_request,
)

router = APIRouter()


@router.get("/", response_model=list[MaintenanceRequestRead])
def read_maintenance_requests(
    skip: int = 0,
    limit: int = 100,
    property_id: int | None = Query(default=None, gt=0),
    status_filter: MaintenanceRequestStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> list[MaintenanceRequestRead]:
    return list_maintenance_requests(
        db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        property_id=property_id,
        status_filter=status_filter,
    )


@router.post("/", response_model=MaintenanceRequestRead, status_code=status.HTTP_201_CREATED)
def create_new_maintenance_request(
    request_in: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> MaintenanceRequestRead:
    return create_maintenance_request(db, request_in=request_in, submitted_by=current_user)


@router.get("/{request_id}", response_model=MaintenanceRequestRead)
def read_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> MaintenanceRequestRead:
    return get_accessible_maintenance_request(
        db,
        request_id=request_id,
        current_user=current_user,
    )


@router.patch("/{request_id}", response_model=MaintenanceRequestRead)
def update_existing_maintenance_request(
    request_id: int,
    request_in: MaintenanceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> MaintenanceRequestRead:
    request = get_accessible_maintenance_request(
        db,
        request_id=request_id,
        current_user=current_user,
    )
    return update_maintenance_request(db, request=request, request_in=request_in)


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    request = get_accessible_maintenance_request(
        db,
        request_id=request_id,
        current_user=current_user,
    )
    delete_maintenance_request(db, request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

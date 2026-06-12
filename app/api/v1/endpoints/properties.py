from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_property_manager, get_db
from app.models.user import User
from app.schemas.property import PropertyCreate, PropertyRead, PropertyUpdate
from app.services.property_service import (
    create_property,
    delete_property,
    get_accessible_property,
    list_properties,
    update_property,
)

router = APIRouter()


@router.get("/", response_model=list[PropertyRead])
def read_properties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> list[PropertyRead]:
    return list_properties(db, current_user=current_user, skip=skip, limit=limit)


@router.post("/", response_model=PropertyRead, status_code=status.HTTP_201_CREATED)
def create_new_property(
    property_in: PropertyCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> PropertyRead:
    return create_property(db, property_in=property_in)


@router.get("/{property_id}", response_model=PropertyRead)
def read_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> PropertyRead:
    return get_accessible_property(db, property_id=property_id, current_user=current_user)


@router.patch("/{property_id}", response_model=PropertyRead)
def update_existing_property(
    property_id: int,
    property_in: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> PropertyRead:
    property_ = get_accessible_property(db, property_id=property_id, current_user=current_user)
    return update_property(db, property_=property_, property_in=property_in)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    property_ = get_accessible_property(db, property_id=property_id, current_user=current_user)
    delete_property(db, property_)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_property_manager, get_db
from app.models.user import User
from app.schemas.fund import PropertyFundCreate, PropertyFundRead, PropertyFundUpdate
from app.services.fund_service import (
    create_fund,
    delete_fund,
    get_accessible_fund,
    list_funds,
    update_fund,
)

router = APIRouter()


@router.get("/", response_model=list[PropertyFundRead])
def read_funds(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> list[PropertyFundRead]:
    return list_funds(db, current_user=current_user, skip=skip, limit=limit)


@router.post("/", response_model=PropertyFundRead, status_code=status.HTTP_201_CREATED)
def create_new_fund(
    fund_in: PropertyFundCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> PropertyFundRead:
    return create_fund(db, fund_in=fund_in)


@router.get("/{fund_id}", response_model=PropertyFundRead)
def read_fund(
    fund_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> PropertyFundRead:
    return get_accessible_fund(db, fund_id=fund_id, current_user=current_user)


@router.patch("/{fund_id}", response_model=PropertyFundRead)
def update_existing_fund(
    fund_id: int,
    fund_in: PropertyFundUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> PropertyFundRead:
    fund = get_accessible_fund(db, fund_id=fund_id, current_user=current_user)
    return update_fund(db, fund=fund, fund_in=fund_in)


@router.delete("/{fund_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_fund(
    fund_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    fund = get_accessible_fund(db, fund_id=fund_id, current_user=current_user)
    delete_fund(db, fund)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

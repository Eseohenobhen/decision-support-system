from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import create_user, get_user_by_email, list_users

router = APIRouter()


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/", response_model=list[UserRead])
def read_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[User]:
    return list_users(db)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> User:
    existing_user = get_user_by_email(db, email=user_in.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    return create_user(db, user_in=user_in)

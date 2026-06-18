from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_property_manager, get_db
from app.models.user import User
from app.schemas.manager_property import ManagerPropertyCreate, ManagerPropertyRead
from app.services.manager_property_service import (
    create_manager_property,
    delete_manager_property,
    get_manager_property,
    list_manager_properties,
)

router = APIRouter()


@router.post(
    "",
    response_model=ManagerPropertyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a property to a project manager",
    description="Creates a property assignment for an active project manager. Admin access is required.",
    responses={
        201: {
            "description": "Property assigned to manager",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "manager_id": 2,
                        "property_id": 10,
                        "assigned_at": "2026-06-18T12:00:00Z",
                        "manager": None,
                        "property": None,
                    }
                }
            },
        },
        403: {"description": "Admin access required"},
        404: {"description": "Property not found"},
        409: {"description": "Manager is already assigned to this property"},
        422: {"description": "manager_id must reference an active project manager"},
    },
)
def assign_property_to_manager(
    assignment_in: ManagerPropertyCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> ManagerPropertyRead:
    return create_manager_property(db, assignment_in=assignment_in)


@router.get(
    "",
    response_model=list[ManagerPropertyRead],
    summary="List manager property assignments",
    description=(
        "Admins can list all assignments. Project managers receive only assignments "
        "that belong to their own user account."
    ),
    responses={
        200: {
            "description": "Manager property assignments",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "manager_id": 2,
                            "property_id": 10,
                            "assigned_at": "2026-06-18T12:00:00Z",
                            "manager": None,
                            "property": None,
                        }
                    ]
                }
            },
        },
        403: {"description": "Authenticated admin or project manager access required"},
    },
)
def read_manager_properties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> list[ManagerPropertyRead]:
    return list_manager_properties(db, current_user=current_user, skip=skip, limit=limit)


@router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a manager property assignment",
    description="Deletes a property assignment from a project manager. Admin access is required.",
    responses={
        204: {"description": "Assignment deleted"},
        403: {"description": "Admin access required"},
        404: {"description": "Manager property assignment not found"},
    },
)
def delete_property_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> Response:
    assignment = get_manager_property(db, assignment_id)
    delete_manager_property(db, assignment)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

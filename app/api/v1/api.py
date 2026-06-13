from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    funds,
    maintenance_allocations,
    maintenance_requests,
    properties,
    reports,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(funds.router, prefix="/funds", tags=["funds"])
api_router.include_router(
    maintenance_requests.router,
    prefix="/maintenance-requests",
    tags=["maintenance requests"],
)
api_router.include_router(
    maintenance_allocations.router,
    prefix="/maintenance-allocations",
    tags=["maintenance allocations"],
)
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

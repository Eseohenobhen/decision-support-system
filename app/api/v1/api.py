from fastapi import APIRouter

from app.api.v1.endpoints import auth, maintenance_allocations, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    maintenance_allocations.router,
    prefix="/maintenance-allocations",
    tags=["maintenance allocations"],
)

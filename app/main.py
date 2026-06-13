from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="1.0.0",
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", tags=["root"])
    def root() -> dict[str, str]:
        return {
            "application": "Decision Support System for Property Fund Allocation and Maintenance Requests",
            "status": "running",
            "version": "1.0.0",
        }

    return app


app = create_app()

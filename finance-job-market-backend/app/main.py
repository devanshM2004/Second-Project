"""FastAPI application entry point.

Run locally with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.config import settings
from app.routes import bls, health


def create_app() -> FastAPI:
    """Factory that builds and configures the FastAPI application."""
    app = FastAPI(
        title="Finance Job Market Backend",
        description=(
            "Backend service that tracks the US job market for entry-level "
            "finance roles. The first integrated data source is the U.S. "
            "Bureau of Labor Statistics (BLS) Public Data API v2."
        ),
        version="0.1.0",
    )

    # Route registration
    app.include_router(health.router)
    app.include_router(bls.router, prefix="/api/bls", tags=["bls"])

    @app.get("/", tags=["root"])
    def root() -> dict:
        """Simple landing route that confirms the service is up."""
        return {
            "app": settings.app_name,
            "env": settings.app_env,
            "message": "Finance Job Market Backend is running.",
            "docs": "/docs",
        }

    return app


app = create_app()

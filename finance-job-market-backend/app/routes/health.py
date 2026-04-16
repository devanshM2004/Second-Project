"""Health check route."""

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Return a simple JSON payload so monitors can confirm the API is up."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "bls_api_key_configured": settings.has_bls_key,
    }

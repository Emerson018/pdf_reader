from fastapi import APIRouter
from apps.api.app.schemas.health import HealthStatus

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
async def get_health():
    """Basic health check endpoint."""
    return HealthStatus(
        status="ok",
        version="1.0.0",
        services={
            "api": "healthy"
        }
    )


@router.get("/health/ready", response_model=HealthStatus)
async def get_readiness():
    """Readiness probe endpoint."""
    return HealthStatus(
        status="ok",
        version="1.0.0",
        services={
            "api": "ready"
        }
    )


@router.get("/health/live", response_model=HealthStatus)
async def get_liveness():
    """Liveness probe endpoint."""
    return HealthStatus(
        status="ok",
        version="1.0.0",
        services={
            "api": "live"
        }
    )

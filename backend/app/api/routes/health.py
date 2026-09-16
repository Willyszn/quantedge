from fastapi import APIRouter

from app.core.config import get_settings
from app.core.database import check_database_connection
from app.core.redis_client import check_redis_connection

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Service health check",
    description="Reports process, database, and Redis health. Never exposes credentials or internals.",
)
async def health_check() -> dict:
    settings = get_settings()
    db_ok = await check_database_connection()
    redis_ok = await check_redis_connection()

    return {
        "status": "ok" if db_ok and redis_ok else "degraded",
        "environment": settings.ENVIRONMENT,
        "database": "ok" if db_ok else "unavailable",
        "redis": "ok" if redis_ok else "unavailable",
    }

import asyncio
from typing import Any

from fastapi import APIRouter, Response, status

from apps.api.health import check_database, check_minio, check_redis

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic liveness probe endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@router.get("/ready")
async def readiness_check(response: Response) -> dict[str, Any]:
    """Readiness probe checking live status of backing services."""
    (
        (db_ok, db_msg),
        (redis_ok, redis_msg),
        (minio_ok, minio_msg),
    ) = await asyncio.gather(
        check_database(),
        check_redis(),
        check_minio(),
    )

    services_status = {
        "database": db_msg,
        "redis": redis_msg,
        "minio": minio_msg,
    }

    all_ready = db_ok and redis_ok and minio_ok
    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "services": services_status,
        }

    return {
        "status": "ready",
        "services": services_status,
    }

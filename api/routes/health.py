"""
Health Check Routes.

Provides endpoints for monitoring service health and readiness.
"""

from datetime import datetime, timezone
from typing import Dict, Any
import redis.asyncio as aioredis

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.models.base import get_db
from api.celery_app import celery_app


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check.

    Returns:
        dict: Health status information
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": settings.app_name,
        "version": settings.app_version
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Deep readiness check - verifies all dependencies are available.

    Checks:
    - Database connectivity
    - Redis connectivity
    - Celery worker availability

    Args:
        db: Database session

    Returns:
        dict: Readiness status information
    """
    checks = {
        "database": "unknown",
        "redis": "unknown",
        "celery": "unknown"
    }

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            checks["database"] = "ok"
        else:
            checks["database"] = "error"
    except Exception as e:
        checks["database"] = f"error: {str(e)[:100]}"

    # Check Redis
    try:
        redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2
        )
        await redis_client.ping()
        checks["redis"] = "ok"
        await redis_client.close()
    except Exception as e:
        checks["redis"] = f"error: {str(e)[:100]}"

    # Check Celery workers
    try:
        # Inspect active workers
        inspect = celery_app.control.inspect(timeout=2.0)
        active_workers = inspect.active()
        if active_workers and len(active_workers) > 0:
            checks["celery"] = f"ok ({len(active_workers)} workers)"
        else:
            checks["celery"] = "error: no active workers"
    except Exception as e:
        checks["celery"] = f"error: {str(e)[:100]}"

    # Determine overall status
    all_ok = all(
        check_status.startswith("ok")
        for check_status in checks.values()
    )

    status_code = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if all_ok else "not_ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "service": settings.app_name,
        "version": settings.app_version
    }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, str]:
    """
    Liveness check - simple check that service is running.

    Returns:
        dict: Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/metrics", status_code=status.HTTP_200_OK)
async def metrics_info() -> Dict[str, Any]:
    """
    Metrics endpoint information.

    Returns:
        dict: Metrics endpoint details
    """
    return {
        "prometheus_enabled": settings.enable_metrics,
        "prometheus_port": settings.metrics_port,
        "prometheus_endpoint": f"http://localhost:{settings.metrics_port}/metrics",
        "grafana_dashboards": "/monitoring/grafana/dashboards/",
    }

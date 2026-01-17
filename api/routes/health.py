"""
Health Check Routes.

Provides endpoints for monitoring service health and readiness.
"""

from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.models.base import get_db


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
    Readiness check - verifies all dependencies are available.

    Checks:
    - Database connectivity
    - Redis connectivity (TODO)
    - External services (TODO)

    Args:
        db: Database session

    Returns:
        dict: Readiness status information
    """
    checks = {
        "database": "unknown",
        "redis": "not_checked",
        "celery": "not_checked"
    }

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            checks["database"] = "ok"
        else:
            checks["database"] = "error"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    # TODO: Check Redis
    # TODO: Check Celery

    # Determine overall status
    all_ok = all(
        status in ["ok", "not_checked"]
        for status in checks.values()
    )

    return {
        "status": "ready" if all_ok else "not_ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks
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

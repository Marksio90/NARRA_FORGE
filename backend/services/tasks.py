"""Celery tasks for NARRA_FORGE."""

import logging

from celery import Celery

from core.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "narra_forge",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
)


@celery_app.task(name="tasks.health_check")  # type: ignore[misc]
def health_check() -> dict[str, str]:
    """Health check task for Celery worker."""
    logger.info("Celery health check task executed")
    return {"status": "healthy", "message": "Celery worker is operational"}

"""
Celery tasks for NarraForge background job processing.

This module defines asynchronous tasks for book generation pipeline.
Full implementation will be added in Phase 2.
"""

from celery import Celery

from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Initialize Celery app
celery_app = Celery(
    "narraforge",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="tasks.health_check", bind=True)
def health_check(self) -> dict:
    """
    Health check task for Celery worker.

    Returns:
        dict: Health status
    """
    logger.info("Celery worker health check", task_id=self.request.id)
    return {"status": "healthy", "worker": "running"}


# Placeholder for book generation task (will be implemented in Phase 2)
# @celery_app.task(name="tasks.generate_book", bind=True)
# def generate_book_task(self, job_id: str):
#     """Generate book asynchronously (Phase 2)."""
#     pass

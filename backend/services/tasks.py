"""Celery tasks for NARRA_FORGE."""

import logging
from typing import Any

from celery import Celery
from celery.result import AsyncResult

from core.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "narra_forge",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery with queues and routing
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
    # Task routing - different queues for different priorities
    task_routes={
        "tasks.health_check": {"queue": "default"},
        "tasks.job.*": {"queue": "jobs"},
        "tasks.agent.*": {"queue": "agents"},
        "tasks.qa.*": {"queue": "qa"},
    },
    # Default queue
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    # Result backend settings
    result_backend_transport_options={
        "master_name": "mymaster",
        "retry_on_timeout": True,
    },
    result_expires=86400,  # 24 hours
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    # Task result settings
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    # Acks late for reliability
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


@celery_app.task(name="tasks.health_check")
def health_check() -> dict[str, str]:
    """Health check task for Celery worker."""
    logger.info("Celery health check task executed")
    return {"status": "healthy", "message": "Celery worker is operational"}


def get_task_status(task_id: str) -> dict[str, Any]:
    """
    Get status of a Celery task.

    Args:
        task_id: Celery task ID

    Returns:
        Dictionary with task status information
    """
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.state,
        "result": result.result if result.ready() else None,
        "traceback": result.traceback if result.failed() else None,
    }


def revoke_task(task_id: str, terminate: bool = False) -> dict[str, Any]:
    """
    Revoke (cancel) a Celery task.

    Args:
        task_id: Celery task ID
        terminate: If True, terminate the task immediately (SIGKILL)

    Returns:
        Dictionary with revocation status
    """
    celery_app.control.revoke(task_id, terminate=terminate)
    logger.info(f"Task {task_id} revoked (terminate={terminate})")
    return {"task_id": task_id, "revoked": True, "terminated": terminate}

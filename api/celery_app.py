"""
Celery application for asynchronous task processing.

Handles long-running narrative generation jobs in the background.
"""

import os
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

from api.config import get_settings


settings = get_settings()

# Create Celery app
celery_app = Celery(
    "narra_forge",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["api.tasks.narrative"]  # Task modules to import
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=settings.celery_task_track_started,
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_time_limit - 300,  # 5 min before hard limit
    task_acks_late=True,  # Acknowledge after task completion
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (prevent memory leaks)
    result_expires=86400,  # Results expire after 24 hours
    task_routes={
        "api.tasks.narrative.*": {"queue": "narrative_generation"},
    },
)


# Task lifecycle hooks
@task_prerun.connect
def task_prerun_handler(task_id, task, args, kwargs, **extra):
    """Log when task starts."""
    print(f"[CELERY] Task {task.name} [{task_id}] started")


@task_postrun.connect
def task_postrun_handler(task_id, task, args, kwargs, retval, **extra):
    """Log when task completes."""
    print(f"[CELERY] Task {task.name} [{task_id}] completed")


@task_failure.connect
def task_failure_handler(task_id, exception, args, kwargs, traceback, einfo, **extra):
    """Log when task fails."""
    print(f"[CELERY] Task [{task_id}] failed: {exception}")


if __name__ == "__main__":
    celery_app.start()

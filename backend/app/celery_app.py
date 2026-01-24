"""
Celery application configuration
"""

from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "narraforge",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.generation_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=7200,  # 2 hours max per task (aligned with generation timeout)
    task_soft_time_limit=6900,  # 1h 55min soft limit (warning before hard kill)
    worker_prefetch_multiplier=1,
)

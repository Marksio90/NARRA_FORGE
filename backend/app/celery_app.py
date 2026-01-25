"""
Celery application configuration

Time limits updated for Beat Sheet Architecture:
- 33 chapters × 5 scenes = 165 scenes
- ~1-2 min per scene (Beat Sheet + prose) = 165-330 minutes
- Buffer for retries and network latency
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
    # Increased limits for Beat Sheet Architecture (scene-by-scene generation)
    # Full novel: ~165 scenes × ~2 min = ~5.5 hours max
    task_time_limit=21600,       # 6 hours max per task (hard kill)
    task_soft_time_limit=21000,  # 5h 50min soft limit (warning before hard kill)
    worker_prefetch_multiplier=1,
)

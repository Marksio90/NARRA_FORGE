"""
Celery tasks for NARRA_FORGE.

Tasks:
- narrative: Narrative generation tasks
"""

from api.tasks.narrative import generate_narrative_task

__all__ = ["generate_narrative_task"]

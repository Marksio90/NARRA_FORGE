"""Job orchestration tasks for literary production pipeline."""

import logging
import uuid
from datetime import datetime
from typing import Any

from core.exceptions import TokenBudgetExceededError
from services.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.job.create", bind=True)
def create_job_task(
    self: Any,
    job_type: str,
    genre: str,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a new literary production job.

    Args:
        job_type: Type of work (short_story, novella, novel, saga)
        genre: Genre (fantasy, sci-fi, thriller, etc.)
        parameters: Job-specific parameters

    Returns:
        Dictionary with job information
    """
    job_id = uuid.uuid4()

    logger.info(
        "Creating job",
        extra={
            "job_id": str(job_id),
            "job_type": job_type,
            "genre": genre,
            "task_id": self.request.id,
        },
    )

    # In a real implementation, this would create a database record
    # For now, return job metadata
    return {
        "job_id": str(job_id),
        "job_type": job_type,
        "genre": genre,
        "status": "created",
        "created_at": datetime.utcnow().isoformat(),
        "parameters": parameters,
        "task_id": self.request.id,
    }


@celery_app.task(name="tasks.job.execute_pipeline", bind=True)
def execute_pipeline_task(
    self: Any,
    job_id: str,
    pipeline_stages: list[str],
) -> dict[str, Any]:
    """
    Execute the full literary production pipeline for a job.

    Args:
        job_id: UUID of the job
        pipeline_stages: List of pipeline stages to execute

    Returns:
        Dictionary with pipeline execution results
    """
    logger.info(
        "Executing pipeline",
        extra={
            "job_id": job_id,
            "stages": pipeline_stages,
            "task_id": self.request.id,
        },
    )

    results = {
        "job_id": job_id,
        "stages_completed": [],
        "stages_failed": [],
        "task_id": self.request.id,
    }

    # In a real implementation, this would orchestrate agent tasks
    # For now, simulate pipeline execution
    for stage in pipeline_stages:
        logger.info(f"Executing stage: {stage}", extra={"job_id": job_id})
        results["stages_completed"].append(stage)

    return results


@celery_app.task(name="tasks.job.update_status", bind=True)
def update_job_status_task(
    self: Any,
    job_id: str,
    status: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Update job status in database.

    Args:
        job_id: UUID of the job
        status: New status (queued, running, completed, failed)
        metadata: Optional metadata to attach

    Returns:
        Dictionary with update confirmation
    """
    logger.info(
        "Updating job status",
        extra={
            "job_id": job_id,
            "new_status": status,
            "task_id": self.request.id,
        },
    )

    return {
        "job_id": job_id,
        "status": status,
        "updated_at": datetime.utcnow().isoformat(),
        "metadata": metadata or {},
        "task_id": self.request.id,
    }


@celery_app.task(name="tasks.job.track_cost", bind=True)
def track_cost_task(
    self: Any,
    job_id: str,
    stage: str,
    cost_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Track cost for a pipeline stage.

    Args:
        job_id: UUID of the job
        stage: Pipeline stage name
        cost_data: Cost information (tokens, cost_usd, model)

    Returns:
        Dictionary with cost tracking confirmation
    """
    logger.info(
        "Tracking cost",
        extra={
            "job_id": job_id,
            "stage": stage,
            "cost_usd": cost_data.get("cost_usd"),
            "task_id": self.request.id,
        },
    )

    return {
        "job_id": job_id,
        "stage": stage,
        "cost_data": cost_data,
        "tracked_at": datetime.utcnow().isoformat(),
        "task_id": self.request.id,
    }


@celery_app.task(
    name="tasks.job.cleanup",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def cleanup_job_task(
    self: Any,
    job_id: str,
    remove_artifacts: bool = False,
) -> dict[str, Any]:
    """
    Clean up job resources after completion or failure.

    Args:
        job_id: UUID of the job
        remove_artifacts: If True, remove all artifacts

    Returns:
        Dictionary with cleanup results
    """
    logger.info(
        "Cleaning up job",
        extra={
            "job_id": job_id,
            "remove_artifacts": remove_artifacts,
            "task_id": self.request.id,
        },
    )

    return {
        "job_id": job_id,
        "cleaned_up": True,
        "artifacts_removed": remove_artifacts,
        "cleanup_at": datetime.utcnow().isoformat(),
        "task_id": self.request.id,
    }


@celery_app.task(name="tasks.job.check_budget", bind=True)
def check_budget_task(
    self: Any,
    job_id: str,
    current_cost: float,
    budget_limit: float,
) -> dict[str, Any]:
    """
    Check if job is within budget limits.

    Args:
        job_id: UUID of the job
        current_cost: Current cumulative cost in USD
        budget_limit: Maximum allowed cost in USD

    Returns:
        Dictionary with budget check results

    Raises:
        TokenBudgetExceededError: If budget is exceeded
    """
    logger.info(
        "Checking budget",
        extra={
            "job_id": job_id,
            "current_cost": current_cost,
            "budget_limit": budget_limit,
            "task_id": self.request.id,
        },
    )

    if current_cost > budget_limit:
        error_msg = f"Budget exceeded: ${current_cost:.2f} > ${budget_limit:.2f}"
        logger.error(error_msg, extra={"job_id": job_id})
        raise TokenBudgetExceededError(error_msg)

    remaining = budget_limit - current_cost
    percent_used = (current_cost / budget_limit) * 100

    return {
        "job_id": job_id,
        "current_cost": current_cost,
        "budget_limit": budget_limit,
        "remaining": remaining,
        "percent_used": percent_used,
        "within_budget": True,
        "task_id": self.request.id,
    }

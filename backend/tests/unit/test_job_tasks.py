"""Unit tests for job orchestration tasks."""

import pytest

from core.exceptions import TokenBudgetExceededError
from services.job_tasks import (
    check_budget_task,
    cleanup_job_task,
    create_job_task,
    execute_pipeline_task,
    track_cost_task,
    update_job_status_task,
)


def test_create_job_task() -> None:
    """Test job creation task."""
    result = create_job_task.apply(
        kwargs={
            "job_type": "short_story",
            "genre": "fantasy",
            "parameters": {"theme": "adventure"},
        }
    ).get()

    assert "job_id" in result
    assert result["job_type"] == "short_story"
    assert result["genre"] == "fantasy"
    assert result["status"] == "created"
    assert result["parameters"]["theme"] == "adventure"
    assert "task_id" in result


def test_execute_pipeline_task() -> None:
    """Test pipeline execution task."""
    stages = ["interpret", "world", "characters", "plot"]
    result = execute_pipeline_task.apply(
        kwargs={"job_id": "job-123", "pipeline_stages": stages}
    ).get()

    assert result["job_id"] == "job-123"
    assert len(result["stages_completed"]) == 4
    assert result["stages_completed"] == stages
    assert len(result["stages_failed"]) == 0
    assert "task_id" in result


def test_update_job_status_task() -> None:
    """Test job status update task."""
    result = update_job_status_task.apply(
        kwargs={
            "job_id": "job-456",
            "status": "running",
            "metadata": {"progress": 50},
        }
    ).get()

    assert result["job_id"] == "job-456"
    assert result["status"] == "running"
    assert result["metadata"]["progress"] == 50
    assert "updated_at" in result
    assert "task_id" in result


def test_track_cost_task() -> None:
    """Test cost tracking task."""
    cost_data = {
        "tokens": 1500,
        "cost_usd": 0.0045,
        "model": "gpt-4o-mini",
    }

    result = track_cost_task.apply(
        kwargs={
            "job_id": "job-789",
            "stage": "prose_generation",
            "cost_data": cost_data,
        }
    ).get()

    assert result["job_id"] == "job-789"
    assert result["stage"] == "prose_generation"
    assert result["cost_data"]["tokens"] == 1500
    assert result["cost_data"]["cost_usd"] == 0.0045
    assert "tracked_at" in result
    assert "task_id" in result


def test_cleanup_job_task() -> None:
    """Test job cleanup task."""
    result = cleanup_job_task.apply(
        kwargs={"job_id": "job-999", "remove_artifacts": True}
    ).get()

    assert result["job_id"] == "job-999"
    assert result["cleaned_up"] is True
    assert result["artifacts_removed"] is True
    assert "cleanup_at" in result
    assert "task_id" in result


def test_cleanup_job_task_keep_artifacts() -> None:
    """Test job cleanup task keeping artifacts."""
    result = cleanup_job_task.apply(
        kwargs={"job_id": "job-888", "remove_artifacts": False}
    ).get()

    assert result["job_id"] == "job-888"
    assert result["cleaned_up"] is True
    assert result["artifacts_removed"] is False


def test_check_budget_task_within_budget() -> None:
    """Test budget check when within limits."""
    result = check_budget_task.apply(
        kwargs={
            "job_id": "job-111",
            "current_cost": 5.0,
            "budget_limit": 10.0,
        }
    ).get()

    assert result["job_id"] == "job-111"
    assert result["current_cost"] == 5.0
    assert result["budget_limit"] == 10.0
    assert result["remaining"] == 5.0
    assert result["percent_used"] == 50.0
    assert result["within_budget"] is True


def test_check_budget_task_exceeds_budget() -> None:
    """Test budget check when exceeding limits."""
    with pytest.raises(TokenBudgetExceededError, match="Budget exceeded"):
        check_budget_task.apply(
            kwargs={
                "job_id": "job-222",
                "current_cost": 15.0,
                "budget_limit": 10.0,
            }
        ).get()


def test_check_budget_task_exact_limit() -> None:
    """Test budget check at exact limit."""
    result = check_budget_task.apply(
        kwargs={
            "job_id": "job-333",
            "current_cost": 10.0,
            "budget_limit": 10.0,
        }
    ).get()

    assert result["within_budget"] is True
    assert result["remaining"] == 0.0
    assert result["percent_used"] == 100.0

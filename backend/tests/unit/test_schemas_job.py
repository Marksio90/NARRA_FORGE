"""Unit tests for job schemas."""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from models.schemas.job import (
    BudgetCheckResponse,
    CreateJobRequest,
    JobResponse,
    JobStatusUpdate,
    PipelineExecutionResponse,
    TaskStatusResponse,
)


def test_create_job_request_valid() -> None:
    """Test CreateJobRequest with valid data."""
    req = CreateJobRequest(
        job_type="short_story",
        genre="fantasy",
        inspiration="A story about magic and dragons",
    )

    assert req.job_type == "short_story"
    assert req.genre == "fantasy"
    assert req.inspiration == "A story about magic and dragons"
    assert req.constraints == {}  # Default


def test_create_job_request_with_constraints() -> None:
    """Test CreateJobRequest with constraints."""
    req = CreateJobRequest(
        job_type="novel",
        genre="sci-fi",
        constraints={
            "max_characters": 10,
            "target_word_count": 80000,
            "themes": ["AI", "consciousness"],
        },
    )

    assert req.constraints["max_characters"] == 10
    assert req.constraints["target_word_count"] == 80000


def test_create_job_request_constraints_validation() -> None:
    """Test CreateJobRequest constraints validation."""
    # Invalid - unknown constraint key
    with pytest.raises(ValidationError, match="Unknown constraint key"):
        CreateJobRequest(
            job_type="short_story",
            genre="fantasy",
            constraints={"invalid_key": "value"},
        )


def test_create_job_request_budget_validation() -> None:
    """Test CreateJobRequest budget validation."""
    # Valid budget
    req = CreateJobRequest(
        job_type="short_story",
        genre="fantasy",
        budget_limit=50.0,
    )
    assert req.budget_limit == 50.0

    # Invalid - negative budget
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        CreateJobRequest(
            job_type="short_story",
            genre="fantasy",
            budget_limit=-10.0,
        )

    # Invalid - budget too high
    with pytest.raises(ValidationError, match="less than or equal to 1000"):
        CreateJobRequest(
            job_type="short_story",
            genre="fantasy",
            budget_limit=1500.0,
        )


def test_create_job_request_genre_validation() -> None:
    """Test CreateJobRequest genre validation."""
    # Invalid genre
    with pytest.raises(ValidationError, match="Invalid genre"):
        CreateJobRequest(
            job_type="short_story",
            genre="invalid_genre",
        )


def test_create_job_request_type_validation() -> None:
    """Test CreateJobRequest job type validation."""
    # Invalid job type
    with pytest.raises(ValidationError, match="Invalid job type"):
        CreateJobRequest(
            job_type="invalid_type",
            genre="fantasy",
        )


def test_job_response_valid() -> None:
    """Test JobResponse with valid data."""
    job_id = uuid4()
    now = datetime.utcnow()

    resp = JobResponse(
        id=job_id,
        type="short_story",
        genre="fantasy",
        status="queued",
        created_at=now,
        updated_at=now,
    )

    assert resp.id == job_id
    assert resp.type == "short_story"
    assert resp.status == "queued"
    assert resp.total_cost is None  # Not set yet
    assert resp.artifacts_count == 0  # Default


def test_job_response_status_validation() -> None:
    """Test JobResponse status validation."""
    job_id = uuid4()
    now = datetime.utcnow()

    # Invalid status
    with pytest.raises(ValidationError, match="Invalid status"):
        JobResponse(
            id=job_id,
            type="short_story",
            genre="fantasy",
            status="invalid_status",
            created_at=now,
            updated_at=now,
        )


def test_job_status_update_valid() -> None:
    """Test JobStatusUpdate with valid data."""
    job_id = uuid4()

    update = JobStatusUpdate(
        job_id=job_id,
        status="running",
        metadata={"stage": "world_creation"},
    )

    assert update.job_id == job_id
    assert update.status == "running"
    assert update.metadata == {"stage": "world_creation"}


def test_job_status_update_validation() -> None:
    """Test JobStatusUpdate status validation."""
    job_id = uuid4()

    # Invalid status
    with pytest.raises(ValidationError, match="Invalid status"):
        JobStatusUpdate(
            job_id=job_id,
            status="invalid_status",
        )


def test_pipeline_execution_response_valid() -> None:
    """Test PipelineExecutionResponse with valid data."""
    job_id = uuid4()
    now = datetime.utcnow()

    resp = PipelineExecutionResponse(
        id=uuid4(),
        job_id=job_id,
        stages_completed=["interpret", "world_creation"],
        stages_failed=[],
        total_stages=5,
        current_stage="character_creation",
        progress_percent=40.0,
        created_at=now,
    )

    assert len(resp.stages_completed) == 2
    assert resp.total_stages == 5
    assert resp.progress_percent == 40.0


def test_pipeline_execution_response_progress_validation() -> None:
    """Test PipelineExecutionResponse progress calculation validation."""
    job_id = uuid4()
    now = datetime.utcnow()

    # Valid - progress matches stages
    resp = PipelineExecutionResponse(
        id=uuid4(),
        job_id=job_id,
        stages_completed=["interpret", "world_creation"],
        stages_failed=[],
        total_stages=5,
        progress_percent=40.0,  # 2/5 = 40%
        created_at=now,
    )
    assert resp.progress_percent == 40.0

    # Invalid - progress doesn't match stages
    with pytest.raises(ValidationError, match="Progress percent inconsistent"):
        PipelineExecutionResponse(
            id=uuid4(),
            job_id=job_id,
            stages_completed=["interpret", "world_creation"],
            stages_failed=[],
            total_stages=5,
            progress_percent=80.0,  # Should be 40%
            created_at=now,
        )


def test_task_status_response_valid() -> None:
    """Test TaskStatusResponse with valid data."""
    now = datetime.utcnow()

    resp = TaskStatusResponse(
        id=uuid4(),
        task_id="abc123",
        status="SUCCESS",
        result={"data": "completed"},
        created_at=now,
    )

    assert resp.task_id == "abc123"
    assert resp.status == "SUCCESS"
    assert resp.result == {"data": "completed"}


def test_task_status_response_failure() -> None:
    """Test TaskStatusResponse with failure data."""
    now = datetime.utcnow()

    resp = TaskStatusResponse(
        id=uuid4(),
        task_id="def456",
        status="FAILURE",
        result=None,
        traceback="Traceback...",
        created_at=now,
    )

    assert resp.status == "FAILURE"
    assert resp.traceback == "Traceback..."


def test_task_status_response_validation() -> None:
    """Test TaskStatusResponse status validation."""
    now = datetime.utcnow()

    # Invalid Celery status
    with pytest.raises(ValidationError, match="Invalid Celery status"):
        TaskStatusResponse(
            id=uuid4(),
            task_id="abc123",
            status="INVALID_STATUS",
            created_at=now,
        )


def test_budget_check_response_valid() -> None:
    """Test BudgetCheckResponse with valid data."""
    job_id = uuid4()
    now = datetime.utcnow()

    resp = BudgetCheckResponse(
        id=uuid4(),
        job_id=job_id,
        current_cost=25.50,
        budget_limit=100.0,
        remaining=74.50,
        percent_used=25.5,
        within_budget=True,
        created_at=now,
    )

    assert resp.current_cost == 25.50
    assert resp.budget_limit == 100.0
    assert resp.remaining == 74.50
    assert resp.percent_used == 25.5
    assert resp.within_budget is True


def test_budget_check_response_remaining_validation() -> None:
    """Test BudgetCheckResponse remaining calculation validation."""
    job_id = uuid4()
    now = datetime.utcnow()

    # Valid - remaining matches calculation
    resp = BudgetCheckResponse(
        id=uuid4(),
        job_id=job_id,
        current_cost=25.50,
        budget_limit=100.0,
        remaining=74.50,
        percent_used=25.5,
        within_budget=True,
        created_at=now,
    )
    assert resp.remaining == 74.50

    # Invalid - remaining doesn't match calculation
    with pytest.raises(ValidationError, match="Remaining budget calculation error"):
        BudgetCheckResponse(
            id=uuid4(),
            job_id=job_id,
            current_cost=25.50,
            budget_limit=100.0,
            remaining=50.0,  # Should be 74.50
            percent_used=25.5,
            within_budget=True,
            created_at=now,
        )


def test_budget_check_response_exceeded() -> None:
    """Test BudgetCheckResponse when budget exceeded."""
    job_id = uuid4()
    now = datetime.utcnow()

    # When budget is exceeded, remaining should be negative
    resp = BudgetCheckResponse(
        id=uuid4(),
        job_id=job_id,
        current_cost=120.0,
        budget_limit=100.0,
        remaining=-20.0,  # Negative when over budget
        percent_used=100.0,  # Cap at 100 for display purposes
        within_budget=False,
        created_at=now,
    )

    assert resp.current_cost > resp.budget_limit
    assert resp.within_budget is False
    assert resp.remaining < 0


def test_create_job_request_inspiration_length() -> None:
    """Test CreateJobRequest inspiration length validation."""
    # Valid
    req = CreateJobRequest(
        job_type="short_story",
        genre="fantasy",
        inspiration="A story about magic",
    )
    assert req.inspiration

    # Invalid - too short
    with pytest.raises(ValidationError, match="at least 10 characters"):
        CreateJobRequest(
            job_type="short_story",
            genre="fantasy",
            inspiration="short",
        )

    # Invalid - too long
    with pytest.raises(ValidationError, match="at most 5000 characters"):
        CreateJobRequest(
            job_type="short_story",
            genre="fantasy",
            inspiration="x" * 5001,
        )


def test_pipeline_execution_response_edge_cases() -> None:
    """Test PipelineExecutionResponse edge cases."""
    job_id = uuid4()
    now = datetime.utcnow()

    # No stages completed yet
    resp = PipelineExecutionResponse(
        id=uuid4(),
        job_id=job_id,
        stages_completed=[],
        stages_failed=[],
        total_stages=5,
        progress_percent=0.0,
        created_at=now,
    )
    assert resp.progress_percent == 0.0

    # All stages completed
    resp = PipelineExecutionResponse(
        id=uuid4(),
        job_id=job_id,
        stages_completed=["stage1", "stage2", "stage3"],
        stages_failed=[],
        total_stages=3,
        progress_percent=100.0,
        created_at=now,
    )
    assert resp.progress_percent == 100.0

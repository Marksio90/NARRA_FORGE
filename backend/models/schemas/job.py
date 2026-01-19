"""Job-related schemas for production pipeline."""

from datetime import datetime
from typing import Any, ClassVar
from uuid import UUID

from pydantic import Field, field_validator

from models.schemas.base import BaseRequest, BaseResponse, GenreValidator, JobTypeValidator


class CreateJobRequest(BaseRequest, GenreValidator, JobTypeValidator):
    """Request schema for creating a new job."""

    job_type: str = Field(..., description="Job type (short_story, novella, novel, saga)")
    genre: str = Field(..., description="Genre of the work")
    inspiration: str | None = Field(
        None, min_length=10, max_length=5000, description="User inspiration/prompt"
    )
    constraints: dict[str, Any] = Field(
        default_factory=dict, description="Job-specific constraints"
    )
    budget_limit: float | None = Field(
        None, ge=0.0, le=1000.0, description="Budget limit in USD (max $1000)"
    )

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate constraint types."""
        allowed_keys = ["max_characters", "target_word_count", "themes", "setting", "tone"]
        for key in v:
            if key not in allowed_keys:
                raise ValueError(
                    f"Unknown constraint key: {key}. Allowed: {', '.join(allowed_keys)}"
                )
        return v


class JobResponse(BaseResponse):
    """Response schema for job information."""

    id: UUID = Field(..., serialization_alias="job_id")
    type: str = Field(..., serialization_alias="job_type", description="Job type")
    genre: str = Field(..., description="Genre")
    status: str = Field(..., description="Job status (queued, running, completed, failed)")
    inspiration: str | None = Field(None, serialization_alias="user_inspiration")
    constraints: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    total_cost: float | None = Field(None, serialization_alias="current_cost", description="Total cost in USD")
    artifacts_count: int = Field(default=0, ge=0)
    budget_limit: float = Field(default=5.0, ge=0.0, description="Budget limit in USD")
    target_word_count: int = Field(default=2000, ge=0, description="Target word count")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage")
    error_message: str | None = Field(None, description="Error message if failed")

    ALLOWED_STATUSES: ClassVar[list[str]] = [
        "queued",
        "running",
        "completed",
        "failed",
        "cancelled",
    ]

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Ensure status is valid."""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {v}. Allowed: {', '.join(cls.ALLOWED_STATUSES)}")
        return v


class JobStatusUpdate(BaseRequest):
    """Schema for updating job status."""

    job_id: UUID = Field(..., description="Job UUID")
    status: str = Field(..., description="New status")
    metadata: dict[str, Any] | None = Field(None, description="Optional metadata")

    ALLOWED_STATUSES: ClassVar[list[str]] = [
        "queued",
        "running",
        "completed",
        "failed",
        "cancelled",
    ]

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Ensure status is valid."""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {v}. Allowed: {', '.join(cls.ALLOWED_STATUSES)}")
        return v


class PipelineExecutionResponse(BaseResponse):
    """Response schema for pipeline execution."""

    job_id: UUID
    stages_completed: list[str] = Field(default_factory=list)
    stages_failed: list[str] = Field(default_factory=list)
    total_stages: int = Field(..., ge=0)
    current_stage: str | None = None
    progress_percent: float = Field(..., ge=0.0, le=100.0)
    created_at: datetime

    @field_validator("progress_percent", mode="after")
    @classmethod
    def validate_progress_calculation(cls, v: float, info: Any) -> float:
        """Ensure progress calculation is consistent."""
        if "stages_completed" in info.data and "total_stages" in info.data:
            completed = len(info.data["stages_completed"])
            total = info.data["total_stages"]
            if total > 0:
                expected_progress = (completed / total) * 100
                if abs(expected_progress - v) > 1.0:  # Allow 1% tolerance
                    raise ValueError(
                        f"Progress percent inconsistent: {v}% vs expected {expected_progress:.1f}%"
                    )
        return v


class TaskStatusResponse(BaseResponse):
    """Response schema for Celery task status."""

    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status (PENDING, STARTED, SUCCESS, FAILURE, etc.)")
    result: Any | None = Field(None, description="Task result if completed")
    traceback: str | None = Field(None, description="Error traceback if failed")
    created_at: datetime

    ALLOWED_STATUSES: ClassVar[list[str]] = [
        "PENDING",
        "STARTED",
        "RETRY",
        "SUCCESS",
        "FAILURE",
        "REVOKED",
    ]

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Ensure Celery status is valid."""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid Celery status: {v}. Allowed: {', '.join(cls.ALLOWED_STATUSES)}"
            )
        return v


class BudgetCheckResponse(BaseResponse):
    """Response schema for budget check."""

    job_id: UUID
    current_cost: float = Field(..., ge=0.0)
    budget_limit: float = Field(..., ge=0.0)
    remaining: float = Field(..., description="Remaining budget (can be negative if exceeded)")
    percent_used: float = Field(..., ge=0.0, description="Percent of budget used (can exceed 100)")
    within_budget: bool
    created_at: datetime

    @field_validator("remaining", mode="after")
    @classmethod
    def validate_remaining_calculation(cls, v: float, info: Any) -> float:
        """Ensure remaining budget is correctly calculated."""
        if "budget_limit" in info.data and "current_cost" in info.data:
            expected_remaining = info.data["budget_limit"] - info.data["current_cost"]
            if abs(expected_remaining - v) > 0.01:  # Allow 1 cent tolerance
                raise ValueError(
                    f"Remaining budget calculation error: {v} vs expected {expected_remaining}"
                )
        return v

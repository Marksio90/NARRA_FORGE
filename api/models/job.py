"""
GenerationJob model for async narrative generation tasks.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, JSON, Enum as SQLEnum, Float, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base
from api.schemas.enums import JobStatus  # Import from single source of truth


class GenerationJob(Base):
    """
    Generation job model - tracks async narrative generation.

    Lifecycle:
    1. User creates job (status=QUEUED)
    2. Celery worker picks it up (status=RUNNING)
    3. Pipeline executes with checkpointing
    4. Job completes (status=COMPLETED) or fails (status=FAILED)

    Features:
    - Async task tracking
    - Progress monitoring (via checkpointing)
    - Cost tracking
    - Error handling
    - Resume support
    """

    __tablename__ = "generation_jobs"

    # Composite indexes for common queries
    __table_args__ = (
        # Query: Get user's jobs by status (most common)
        Index('ix_jobs_user_status', 'user_id', 'status'),
        # Query: Get project's jobs
        Index('ix_jobs_project_status', 'project_id', 'status'),
        # Query: Get user's jobs ordered by creation time
        Index('ix_jobs_user_created', 'user_id', 'created_at'),
        # Query: Get running jobs for monitoring
        Index('ix_jobs_status_created', 'status', 'created_at'),
    )

    # Override id to use UUID
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Ownership
    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    project_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Job status
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus),
        default=JobStatus.QUEUED,
        nullable=False,
        index=True
    )

    # Input (ProductionBrief)
    production_brief: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Output (NarrativeOutput - set when completed)
    output: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Progress tracking
    current_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    completed_stages: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Cost tracking
    estimated_cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    can_resume: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Celery task ID (for task management)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # Relationships
    # user = relationship("User")
    # project = relationship("Project", back_populates="jobs")
    # narrative = relationship("Narrative", back_populates="job", uselist=False)  # One-to-one

    def __repr__(self) -> str:
        return f"<GenerationJob {self.id} ({self.status.value})>"

    @property
    def is_running(self) -> bool:
        """Check if job is currently running."""
        return self.status == JobStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        """Check if job completed successfully."""
        return self.status == JobStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.status == JobStatus.FAILED

    @property
    def can_cancel(self) -> bool:
        """Check if job can be cancelled."""
        return self.status in [JobStatus.QUEUED, JobStatus.RUNNING]

    def calculate_duration(self) -> None:
        """Calculate job duration."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())

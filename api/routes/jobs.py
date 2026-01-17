"""
Generation Job Routes.

Handles narrative generation job management and monitoring.
"""

import uuid
from datetime import datetime, timezone
from typing import Annotated, Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.models.base import get_db
from api.models.user import User
from api.models.project import Project
from api.models.job import GenerationJob, JobStatus
from api.schemas.job import (
    JobCreateRequest,
    JobResponse,
    JobStatusResponse,
    JobListResponse
)
from api.schemas.auth import MessageResponse
from api.auth import get_current_active_user
from api.tasks.narrative import generate_narrative_task
from api.celery_app import celery_app


router = APIRouter(prefix="/jobs", tags=["Generation Jobs"])


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status (QUEUED, RUNNING, COMPLETED, FAILED)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List all jobs for current user with pagination and filtering.

    Filters:
    - project_id: Show jobs for specific project
    - status: Filter by job status
    """
    # Build query
    offset = (page - 1) * page_size

    # Base filter - user's jobs only
    filters = [GenerationJob.user_id == current_user.id]

    if project_id:
        filters.append(GenerationJob.project_id == project_id)

    if status_filter:
        try:
            job_status = JobStatus(status_filter)
            filters.append(GenerationJob.status == job_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    # Get total count
    count_stmt = select(func.count(GenerationJob.id)).where(*filters)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get jobs
    stmt = (
        select(GenerationJob)
        .where(*filters)
        .order_by(GenerationJob.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    total_pages = ceil(total / page_size) if total > 0 else 0

    return JobListResponse(
        jobs=[JobResponse.model_validate(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: JobCreateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new generation job and dispatch to Celery.

    The job will be queued for asynchronous processing.
    Use GET /jobs/{job_id}/status to monitor progress.
    """
    # Verify project exists and user owns it
    stmt = select(Project).where(
        Project.id == request.project_id,
        Project.user_id == current_user.id
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check user's monthly limits
    if current_user.monthly_generations_used >= current_user.monthly_generation_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Monthly generation limit reached ({current_user.monthly_generation_limit})"
        )

    # Estimate cost (rough estimate based on target length)
    target_length = request.production_brief.get("target_length", 5000)
    estimated_cost = (target_length / 1000) * 0.05  # $0.05 per 1000 words estimate

    # Check cost limit
    if current_user.monthly_cost_used_usd + estimated_cost > current_user.monthly_cost_limit_usd:
        if current_user.monthly_cost_limit_usd > 0:  # Only check if limit is set
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Monthly cost limit would be exceeded (${current_user.monthly_cost_limit_usd:.2f})"
            )

    # Create job
    new_job = GenerationJob(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        project_id=request.project_id,
        status=JobStatus.QUEUED,
        production_brief=request.production_brief,
        completed_stages=[],
        progress_percentage=0.0,
        estimated_cost_usd=estimated_cost,
        actual_cost_usd=0.0,
        tokens_used=0,
        retry_count=0,
        can_resume=False
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # Dispatch Celery task
    task = generate_narrative_task.apply_async(
        args=[new_job.id],
        queue="narrative_generation"
    )

    # Save Celery task ID
    new_job.celery_task_id = task.id
    await db.commit()
    await db.refresh(new_job)

    return JobResponse.model_validate(new_job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get full job details by ID.
    """
    stmt = select(GenerationJob).where(
        GenerationJob.id == job_id,
        GenerationJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return JobResponse.model_validate(job)


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get job status and progress (lightweight).

    Use this endpoint for frequent polling without loading full job details.
    """
    stmt = select(GenerationJob).where(
        GenerationJob.id == job_id,
        GenerationJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Optionally check Celery task state for real-time updates
    if job.celery_task_id and job.status == JobStatus.RUNNING:
        task_result = celery_app.AsyncResult(job.celery_task_id)
        if task_result.state == "PROGRESS" and task_result.info:
            # Update progress from Celery (without committing to DB)
            job.current_stage = task_result.info.get("stage")
            job.progress_percentage = task_result.info.get("progress", job.progress_percentage)

    return JobStatusResponse.model_validate(job)


@router.post("/{job_id}/cancel", response_model=MessageResponse)
async def cancel_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Cancel a running or queued job.

    This will revoke the Celery task and mark the job as CANCELLED.
    """
    stmt = select(GenerationJob).where(
        GenerationJob.id == job_id,
        GenerationJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Only cancel if QUEUED or RUNNING
    if job.status not in [JobStatus.QUEUED, JobStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status {job.status.value}"
        )

    # Revoke Celery task
    if job.celery_task_id:
        celery_app.control.revoke(job.celery_task_id, terminate=True)

    # Update job status
    job.status = JobStatus.CANCELLED
    job.error_message = "Job cancelled by user"
    job.completed_at = datetime.now(timezone.utc)

    if job.started_at:
        duration = (job.completed_at - job.started_at).total_seconds()
        job.duration_seconds = int(duration)

    await db.commit()

    return MessageResponse(message="Job cancelled successfully")


@router.post("/{job_id}/resume", response_model=JobResponse)
async def resume_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Resume a failed job from checkpoint.

    Only works if the job failed and can_resume is True.
    """
    stmt = select(GenerationJob).where(
        GenerationJob.id == job_id,
        GenerationJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Verify job can be resumed
    if job.status != JobStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only failed jobs can be resumed"
        )

    if not job.can_resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job cannot be resumed (no checkpoint available)"
        )

    # Reset job for retry
    job.status = JobStatus.QUEUED
    job.error_message = None
    job.retry_count += 1
    job.completed_at = None
    job.duration_seconds = None

    await db.commit()

    # Dispatch new Celery task
    task = generate_narrative_task.apply_async(
        args=[job.id],
        queue="narrative_generation"
    )

    job.celery_task_id = task.id
    await db.commit()
    await db.refresh(job)

    return JobResponse.model_validate(job)



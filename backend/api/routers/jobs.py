"""Jobs API router."""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.schema import Job
from models.schemas.job import CreateJobRequest, JobResponse
from services.job_tasks import create_job_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: CreateJobRequest,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """
    Create a new literary production job.

    Args:
        request: Job creation request with type, genre, inspiration, etc.
        db: Database session

    Returns:
        Created job response
    """
    logger.info(
        "Creating new job",
        extra={
            "job_type": request.job_type,
            "genre": request.genre,
        },
    )

    # Create job in database
    job = Job(
        type=request.job_type,
        genre=request.genre,
        inspiration=request.inspiration,
        constraints=request.constraints,
        status="queued",
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Queue Celery task for pipeline execution (async)
    create_job_task.delay(
        job_type=job.type,
        genre=job.genre,
        parameters={
            "job_id": str(job.id),
            "inspiration": job.inspiration,
            "constraints": job.constraints,
            "budget_limit": request.budget_limit,
        },
    )

    logger.info("Job created successfully", extra={"job_id": str(job.id)})

    # Return response
    return JobResponse(
        id=job.id,
        type=job.type,
        genre=job.genre,
        status=job.status,
        inspiration=job.inspiration,
        constraints=job.constraints,
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at,
        total_cost=None,
        artifacts_count=0,
        budget_limit=request.budget_limit or 5.0,
        target_word_count=request.constraints.get("target_word_count", 2000),
        progress=0.0,
        error_message=None,
    )


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[JobResponse]:
    """
    List all jobs with optional filtering.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        status_filter: Optional status filter (queued, running, completed, failed)
        db: Database session

    Returns:
        List of jobs
    """
    query = select(Job).offset(skip).limit(limit).order_by(Job.created_at.desc())

    if status_filter:
        query = query.where(Job.status == status_filter)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return [
        JobResponse(
            id=job.id,
            type=job.type,
            genre=job.genre,
            status=job.status,
            inspiration=job.inspiration,
            constraints=job.constraints,
            created_at=job.created_at,
            updated_at=job.updated_at,
            completed_at=job.completed_at,
            total_cost=None,  # TODO: Calculate from cost_snapshots
            artifacts_count=len(job.artifacts),
        )
        for job in jobs
    ]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """
    Get a specific job by ID.

    Args:
        job_id: Job UUID
        db: Database session

    Returns:
        Job details

    Raises:
        HTTPException: If job not found
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    return JobResponse(
        id=job.id,
        type=job.type,
        genre=job.genre,
        status=job.status,
        inspiration=job.inspiration,
        constraints=job.constraints,
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at,
        total_cost=None,  # TODO: Calculate from cost_snapshots
        artifacts_count=len(job.artifacts),
    )


@router.post("/{job_id}/cancel", response_model=dict[str, str])
async def cancel_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Cancel a running job.

    Args:
        job_id: Job UUID
        db: Database session

    Returns:
        Cancellation confirmation

    Raises:
        HTTPException: If job not found or cannot be cancelled
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    if job.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job in status: {job.status}",
        )

    job.status = "cancelled"
    job.updated_at = datetime.utcnow()
    await db.commit()

    logger.info("Job cancelled", extra={"job_id": str(job_id)})

    return {"message": f"Job {job_id} cancelled successfully"}

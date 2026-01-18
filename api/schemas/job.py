"""
Pydantic schemas for GenerationJob endpoints.

STRONGLY TYPED - No more Dict[str, Any]!
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from api.schemas.production import ProductionBriefSchema, NarrativeOutputSchema
from api.schemas.enums import JobStatus


class JobCreateRequest(BaseModel):
    """
    Job creation request - STRONGLY TYPED.

    Uses ProductionBriefSchema instead of Dict[str, Any].
    This ensures type safety and auto-generates accurate TypeScript types.
    """
    project_id: str = Field(..., description="Project ID")
    production_brief: ProductionBriefSchema = Field(
        ...,
        description="Strongly-typed production brief with validation"
    )


class JobStatusResponse(BaseModel):
    """Job status response (lightweight) - STRONGLY TYPED."""
    id: str
    status: JobStatus  # ✅ Enum instead of str
    current_stage: Optional[str] = None
    progress_percentage: float
    estimated_cost_usd: Optional[float] = None
    actual_cost_usd: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    can_resume: bool

    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    """
    Full job response - STRONGLY TYPED.

    Uses ProductionBriefSchema and NarrativeOutputSchema instead of Dict[str, Any].
    This provides full type safety and accurate API documentation.
    """
    id: str
    user_id: str
    project_id: str
    status: JobStatus  # ✅ Enum instead of str
    production_brief: ProductionBriefSchema  # ✅ Strongly typed instead of Dict[str, Any]
    output: Optional[NarrativeOutputSchema] = None  # ✅ Strongly typed instead of Dict[str, Any]
    current_stage: Optional[str] = None
    completed_stages: List[str]
    progress_percentage: float
    estimated_cost_usd: Optional[float] = None
    actual_cost_usd: float
    tokens_used: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int
    can_resume: bool
    celery_task_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """List of jobs with pagination."""
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

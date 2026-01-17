"""
Pydantic schemas for GenerationJob endpoints.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    """Job creation request."""
    project_id: str = Field(..., description="Project ID")
    production_brief: Dict[str, Any] = Field(..., description="Production brief (JSON)")
    
    # Example production_brief structure:
    # {
    #     "production_type": "short_story",
    #     "genre": "fantasy",
    #     "subject": "A wizard's apprentice discovers forbidden magic",
    #     "style_instructions": "Dark and mysterious tone",
    #     "target_length": 5000,
    #     "character_count": 3
    # }


class JobStatusResponse(BaseModel):
    """Job status response (lightweight)."""
    id: str
    status: str
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
    """Full job response."""
    id: str
    user_id: str
    project_id: str
    status: str
    production_brief: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
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

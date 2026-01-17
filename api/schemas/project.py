"""
Pydantic schemas for Project endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    """Project creation request."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    world_id: Optional[str] = Field(None, description="World ID from memory system")
    default_genre: Optional[str] = Field(None, max_length=50, description="Default genre")
    default_production_type: Optional[str] = Field(None, max_length=50, description="Default production type")


class ProjectUpdateRequest(BaseModel):
    """Project update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    world_id: Optional[str] = Field(None, description="World ID from memory system")
    default_genre: Optional[str] = Field(None, max_length=50, description="Default genre")
    default_production_type: Optional[str] = Field(None, max_length=50, description="Default production type")


class ProjectResponse(BaseModel):
    """Project response."""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    world_id: Optional[str] = None
    default_genre: Optional[str] = None
    default_production_type: Optional[str] = None
    narrative_count: int
    total_word_count: int
    total_cost_usd: float
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """List of projects with pagination."""
    projects: list[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

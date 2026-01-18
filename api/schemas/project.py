"""
Pydantic schemas for Project endpoints - STRONGLY TYPED.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from api.schemas.enums import ProductionType, Genre


class ProjectCreateRequest(BaseModel):
    """Project creation request - STRONGLY TYPED."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    world_id: Optional[str] = Field(None, description="World ID from memory system")
    default_genre: Optional[Genre] = Field(None, description="Default genre")  # ✅ Enum instead of str
    default_production_type: Optional[ProductionType] = Field(None, description="Default production type")  # ✅ Enum instead of str


class ProjectUpdateRequest(BaseModel):
    """Project update request - STRONGLY TYPED."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    world_id: Optional[str] = Field(None, description="World ID from memory system")
    default_genre: Optional[Genre] = Field(None, description="Default genre")  # ✅ Enum instead of str
    default_production_type: Optional[ProductionType] = Field(None, description="Default production type")  # ✅ Enum instead of str


class ProjectResponse(BaseModel):
    """Project response - STRONGLY TYPED."""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    world_id: Optional[str] = None
    default_genre: Optional[Genre] = None  # ✅ Enum instead of str
    default_production_type: Optional[ProductionType] = None  # ✅ Enum instead of str
    narrative_count: int
    total_word_count: int
    total_cost_usd: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """List of projects with pagination."""
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

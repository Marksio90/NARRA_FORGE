"""
Project schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class GenreEnum(str, Enum):
    """Literary genres supported by NarraForge"""
    SCI_FI = "sci-fi"
    FANTASY = "fantasy"
    THRILLER = "thriller"
    HORROR = "horror"
    ROMANCE = "romance"
    DRAMA = "drama"
    COMEDY = "comedy"
    MYSTERY = "mystery"
    RELIGIOUS = "religious"


class ProjectStatusEnum(str, Enum):
    """Project generation status"""
    INITIALIZING = "initializing"
    SIMULATING = "simulating"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProjectCreate(BaseModel):
    """Schema for creating a new project - ONLY genre is required!"""
    genre: GenreEnum = Field(..., description="Literary genre - the ONLY user choice!")
    name: Optional[str] = Field(None, description="Optional custom name for the project")
    
    class Config:
        json_schema_extra = {
            "example": {
                "genre": "sci-fi",
                "name": "My Epic Space Opera"
            }
        }


class ProjectSimulation(BaseModel):
    """Intelligent cost and step simulation before generation"""
    estimated_steps: List[Dict[str, Any]] = Field(..., description="All 15 steps with details")
    estimated_total_cost: float = Field(..., description="Total estimated cost in USD")
    estimated_duration_minutes: int = Field(..., description="Estimated time to complete")
    ai_decisions: Dict[str, Any] = Field(..., description="AI-determined parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "estimated_steps": [
                    {
                        "step": 1,
                        "name": "Inicjalizacja Projektu",
                        "estimated_cost": 0.05,
                        "model_tier": "tier1",
                        "description": "Utworzenie projektu i inicjalizacja"
                    }
                ],
                "estimated_total_cost": 15.75,
                "estimated_duration_minutes": 45,
                "ai_decisions": {
                    "target_word_count": 95000,
                    "planned_volumes": 1,
                    "chapter_count": 28,
                    "main_characters": 6,
                    "subplot_count": 3
                }
            }
        }


class ProjectResponse(BaseModel):
    """Complete project response"""
    id: int
    name: str
    genre: GenreEnum
    status: ProjectStatusEnum
    parameters: Dict[str, Any]
    estimated_cost: float
    actual_cost: float
    current_step: int
    progress_percentage: float
    current_activity: Optional[str]
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    simulation_data: Optional[Dict[str, Any]] = None
    estimated_duration_minutes: Optional[int] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """List of projects"""
    projects: List[ProjectResponse]
    total: int


class ProjectStatusResponse(BaseModel):
    """Real-time project status"""
    project_id: int
    status: ProjectStatusEnum
    current_step: int
    total_steps: int = 15
    progress_percentage: float
    current_activity: Optional[str]
    estimated_cost: float
    actual_cost: float
    started_at: Optional[datetime]
    estimated_completion: Optional[datetime]
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "status": "generating",
                "current_step": 11,
                "total_steps": 15,
                "progress_percentage": 73.3,
                "current_activity": "Generowanie rozdziału 18/28",
                "estimated_cost": 15.75,
                "actual_cost": 11.52,
                "started_at": "2026-01-20T10:00:00",
                "estimated_completion": "2026-01-20T10:45:00"
            }
        }

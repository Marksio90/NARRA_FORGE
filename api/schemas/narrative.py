"""
Pydantic schemas for Narrative endpoints.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class NarrativeResponse(BaseModel):
    """Narrative response (without full text for lists)."""
    id: str
    user_id: str
    project_id: str
    job_id: Optional[str] = None
    title: Optional[str] = None
    production_type: str
    genre: str
    word_count: int
    overall_quality_score: Optional[float] = None
    generation_cost_usd: float
    tokens_used: int
    version: int
    view_count: int
    download_count: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class NarrativeDetailResponse(BaseModel):
    """Full narrative response with text and metadata."""
    id: str
    user_id: str
    project_id: str
    job_id: Optional[str] = None
    title: Optional[str] = None
    production_type: str
    genre: str
    narrative_text: str  # Full text
    word_count: int
    narrative_metadata: Dict[str, Any]  # Characters, structure, segments
    quality_metrics: Optional[Dict[str, Any]] = None
    overall_quality_score: Optional[float] = None
    generation_cost_usd: float
    tokens_used: int
    version: int
    parent_narrative_id: Optional[str] = None
    exported_formats: List[str]
    view_count: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class NarrativeListResponse(BaseModel):
    """List of narratives with pagination."""
    narratives: List[NarrativeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

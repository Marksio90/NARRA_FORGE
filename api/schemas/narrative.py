"""
Pydantic schemas for Narrative endpoints - STRONGLY TYPED.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from api.schemas.enums import ProductionType, Genre
from api.schemas.production import NarrativeMetadataSchema, QualityMetricsSchema


class NarrativeResponse(BaseModel):
    """Narrative response (without full text for lists) - STRONGLY TYPED."""
    id: str
    user_id: str
    project_id: str
    job_id: Optional[str] = None
    title: Optional[str] = None
    production_type: ProductionType  # ✅ Enum instead of str
    genre: Genre  # ✅ Enum instead of str
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
    """Full narrative response with text and metadata - STRONGLY TYPED."""
    id: str
    user_id: str
    project_id: str
    job_id: Optional[str] = None
    title: Optional[str] = None
    production_type: ProductionType  # ✅ Enum instead of str
    genre: Genre  # ✅ Enum instead of str
    narrative_text: str  # Full text
    word_count: int
    narrative_metadata: NarrativeMetadataSchema  # ✅ Strongly typed instead of Dict[str, Any]
    quality_metrics: Optional[QualityMetricsSchema] = None  # ✅ Strongly typed instead of Dict[str, Any]
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

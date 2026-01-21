"""
Chapter schemas
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class ChapterResponse(BaseModel):
    """Individual chapter response"""
    id: int
    project_id: int
    number: int
    title: Optional[str]
    pov_character_id: Optional[int]
    outline: Dict[str, Any]
    content: Optional[str]
    word_count: int
    quality_score: float
    is_complete: int
    
    class Config:
        from_attributes = True


class ChapterListResponse(BaseModel):
    """List of chapters"""
    chapters: List[ChapterResponse]
    total: int


class ChapterContentResponse(BaseModel):
    """Chapter with full content"""
    chapter: ChapterResponse
    pov_character_name: Optional[str] = None

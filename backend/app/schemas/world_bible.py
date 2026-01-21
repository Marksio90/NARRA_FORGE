"""
WorldBible schemas
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional


class WorldBibleResponse(BaseModel):
    """World Bible complete response"""
    id: int
    project_id: int
    geography: Dict[str, Any]
    history: Dict[str, Any]
    systems: Dict[str, Any]
    cultures: Dict[str, Any]
    rules: Dict[str, Any]
    glossary: Dict[str, Any]
    notes: Optional[str]
    
    class Config:
        from_attributes = True

"""
Character schemas
"""

from pydantic import BaseModel
from typing import Dict, Any, List
from enum import Enum


class CharacterRoleEnum(str, Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"
    EPISODIC = "episodic"


class CharacterResponse(BaseModel):
    """Individual character response"""
    id: int
    project_id: int
    name: str
    role: CharacterRoleEnum
    profile: Dict[str, Any]
    arc: Dict[str, Any]
    voice_guide: str | None
    relationships: Dict[str, Any]
    
    class Config:
        from_attributes = True


class CharacterListResponse(BaseModel):
    """List of characters"""
    characters: List[CharacterResponse]
    total: int

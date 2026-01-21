"""
Plot structure schemas
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class PlotStructureResponse(BaseModel):
    """Plot structure response"""
    id: int
    project_id: int
    structure_type: str
    acts: Dict[str, Any]
    main_conflict: Dict[str, Any]
    stakes: Dict[str, Any]
    plot_points: Dict[str, Any]
    subplots: List[Dict[str, Any]]
    tension_graph: List[Dict[str, Any]]
    foreshadowing: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

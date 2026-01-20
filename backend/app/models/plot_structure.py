"""
PlotStructure model - represents the narrative structure
"""

from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class PlotStructure(Base):
    __tablename__ = "plot_structures"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    
    # Structure metadata
    structure_type = Column(Text, nullable=False)  # "Hero's Journey", "7-Point", etc.
    
    # Acts breakdown
    acts = Column(JSONB, default=dict)
    # {
    #   "act_1": {
    #     "name": "Setup",
    #     "chapters": [1, 2, 3, 4, 5],
    #     "key_events": [...],
    #     "goals": [...]
    #   },
    #   "act_2a": {...},
    #   "act_2b": {...},
    #   "act_3": {...}
    # }
    
    # Main conflict
    main_conflict = Column(Text, nullable=True)
    
    # Stakes
    stakes = Column(JSONB, default=dict)
    # {
    #   "personal": "...",
    #   "global": "...",
    #   "escalation": [...]
    # }
    
    # Key plot points
    plot_points = Column(JSONB, default=dict)
    # {
    #   "inciting_incident": {...},
    #   "first_plot_point": {...},
    #   "midpoint": {...},
    #   "second_plot_point": {...},
    #   "climax": {...},
    #   "resolution": {...}
    # }
    
    # Subplots
    subplots = Column(JSONB, default=list)
    # [
    #   {
    #     "name": "B-Story: Romance",
    #     "characters": [...],
    #     "description": "...",
    #     "intersection_points": [chapter_3, chapter_7, ...]
    #   }
    # ]
    
    # Tension/emotion graph
    tension_graph = Column(JSONB, default=list)
    # [
    #   {"chapter": 1, "tension": 3, "emotion": "curious"},
    #   {"chapter": 2, "tension": 5, "emotion": "anxious"},
    #   ...
    # ]
    
    # Foreshadowing map
    foreshadowing = Column(JSONB, default=list)
    # [
    #   {
    #     "planted_in_chapter": 3,
    #     "payoff_in_chapter": 18,
    #     "description": "..."
    #   }
    # ]
    
    # Relationship
    project = relationship("Project", back_populates="plot_structure")
    
    def __repr__(self):
        return f"<PlotStructure(project_id={self.project_id}, type='{self.structure_type}')>"

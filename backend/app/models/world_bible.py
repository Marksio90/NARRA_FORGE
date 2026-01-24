"""
WorldBible model - complete documentation of the fictional world
"""

from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class WorldBible(Base):
    __tablename__ = "world_bibles"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Geography and locations
    geography = Column(JSONB, default=dict)
    # {
    #   "world_type": "planet/galaxy/multiverse",
    #   "locations": [{
    #     "name": "New Alexandria",
    #     "type": "city",
    #     "description": "...",
    #     "population": 5000000,
    #     "coordinates": {...}
    #   }],
    #   "maps": ["url_to_map1", ...]
    # }
    
    # History and timeline
    history = Column(JSONB, default=dict)
    # {
    #   "eras": [{
    #     "name": "The Great Expansion",
    #     "start_year": -500,
    #     "end_year": 0,
    #     "key_events": [...]
    #   }],
    #   "current_year": 2247
    # }
    
    # Systems (magic, technology, etc.)
    systems = Column(JSONB, default=dict)
    # {
    #   "magic_system": {...},
    #   "technology_level": "hard sci-fi FTL",
    #   "economic_system": {...},
    #   "political_system": {...}
    # }
    
    # Cultures and societies
    cultures = Column(JSONB, default=dict)
    # {
    #   "cultures": [{
    #     "name": "Terran Union",
    #     "values": [...],
    #     "customs": [...],
    #     "language": "..."
    #   }]
    # }
    
    # Physics and rules
    rules = Column(JSONB, default=dict)
    # {
    #   "physics": "...",
    #   "magic_rules": [...],
    #   "limitations": [...]
    # }
    
    # Glossary of terms
    glossary = Column(JSONB, default=dict)
    # {
    #   "terms": [{
    #     "term": "Quantum Fold",
    #     "definition": "...",
    #     "usage": "..."
    #   }]
    # }
    
    # Additional notes
    notes = Column(Text, nullable=True)
    
    # Relationship
    project = relationship("Project", back_populates="world_bible")
    
    def __repr__(self):
        return f"<WorldBible(project_id={self.project_id})>"

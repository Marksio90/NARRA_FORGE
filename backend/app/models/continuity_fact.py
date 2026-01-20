"""
ContinuityFact model - tracks all facts for continuity checking
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from pgvector.sqlalchemy import Vector

from app.database import Base


class ContinuityFact(Base):
    __tablename__ = "continuity_facts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # The actual fact
    fact = Column(Text, nullable=False)
    
    # Where this fact appears
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    source_location = Column(String(500), nullable=True)  # e.g., "Chapter 3, Scene 2"
    
    # Fact categorization
    fact_type = Column(String(100), nullable=True)  # "character_trait", "location", "event", "date", etc.
    related_entity = Column(String(255), nullable=True)  # Character name, location name, etc.
    
    # Vector embedding for RAG
    embedding = Column(Vector(1536), nullable=True)
    
    # Tags for easier filtering
    tags = Column(ARRAY(String), default=list)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    project = relationship("Project", back_populates="continuity_facts")
    
    def __repr__(self):
        return f"<ContinuityFact(id={self.id}, type='{self.fact_type}')>"

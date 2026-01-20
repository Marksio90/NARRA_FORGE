"""
Chapter model - represents individual chapters
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    number = Column(Integer, nullable=False)  # Chapter number (1, 2, 3, ...)
    title = Column(String(500), nullable=True)  # Working title
    
    # POV character
    pov_character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    
    # Outline/plan for this chapter
    outline = Column(JSONB, default=dict)
    # {
    #   "setting": "...",
    #   "characters_present": [...],
    #   "goal": "...",
    #   "emotional_beat": "...",
    #   "cliffhanger": "...",
    #   "key_reveals": [...]
    # }
    
    # Actual prose content
    content = Column(Text, nullable=True)
    
    # Draft versions (for revisions)
    drafts = Column(JSONB, default=list)
    # [
    #   {
    #     "version": 1,
    #     "content": "...",
    #     "timestamp": "..."
    #   }
    # ]
    
    # Metadata
    word_count = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)  # 0-100
    
    # Status
    is_complete = Column(Integer, default=0)  # 0 = draft, 1 = polished, 2 = final
    
    # Relationships
    project = relationship("Project", back_populates="chapters")
    scenes = relationship("Scene", back_populates="chapter", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, number={self.number}, title='{self.title}')>"

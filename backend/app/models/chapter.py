"""
Chapter model - represents individual chapters
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    number = Column(Integer, nullable=False)  # Chapter number (1, 2, 3, ...)
    title = Column(String(500), nullable=True)  # Working title

    # POV character
    pov_character_id = Column(Integer, ForeignKey("characters.id", ondelete="SET NULL"), nullable=True)
    
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
    pov_character = relationship("Character", back_populates="pov_chapters", foreign_keys=[pov_character_id])
    scenes = relationship("Scene", back_populates="chapter", cascade="all, delete-orphan")

    # Indexes and constraints for better performance
    __table_args__ = (
        Index('idx_chapters_project_id', 'project_id'),
        Index('idx_chapters_pov_character_id', 'pov_character_id'),
        Index('idx_chapters_project_number', 'project_id', 'number'),  # Composite for ordering
        UniqueConstraint('project_id', 'number', name='uq_chapter_project_number'),
    )

    def __repr__(self):
        return f"<Chapter(id={self.id}, number={self.number}, title='{self.title}')>"

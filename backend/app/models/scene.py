"""
Scene model - detailed breakdown of scenes within chapters
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.database import Base


class Scene(Base):
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    
    number = Column(Integer, nullable=False)  # Scene number within chapter
    description = Column(Text, nullable=True)  # What happens in this scene
    
    # Characters involved (array of character IDs)
    character_ids = Column(ARRAY(Integer), default=list)
    
    # Scene beats and structure
    beats = Column(JSONB, default=dict)
    # {
    #   "opening": "...",
    #   "conflict": "...",
    #   "turning_point": "...",
    #   "closing": "...",
    #   "emotional_beat": "...",
    #   "info_reveals": [...]
    # }
    
    # Setting details
    setting = Column(JSONB, default=dict)
    # {
    #   "location": "...",
    #   "time_of_day": "...",
    #   "atmosphere": "...",
    #   "sensory_details": [...]
    # }
    
    # Relationship
    chapter = relationship("Chapter", back_populates="scenes")

    # Indexes and constraints for better performance
    __table_args__ = (
        Index('idx_scenes_chapter_id', 'chapter_id'),
        UniqueConstraint('chapter_id', 'number', name='uq_scene_chapter_number'),
    )

    def __repr__(self):
        return f"<Scene(id={self.id}, chapter_id={self.chapter_id}, number={self.number})>"

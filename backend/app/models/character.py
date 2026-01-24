"""
Character model - represents characters in the story
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class CharacterRole(str, enum.Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"
    EPISODIC = "episodic"


class Character(Base):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    role = Column(Enum(CharacterRole), nullable=False)
    
    # Complete character profile
    profile = Column(JSONB, default=dict)
    # {
    #   "biography": {
    #     "age": 35,
    #     "background": "...",
    #     "occupation": "...",
    #     "education": "..."
    #   },
    #   "psychology": {
    #     "mbti": "INTJ",
    #     "enneagram": "5w6",
    #     "traits": [...],
    #     "fears": [...],
    #     "desires": [...]
    #   },
    #   "physical": {
    #     "appearance": "...",
    #     "height": "...",
    #     "distinctive_features": [...]
    #   },
    #   "ghost_wound": {
    #     "ghost": "Past trauma...",
    #     "wound": "Current issue..."
    #   }
    # }
    
    # Character arc
    arc = Column(JSONB, default=dict)
    # {
    #   "starting_state": "...",
    #   "want_vs_need": {
    #     "want": "...",
    #     "need": "..."
    #   },
    #   "transformation_moments": [...],
    #   "ending_state": "..."
    # }
    
    # Voice and speech patterns (stored as JSONB for structured data)
    voice_guide = Column(JSONB, nullable=True)
    # Detailed guide on how this character speaks, vocabulary, speech patterns
    # {
    #   "speechPatterns": "...",
    #   "vocabularyLevel": "...",
    #   "signature_phrases": [...]
    # }
    
    # Relationships with other characters
    relationships = Column(JSONB, default=dict)
    # {
    #   "character_id_123": {
    #     "type": "romantic/family/rival/mentor",
    #     "description": "...",
    #     "dynamic": "..."
    #   }
    # }
    
    # Relationships
    project = relationship("Project", back_populates="characters")
    pov_chapters = relationship("Chapter", back_populates="pov_character", foreign_keys="Chapter.pov_character_id")

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_characters_project_id', 'project_id'),
    )

    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', role='{self.role}')>"

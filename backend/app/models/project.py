"""
Project model - represents a book generation project
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class ProjectStatus(str, enum.Enum):
    INITIALIZING = "initializing"
    SIMULATING = "simulating"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenreType(str, enum.Enum):
    SCI_FI = "sci-fi"
    FANTASY = "fantasy"
    THRILLER = "thriller"
    HORROR = "horror"
    ROMANCE = "romance"
    DRAMA = "drama"
    COMEDY = "comedy"
    MYSTERY = "mystery"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    genre = Column(Enum(GenreType), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.INITIALIZING, nullable=False)

    # User ownership (optional for backward compatibility)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Series support (optional)
    series_id = Column(Integer, ForeignKey("series.id", ondelete="SET NULL"), nullable=True, index=True)
    book_number_in_series = Column(Integer, nullable=True)
    
    # AI-determined parameters (stored as JSONB)
    parameters = Column(JSONB, default=dict)
    # Example structure:
    # {
    #   "target_word_count": 90000,
    #   "planned_volumes": 1,
    #   "world_detail_level": "high",
    #   "character_count": {"main": 5, "supporting": 10, "minor": 20},
    #   "subplot_count": 3,
    #   "chapter_count": 25,
    # }
    
    # Cost tracking
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)

    # Simulation data (stored after /simulate endpoint is called)
    simulation_data = Column(JSONB, nullable=True)
    # Structure:
    # {
    #   "estimated_steps": [...],
    #   "estimated_total_cost": 15.75,
    #   "estimated_duration_minutes": 45,
    #   "ai_decisions": {...}
    # }
    estimated_duration_minutes = Column(Integer, nullable=True)

    # Progress tracking
    current_step = Column(Integer, default=0)  # 0-15
    progress_percentage = Column(Float, default=0.0)
    current_activity = Column(Text, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)  # Stores error details if generation fails

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    series = relationship("Series", back_populates="books")
    world_bible = relationship("WorldBible", back_populates="project", uselist=False)
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    plot_structure = relationship("PlotStructure", back_populates="project", uselist=False)
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    continuity_facts = relationship("ContinuityFact", back_populates="project", cascade="all, delete-orphan")
    generation_logs = relationship("GenerationLog", back_populates="project", cascade="all, delete-orphan")
    publishing_metadata = relationship("PublishingMetadata", back_populates="project", uselist=False)

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_projects_status', 'status'),
        Index('idx_projects_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', genre='{self.genre}', status='{self.status}')>"

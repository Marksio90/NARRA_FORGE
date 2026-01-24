"""
GenerationLog model - tracks all AI generation calls for cost and monitoring
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class ModelTier(str, enum.Enum):
    TIER1 = "tier1"  # GPT-4o-mini
    TIER2 = "tier2"  # GPT-4o
    TIER3 = "tier3"  # GPT-4/o1


class GenerationLog(Base):
    __tablename__ = "generation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Pipeline step (1-15)
    step = Column(Integer, nullable=False)
    step_name = Column(String(100), nullable=False)  # "world_building", "prose_generation", etc.
    
    # Agent that performed the task
    agent_name = Column(String(100), nullable=True)  # "WORLD_ARCHITECT", "PROSE_WEAVER", etc.
    
    # Model used
    model_tier = Column(Enum(ModelTier), nullable=False)
    model_name = Column(String(50), nullable=False)  # "gpt-4o-mini", "gpt-4o", etc.
    
    # Token usage
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    
    # Cost (in USD)
    cost = Column(Float, default=0.0)
    
    # Task description
    task_description = Column(Text, nullable=True)
    
    # Success/failure
    success = Column(Integer, default=1)  # 1 = success, 0 = failure
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_seconds = Column(Float, nullable=True)
    
    # Relationship
    project = relationship("Project", back_populates="generation_logs")

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_generation_logs_project_id', 'project_id'),
        Index('idx_generation_logs_project_step', 'project_id', 'step'),
    )

    def __repr__(self):
        return f"<GenerationLog(id={self.id}, step={self.step}, model='{self.model_name}', cost=${self.cost:.4f})>"

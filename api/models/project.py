"""
Project model for workspace management.
"""

import uuid
from typing import Optional

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base


class Project(Base):
    """
    Project model - user workspace for organizing narratives.

    A project can contain:
    - Multiple narratives
    - Shared world settings
    - Character library
    - Project-specific settings
    """

    __tablename__ = "projects"

    # Override id to use UUID
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Ownership
    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Project info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # World settings (optional - links to memory system)
    world_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)

    # Project settings
    default_genre: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    default_production_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Statistics
    narrative_count: Mapped[int] = mapped_column(default=0, nullable=False)
    total_word_count: Mapped[int] = mapped_column(default=0, nullable=False)
    total_cost_usd: Mapped[float] = mapped_column(default=0.0, nullable=False)

    # Relationships
    # user = relationship("User", back_populates="projects")
    # narratives = relationship("Narrative", back_populates="project", cascade="all, delete-orphan")
    # jobs = relationship("GenerationJob", back_populates="project")

    def __repr__(self) -> str:
        return f"<Project {self.name} (user={self.user_id})>"

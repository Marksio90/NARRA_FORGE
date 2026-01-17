"""
Narrative model for storing generated narratives.
"""

import uuid
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base


class Narrative(Base):
    """
    Narrative model - stores generated narratives (versioned).

    Features:
    - Full narrative text storage
    - Metadata (characters, structure, etc.)
    - Quality metrics
    - Version control
    - Export support
    """

    __tablename__ = "narratives"

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
    project_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    job_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("generation_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Narrative info
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    production_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    genre: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Content
    narrative_text: Mapped[str] = mapped_column(Text, nullable=False)  # Full text
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Metadata (from NarrativeOutput)
    # NOTE: Use 'narrative_metadata' as Python attribute name to avoid conflict with Base.metadata
    narrative_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False)  # Characters, structure, segments, etc.

    # Quality metrics
    quality_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Coherence, logic, etc.
    overall_quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Cost tracking
    generation_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    parent_narrative_id: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey("narratives.id", ondelete="SET NULL"),
        nullable=True
    )  # For versioning/regeneration

    # Export tracking
    exported_formats: Mapped[list] = mapped_column(JSON, default=list, nullable=False)  # ["txt", "epub", "pdf"]

    # Statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    # user = relationship("User")
    # project = relationship("Project", back_populates="narratives")
    # job = relationship("GenerationJob", back_populates="narrative")
    # versions = relationship("Narrative", backref="parent", remote_side=[id])

    def __repr__(self) -> str:
        return f"<Narrative {self.title or self.id} ({self.word_count} words)>"

    @property
    def is_published(self) -> bool:
        """Check if narrative has been published/shared."""
        return self.view_count > 0

    def increment_view_count(self) -> None:
        """Increment view count."""
        self.view_count += 1

    def increment_download_count(self, format: str) -> None:
        """Increment download count and track format."""
        self.download_count += 1
        if format not in self.exported_formats:
            self.exported_formats.append(format)

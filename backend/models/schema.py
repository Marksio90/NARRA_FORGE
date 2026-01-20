"""
SQLAlchemy ORM models for NarraForge database schema.

Tables:
- jobs: Main job records for book generation
- worlds: World building data (geography, rules, history)
- characters: Character profiles and trajectories
- plots: Plot structures and scenes
- prose_chunks: Generated prose content (chapters)
- cost_snapshots: Cost tracking per stage
- embeddings: Vector embeddings for RAG (future)
"""

import uuid
from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, BigInteger, CheckConstraint, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.database import Base


class Job(Base):
    """Main job record for book generation."""

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    genre: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    inspiration: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    budget_limit: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="queued", index=True
    )  # queued, running, completed, failed
    current_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0.0 - 1.0
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Cost tracking
    cost_current: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tokens_used: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    world: Mapped[Optional["World"]] = relationship("World", back_populates="job", uselist=False, cascade="all, delete")
    characters: Mapped[list["Character"]] = relationship("Character", back_populates="job", cascade="all, delete")
    plot: Mapped[Optional["Plot"]] = relationship("Plot", back_populates="job", uselist=False, cascade="all, delete")
    prose_chunks: Mapped[list["ProseChunk"]] = relationship("ProseChunk", back_populates="job", cascade="all, delete")
    cost_snapshots: Mapped[list["CostSnapshot"]] = relationship(
        "CostSnapshot", back_populates="job", cascade="all, delete"
    )

    __table_args__ = (
        CheckConstraint("status IN ('queued', 'running', 'completed', 'failed')", name="check_job_status"),
        CheckConstraint("progress >= 0.0 AND progress <= 1.0", name="check_job_progress"),
        CheckConstraint("cost_current >= 0.0", name="check_job_cost"),
        CheckConstraint("budget_limit > 0.0", name="check_budget_limit"),
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, genre={self.genre}, status={self.status})>"


class World(Base):
    """World building data for generated stories."""

    __tablename__ = "worlds"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)

    # World data
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rules: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # List of world rules
    geography: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)  # Geographic details
    history: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # Historical timeline
    themes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # Thematic elements
    systems: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )  # Magic/tech systems, economy, politics

    # Metadata
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # For validation
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="world")

    def __repr__(self) -> str:
        return f"<World(id={self.id}, name={self.name})>"


class Character(Base):
    """Character profiles and development arcs."""

    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    world_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("worlds.id", ondelete="SET NULL"), nullable=True
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="main"
    )  # main, supporting, minor
    profile: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )  # Biography, psychology, appearance, voice

    # Character arc
    trajectory: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )  # Ghost, wound, desires, fears, arc stages
    relationships: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )  # Relationships with other characters

    # Metadata
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="characters")

    __table_args__ = (
        CheckConstraint("role IN ('main', 'supporting', 'minor')", name="check_character_role"),
        Index("ix_characters_job_role", "job_id", "role"),
    )

    def __repr__(self) -> str:
        return f"<Character(id={self.id}, name={self.name}, role={self.role})>"


class Plot(Base):
    """Plot structure and scene planning."""

    __tablename__ = "plots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)

    # Plot structure
    structure: Mapped[str] = mapped_column(
        String(50), nullable=False, default="three_act"
    )  # three_act, hero_journey, save_the_cat
    acts: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # Act breakdown
    scenes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # Scene details
    conflicts: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)  # Main conflicts and stakes

    # Story elements
    main_conflict: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stakes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    turning_points: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="plot")

    def __repr__(self) -> str:
        return f"<Plot(id={self.id}, structure={self.structure}, acts={len(self.acts)})>"


class ProseChunk(Base):
    """Generated prose content (chapters/scenes)."""

    __tablename__ = "prose_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plots.id", ondelete="SET NULL"), nullable=True
    )

    # Content
    chapter_number: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    word_count: Mapped[int] = mapped_column(nullable=False, default=0)
    pov_character: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    scene_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Versioning
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    is_final: Mapped[bool] = mapped_column(nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="prose_chunks")

    __table_args__ = (
        CheckConstraint("chapter_number > 0", name="check_chapter_number"),
        CheckConstraint("word_count >= 0", name="check_word_count"),
        Index("ix_prose_chunks_job_chapter", "job_id", "chapter_number"),
    )

    def __repr__(self) -> str:
        return f"<ProseChunk(id={self.id}, chapter={self.chapter_number}, words={self.word_count})>"


class CostSnapshot(Base):
    """Cost tracking snapshots per pipeline stage."""

    __tablename__ = "cost_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Stage info
    stage: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model_used: Mapped[str] = mapped_column(String(50), nullable=False)

    # Token usage
    tokens_input: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    tokens_output: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    tokens_total: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    # Cost
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="cost_snapshots")

    __table_args__ = (
        CheckConstraint("tokens_input >= 0", name="check_tokens_input"),
        CheckConstraint("tokens_output >= 0", name="check_tokens_output"),
        CheckConstraint("cost_usd >= 0.0", name="check_cost_usd"),
        Index("ix_cost_snapshots_job_stage", "job_id", "stage"),
    )

    def __repr__(self) -> str:
        return f"<CostSnapshot(stage={self.stage}, model={self.model_used}, cost=${self.cost_usd:.4f})>"


class Embedding(Base):
    """Vector embeddings for RAG and continuity checking (future feature)."""

    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Content reference
    content_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # world, character, plot, prose
    content_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Vector embedding (1536 dimensions for OpenAI text-embedding-3-small)
    embedding: Mapped[Vector] = mapped_column(Vector(1536), nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "content_type IN ('world', 'character', 'plot', 'prose')",
            name="check_embedding_content_type",
        ),
        Index("ix_embeddings_job_type", "job_id", "content_type"),
        # Index for vector similarity search (will be created via migration)
        # CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    )

    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, type={self.content_type})>"

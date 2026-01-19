"""Database schema models."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.database import Base


class Job(Base):  # type: ignore[misc]
    """Job model — represents a production job."""

    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)  # short_story, novella, novel, saga
    genre = Column(String(100), nullable=False)
    inspiration = Column(Text, nullable=True)
    constraints = Column(JSON, nullable=False, default=dict)
    status = Column(
        String(50), nullable=False, default="queued"
    )  # queued, running, completed, failed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    artifacts = relationship("Artifact", back_populates="job", cascade="all, delete-orphan")
    qa_reports = relationship("QAReport", back_populates="job", cascade="all, delete-orphan")
    cost_snapshots = relationship(
        "CostSnapshot", back_populates="job", cascade="all, delete-orphan"
    )


class Artifact(Base):  # type: ignore[misc]
    """Artifact model — stores all production artifacts."""

    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    type = Column(
        String(50), nullable=False
    )  # world_spec, character_spec, narrative_blueprint, etc.
    version = Column(Integer, nullable=False, default=1)
    data = Column(JSON, nullable=False)
    checksum = Column(String(64), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="artifacts")


class World(Base):  # type: ignore[misc]
    """World model — IP-level world specifications."""

    __tablename__ = "worlds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, unique=True)
    rules = Column(JSON, nullable=False, default=list)  # List of world rules
    geography = Column(JSON, nullable=False, default=dict)
    history = Column(JSON, nullable=False, default=list)  # Timeline nodes
    themes = Column(JSON, nullable=False, default=list)
    version = Column(Integer, nullable=False, default=1)
    checksum = Column(String(64), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    characters = relationship("Character", back_populates="world", cascade="all, delete-orphan")
    timelines = relationship("Timeline", back_populates="world", cascade="all, delete-orphan")


class Character(Base):  # type: ignore[misc]
    """Character model — character trajectories and transformations."""

    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(UUID(as_uuid=True), ForeignKey("worlds.id"), nullable=False)
    name = Column(String(200), nullable=False)
    trajectory = Column(JSON, nullable=False, default=list)  # List of transformation nodes
    relationships = Column(JSON, nullable=False, default=list)
    constraints = Column(JSON, nullable=False, default=list)  # Psychological constraints
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    world = relationship("World", back_populates="characters")


class Timeline(Base):  # type: ignore[misc]
    """Timeline model — event timelines for worlds."""

    __tablename__ = "timelines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(UUID(as_uuid=True), ForeignKey("worlds.id"), nullable=False)
    nodes = Column(JSON, nullable=False, default=list)  # List of timeline event nodes
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    world = relationship("World", back_populates="timelines")


class QAReport(Base):  # type: ignore[misc]
    """QA Report model — quality gate reports."""

    __tablename__ = "qa_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    logic_score = Column(Float, nullable=False)  # 0.0 - 1.0
    psychology_score = Column(Float, nullable=False)  # 0.0 - 1.0
    timeline_score = Column(Float, nullable=False)  # 0.0 - 1.0
    critical_errors = Column(JSON, nullable=False, default=list)  # List of critical errors
    warnings = Column(JSON, nullable=False, default=list)  # List of warnings
    passed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="qa_reports")


class CostSnapshot(Base):  # type: ignore[misc]
    """Cost Snapshot model — tracks costs per stage."""

    __tablename__ = "cost_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    stage = Column(String(100), nullable=False)  # e.g., "world_architect", "generator"
    tokens_used = Column(Integer, nullable=False)
    cost_usd = Column(Float, nullable=False)
    model = Column(String(50), nullable=False)  # gpt-4o-mini or gpt-4o
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="cost_snapshots")


class Embedding(Base):  # type: ignore[misc]
    """Embedding model — semantic search with pgvector."""

    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    artifact_id = Column(UUID(as_uuid=True), ForeignKey("artifacts.id"), nullable=False)
    vector = Column("vector", String, nullable=False)  # pgvector VECTOR type (placeholder)
    content_type = Column(
        String(50), nullable=False
    )  # segment_summary, event, motif, character_state
    content_summary = Column(Text, nullable=False)  # Summary text (NOT full text)
    meta = Column(
        "metadata", JSON, nullable=False, default=dict
    )  # 'metadata' is reserved in SQLAlchemy
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    artifact = relationship("Artifact")

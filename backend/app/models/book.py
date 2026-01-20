"""
Book and related database models.
"""
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, Text, Numeric, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any

from app.db.database import Base


class BookStatus(PyEnum):
    """Book status enum."""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class GenreType(PyEnum):
    """Genre type enum."""
    SCIFI = "scifi"
    FANTASY = "fantasy"
    THRILLER = "thriller"
    HORROR = "horror"
    ROMANCE = "romance"
    MYSTERY = "mystery"
    DRAMA = "drama"
    COMEDY = "comedy"
    DYSTOPIA = "dystopia"
    HISTORICAL = "historical"


class Series(Base):
    """Series model."""
    __tablename__ = "series"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    genre = Column(Enum(GenreType), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    books = relationship("Book", back_populates="series")


class Book(Base):
    """Book model."""
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    series_id = Column(UUID(as_uuid=True), ForeignKey("series.id"), nullable=True)
    volume_number = Column(Integer, default=1)

    title = Column(String(500))
    subtitle = Column(String(500))
    tagline = Column(Text)
    blurb = Column(Text)
    genre = Column(Enum(GenreType), nullable=False)
    status = Column(Enum(BookStatus), default=BookStatus.DRAFT)

    word_count = Column(Integer, default=0)
    chapter_count = Column(Integer, default=0)
    estimated_reading_time = Column(Integer, default=0)

    cost_total = Column(Numeric(10, 6), default=0)
    cost_breakdown = Column(JSONB, default={})

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(TIMESTAMP(timezone=True))

    # Relationships
    world = relationship("World", back_populates="book", uselist=False)
    characters = relationship("Character", back_populates="book")
    plot = relationship("Plot", back_populates="book", uselist=False)
    chapters = relationship("Chapter", back_populates="book", order_by="Chapter.number")
    series = relationship("Series", back_populates="books")


class World(Base):
    """World model."""
    __tablename__ = "worlds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)

    name = Column(String(500), nullable=False)
    description = Column(Text)

    geography = Column(JSONB, default={})
    history = Column(JSONB, default={})
    rules = Column(JSONB, default={})
    societies = Column(JSONB, default={})
    details = Column(JSONB, default={})

    embedding = Column(Vector(1536))

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    book = relationship("Book", back_populates="world")


class Character(Base):
    """Character model."""
    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)

    name = Column(String(200), nullable=False)
    full_name = Column(String(500))
    role = Column(String(100))

    appearance = Column(JSONB, default={})
    personality = Column(JSONB, default={})
    backstory = Column(JSONB, default={})
    motivations = Column(JSONB, default={})
    voice = Column(JSONB, default={})
    arc = Column(JSONB, default={})
    relationships = Column(JSONB, default=[])

    embedding = Column(Vector(1536))

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    book = relationship("Book", back_populates="characters")


class Plot(Base):
    """Plot model."""
    __tablename__ = "plots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)

    structure_type = Column(String(100))
    theme = Column(Text)

    hook = Column(Text)
    inciting_incident = Column(Text)
    midpoint = Column(Text)
    climax = Column(Text)
    resolution = Column(Text)

    subplots = Column(JSONB, default=[])
    open_threads = Column(JSONB, default=[])
    cliffhangers = Column(JSONB, default=[])

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    book = relationship("Book", back_populates="plot")


class Chapter(Base):
    """Chapter model."""
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)

    number = Column(Integer, nullable=False)
    title = Column(String(500))

    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)

    outline_goal = Column(Text)
    outline_summary = Column(Text)

    character_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])
    pov_character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id"))
    location = Column(String(500))
    time_in_story = Column(String(200))

    embedding = Column(Vector(1536))

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    book = relationship("Book", back_populates="chapters")


class ConsistencyCheck(Base):
    """Consistency check log model."""
    __tablename__ = "consistency_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=True)

    is_consistent = Column(String(10), nullable=False)  # Changed from Boolean to String
    issues = Column(JSONB, default=[])
    repairs_made = Column(JSONB, default=[])

    checked_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class CostLog(Base):
    """Cost log model."""
    __tablename__ = "cost_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)

    model = Column(String(100), nullable=False)
    phase = Column(String(100), nullable=False)
    task_type = Column(String(100))

    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    cost = Column(Numeric(10, 6), nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

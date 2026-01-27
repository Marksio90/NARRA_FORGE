"""
Series model for multi-book sagas with continuity tracking

Supports:
- Multi-book series planning
- Character arcs spanning books
- Plot thread tracking
- World bible sharing
- Timeline consistency
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base


class Series(Base):
    """
    Series model representing a multi-book saga.
    Maintains continuity and shared elements across books.
    """
    __tablename__ = "series"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    genre = Column(String(50), nullable=False)
    language = Column(String(20), default="polski", nullable=False)

    # Series planning
    planned_books = Column(Integer, default=3, nullable=False)
    completed_books = Column(Integer, default=0, nullable=False)

    # Shared universe
    shared_world_bible_id = Column(Integer, ForeignKey("world_bibles.id", ondelete="SET NULL"), nullable=True)

    # Series arc (overarching story across all books)
    series_arc = Column(Text, nullable=True)

    # Timeline tracking
    # Structure: [{"book": 1, "year_start": "1200", "year_end": "1201", "key_events": [...]}]
    timeline = Column(JSONB, nullable=True, default=list)

    # Recurring characters tracking
    # Structure: [{"name": "John", "first_book": 1, "status": "alive", "arc_summary": "..."}]
    recurring_characters = Column(JSONB, nullable=True, default=list)

    # Unresolved plot threads
    # Structure: [{"name": "Mystery of...", "introduced_book": 1, "resolved_book": null}]
    plot_threads = Column(JSONB, nullable=True, default=list)

    # World elements shared across books
    # Structure: {"locations": [...], "factions": [...], "artifacts": [...]}
    shared_elements = Column(JSONB, nullable=True, default=dict)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_complete = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # Relationships
    user = relationship("User", back_populates="series")
    books = relationship("Project", back_populates="series", order_by="Project.book_number_in_series")
    shared_world_bible = relationship("WorldBible", foreign_keys=[shared_world_bible_id])
    character_arcs = relationship("SeriesCharacterArc", back_populates="series", cascade="all, delete-orphan")
    plot_thread_details = relationship("SeriesPlotThread", back_populates="series", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_series_user_id', 'user_id'),
        Index('idx_series_genre', 'genre'),
    )

    def get_next_book_number(self) -> int:
        """Get the number for the next book in series"""
        return self.completed_books + 1

    def is_ready_for_next_book(self) -> bool:
        """Check if series is ready for generating next book"""
        return (
            self.completed_books < self.planned_books and
            self.is_active and
            not self.is_complete
        )

    def mark_book_completed(self):
        """Mark a book as completed in the series"""
        self.completed_books += 1
        if self.completed_books >= self.planned_books:
            self.is_complete = True

    def add_recurring_character(self, name: str, first_book: int, arc_summary: str = ""):
        """Add a recurring character to the series"""
        if self.recurring_characters is None:
            self.recurring_characters = []
        self.recurring_characters.append({
            "name": name,
            "first_book": first_book,
            "status": "alive",
            "arc_summary": arc_summary
        })

    def add_plot_thread(self, name: str, introduced_book: int, description: str = ""):
        """Add a plot thread to track across books"""
        if self.plot_threads is None:
            self.plot_threads = []
        self.plot_threads.append({
            "name": name,
            "introduced_book": introduced_book,
            "resolved_book": None,
            "description": description
        })

    def resolve_plot_thread(self, name: str, resolved_book: int):
        """Mark a plot thread as resolved"""
        if self.plot_threads:
            for thread in self.plot_threads:
                if thread["name"] == name:
                    thread["resolved_book"] = resolved_book
                    break

    def get_unresolved_threads(self) -> list:
        """Get all unresolved plot threads"""
        if not self.plot_threads:
            return []
        return [t for t in self.plot_threads if t.get("resolved_book") is None]

    def get_living_characters(self) -> list:
        """Get all living recurring characters"""
        if not self.recurring_characters:
            return []
        return [c for c in self.recurring_characters if c.get("status") == "alive"]

    def __repr__(self):
        return f"<Series(id={self.id}, name='{self.name}', books={self.completed_books}/{self.planned_books})>"


class SeriesCharacterArc(Base):
    """
    Track character development across the entire series.
    More detailed than the JSONB field in Series.
    """
    __tablename__ = "series_character_arcs"

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("series.id", ondelete="CASCADE"), nullable=False, index=True)
    character_name = Column(String(255), nullable=False)

    # Arc tracking
    starting_state = Column(Text, nullable=True)  # Book 1 starting point
    current_state = Column(Text, nullable=True)  # Current state after last book
    target_end_state = Column(Text, nullable=True)  # Planned ending state

    # Appearances
    first_appearance_book = Column(Integer, nullable=False)
    last_appearance_book = Column(Integer, nullable=True)

    # Development milestones
    # Structure: [{"book": 1, "chapter": 5, "milestone": "Learns the truth about..."}]
    key_moments = Column(JSONB, nullable=True, default=list)

    # Relationships with other characters
    # Structure: {"character_name": "relationship_type", ...}
    relationships = Column(JSONB, nullable=True, default=dict)

    # Status tracking
    is_alive = Column(Boolean, default=True, nullable=False)
    is_recurring = Column(Boolean, default=True, nullable=False)
    death_book = Column(Integer, nullable=True)
    death_chapter = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # Relationships
    series = relationship("Series", back_populates="character_arcs")

    def add_key_moment(self, book: int, chapter: int, milestone: str):
        """Add a key development moment"""
        if self.key_moments is None:
            self.key_moments = []
        self.key_moments.append({
            "book": book,
            "chapter": chapter,
            "milestone": milestone
        })
        self.last_appearance_book = book

    def mark_dead(self, book: int, chapter: int):
        """Mark character as dead"""
        self.is_alive = False
        self.death_book = book
        self.death_chapter = chapter

    def update_relationship(self, other_character: str, relationship_type: str):
        """Update relationship with another character"""
        if self.relationships is None:
            self.relationships = {}
        self.relationships[other_character] = relationship_type

    def __repr__(self):
        return f"<SeriesCharacterArc(character='{self.character_name}', alive={self.is_alive})>"


class SeriesPlotThread(Base):
    """
    Detailed tracking of plot threads across the series.
    More detailed than the JSONB field in Series.
    """
    __tablename__ = "series_plot_threads"

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("series.id", ondelete="CASCADE"), nullable=False, index=True)

    # Thread info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    thread_type = Column(String(50), nullable=True)  # mystery, romance, conflict, etc.

    # Status
    introduced_in_book = Column(Integer, nullable=False)
    introduced_in_chapter = Column(Integer, nullable=True)
    resolved_in_book = Column(Integer, nullable=True)
    resolved_in_chapter = Column(Integer, nullable=True)
    is_resolved = Column(Boolean, default=False, nullable=False)

    # Importance
    is_main_plot = Column(Boolean, default=False, nullable=False)  # vs subplot

    # Connections
    # Structure: ["character_name1", "character_name2"]
    related_characters = Column(JSONB, nullable=True, default=list)

    # Key events in this thread
    # Structure: [{"book": 1, "chapter": 3, "event": "..."}]
    key_events = Column(JSONB, nullable=True, default=list)

    # Foreshadowing elements
    # Structure: [{"book": 1, "chapter": 2, "element": "..."}]
    foreshadowing = Column(JSONB, nullable=True, default=list)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # Relationships
    series = relationship("Series", back_populates="plot_thread_details")

    def add_key_event(self, book: int, chapter: int, event: str):
        """Add a key event in this plot thread"""
        if self.key_events is None:
            self.key_events = []
        self.key_events.append({
            "book": book,
            "chapter": chapter,
            "event": event
        })

    def add_foreshadowing(self, book: int, chapter: int, element: str):
        """Add a foreshadowing element"""
        if self.foreshadowing is None:
            self.foreshadowing = []
        self.foreshadowing.append({
            "book": book,
            "chapter": chapter,
            "element": element
        })

    def resolve(self, book: int, chapter: int):
        """Mark thread as resolved"""
        self.is_resolved = True
        self.resolved_in_book = book
        self.resolved_in_chapter = chapter

    def __repr__(self):
        return f"<SeriesPlotThread(name='{self.name}', resolved={self.is_resolved})>"

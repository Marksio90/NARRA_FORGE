"""
Chapter model - represents individual chapters with production state machine
"""

import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, Index, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class ChapterStatus(enum.Enum):
    """Production state machine for chapters"""
    PLANNED = "planned"           # Outline exists, no prose yet
    DRAFTING = "drafting"         # Currently being generated (scene by scene)
    DRAFTED = "drafted"           # First draft complete, needs validation
    VALIDATING = "validating"     # QA in progress
    VALIDATED = "validated"       # Passed QA thresholds
    REPAIR_NEEDED = "repair_needed"  # Failed QA, needs repair
    REPAIRING = "repairing"       # Repair agent working
    FINALIZED = "finalized"       # Ready for export
    EXPORTED = "exported"         # Successfully exported


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    number = Column(Integer, nullable=False)  # Chapter number (1, 2, 3, ...)
    title = Column(String(500), nullable=True)  # Working title

    # POV character
    pov_character_id = Column(Integer, ForeignKey("characters.id", ondelete="SET NULL"), nullable=True)

    # STATE MACHINE
    status = Column(Enum(ChapterStatus), default=ChapterStatus.PLANNED, nullable=False)

    # Outline/plan for this chapter
    outline = Column(JSONB, default=dict)
    # {
    #   "setting": "...",
    #   "characters_present": [...],
    #   "goal": "...",
    #   "conflict": "...",
    #   "turning_point": "...",
    #   "emotional_beat": "...",
    #   "cliffhanger": "...",
    #   "key_reveals": [...],
    #   "scenes": [
    #     {"number": 1, "goal": "...", "conflict": "...", "characters": [...], "setting": "..."},
    #     ...
    #   ]
    # }

    # Actual prose content
    content = Column(Text, nullable=True)

    # Scene-based generation tracking
    scenes_content = Column(JSONB, default=list)
    # [
    #   {"scene_num": 1, "content": "...", "word_count": 500, "status": "finalized", "qa_score": 85},
    #   {"scene_num": 2, "content": "...", "word_count": 600, "status": "repair_needed", "qa_score": 65},
    # ]
    current_scene = Column(Integer, default=0)  # Which scene we're generating

    # Draft versions (for revisions)
    drafts = Column(JSONB, default=list)
    # [
    #   {
    #     "version": 1,
    #     "content": "...",
    #     "timestamp": "...",
    #     "qa_scores": {...}
    #   }
    # ]

    # QA SCORING (hard thresholds)
    qa_scores = Column(JSONB, default=dict)
    # {
    #   "structural": 85,     # Has scenes, conflict, change, word count OK
    #   "continuity": 90,     # No contradictions with canon
    #   "style": 80,          # No AI-isms, natural prose
    #   "dialog": 85,         # Distinct voices, subtext, no info-dump
    #   "total": 85,          # Weighted average
    #   "issues": ["dialog lacks subtext in scene 2", ...]
    # }

    # Metadata
    word_count = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)  # 0-100 (legacy, use qa_scores.total)

    # Generation metadata
    generation_meta = Column(JSONB, default=dict)
    # {
    #   "model_tier": "TIER_2",
    #   "model_name": "gpt-4o",
    #   "tokens_in": 5000,
    #   "tokens_out": 8000,
    #   "cost": 0.15,
    #   "duration_sec": 45,
    #   "retry_count": 0,
    #   "repair_count": 0,
    #   "escalated_to_tier": null  # or "TIER_3" if escalated
    # }

    # Status (legacy - use 'status' enum instead)
    is_complete = Column(Integer, default=0)  # 0 = draft, 1 = polished, 2 = final

    # Immutable snapshot for export (prevents race conditions)
    export_snapshot = Column(JSONB, nullable=True)
    # {
    #   "version": 3,
    #   "content": "...",
    #   "word_count": 3500,
    #   "finalized_at": "2024-01-25T12:00:00Z",
    #   "checksum": "sha256:..."
    # }

    # Relationships
    project = relationship("Project", back_populates="chapters")
    pov_character = relationship("Character", back_populates="pov_chapters", foreign_keys=[pov_character_id])
    scenes = relationship("Scene", back_populates="chapter", cascade="all, delete-orphan")

    # Indexes and constraints for better performance
    __table_args__ = (
        Index('idx_chapters_project_id', 'project_id'),
        Index('idx_chapters_pov_character_id', 'pov_character_id'),
        Index('idx_chapters_project_number', 'project_id', 'number'),  # Composite for ordering
        Index('idx_chapters_status', 'status'),  # For querying by state
        UniqueConstraint('project_id', 'number', name='uq_chapter_project_number'),
    )

    def __repr__(self):
        return f"<Chapter(id={self.id}, number={self.number}, status={self.status.value})>"

    # STATE MACHINE TRANSITIONS
    def can_transition_to(self, new_status: ChapterStatus) -> bool:
        """Check if transition is valid"""
        valid_transitions = {
            ChapterStatus.PLANNED: [ChapterStatus.DRAFTING],
            ChapterStatus.DRAFTING: [ChapterStatus.DRAFTED, ChapterStatus.PLANNED],  # Can reset
            ChapterStatus.DRAFTED: [ChapterStatus.VALIDATING],
            ChapterStatus.VALIDATING: [ChapterStatus.VALIDATED, ChapterStatus.REPAIR_NEEDED],
            ChapterStatus.VALIDATED: [ChapterStatus.FINALIZED],
            ChapterStatus.REPAIR_NEEDED: [ChapterStatus.REPAIRING, ChapterStatus.DRAFTING],  # Can restart
            ChapterStatus.REPAIRING: [ChapterStatus.VALIDATING, ChapterStatus.DRAFTING],  # Re-validate after repair
            ChapterStatus.FINALIZED: [ChapterStatus.EXPORTED, ChapterStatus.REPAIRING],  # Can re-repair
            ChapterStatus.EXPORTED: [ChapterStatus.FINALIZED],  # Can re-export
        }
        return new_status in valid_transitions.get(self.status, [])

    def transition_to(self, new_status: ChapterStatus) -> bool:
        """Transition to new status if valid"""
        if self.can_transition_to(new_status):
            self.status = new_status
            return True
        return False

    def get_qa_total(self) -> float:
        """Get total QA score"""
        if not self.qa_scores:
            return 0.0
        return self.qa_scores.get('total', 0.0)

    def needs_repair(self) -> bool:
        """Check if chapter needs repair based on QA scores"""
        total = self.get_qa_total()
        return 0 < total < 85  # Below threshold but has been scored

    def is_ready_for_export(self) -> bool:
        """Check if chapter can be exported"""
        return self.status in [ChapterStatus.FINALIZED, ChapterStatus.EXPORTED]


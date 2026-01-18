"""
Shared enums for type-safe API contracts.

These enums are the SINGLE SOURCE OF TRUTH for:
- Backend validation (Pydantic schemas)
- Database constraints (SQLAlchemy models)
- Frontend TypeScript types (auto-generated from OpenAPI)
"""

from enum import Enum


class ProductionType(str, Enum):
    """Production type for narrative generation."""
    SHORT_STORY = "short_story"
    NOVELLA = "novella"
    NOVEL = "novel"
    SCREENPLAY = "screenplay"
    STAGE_PLAY = "stage_play"
    PODCAST_SCRIPT = "podcast_script"

    @classmethod
    def get_default_length(cls, production_type: str) -> int:
        """Get default target length for production type."""
        defaults = {
            cls.SHORT_STORY.value: 5000,
            cls.NOVELLA.value: 30000,
            cls.NOVEL.value: 80000,
            cls.SCREENPLAY.value: 25000,
            cls.STAGE_PLAY.value: 20000,
            cls.PODCAST_SCRIPT.value: 8000,
        }
        return defaults.get(production_type, 5000)


class Genre(str, Enum):
    """Genre for narrative generation."""
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    MYSTERY = "mystery"
    THRILLER = "thriller"
    ROMANCE = "romance"
    HORROR = "horror"
    HISTORICAL = "historical"
    CONTEMPORARY = "contemporary"
    LITERARY = "literary"
    ADVENTURE = "adventure"
    CRIME = "crime"
    DRAMA = "drama"
    COMEDY = "comedy"
    DYSTOPIAN = "dystopian"
    MAGICAL_REALISM = "magical_realism"


class JobStatus(str, Enum):
    """Job status values (matches database enum)."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NarrativeStage(str, Enum):
    """Pipeline stages for narrative generation."""
    CONCEPT_EXPANSION = "concept_expansion"
    WORLD_BUILDING = "world_building"
    CHARACTER_CREATION = "character_creation"
    PLOT_STRUCTURING = "plot_structuring"
    SCENE_BREAKDOWN = "scene_breakdown"
    DIALOGUE_GENERATION = "dialogue_generation"
    PROSE_WRITING = "prose_writing"
    REFINEMENT = "refinement"
    QUALITY_CHECK = "quality_check"
    FINAL_POLISH = "final_polish"

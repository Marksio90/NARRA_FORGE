"""
Core type definitions for NARRA_FORGE system.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


class NarrativeForm(Enum):
    """Narrative form/length."""
    SHORT_STORY = "short_story"
    NOVELLA = "novella"
    NOVEL = "novel"
    EPIC_SAGA = "epic_saga"


class Genre(Enum):
    """Literary genres."""
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    HORROR = "horror"
    THRILLER = "thriller"
    MYSTERY = "mystery"
    LITERARY = "literary"
    HISTORICAL = "historical"
    ROMANCE = "romance"
    HYBRID = "hybrid"


class PipelineStage(Enum):
    """10-stage production pipeline."""
    BRIEF_INTERPRETATION = 1
    WORLD_ARCHITECTURE = 2
    CHARACTER_ARCHITECTURE = 3
    NARRATIVE_STRUCTURE = 4
    SEGMENT_PLANNING = 5
    SEQUENTIAL_GENERATION = 6
    COHERENCE_CONTROL = 7
    LANGUAGE_STYLIZATION = 8
    EDITORIAL_REVIEW = 9
    FINAL_OUTPUT = 10


class MemoryType(Enum):
    """Triple memory system types."""
    STRUCTURAL = "structural"      # Worlds, characters, rules
    SEMANTIC = "semantic"          # Events, motifs, relationships
    EVOLUTIONARY = "evolutionary"  # Changes over time


@dataclass
class WorldBible:
    """Complete world definition - the IP container."""
    world_id: str
    name: str
    created_at: datetime

    # Core world definition
    laws_of_reality: Dict[str, Any]  # Physical, magical, technological rules
    boundaries: Dict[str, Any]        # Spatial, temporal, dimensional limits
    anomalies: List[str]              # Exceptions to rules

    # Meta-information
    core_conflict: str                # Overarching conflict
    existential_theme: str            # Why this world exists narratively
    archetype_system: Dict[str, Any]  # World-specific archetypes

    # Evolution tracking
    timeline: List[Dict[str, Any]]    # Historical events
    current_state: Dict[str, Any]     # Current world state

    # Cross-world relationships
    related_worlds: List[str] = field(default_factory=list)
    isolation_level: str = "isolated"  # isolated, connected, permeable


@dataclass
class Character:
    """Character as a process, not a static entity."""
    character_id: str
    name: str
    world_id: str

    # Core identity
    internal_trajectory: str          # Character's internal arc
    contradictions: List[str]         # Internal conflicts
    cognitive_limits: List[str]       # What they can't understand/perceive
    evolution_capacity: float         # 0.0-1.0: resistance to change vs adaptability

    # Psychological model
    motivations: List[str]
    fears: List[str]
    blind_spots: List[str]

    # Relational
    relationships: Dict[str, Dict[str, Any]]  # character_id -> relationship data

    # State tracking
    current_state: Dict[str, Any]
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class NarrativeSegment:
    """Single segment (chapter/scene/sequence)."""
    segment_id: str
    order: int

    # Functional
    narrative_function: str           # What this segment does
    narrative_weight: float           # Importance (0.0-1.0)
    world_impact: List[str]           # How it changes the world

    # Content
    content: str
    involved_characters: List[str]
    location: str
    timestamp: Optional[str] = None

    # Meta
    generated_at: datetime = field(default_factory=datetime.now)
    validated: bool = False


@dataclass
class ProjectBrief:
    """Initial request interpretation."""
    form: NarrativeForm
    genre: Genre
    world_scale: str                  # "intimate", "regional", "global", "cosmic"
    expansion_potential: str          # "one_shot", "series", "universe"

    # Additional requirements
    target_audience: Optional[str] = None
    length_target: Optional[int] = None  # approximate word count
    special_requirements: List[str] = field(default_factory=list)

    # Creative direction
    thematic_focus: List[str] = field(default_factory=list)
    stylistic_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProductionContext:
    """Complete production state for a narrative."""
    project_id: str
    brief: ProjectBrief
    world: WorldBible
    characters: Dict[str, Character]
    segments: List[NarrativeSegment]

    # Pipeline state
    current_stage: PipelineStage
    stage_outputs: Dict[PipelineStage, Any] = field(default_factory=dict)

    # Quality metrics
    coherence_score: float = 0.0
    quality_checks: Dict[str, bool] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

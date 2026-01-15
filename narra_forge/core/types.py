"""
Core data types for NARRA_FORGE V2
All dataclasses used across the system
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


# ═══════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════


class ProductionType(str, Enum):
    """Type of narrative production"""

    SHORT_STORY = "short_story"  # 5k-10k words
    NOVELLA = "novella"  # 10k-40k words
    NOVEL = "novel"  # 40k-120k words
    EPIC_SAGA = "epic_saga"  # Multi-volume


class Genre(str, Enum):
    """Narrative genres"""

    FANTASY = "fantasy"
    SCIFI = "scifi"
    HORROR = "horror"
    THRILLER = "thriller"
    MYSTERY = "mystery"
    DRAMA = "drama"
    ROMANCE = "romance"
    HYBRID = "hybrid"  # Mix of genres


class PipelineStage(str, Enum):
    """10-stage production pipeline"""

    BRIEF_INTERPRETATION = "01_brief_interpretation"
    WORLD_ARCHITECTURE = "02_world_architecture"
    CHARACTER_ARCHITECTURE = "03_character_architecture"
    STRUCTURE_DESIGN = "04_structure_design"
    SEGMENT_PLANNING = "05_segment_planning"
    SEQUENTIAL_GENERATION = "06_sequential_generation"
    COHERENCE_VALIDATION = "07_coherence_validation"
    LANGUAGE_STYLIZATION = "08_language_stylization"
    EDITORIAL_REVIEW = "09_editorial_review"
    OUTPUT_PROCESSING = "10_output_processing"


class JobStatus(str, Enum):
    """Production job status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ═══════════════════════════════════════════
# BRIEF & PRODUCTION REQUEST
# ═══════════════════════════════════════════


@dataclass
class ProductionBrief:
    """User's production request"""

    production_type: ProductionType
    genre: Genre
    inspiration: Optional[str] = None
    world_id: Optional[str] = None  # Use existing world
    additional_params: Dict[str, Any] = field(default_factory=dict)

    # Auto-generated
    brief_id: str = field(default_factory=lambda: f"brief_{uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=datetime.now)


# ═══════════════════════════════════════════
# WORLD (IP)
# ═══════════════════════════════════════════


@dataclass
class RealityLaws:
    """Laws that govern a world"""

    physics: Dict[str, Any]  # Physical laws
    magic: Optional[Dict[str, Any]] = None  # Magic system (if applicable)
    technology: Optional[Dict[str, Any]] = None  # Tech level
    constraints: List[str] = field(default_factory=list)  # Hard limits


@dataclass
class WorldBoundaries:
    """Spatial, temporal, dimensional boundaries"""

    spatial: Dict[str, Any]  # Geography, size
    temporal: Dict[str, Any]  # Time flow, history depth
    dimensional: Optional[Dict[str, Any]] = None  # Other dimensions


@dataclass
class World:
    """A complete universe/IP"""

    world_id: str
    name: str
    reality_laws: RealityLaws
    boundaries: WorldBoundaries
    anomalies: List[Dict[str, Any]]  # Intentional exceptions
    core_conflict: str  # The world's central tension
    existential_theme: str  # Deep philosophical theme

    # Metadata
    genre: Genre
    created_at: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None
    linked_worlds: List[str] = field(default_factory=list)  # Multi-universe


# ═══════════════════════════════════════════
# CHARACTER
# ═══════════════════════════════════════════


@dataclass
class InternalTrajectory:
    """Character's psychological journey"""

    starting_state: Dict[str, Any]
    potential_arcs: List[Dict[str, Any]]
    triggers: List[str]  # What can change them
    resistance_points: List[str]  # What they resist


@dataclass
class Character:
    """A character as a dynamic process"""

    character_id: str
    world_id: str
    name: str
    internal_trajectory: InternalTrajectory
    contradictions: List[str]  # Internal conflicts
    cognitive_limits: List[str]  # What they can't perceive/understand
    evolution_capacity: float  # 0.0-1.0, how much can they change

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    archetype: Optional[str] = None
    role: Optional[str] = None


# ═══════════════════════════════════════════
# NARRATIVE STRUCTURE
# ═══════════════════════════════════════════


@dataclass
class NarrativeStructure:
    """The chosen narrative structure"""

    structure_type: str  # "three_act", "hero_journey", "kishotenketsu", etc.
    acts: List[Dict[str, Any]]
    key_beats: List[Dict[str, Any]]  # Story beats
    pacing_map: Dict[str, Any]  # Tension/pacing curve
    estimated_word_count: int


@dataclass
class Segment:
    """A segment of narrative (chapter/scene)"""

    segment_id: str
    segment_number: int
    title: Optional[str]
    summary: str
    key_events: List[str]
    characters_involved: List[str]
    location: Optional[str]
    estimated_words: int
    narrative_function: str  # What this segment does in the story


# ═══════════════════════════════════════════
# GENERATION & VALIDATION
# ═══════════════════════════════════════════


@dataclass
class GeneratedSegment:
    """A generated segment with metadata"""

    segment: Segment
    text: str
    word_count: int
    tokens_used: int
    cost_usd: float
    generation_time_seconds: float


@dataclass
class CoherenceValidation:
    """Validation results"""

    passed: bool
    coherence_score: float  # 0.0-1.0
    logical_consistency: bool
    psychological_consistency: bool
    temporal_consistency: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════
# FINAL OUTPUT
# ═══════════════════════════════════════════


@dataclass
class NarrativeOutput:
    """Final production output"""

    job_id: str
    success: bool

    # Generated content
    narrative_text: str
    audiobook_text: Optional[str] = None  # With narrator markers

    # Structure
    world: World
    characters: List[Character]
    structure: NarrativeStructure
    segments: List[Segment]

    # Metadata
    production_type: ProductionType
    genre: Genre
    word_count: int
    quality_metrics: Dict[str, Any]

    # Cost & Performance
    total_tokens: int
    total_cost_usd: float
    generation_time_seconds: float
    model_usage: Dict[str, Any]  # Which models were used where

    # Files
    output_dir: str
    files: Dict[str, str]  # filename -> path

    # Timestamps
    started_at: datetime
    completed_at: datetime


# ═══════════════════════════════════════════
# PRODUCTION JOB
# ═══════════════════════════════════════════


@dataclass
class ProductionJob:
    """A batch production job"""

    job_id: str
    brief: ProductionBrief
    status: JobStatus
    current_stage: Optional[PipelineStage] = None

    # Progress tracking
    stages_completed: List[PipelineStage] = field(default_factory=list)
    stages_failed: List[PipelineStage] = field(default_factory=list)

    # Intermediate results
    world: Optional[World] = None
    characters: List[Character] = field(default_factory=list)
    structure: Optional[NarrativeStructure] = None
    segments: List[Segment] = field(default_factory=list)

    # Cost tracking
    tokens_used: int = 0
    cost_usd: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Output
    output: Optional[NarrativeOutput] = None
    error: Optional[str] = None


# ═══════════════════════════════════════════
# MEMORY STRUCTURES
# ═══════════════════════════════════════════


@dataclass
class SemanticNode:
    """Node in semantic memory (event, motif, relationship)"""

    node_id: str
    node_type: str  # "event", "motif", "relationship", "conflict"
    content: str
    embedding: Optional[List[float]] = None  # OpenAI embedding
    connections: List[str] = field(default_factory=list)  # Connected node IDs
    significance: float = 0.5  # 0.0-1.0
    timestamp_in_story: Optional[int] = None  # Position in narrative
    world_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionEntry:
    """Entry in evolutionary memory (how things change)"""

    entry_id: str
    entity_id: str  # What changed
    entity_type: str  # "character", "world", "relationship"
    timestamp: datetime
    change_type: str  # "psychological_shift", "world_event", etc.
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    trigger: Optional[str] = None  # What caused it
    significance: float = 0.5  # 0.0-1.0


# ═══════════════════════════════════════════
# MODEL USAGE
# ═══════════════════════════════════════════


@dataclass
class ModelCall:
    """Record of a model API call"""

    call_id: str
    model_name: str  # "gpt-4o-mini" or "gpt-4o"
    purpose: str  # What it was used for
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)


# ═══════════════════════════════════════════
# AGENT RESULTS
# ═══════════════════════════════════════════


@dataclass
class AgentResult:
    """Result from an agent execution"""

    agent_name: str
    stage: PipelineStage
    success: bool
    data: Dict[str, Any]  # Agent-specific output
    model_calls: List[ModelCall] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0

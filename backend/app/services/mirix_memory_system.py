"""
MIRIX Memory Architecture for NarraForge 3.0

Advanced multi-layered memory system inspired by human cognitive architecture.
Enables true learning between sessions and projects.

6 Memory Types:
1. Core Memory - Immutable facts, world rules, physics laws
2. Episodic Memory - Scenes as episodes with full emotional context
3. Semantic Memory - Network of concepts, motifs, symbols, relationships
4. Procedural Memory - Narrative patterns, writing techniques, author styles
5. Resource Memory - Inspirations, quotes, metaphors, comparisons
6. Knowledge Vault - World encyclopedia, character biographies, chronicles

Author: NarraForge 3.0 Divine Evolution
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
import json
import hashlib
import logging
import asyncio
from collections import defaultdict

from app.services.ai_service import AIService
from app.models.project import GenreType

logger = logging.getLogger(__name__)


# =============================================================================
# MEMORY TYPE DEFINITIONS
# =============================================================================

class MemoryType(str, Enum):
    """Six types of MIRIX memory"""
    CORE = "core"                   # Immutable facts, rules
    EPISODIC = "episodic"           # Scene episodes with emotions
    SEMANTIC = "semantic"           # Concept networks
    PROCEDURAL = "procedural"       # Narrative techniques
    RESOURCE = "resource"           # Inspirations, metaphors
    KNOWLEDGE_VAULT = "knowledge"   # Encyclopedia


class MemoryPriority(str, Enum):
    """Memory access priority levels"""
    CRITICAL = "critical"           # Must always be considered
    HIGH = "high"                   # Important for consistency
    MEDIUM = "medium"               # Enhances quality
    LOW = "low"                     # Nice to have
    BACKGROUND = "background"       # Passive influence


class EmotionalValence(str, Enum):
    """Emotional valence for episodic memories"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    MIXED = "mixed"
    TRANSFORMATIVE = "transformative"


# =============================================================================
# MEMORY ITEM DATA CLASSES
# =============================================================================

@dataclass
class MemoryItem(ABC):
    """Base class for all memory items"""
    id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    priority: MemoryPriority = MemoryPriority.MEDIUM
    tags: List[str] = field(default_factory=list)

    @abstractmethod
    def to_dict(self) -> Dict:
        pass

    def touch(self):
        """Update access time and count"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1


@dataclass
class CoreMemoryItem(MemoryItem):
    """
    CORE MEMORY - Immutable facts about the world

    These are absolute truths that CANNOT change:
    - Physical laws of the world
    - Magic/technology system rules
    - Historical facts (dates, events)
    - Character birth traits (eye color, birth date)
    - Geographic constants
    """
    fact: str = ""
    category: str = ""  # "world_rule", "physical_law", "magic_system", "history", "geography"
    entities: List[str] = field(default_factory=list)
    source: str = ""
    confidence: float = 1.0
    is_absolute: bool = True  # Cannot be overridden
    contradicts_if: List[str] = field(default_factory=list)  # Patterns that would contradict

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": "core",
            "fact": self.fact,
            "category": self.category,
            "entities": self.entities,
            "source": self.source,
            "confidence": self.confidence,
            "is_absolute": self.is_absolute,
            "priority": self.priority.value,
            "tags": self.tags
        }


@dataclass
class EpisodicMemoryItem(MemoryItem):
    """
    EPISODIC MEMORY - Scenes as complete episodes

    Each scene is stored with full context:
    - What happened (events)
    - Who was there (characters)
    - How they felt (emotions)
    - What changed (state transitions)
    - Sensory details (sights, sounds, smells)
    """
    scene_id: str = ""
    chapter: int = 0
    summary: str = ""
    characters_present: List[str] = field(default_factory=list)
    location: str = ""
    time_in_story: str = ""

    # Emotional context
    dominant_emotion: str = ""
    emotional_valence: EmotionalValence = EmotionalValence.NEUTRAL
    emotional_intensity: float = 0.5  # 0-1 scale
    emotional_vector: Dict[str, float] = field(default_factory=dict)  # 12-dim emotions

    # State changes
    character_states_before: Dict[str, str] = field(default_factory=dict)
    character_states_after: Dict[str, str] = field(default_factory=dict)
    relationship_changes: List[Dict] = field(default_factory=list)

    # Sensory details
    sensory_details: Dict[str, List[str]] = field(default_factory=dict)

    # Narrative importance
    plot_significance: float = 0.5  # 0-1 scale
    is_turning_point: bool = False
    foreshadowing: List[str] = field(default_factory=list)
    callbacks: List[str] = field(default_factory=list)  # References to earlier scenes

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": "episodic",
            "scene_id": self.scene_id,
            "chapter": self.chapter,
            "summary": self.summary,
            "characters_present": self.characters_present,
            "location": self.location,
            "time_in_story": self.time_in_story,
            "dominant_emotion": self.dominant_emotion,
            "emotional_valence": self.emotional_valence.value,
            "emotional_intensity": self.emotional_intensity,
            "emotional_vector": self.emotional_vector,
            "character_states_before": self.character_states_before,
            "character_states_after": self.character_states_after,
            "relationship_changes": self.relationship_changes,
            "sensory_details": self.sensory_details,
            "plot_significance": self.plot_significance,
            "is_turning_point": self.is_turning_point,
            "foreshadowing": self.foreshadowing,
            "callbacks": self.callbacks,
            "priority": self.priority.value,
            "tags": self.tags
        }


@dataclass
class SemanticMemoryItem(MemoryItem):
    """
    SEMANTIC MEMORY - Network of concepts and relationships

    Stores:
    - Themes and motifs
    - Symbols and their meanings
    - Character archetypes
    - Conceptual relationships
    - Narrative patterns
    """
    concept: str = ""
    concept_type: str = ""  # "theme", "motif", "symbol", "archetype", "pattern"
    definition: str = ""

    # Relationships to other concepts
    related_concepts: List[Tuple[str, str, float]] = field(default_factory=list)  # (concept, relation_type, strength)

    # Occurrences
    occurrences: List[Dict] = field(default_factory=list)  # Where this concept appears

    # Symbolic meaning
    symbolic_meaning: str = ""
    cultural_context: str = ""

    # Usage patterns
    typical_contexts: List[str] = field(default_factory=list)
    avoided_contexts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": "semantic",
            "concept": self.concept,
            "concept_type": self.concept_type,
            "definition": self.definition,
            "related_concepts": self.related_concepts,
            "occurrences": self.occurrences,
            "symbolic_meaning": self.symbolic_meaning,
            "cultural_context": self.cultural_context,
            "typical_contexts": self.typical_contexts,
            "avoided_contexts": self.avoided_contexts,
            "priority": self.priority.value,
            "tags": self.tags
        }


@dataclass
class ProceduralMemoryItem(MemoryItem):
    """
    PROCEDURAL MEMORY - How to write specific things

    Stores:
    - Narrative techniques
    - Writing patterns
    - Author style fingerprints
    - Genre conventions
    - Effective formulas
    """
    technique_name: str = ""
    technique_type: str = ""  # "style", "pacing", "dialogue", "description", "structure"
    description: str = ""

    # How to apply
    when_to_use: List[str] = field(default_factory=list)
    how_to_apply: str = ""
    examples: List[str] = field(default_factory=list)

    # Effectiveness
    effectiveness_score: float = 0.5
    genre_affinity: Dict[str, float] = field(default_factory=dict)  # Genre -> effectiveness

    # Style parameters
    style_parameters: Dict[str, Any] = field(default_factory=dict)

    # Learning source
    learned_from: str = ""  # "bestseller_analysis", "user_feedback", "training"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": "procedural",
            "technique_name": self.technique_name,
            "technique_type": self.technique_type,
            "description": self.description,
            "when_to_use": self.when_to_use,
            "how_to_apply": self.how_to_apply,
            "examples": self.examples,
            "effectiveness_score": self.effectiveness_score,
            "genre_affinity": self.genre_affinity,
            "style_parameters": self.style_parameters,
            "learned_from": self.learned_from,
            "priority": self.priority.value,
            "tags": self.tags
        }


@dataclass
class ResourceMemoryItem(MemoryItem):
    """
    RESOURCE MEMORY - Creative building blocks

    Stores:
    - Metaphors and similes
    - Quotes and references
    - Descriptive phrases
    - Sensory descriptions
    - Emotional expressions
    """
    resource_type: str = ""  # "metaphor", "simile", "quote", "description", "expression"
    content: str = ""

    # Context
    emotional_context: List[str] = field(default_factory=list)
    genre_context: List[str] = field(default_factory=list)
    situational_context: List[str] = field(default_factory=list)

    # Quality metrics
    originality_score: float = 0.5
    impact_score: float = 0.5
    usage_count: int = 0

    # Variations
    variations: List[str] = field(default_factory=list)

    # Source
    source_type: str = ""  # "generated", "analyzed", "curated"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": "resource",
            "resource_type": self.resource_type,
            "content": self.content,
            "emotional_context": self.emotional_context,
            "genre_context": self.genre_context,
            "situational_context": self.situational_context,
            "originality_score": self.originality_score,
            "impact_score": self.impact_score,
            "usage_count": self.usage_count,
            "variations": self.variations,
            "source_type": self.source_type,
            "priority": self.priority.value,
            "tags": self.tags
        }


@dataclass
class KnowledgeVaultItem(MemoryItem):
    """
    KNOWLEDGE VAULT - Deep world encyclopedia

    Stores:
    - Character biographies
    - Location histories
    - Object descriptions
    - Event chronicles
    - Cultural details
    """
    entry_type: str = ""  # "character", "location", "object", "event", "culture", "organization"
    name: str = ""
    full_content: str = ""

    # Structured data
    attributes: Dict[str, Any] = field(default_factory=dict)
    timeline: List[Dict] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)

    # Cross-references
    related_entries: List[str] = field(default_factory=list)
    mentioned_in_chapters: List[int] = field(default_factory=list)

    # Visibility
    reader_knows: bool = True  # Has this been revealed to the reader?
    first_mention_chapter: Optional[int] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": "knowledge_vault",
            "entry_type": self.entry_type,
            "name": self.name,
            "full_content": self.full_content,
            "attributes": self.attributes,
            "timeline": self.timeline,
            "relationships": self.relationships,
            "related_entries": self.related_entries,
            "mentioned_in_chapters": self.mentioned_in_chapters,
            "reader_knows": self.reader_knows,
            "first_mention_chapter": self.first_mention_chapter,
            "priority": self.priority.value,
            "tags": self.tags
        }


# =============================================================================
# MEMORY LAYER CLASSES
# =============================================================================

class MemoryLayer(ABC):
    """Abstract base class for memory layers"""

    def __init__(self, layer_type: MemoryType):
        self.layer_type = layer_type
        self.items: Dict[str, MemoryItem] = {}
        self.index: Dict[str, Set[str]] = defaultdict(set)  # tag -> item_ids

    @abstractmethod
    async def store(self, item: MemoryItem) -> str:
        """Store an item in this layer"""
        pass

    @abstractmethod
    async def retrieve(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Retrieve items matching query"""
        pass

    @abstractmethod
    async def query_by_context(self, context: Dict) -> List[MemoryItem]:
        """Query items based on context"""
        pass

    def _index_item(self, item: MemoryItem):
        """Add item to tag index"""
        for tag in item.tags:
            self.index[tag.lower()].add(item.id)

    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content"""
        return hashlib.md5(
            f"{self.layer_type.value}:{content}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]


class CoreMemoryLayer(MemoryLayer):
    """Layer for immutable core facts"""

    def __init__(self):
        super().__init__(MemoryType.CORE)
        self.category_index: Dict[str, Set[str]] = defaultdict(set)
        self.entity_index: Dict[str, Set[str]] = defaultdict(set)

    async def store(self, item: CoreMemoryItem) -> str:
        if not item.id:
            item.id = self._generate_id(item.fact)

        self.items[item.id] = item
        self._index_item(item)
        self.category_index[item.category].add(item.id)

        for entity in item.entities:
            self.entity_index[entity.lower()].add(item.id)

        logger.debug(f"Stored core memory: {item.fact[:50]}...")
        return item.id

    async def retrieve(self, query: str, limit: int = 10) -> List[CoreMemoryItem]:
        """Retrieve core facts matching query.

        For small datasets (<1000 items), uses in-memory scan.
        For larger datasets, delegates to pgvector SQL full-text search.
        """
        # Fast path: SQL-based filtering for large datasets
        if len(self.items) > 500:
            return await self._retrieve_via_sql(query, limit)

        results = []
        query_lower = query.lower()

        for item in self.items.values():
            if query_lower in item.fact.lower():
                item.touch()
                results.append(item)

            if len(results) >= limit:
                break

        return sorted(results, key=lambda x: x.priority.value)[:limit]

    async def _retrieve_via_sql(self, query: str, limit: int) -> List[CoreMemoryItem]:
        """SQL-based retrieval - offloads filtering to PostgreSQL."""
        try:
            from app.database import engine
            from sqlalchemy import text as sa_text

            with engine.connect() as conn:
                result = conn.execute(sa_text("""
                    SELECT id, content, metadata
                    FROM mirix_vectors
                    WHERE collection LIKE '%core%'
                      AND content ILIKE :query
                    LIMIT :limit
                """), {"query": f"%{query[:100]}%", "limit": limit})

                sql_results = []
                for row in result.fetchall():
                    meta = json.loads(row[1]) if isinstance(row[1], str) else row[1] or {}
                    # If item exists in memory, return the rich object
                    item_id = row[0]
                    if item_id in self.items:
                        self.items[item_id].touch()
                        sql_results.append(self.items[item_id])
                    else:
                        # Reconstruct from DB
                        sql_results.append(CoreMemoryItem(
                            id=item_id,
                            fact=row[0] if not isinstance(row[1], str) else row[0],
                            category=meta.get("category", "unknown"),
                            entities=meta.get("entities", "").split(", ") if meta.get("entities") else [],
                            source=meta.get("source", ""),
                            is_absolute=True,
                        ))
                return sql_results
        except Exception as e:
            logger.debug(f"SQL retrieve fallback to in-memory: {e}")
            # Fallback to in-memory scan
            results = []
            query_lower = query.lower()
            for item in self.items.values():
                if query_lower in item.fact.lower():
                    results.append(item)
                if len(results) >= limit:
                    break
            return results

    async def query_by_context(self, context: Dict) -> List[CoreMemoryItem]:
        """Query core facts by context"""
        results = []

        # Query by entities
        entities = context.get("entities", [])
        for entity in entities:
            item_ids = self.entity_index.get(entity.lower(), set())
            for item_id in item_ids:
                if item_id in self.items:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)

        # Query by category
        category = context.get("category")
        if category:
            item_ids = self.category_index.get(category, set())
            for item_id in item_ids:
                if item_id in self.items and self.items[item_id] not in results:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)

        return results

    async def check_contradiction(self, new_fact: str, entities: List[str]) -> Optional[CoreMemoryItem]:
        """Check if new fact contradicts existing core memory"""
        for entity in entities:
            item_ids = self.entity_index.get(entity.lower(), set())
            for item_id in item_ids:
                item = self.items.get(item_id)
                if item and item.is_absolute:
                    # Check contradiction patterns
                    for pattern in item.contradicts_if:
                        if pattern.lower() in new_fact.lower():
                            return item
        return None


class EpisodicMemoryLayer(MemoryLayer):
    """Layer for scene episodes"""

    def __init__(self):
        super().__init__(MemoryType.EPISODIC)
        self.chapter_index: Dict[int, List[str]] = defaultdict(list)
        self.character_index: Dict[str, Set[str]] = defaultdict(set)
        self.location_index: Dict[str, Set[str]] = defaultdict(set)
        self.emotion_index: Dict[str, Set[str]] = defaultdict(set)

    async def store(self, item: EpisodicMemoryItem) -> str:
        if not item.id:
            item.id = self._generate_id(item.summary)

        self.items[item.id] = item
        self._index_item(item)

        self.chapter_index[item.chapter].append(item.id)

        for char in item.characters_present:
            self.character_index[char.lower()].add(item.id)

        if item.location:
            self.location_index[item.location.lower()].add(item.id)

        if item.dominant_emotion:
            self.emotion_index[item.dominant_emotion.lower()].add(item.id)

        logger.debug(f"Stored episodic memory: Chapter {item.chapter} - {item.summary[:50]}...")
        return item.id

    async def retrieve(self, query: str, limit: int = 10) -> List[EpisodicMemoryItem]:
        """Retrieve episodes matching query. Uses SQL for large datasets."""
        # SQL fast-path for large datasets
        if len(self.items) > 500:
            return await self._retrieve_via_sql(query, limit)

        results = []
        query_lower = query.lower()

        for item in self.items.values():
            if query_lower in item.summary.lower():
                item.touch()
                results.append(item)

        return sorted(results, key=lambda x: x.chapter)[:limit]

    async def _retrieve_via_sql(self, query: str, limit: int) -> List[EpisodicMemoryItem]:
        """SQL-based retrieval for large episodic memory sets."""
        try:
            from app.database import engine
            from sqlalchemy import text as sa_text

            with engine.connect() as conn:
                result = conn.execute(sa_text("""
                    SELECT id, content, metadata
                    FROM mirix_vectors
                    WHERE collection LIKE '%episod%'
                      AND content ILIKE :query
                    ORDER BY created_at DESC
                    LIMIT :limit
                """), {"query": f"%{query[:100]}%", "limit": limit})

                sql_results = []
                for row in result.fetchall():
                    item_id = row[0]
                    if item_id in self.items:
                        self.items[item_id].touch()
                        sql_results.append(self.items[item_id])
                return sql_results
        except Exception as e:
            logger.debug(f"SQL episodic retrieve fallback: {e}")
            results = []
            query_lower = query.lower()
            for item in self.items.values():
                if query_lower in item.summary.lower():
                    results.append(item)
                if len(results) >= limit:
                    break
            return results

    async def query_by_context(self, context: Dict) -> List[EpisodicMemoryItem]:
        results = []
        seen_ids = set()

        # By character
        characters = context.get("characters", [])
        for char in characters:
            item_ids = self.character_index.get(char.lower(), set())
            for item_id in item_ids:
                if item_id not in seen_ids and item_id in self.items:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)
                    seen_ids.add(item_id)

        # By location
        location = context.get("location")
        if location:
            item_ids = self.location_index.get(location.lower(), set())
            for item_id in item_ids:
                if item_id not in seen_ids and item_id in self.items:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)
                    seen_ids.add(item_id)

        # By chapter range
        chapter_start = context.get("chapter_start", 0)
        chapter_end = context.get("chapter_end", 999)
        for chapter in range(chapter_start, chapter_end + 1):
            for item_id in self.chapter_index.get(chapter, []):
                if item_id not in seen_ids and item_id in self.items:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)
                    seen_ids.add(item_id)

        return sorted(results, key=lambda x: x.chapter)

    async def get_emotional_trajectory(self) -> List[Dict]:
        """Get emotional trajectory across all episodes"""
        episodes = sorted(self.items.values(), key=lambda x: x.chapter)
        return [
            {
                "chapter": ep.chapter,
                "emotion": ep.dominant_emotion,
                "valence": ep.emotional_valence.value,
                "intensity": ep.emotional_intensity,
                "vector": ep.emotional_vector
            }
            for ep in episodes
        ]

    async def find_callbacks_for(self, chapter: int, characters: List[str]) -> List[EpisodicMemoryItem]:
        """Find relevant earlier episodes to reference"""
        current_episodes = self.chapter_index.get(chapter, [])
        callbacks = []

        for char in characters:
            char_episodes = self.character_index.get(char.lower(), set())
            for ep_id in char_episodes:
                ep = self.items.get(ep_id)
                if ep and ep.chapter < chapter and ep.plot_significance > 0.6:
                    callbacks.append(ep)

        return sorted(callbacks, key=lambda x: x.plot_significance, reverse=True)[:5]


class SemanticMemoryLayer(MemoryLayer):
    """Layer for concepts and relationships"""

    def __init__(self):
        super().__init__(MemoryType.SEMANTIC)
        self.concept_type_index: Dict[str, Set[str]] = defaultdict(set)
        self.concept_graph: Dict[str, Dict[str, float]] = defaultdict(dict)  # concept -> related -> strength

    async def store(self, item: SemanticMemoryItem) -> str:
        if not item.id:
            item.id = self._generate_id(item.concept)

        self.items[item.id] = item
        self._index_item(item)
        self.concept_type_index[item.concept_type].add(item.id)

        # Build concept graph
        for related, relation, strength in item.related_concepts:
            self.concept_graph[item.concept][related] = strength
            self.concept_graph[related][item.concept] = strength * 0.8  # Bidirectional with decay

        logger.debug(f"Stored semantic memory: {item.concept}")
        return item.id

    async def retrieve(self, query: str, limit: int = 10) -> List[SemanticMemoryItem]:
        results = []
        query_lower = query.lower()

        for item in self.items.values():
            if query_lower in item.concept.lower() or query_lower in item.definition.lower():
                item.touch()
                results.append(item)

        return results[:limit]

    async def query_by_context(self, context: Dict) -> List[SemanticMemoryItem]:
        results = []

        concept_type = context.get("concept_type")
        if concept_type:
            item_ids = self.concept_type_index.get(concept_type, set())
            for item_id in item_ids:
                if item_id in self.items:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)

        return results

    async def get_related_concepts(self, concept: str, depth: int = 2) -> Dict[str, float]:
        """Get related concepts with strengths up to given depth"""
        related = {}
        visited = {concept}
        current_level = {concept: 1.0}

        for _ in range(depth):
            next_level = {}
            for c, strength in current_level.items():
                for rel, rel_strength in self.concept_graph.get(c, {}).items():
                    if rel not in visited:
                        combined = strength * rel_strength
                        if rel in next_level:
                            next_level[rel] = max(next_level[rel], combined)
                        else:
                            next_level[rel] = combined
                        related[rel] = max(related.get(rel, 0), combined)
                        visited.add(rel)
            current_level = next_level

        return dict(sorted(related.items(), key=lambda x: x[1], reverse=True))

    async def get_theme_network(self) -> Dict:
        """Get the full theme/motif network for visualization"""
        themes = self.concept_type_index.get("theme", set())
        motifs = self.concept_type_index.get("motif", set())

        nodes = []
        edges = []

        for item_id in themes | motifs:
            item = self.items.get(item_id)
            if item:
                nodes.append({
                    "id": item.concept,
                    "type": item.concept_type,
                    "meaning": item.symbolic_meaning
                })

                for related, _, strength in item.related_concepts:
                    edges.append({
                        "source": item.concept,
                        "target": related,
                        "strength": strength
                    })

        return {"nodes": nodes, "edges": edges}


class ProceduralMemoryLayer(MemoryLayer):
    """Layer for writing techniques"""

    def __init__(self):
        super().__init__(MemoryType.PROCEDURAL)
        self.technique_type_index: Dict[str, Set[str]] = defaultdict(set)
        self.genre_index: Dict[str, Set[str]] = defaultdict(set)

    async def store(self, item: ProceduralMemoryItem) -> str:
        if not item.id:
            item.id = self._generate_id(item.technique_name)

        self.items[item.id] = item
        self._index_item(item)
        self.technique_type_index[item.technique_type].add(item.id)

        for genre, effectiveness in item.genre_affinity.items():
            if effectiveness > 0.5:
                self.genre_index[genre.lower()].add(item.id)

        logger.debug(f"Stored procedural memory: {item.technique_name}")
        return item.id

    async def retrieve(self, query: str, limit: int = 10) -> List[ProceduralMemoryItem]:
        results = []
        query_lower = query.lower()

        for item in self.items.values():
            if query_lower in item.technique_name.lower() or query_lower in item.description.lower():
                item.touch()
                results.append(item)

        return sorted(results, key=lambda x: x.effectiveness_score, reverse=True)[:limit]

    async def query_by_context(self, context: Dict) -> List[ProceduralMemoryItem]:
        results = []

        # By genre
        genre = context.get("genre")
        if genre:
            item_ids = self.genre_index.get(genre.lower(), set())
            for item_id in item_ids:
                if item_id in self.items:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)

        # By technique type
        technique_type = context.get("technique_type")
        if technique_type:
            item_ids = self.technique_type_index.get(technique_type, set())
            for item_id in item_ids:
                if item_id in self.items and self.items[item_id] not in results:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)

        return sorted(results, key=lambda x: x.effectiveness_score, reverse=True)

    async def get_techniques_for_scene(
        self,
        scene_type: str,
        genre: str,
        emotional_target: str
    ) -> List[ProceduralMemoryItem]:
        """Get best techniques for a specific scene type"""
        candidates = []

        for item in self.items.values():
            score = 0

            # Genre match
            genre_eff = item.genre_affinity.get(genre.lower(), 0.5)
            score += genre_eff * 0.4

            # Scene type match
            if scene_type.lower() in [w.lower() for w in item.when_to_use]:
                score += 0.3

            # Emotional context match
            if emotional_target.lower() in item.description.lower():
                score += 0.3

            score *= item.effectiveness_score

            if score > 0.3:
                candidates.append((item, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in candidates[:5]]


class ResourceMemoryLayer(MemoryLayer):
    """Layer for creative resources"""

    def __init__(self):
        super().__init__(MemoryType.RESOURCE)
        self.resource_type_index: Dict[str, Set[str]] = defaultdict(set)
        self.emotion_index: Dict[str, Set[str]] = defaultdict(set)
        self.genre_index: Dict[str, Set[str]] = defaultdict(set)

    async def store(self, item: ResourceMemoryItem) -> str:
        if not item.id:
            item.id = self._generate_id(item.content)

        self.items[item.id] = item
        self._index_item(item)
        self.resource_type_index[item.resource_type].add(item.id)

        for emotion in item.emotional_context:
            self.emotion_index[emotion.lower()].add(item.id)

        for genre in item.genre_context:
            self.genre_index[genre.lower()].add(item.id)

        logger.debug(f"Stored resource memory: {item.content[:50]}...")
        return item.id

    async def retrieve(self, query: str, limit: int = 10) -> List[ResourceMemoryItem]:
        results = []
        query_lower = query.lower()

        for item in self.items.values():
            if query_lower in item.content.lower():
                item.touch()
                results.append(item)

        return sorted(results, key=lambda x: x.impact_score, reverse=True)[:limit]

    async def query_by_context(self, context: Dict) -> List[ResourceMemoryItem]:
        results = []
        seen_ids = set()

        # By resource type
        resource_type = context.get("resource_type")
        if resource_type:
            item_ids = self.resource_type_index.get(resource_type, set())
            for item_id in item_ids:
                if item_id in self.items:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)
                    seen_ids.add(item_id)

        # By emotion
        emotion = context.get("emotion")
        if emotion:
            item_ids = self.emotion_index.get(emotion.lower(), set())
            for item_id in item_ids:
                if item_id not in seen_ids and item_id in self.items:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)
                    seen_ids.add(item_id)

        # By genre
        genre = context.get("genre")
        if genre:
            item_ids = self.genre_index.get(genre.lower(), set())
            for item_id in item_ids:
                if item_id not in seen_ids and item_id in self.items:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)
                    seen_ids.add(item_id)

        return sorted(results, key=lambda x: x.impact_score, reverse=True)

    async def get_metaphor_for(
        self,
        target_concept: str,
        emotion: str,
        genre: str,
        used_already: List[str] = None
    ) -> Optional[ResourceMemoryItem]:
        """Get best metaphor for a concept"""
        used_already = used_already or []
        candidates = []

        metaphor_ids = self.resource_type_index.get("metaphor", set())
        for item_id in metaphor_ids:
            item = self.items.get(item_id)
            if not item or item.content in used_already:
                continue

            score = item.impact_score * item.originality_score

            if emotion.lower() in item.emotional_context:
                score *= 1.3
            if genre.lower() in item.genre_context:
                score *= 1.2

            # Penalize overused
            score *= max(0.5, 1.0 - (item.usage_count * 0.1))

            candidates.append((item, score))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            chosen = candidates[0][0]
            chosen.usage_count += 1
            return chosen

        return None


class KnowledgeVaultLayer(MemoryLayer):
    """Layer for world encyclopedia"""

    def __init__(self):
        super().__init__(MemoryType.KNOWLEDGE_VAULT)
        self.entry_type_index: Dict[str, Set[str]] = defaultdict(set)
        self.name_index: Dict[str, str] = {}  # name -> id
        self.chapter_index: Dict[int, Set[str]] = defaultdict(set)

    async def store(self, item: KnowledgeVaultItem) -> str:
        if not item.id:
            item.id = self._generate_id(f"{item.entry_type}:{item.name}")

        self.items[item.id] = item
        self._index_item(item)
        self.entry_type_index[item.entry_type].add(item.id)
        self.name_index[item.name.lower()] = item.id

        for chapter in item.mentioned_in_chapters:
            self.chapter_index[chapter].add(item.id)

        logger.debug(f"Stored knowledge vault entry: {item.entry_type} - {item.name}")
        return item.id

    async def retrieve(self, query: str, limit: int = 10) -> List[KnowledgeVaultItem]:
        results = []
        query_lower = query.lower()

        # Direct name match
        if query_lower in self.name_index:
            item = self.items.get(self.name_index[query_lower])
            if item:
                item.touch()
                results.append(item)

        # Content search
        for item in self.items.values():
            if item not in results:
                if query_lower in item.name.lower() or query_lower in item.full_content.lower():
                    item.touch()
                    results.append(item)

        return results[:limit]

    async def query_by_context(self, context: Dict) -> List[KnowledgeVaultItem]:
        results = []

        # By entry type
        entry_type = context.get("entry_type")
        if entry_type:
            item_ids = self.entry_type_index.get(entry_type, set())
            for item_id in item_ids:
                if item_id in self.items:
                    item = self.items[item_id]
                    item.touch()
                    results.append(item)

        # By name
        name = context.get("name")
        if name:
            item_id = self.name_index.get(name.lower())
            if item_id and item_id in self.items:
                item = self.items[item_id]
                if item not in results:
                    item.touch()
                    results.append(item)

        return results

    async def get_character_biography(self, name: str) -> Optional[KnowledgeVaultItem]:
        """Get full character biography"""
        item_id = self.name_index.get(name.lower())
        if item_id:
            item = self.items.get(item_id)
            if item and item.entry_type == "character":
                item.touch()
                return item
        return None

    async def get_location_details(self, name: str) -> Optional[KnowledgeVaultItem]:
        """Get location details"""
        item_id = self.name_index.get(name.lower())
        if item_id:
            item = self.items.get(item_id)
            if item and item.entry_type == "location":
                item.touch()
                return item
        return None

    async def get_entries_for_chapter(self, chapter: int) -> List[KnowledgeVaultItem]:
        """Get all entries relevant to a chapter"""
        results = []
        item_ids = self.chapter_index.get(chapter, set())
        for item_id in item_ids:
            item = self.items.get(item_id)
            if item:
                item.touch()
                results.append(item)
        return results

    async def mark_revealed_to_reader(self, name: str, chapter: int):
        """Mark information as revealed to reader"""
        item_id = self.name_index.get(name.lower())
        if item_id and item_id in self.items:
            item = self.items[item_id]
            item.reader_knows = True
            if item.first_mention_chapter is None:
                item.first_mention_chapter = chapter


# =============================================================================
# VECTOR MEMORY LAYER (Semantic Search via pgvector)
# =============================================================================

class VectorMemoryLayer:
    """
    Vector-based semantic search layer for MIRIX.

    Uses pgvector (PostgreSQL extension) for embedding storage and retrieval.
    This eliminates the ChromaDB dependency and keeps everything in the
    existing PostgreSQL infrastructure.

    Hybrid approach: keyword search (fast, deterministic) + semantic search (fuzzy, intelligent)
    """

    # OpenAI text-embedding-3-small returns 1536 dimensions
    EMBEDDING_DIM = 1536

    def __init__(self, collection_name: str = "narrative_memory"):
        self._initialized = False
        self._collection_name = collection_name
        self._openai_client = None
        self._item_count = 0

    def _ensure_initialized(self) -> bool:
        """Lazy initialization – create the pgvector table if it doesn't exist."""
        if self._initialized:
            return True

        try:
            from app.database import engine
            from sqlalchemy import text as sa_text

            with engine.connect() as conn:
                conn.execute(sa_text("""
                    CREATE TABLE IF NOT EXISTS mirix_vectors (
                        id TEXT PRIMARY KEY,
                        collection TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB DEFAULT '{}',
                        embedding vector(1536),
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                conn.execute(sa_text("""
                    CREATE INDEX IF NOT EXISTS idx_mirix_vectors_collection
                    ON mirix_vectors (collection)
                """))
                # HNSW index: no training phase needed, works on empty tables,
                # better recall than ivfflat at comparable speed.
                try:
                    conn.execute(sa_text("""
                        CREATE INDEX IF NOT EXISTS idx_mirix_vectors_embedding
                        ON mirix_vectors USING hnsw (embedding vector_cosine_ops)
                        WITH (m = 16, ef_construction = 64)
                    """))
                except Exception:
                    pass
                conn.commit()

            self._initialized = True
            logger.info(f"VectorMemoryLayer (pgvector) initialized: collection '{self._collection_name}'")
            return True
        except Exception as e:
            logger.warning(f"VectorMemoryLayer pgvector init failed: {e}. Semantic search disabled.")
            return False

    async def _get_embedding(self, text: str) -> list:
        """Generate embedding using OpenAI text-embedding-3-small."""
        try:
            if self._openai_client is None:
                from openai import AsyncOpenAI
                self._openai_client = AsyncOpenAI()

            response = await self._openai_client.embeddings.create(
                input=text[:8000],  # Limit input length
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.debug(f"OpenAI embedding failed: {e}")
            return None

    async def store(
        self,
        text: str,
        metadata: dict,
        doc_id: str
    ) -> bool:
        """Store a text with its embedding for semantic retrieval.

        Args:
            text: The text content to store and make searchable
            metadata: Structured metadata (chapter, characters, type, etc.)
            doc_id: Unique identifier for this document

        Returns:
            True if stored successfully
        """
        if not self._ensure_initialized():
            return False

        try:
            # Clean metadata for JSONB
            clean_metadata = {}
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_metadata[k] = v
                elif isinstance(v, list):
                    clean_metadata[k] = ", ".join(str(item) for item in v)
                else:
                    clean_metadata[k] = str(v)

            embedding = await self._get_embedding(text)

            from app.database import engine
            from sqlalchemy import text as sa_text

            with engine.connect() as conn:
                if embedding:
                    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
                    conn.execute(sa_text("""
                        INSERT INTO mirix_vectors (id, collection, content, metadata, embedding)
                        VALUES (:id, :collection, :content, :metadata, :embedding::vector)
                        ON CONFLICT (id) DO UPDATE SET
                            content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding
                    """), {
                        "id": doc_id,
                        "collection": self._collection_name,
                        "content": text,
                        "metadata": json.dumps(clean_metadata),
                        "embedding": embedding_str,
                    })
                else:
                    # Store without embedding (text-only fallback)
                    conn.execute(sa_text("""
                        INSERT INTO mirix_vectors (id, collection, content, metadata)
                        VALUES (:id, :collection, :content, :metadata)
                        ON CONFLICT (id) DO UPDATE SET
                            content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata
                    """), {
                        "id": doc_id,
                        "collection": self._collection_name,
                        "content": text,
                        "metadata": json.dumps(clean_metadata),
                    })
                conn.commit()

            self._item_count += 1
            return True
        except Exception as e:
            logger.warning(f"VectorMemoryLayer.store failed: {e}")
            return False

    async def retrieve_relevant(
        self,
        query_text: str,
        limit: int = 5,
        where_filter: dict = None
    ) -> list:
        """Retrieve semantically similar documents via pgvector cosine distance.

        Args:
            query_text: The query to search for
            limit: Maximum number of results
            where_filter: Optional filter dict (e.g. {"chapter": 3})

        Returns:
            List of dicts with 'text', 'metadata', 'distance', 'relevance' keys
        """
        if not self._ensure_initialized():
            return []

        try:
            query_embedding = await self._get_embedding(query_text)

            from app.database import engine
            from sqlalchemy import text as sa_text

            with engine.connect() as conn:
                if query_embedding:
                    # Cosine distance search via pgvector <=> operator
                    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

                    where_clause = "collection = :collection AND embedding IS NOT NULL"
                    params = {
                        "collection": self._collection_name,
                        "embedding": embedding_str,
                        "limit": limit,
                    }

                    # Apply metadata filters
                    if where_filter:
                        for key, value in where_filter.items():
                            where_clause += f" AND metadata->>'{key}' = :filter_{key}"
                            params[f"filter_{key}"] = str(value)

                    result = conn.execute(sa_text(f"""
                        SELECT content, metadata, embedding <=> :embedding::vector AS distance
                        FROM mirix_vectors
                        WHERE {where_clause}
                        ORDER BY distance
                        LIMIT :limit
                    """), params)

                    rows = result.fetchall()
                else:
                    # Fallback: text similarity search (no embedding available)
                    where_clause = "collection = :collection"
                    params = {
                        "collection": self._collection_name,
                        "query": f"%{query_text[:100]}%",
                        "limit": limit,
                    }

                    if where_filter:
                        for key, value in where_filter.items():
                            where_clause += f" AND metadata->>'{key}' = :filter_{key}"
                            params[f"filter_{key}"] = str(value)

                    result = conn.execute(sa_text(f"""
                        SELECT content, metadata, 0.5 AS distance
                        FROM mirix_vectors
                        WHERE {where_clause} AND content ILIKE :query
                        LIMIT :limit
                    """), params)

                    rows = result.fetchall()

            formatted = []
            for row in rows:
                meta = row[1] if isinstance(row[1], dict) else json.loads(row[1]) if row[1] else {}
                dist = float(row[2])
                formatted.append({
                    "text": row[0],
                    "metadata": meta,
                    "distance": dist,
                    "relevance": max(0.0, 1.0 - dist),
                })

            return formatted

        except Exception as e:
            logger.warning(f"VectorMemoryLayer.retrieve_relevant failed: {e}")
            return []

    def get_stats(self) -> dict:
        """Get vector memory statistics."""
        if not self._ensure_initialized():
            return {"initialized": False, "count": 0, "backend": "pgvector"}

        try:
            from app.database import engine
            from sqlalchemy import text as sa_text

            with engine.connect() as conn:
                result = conn.execute(sa_text(
                    "SELECT COUNT(*) FROM mirix_vectors WHERE collection = :col"
                ), {"col": self._collection_name})
                count = result.scalar() or 0

            return {
                "initialized": True,
                "backend": "pgvector",
                "collection": self._collection_name,
                "count": count,
            }
        except Exception:
            return {"initialized": True, "backend": "pgvector", "count": self._item_count}


# =============================================================================
# MAIN MIRIX MEMORY SYSTEM
# =============================================================================

class MIRIXMemorySystem:
    """
    MIRIX Memory Architecture - Main System

    Orchestrates all 6 memory layers and provides unified interface.
    Supports cross-project learning and persistent memory.
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()

        # Initialize all memory layers
        self.core = CoreMemoryLayer()
        self.episodic = EpisodicMemoryLayer()
        self.semantic = SemanticMemoryLayer()
        self.procedural = ProceduralMemoryLayer()
        self.resource = ResourceMemoryLayer()
        self.knowledge_vault = KnowledgeVaultLayer()

        # Layer registry for easy iteration
        self._layers: Dict[MemoryType, MemoryLayer] = {
            MemoryType.CORE: self.core,
            MemoryType.EPISODIC: self.episodic,
            MemoryType.SEMANTIC: self.semantic,
            MemoryType.PROCEDURAL: self.procedural,
            MemoryType.RESOURCE: self.resource,
            MemoryType.KNOWLEDGE_VAULT: self.knowledge_vault
        }

        # Vector memory layers per project (semantic search)
        self._vector_layers: Dict[str, VectorMemoryLayer] = {}

        # Project-specific memory stores
        self.project_memories: Dict[str, Dict[MemoryType, MemoryLayer]] = {}

        # Cross-project learning store
        self.global_procedural = ProceduralMemoryLayer()
        self.global_resources = ResourceMemoryLayer()

        logger.info("MIRIX Memory System initialized with 6 layers + vector search")

    # =========================================================================
    # PROJECT INITIALIZATION
    # =========================================================================

    def _get_vector_layer(self, project_id: str) -> VectorMemoryLayer:
        """Get or create vector memory layer for a project."""
        if project_id not in self._vector_layers:
            self._vector_layers[project_id] = VectorMemoryLayer(
                collection_name=f"project_{project_id[:16]}"
            )
        return self._vector_layers[project_id]

    async def semantic_search(
        self,
        project_id: str,
        query: str,
        limit: int = 10,
        chapter_filter: int = None
    ) -> List[Dict]:
        """
        Perform semantic (vector) search across all stored memories for a project.

        This is the key improvement over keyword search - it finds semantically
        similar content even without exact keyword matches.

        Example: query "kolor oczu matki" will find "Jej oczy miały barwę bursztynu"

        Args:
            project_id: Project to search in
            query: Natural language query
            limit: Max results
            chapter_filter: Optional - restrict to specific chapter

        Returns:
            List of relevant memory fragments with metadata
        """
        vector_layer = self._get_vector_layer(project_id)
        where_filter = {"chapter": chapter_filter} if chapter_filter else None
        return await vector_layer.retrieve_relevant(query, limit, where_filter)

    async def initialize_project(self, project_id: str, genre: GenreType) -> Dict:
        """Initialize MIRIX memory for a new project"""
        if project_id not in self.project_memories:
            self.project_memories[project_id] = {
                MemoryType.CORE: CoreMemoryLayer(),
                MemoryType.EPISODIC: EpisodicMemoryLayer(),
                MemoryType.SEMANTIC: SemanticMemoryLayer(),
                MemoryType.PROCEDURAL: ProceduralMemoryLayer(),
                MemoryType.RESOURCE: ResourceMemoryLayer(),
                MemoryType.KNOWLEDGE_VAULT: KnowledgeVaultLayer()
            }

            # Copy relevant global procedural knowledge
            await self._copy_genre_procedural(project_id, genre)

            logger.info(f"Initialized MIRIX memory for project {project_id}")

        return {
            "project_id": project_id,
            "layers_initialized": list(self.project_memories[project_id].keys()),
            "global_techniques_copied": True
        }

    async def _copy_genre_procedural(self, project_id: str, genre: GenreType):
        """Copy genre-relevant procedural knowledge to project"""
        genre_str = genre.value.lower()
        project_procedural = self.project_memories[project_id][MemoryType.PROCEDURAL]

        for item in self.global_procedural.items.values():
            if genre_str in item.genre_affinity and item.genre_affinity[genre_str] > 0.6:
                await project_procedural.store(item)

    def get_project_layer(self, project_id: str, layer_type: MemoryType) -> Optional[MemoryLayer]:
        """Get specific memory layer for a project"""
        if project_id in self.project_memories:
            return self.project_memories[project_id].get(layer_type)
        return None

    # =========================================================================
    # UNIFIED STORE OPERATIONS
    # =========================================================================

    async def store_core_fact(
        self,
        project_id: str,
        fact: str,
        category: str,
        entities: List[str],
        source: str = "",
        is_absolute: bool = True
    ) -> str:
        """Store an immutable core fact (dict + vector indexed)"""
        layer = self.get_project_layer(project_id, MemoryType.CORE)
        if not layer:
            await self.initialize_project(project_id, GenreType.FANTASY)  # Default
            layer = self.get_project_layer(project_id, MemoryType.CORE)

        item = CoreMemoryItem(
            id="",
            fact=fact,
            category=category,
            entities=entities,
            source=source,
            is_absolute=is_absolute,
            priority=MemoryPriority.CRITICAL if is_absolute else MemoryPriority.HIGH
        )

        item_id = await layer.store(item)

        # Also index in vector layer for semantic search
        vector_layer = self._get_vector_layer(project_id)
        await vector_layer.store(
            text=fact,
            metadata={
                "type": "core_fact",
                "category": category,
                "entities": ", ".join(entities),
                "source": source
            },
            doc_id=f"core_{item_id}"
        )

        return item_id

    async def store_episode(
        self,
        project_id: str,
        scene_id: str,
        chapter: int,
        summary: str,
        characters: List[str],
        location: str = "",
        emotional_data: Dict = None
    ) -> str:
        """Store a scene as episodic memory (dict + vector indexed)"""
        layer = self.get_project_layer(project_id, MemoryType.EPISODIC)
        if not layer:
            await self.initialize_project(project_id, GenreType.FANTASY)
            layer = self.get_project_layer(project_id, MemoryType.EPISODIC)

        emotional_data = emotional_data or {}

        item = EpisodicMemoryItem(
            id="",
            scene_id=scene_id,
            chapter=chapter,
            summary=summary,
            characters_present=characters,
            location=location,
            dominant_emotion=emotional_data.get("dominant_emotion", ""),
            emotional_valence=EmotionalValence(emotional_data.get("valence", "neutral")),
            emotional_intensity=emotional_data.get("intensity", 0.5),
            emotional_vector=emotional_data.get("vector", {}),
            plot_significance=emotional_data.get("significance", 0.5),
            is_turning_point=emotional_data.get("is_turning_point", False)
        )

        item_id = await layer.store(item)

        # Also index in vector layer for semantic search
        vector_layer = self._get_vector_layer(project_id)
        search_text = f"{summary} Postacie: {', '.join(characters)}. Lokacja: {location}."
        await vector_layer.store(
            text=search_text,
            metadata={
                "type": "episode",
                "chapter": chapter,
                "scene_id": scene_id,
                "characters": ", ".join(characters),
                "location": location,
                "emotion": emotional_data.get("dominant_emotion", "")
            },
            doc_id=f"episode_{item_id}"
        )

        return item_id

    async def store_concept(
        self,
        project_id: str,
        concept: str,
        concept_type: str,
        definition: str,
        related: List[Tuple[str, str, float]] = None,
        symbolic_meaning: str = ""
    ) -> str:
        """Store a semantic concept"""
        layer = self.get_project_layer(project_id, MemoryType.SEMANTIC)
        if not layer:
            await self.initialize_project(project_id, GenreType.FANTASY)
            layer = self.get_project_layer(project_id, MemoryType.SEMANTIC)

        item = SemanticMemoryItem(
            id="",
            concept=concept,
            concept_type=concept_type,
            definition=definition,
            related_concepts=related or [],
            symbolic_meaning=symbolic_meaning
        )

        return await layer.store(item)

    async def store_technique(
        self,
        technique_name: str,
        technique_type: str,
        description: str,
        how_to_apply: str,
        examples: List[str],
        genre_affinity: Dict[str, float],
        effectiveness: float = 0.7,
        global_learn: bool = True
    ) -> str:
        """Store a writing technique (optionally to global memory)"""
        item = ProceduralMemoryItem(
            id="",
            technique_name=technique_name,
            technique_type=technique_type,
            description=description,
            how_to_apply=how_to_apply,
            examples=examples,
            genre_affinity=genre_affinity,
            effectiveness_score=effectiveness
        )

        item_id = await self.global_procedural.store(item)

        if global_learn:
            logger.info(f"Learned technique globally: {technique_name}")

        return item_id

    async def store_resource(
        self,
        resource_type: str,
        content: str,
        emotional_context: List[str],
        genre_context: List[str],
        originality: float = 0.5,
        impact: float = 0.5
    ) -> str:
        """Store a creative resource"""
        item = ResourceMemoryItem(
            id="",
            resource_type=resource_type,
            content=content,
            emotional_context=emotional_context,
            genre_context=genre_context,
            originality_score=originality,
            impact_score=impact
        )

        return await self.global_resources.store(item)

    async def store_knowledge_entry(
        self,
        project_id: str,
        entry_type: str,
        name: str,
        full_content: str,
        attributes: Dict = None,
        relationships: Dict = None
    ) -> str:
        """Store a knowledge vault entry"""
        layer = self.get_project_layer(project_id, MemoryType.KNOWLEDGE_VAULT)
        if not layer:
            await self.initialize_project(project_id, GenreType.FANTASY)
            layer = self.get_project_layer(project_id, MemoryType.KNOWLEDGE_VAULT)

        item = KnowledgeVaultItem(
            id="",
            entry_type=entry_type,
            name=name,
            full_content=full_content,
            attributes=attributes or {},
            relationships=relationships or {}
        )

        return await layer.store(item)

    # =========================================================================
    # UNIFIED QUERY OPERATIONS
    # =========================================================================

    async def query_all_layers(
        self,
        project_id: str,
        query: str,
        limit_per_layer: int = 5
    ) -> Dict[str, List[Dict]]:
        """Query all memory layers for relevant information"""
        results = {}

        if project_id not in self.project_memories:
            return results

        for layer_type, layer in self.project_memories[project_id].items():
            items = await layer.retrieve(query, limit_per_layer)
            results[layer_type.value] = [item.to_dict() for item in items]

        return results

    async def get_context_for_scene(
        self,
        project_id: str,
        chapter: int,
        characters: List[str],
        location: str,
        emotional_target: str
    ) -> Dict:
        """Get comprehensive context for writing a scene.

        Uses HYBRID approach: keyword indexes (fast) + vector semantic search (fuzzy).
        """
        context = {
            "core_facts": [],
            "relevant_episodes": [],
            "active_themes": [],
            "applicable_techniques": [],
            "available_resources": [],
            "character_info": [],
            "location_info": None,
            "semantic_matches": []  # NEW: vector search results
        }

        if project_id not in self.project_memories:
            return context

        layers = self.project_memories[project_id]

        # Core facts about characters and location
        core_layer = layers[MemoryType.CORE]
        for char in characters:
            facts = await core_layer.query_by_context({"entities": [char]})
            context["core_facts"].extend([f.to_dict() for f in facts])

        if location:
            location_facts = await core_layer.query_by_context({"entities": [location]})
            context["core_facts"].extend([f.to_dict() for f in location_facts])

        # Relevant earlier episodes
        episodic_layer = layers[MemoryType.EPISODIC]
        callbacks = await episodic_layer.find_callbacks_for(chapter, characters)
        context["relevant_episodes"] = [ep.to_dict() for ep in callbacks]

        # Active themes
        semantic_layer = layers[MemoryType.SEMANTIC]
        themes = await semantic_layer.query_by_context({"concept_type": "theme"})
        context["active_themes"] = [t.to_dict() for t in themes[:5]]

        # Applicable techniques
        proc_layer = layers[MemoryType.PROCEDURAL]
        techniques = await proc_layer.get_techniques_for_scene(
            scene_type="dialogue" if len(characters) > 1 else "description",
            genre="fantasy",  # TODO: Get from project
            emotional_target=emotional_target
        )
        context["applicable_techniques"] = [t.to_dict() for t in techniques]

        # Character info from knowledge vault
        kv_layer = layers[MemoryType.KNOWLEDGE_VAULT]
        for char in characters:
            bio = await kv_layer.get_character_biography(char)
            if bio:
                context["character_info"].append(bio.to_dict())

        # Location info
        if location:
            loc_info = await kv_layer.get_location_details(location)
            if loc_info:
                context["location_info"] = loc_info.to_dict()

        # SEMANTIC VECTOR SEARCH - find contextually relevant memories
        # Build a natural language query from scene parameters
        query_parts = []
        if characters:
            query_parts.append(f"Postacie: {', '.join(characters)}")
        if location:
            query_parts.append(f"Lokacja: {location}")
        if emotional_target:
            query_parts.append(f"Emocja: {emotional_target}")
        query_parts.append(f"Rozdział {chapter}")

        semantic_query = ". ".join(query_parts)
        semantic_results = await self.semantic_search(
            project_id=project_id,
            query=semantic_query,
            limit=10
        )
        context["semantic_matches"] = semantic_results

        return context

    async def check_consistency(
        self,
        project_id: str,
        new_fact: str,
        entities: List[str]
    ) -> Optional[Dict]:
        """Check if a new fact contradicts core memory"""
        if project_id not in self.project_memories:
            return None

        core_layer = self.project_memories[project_id][MemoryType.CORE]
        contradiction = await core_layer.check_contradiction(new_fact, entities)

        if contradiction:
            return {
                "has_contradiction": True,
                "contradicting_fact": contradiction.fact,
                "category": contradiction.category,
                "source": contradiction.source
            }

        return {"has_contradiction": False}

    # =========================================================================
    # AI-POWERED EXTRACTION
    # =========================================================================

    async def extract_and_store_from_world_bible(
        self,
        project_id: str,
        world_bible: Dict
    ) -> Dict[str, int]:
        """Extract and store all memory types from world bible"""
        counts = {
            "core_facts": 0,
            "concepts": 0,
            "knowledge_entries": 0
        }

        # Extract core facts (world rules, geography, etc.)
        if "systems" in world_bible:
            for system_name, system_data in world_bible["systems"].items():
                if isinstance(system_data, dict):
                    rules = system_data.get("rules", [])
                    for rule in rules:
                        await self.store_core_fact(
                            project_id=project_id,
                            fact=rule,
                            category="world_rule",
                            entities=[system_name],
                            source="world_bible"
                        )
                        counts["core_facts"] += 1

        # Extract geography as core facts
        if "geography" in world_bible:
            geo = world_bible["geography"]
            if isinstance(geo, dict):
                for location, desc in geo.items():
                    await self.store_core_fact(
                        project_id=project_id,
                        fact=f"{location}: {str(desc)[:200]}",
                        category="geography",
                        entities=[location],
                        source="world_bible"
                    )
                    counts["core_facts"] += 1

                    # Also store in knowledge vault
                    await self.store_knowledge_entry(
                        project_id=project_id,
                        entry_type="location",
                        name=location,
                        full_content=str(desc),
                        attributes={"source": "world_bible"}
                    )
                    counts["knowledge_entries"] += 1

        # Extract themes and motifs
        if "themes" in world_bible:
            themes = world_bible.get("themes", [])
            if isinstance(themes, list):
                for theme in themes:
                    if isinstance(theme, str):
                        await self.store_concept(
                            project_id=project_id,
                            concept=theme,
                            concept_type="theme",
                            definition=f"Central theme: {theme}"
                        )
                        counts["concepts"] += 1

        logger.info(f"Extracted from world bible: {counts}")
        return counts

    async def extract_and_store_from_characters(
        self,
        project_id: str,
        characters: List[Dict]
    ) -> Dict[str, int]:
        """Extract and store memory from character profiles"""
        counts = {
            "core_facts": 0,
            "knowledge_entries": 0,
            "concepts": 0
        }

        for char in characters:
            name = char.get("name", "")
            if not name:
                continue

            # Store full profile in knowledge vault
            await self.store_knowledge_entry(
                project_id=project_id,
                entry_type="character",
                name=name,
                full_content=json.dumps(char, ensure_ascii=False, indent=2),
                attributes={
                    "role": char.get("role", ""),
                    "archetype": char.get("archetype", "")
                },
                relationships=char.get("relationships", {})
            )
            counts["knowledge_entries"] += 1

            # Extract immutable physical traits as core facts
            physical = char.get("physical", {}) or char.get("profile", {}).get("physical", {})
            if isinstance(physical, dict):
                for trait, value in physical.items():
                    if trait in ["eye_color", "hair_color", "height", "age", "distinguishing_marks"]:
                        await self.store_core_fact(
                            project_id=project_id,
                            fact=f"{name} ma {trait}: {value}",
                            category="character_appearance",
                            entities=[name],
                            source="character_profile",
                            is_absolute=True
                        )
                        counts["core_facts"] += 1

            # Extract archetype as semantic concept
            archetype = char.get("archetype", "")
            if archetype:
                await self.store_concept(
                    project_id=project_id,
                    concept=f"{name} - {archetype}",
                    concept_type="archetype",
                    definition=f"{name} represents the {archetype} archetype",
                    related=[(archetype, "is_instance_of", 1.0)]
                )
                counts["concepts"] += 1

        logger.info(f"Extracted from characters: {counts}")
        return counts

    async def extract_and_store_from_chapter(
        self,
        project_id: str,
        chapter_num: int,
        content: str,
        scenes: List[Dict]
    ) -> Dict[str, int]:
        """Extract and store memory from a completed chapter"""
        counts = {
            "episodes": 0,
            "core_facts": 0
        }

        # Store each scene as an episode
        for i, scene in enumerate(scenes):
            scene_id = f"ch{chapter_num}_scene{i+1}"

            # Extract emotional data using AI
            emotional_data = await self._analyze_scene_emotions(scene.get("content", ""))

            await self.store_episode(
                project_id=project_id,
                scene_id=scene_id,
                chapter=chapter_num,
                summary=scene.get("summary", scene.get("description", "")[:200]),
                characters=scene.get("characters", []),
                location=scene.get("location", ""),
                emotional_data=emotional_data
            )
            counts["episodes"] += 1

        # Extract any new facts from chapter content
        new_facts = await self._extract_facts_from_prose(content)
        for fact in new_facts:
            await self.store_core_fact(
                project_id=project_id,
                fact=fact["text"],
                category=fact["category"],
                entities=fact["entities"],
                source=f"chapter_{chapter_num}",
                is_absolute=fact.get("is_immutable", False)
            )
            counts["core_facts"] += 1

        logger.info(f"Extracted from chapter {chapter_num}: {counts}")
        return counts

    async def _analyze_scene_emotions(self, scene_content: str) -> Dict:
        """Analyze emotional content of a scene using AI"""
        if not scene_content or len(scene_content) < 50:
            return {
                "dominant_emotion": "neutral",
                "valence": "neutral",
                "intensity": 0.5,
                "vector": {},
                "significance": 0.5,
                "is_turning_point": False
            }

        prompt = f"""Przeanalizuj emocjonalną zawartość tej sceny:

{scene_content[:2000]}

Odpowiedz TYLKO w formacie JSON:
{{
    "dominant_emotion": "główna emocja (strach/nadzieja/smutek/radość/gniew/zaskoczenie/napięcie/ulga)",
    "valence": "very_positive/positive/neutral/negative/very_negative/mixed/transformative",
    "intensity": 0.0-1.0,
    "vector": {{"strach": 0.0-1.0, "nadzieja": 0.0-1.0, "smutek": 0.0-1.0, "radość": 0.0-1.0, "gniew": 0.0-1.0, "zaskoczenie": 0.0-1.0, "napięcie": 0.0-1.0, "ulga": 0.0-1.0}},
    "significance": 0.0-1.0,
    "is_turning_point": true/false
}}"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=1,
                max_tokens=500,
                temperature=0.2
            )

            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            logger.error(f"Failed to analyze scene emotions: {e}")

        return {
            "dominant_emotion": "neutral",
            "valence": "neutral",
            "intensity": 0.5,
            "vector": {},
            "significance": 0.5,
            "is_turning_point": False
        }

    async def _extract_facts_from_prose(self, content: str) -> List[Dict]:
        """Extract facts from prose content"""
        if not content or len(content) < 100:
            return []

        prompt = f"""Wyekstrahuj TYLKO NOWE, KONKRETNE fakty z tego tekstu, które należy zapamiętać:

{content[:3000]}

Szukaj:
- Nowych informacji o wyglądzie postaci
- Nowych zasad świata (magia, technologia)
- Nowych relacji między postaciami
- Ważnych wydarzeń z datami

Odpowiedz w JSON:
{{
    "facts": [
        {{"text": "fakt", "category": "character_appearance/world_rule/relationship/event", "entities": ["nazwy"], "is_immutable": true/false}}
    ]
}}

Wyekstrahuj MAX 5 najważniejszych faktów. Jeśli nie ma nowych faktów, zwróć pustą listę."""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=1,
                max_tokens=1000,
                temperature=0.2
            )

            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return data.get("facts", [])
        except Exception as e:
            logger.error(f"Failed to extract facts from prose: {e}")

        return []

    # =========================================================================
    # STATISTICS AND EXPORT
    # =========================================================================

    def get_memory_statistics(self, project_id: str) -> Dict:
        """Get statistics about project memory usage"""
        if project_id not in self.project_memories:
            return {"error": "Project not initialized"}

        stats = {
            "project_id": project_id,
            "layers": {}
        }

        for layer_type, layer in self.project_memories[project_id].items():
            stats["layers"][layer_type.value] = {
                "item_count": len(layer.items),
                "total_accesses": sum(item.access_count for item in layer.items.values())
            }

        stats["total_items"] = sum(
            len(layer.items)
            for layer in self.project_memories[project_id].values()
        )

        # Vector memory stats
        if project_id in self._vector_layers:
            stats["vector_memory"] = self._vector_layers[project_id].get_stats()
        else:
            stats["vector_memory"] = {"initialized": False, "count": 0}

        return stats

    def export_project_memory(self, project_id: str) -> Dict:
        """Export all project memory as JSON"""
        if project_id not in self.project_memories:
            return {"error": "Project not initialized"}

        export = {
            "project_id": project_id,
            "exported_at": datetime.utcnow().isoformat(),
            "layers": {}
        }

        for layer_type, layer in self.project_memories[project_id].items():
            export["layers"][layer_type.value] = [
                item.to_dict() for item in layer.items.values()
            ]

        return export

    async def import_project_memory(self, project_id: str, data: Dict) -> bool:
        """Import project memory from JSON"""
        # TODO: Implement import functionality
        logger.warning("Memory import not yet implemented")
        return False


# =============================================================================
# SINGLETON AND FACTORY
# =============================================================================

_mirix_system: Optional[MIRIXMemorySystem] = None


def get_mirix_system() -> MIRIXMemorySystem:
    """Get or create MIRIX memory system instance"""
    global _mirix_system
    if _mirix_system is None:
        _mirix_system = MIRIXMemorySystem()
    return _mirix_system


async def initialize_mirix_for_project(project_id: str, genre: GenreType) -> MIRIXMemorySystem:
    """Initialize MIRIX system for a specific project"""
    system = get_mirix_system()
    await system.initialize_project(project_id, genre)
    return system

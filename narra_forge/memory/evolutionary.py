"""
Evolutionary Memory: Tracking how worlds and characters change over time.
Stores TRANSFORMATION and GROWTH patterns.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .base import MemorySystem, MemoryEntry


class EvolutionaryMemory:
    """
    Manages evolutionary memory: how things change.
    - Character evolution/arcs
    - World state changes
    - Relationship evolution
    - Learning and adaptation
    """

    def __init__(self, memory_system: MemorySystem):
        self.memory = memory_system

    def track_character_evolution(
        self,
        world_id: str,
        character_id: str,
        evolution_data: Dict[str, Any]
    ) -> str:
        """
        Track a character evolution point.

        Args:
            world_id: World ID
            character_id: Character ID
            evolution_data: Evolution details (what changed, why, impact)

        Returns:
            Evolution entry ID
        """
        evo_id = str(uuid.uuid4())

        entry = MemoryEntry(
            entry_id=f"evo_char_{evo_id}",
            memory_type="evolutionary",
            world_id=world_id,
            content={
                "type": "character_evolution",
                "evolution_id": evo_id,
                "character_id": character_id,
                "timestamp": evolution_data.get("timestamp", datetime.now().isoformat()),
                "trigger_event": evolution_data.get("trigger_event"),
                "changes": evolution_data.get("changes", {}),
                "internal_state_before": evolution_data.get("state_before", {}),
                "internal_state_after": evolution_data.get("state_after", {}),
                "arc_progress": evolution_data.get("arc_progress", 0.0),  # 0.0 to 1.0
                "narrative_significance": evolution_data.get("significance", "medium")
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={
                "arc_type": evolution_data.get("arc_type", "growth")
            }
        )

        self.memory.store(entry)
        return evo_id

    def get_character_evolution_history(
        self,
        world_id: str,
        character_id: str
    ) -> List[Dict[str, Any]]:
        """Get complete evolution history of a character."""
        entries = self.memory.query({
            "world_id": world_id,
            "memory_type": "evolutionary"
        })

        history = []
        for entry in entries:
            if (entry.content.get("type") == "character_evolution" and
                entry.content.get("character_id") == character_id):
                history.append(entry.content)

        # Sort chronologically
        history.sort(key=lambda e: e.get("timestamp", ""))

        return history

    def track_world_state_change(
        self,
        world_id: str,
        change_data: Dict[str, Any]
    ) -> str:
        """
        Track a world state change.

        Args:
            world_id: World ID
            change_data: What changed in the world

        Returns:
            Change entry ID
        """
        change_id = str(uuid.uuid4())

        entry = MemoryEntry(
            entry_id=f"evo_world_{change_id}",
            memory_type="evolutionary",
            world_id=world_id,
            content={
                "type": "world_evolution",
                "change_id": change_id,
                "timestamp": change_data.get("timestamp", datetime.now().isoformat()),
                "trigger": change_data.get("trigger"),
                "affected_systems": change_data.get("affected_systems", []),
                "state_before": change_data.get("state_before", {}),
                "state_after": change_data.get("state_after", {}),
                "scope": change_data.get("scope", "local"),
                "reversibility": change_data.get("reversibility", "irreversible")
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )

        self.memory.store(entry)
        return change_id

    def get_world_evolution_timeline(self, world_id: str) -> List[Dict[str, Any]]:
        """Get chronological timeline of world changes."""
        entries = self.memory.query({
            "world_id": world_id,
            "memory_type": "evolutionary"
        })

        timeline = []
        for entry in entries:
            if entry.content.get("type") == "world_evolution":
                timeline.append(entry.content)

        timeline.sort(key=lambda e: e.get("timestamp", ""))

        return timeline

    def track_relationship_evolution(
        self,
        world_id: str,
        entity_a: str,
        entity_b: str,
        evolution_data: Dict[str, Any]
    ) -> str:
        """
        Track how a relationship evolves.

        Args:
            world_id: World ID
            entity_a: First entity
            entity_b: Second entity
            evolution_data: How relationship changed
        """
        evo_id = str(uuid.uuid4())

        entry = MemoryEntry(
            entry_id=f"evo_rel_{evo_id}",
            memory_type="evolutionary",
            world_id=world_id,
            content={
                "type": "relationship_evolution",
                "evolution_id": evo_id,
                "entity_a": entity_a,
                "entity_b": entity_b,
                "timestamp": evolution_data.get("timestamp", datetime.now().isoformat()),
                "trigger": evolution_data.get("trigger"),
                "strength_before": evolution_data.get("strength_before"),
                "strength_after": evolution_data.get("strength_after"),
                "valence_before": evolution_data.get("valence_before"),
                "valence_after": evolution_data.get("valence_after"),
                "qualitative_change": evolution_data.get("change_description")
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )

        self.memory.store(entry)
        return evo_id

    def get_relationship_evolution(
        self,
        world_id: str,
        entity_a: str,
        entity_b: str
    ) -> List[Dict[str, Any]]:
        """Get evolution history of a relationship."""
        entries = self.memory.query({
            "world_id": world_id,
            "memory_type": "evolutionary"
        })

        history = []
        for entry in entries:
            if entry.content.get("type") == "relationship_evolution":
                if ((entry.content.get("entity_a") == entity_a and
                     entry.content.get("entity_b") == entity_b) or
                    (entry.content.get("entity_a") == entity_b and
                     entry.content.get("entity_b") == entity_a)):
                    history.append(entry.content)

        history.sort(key=lambda e: e.get("timestamp", ""))

        return history

    def track_learning(
        self,
        world_id: str,
        character_id: str,
        learning_data: Dict[str, Any]
    ) -> str:
        """
        Track what a character learns/realizes.

        Args:
            world_id: World ID
            character_id: Character ID
            learning_data: What was learned and how it changes behavior
        """
        learn_id = str(uuid.uuid4())

        entry = MemoryEntry(
            entry_id=f"evo_learn_{learn_id}",
            memory_type="evolutionary",
            world_id=world_id,
            content={
                "type": "learning",
                "learning_id": learn_id,
                "character_id": character_id,
                "timestamp": learning_data.get("timestamp", datetime.now().isoformat()),
                "trigger": learning_data.get("trigger"),
                "knowledge_gained": learning_data.get("knowledge"),
                "cognitive_shift": learning_data.get("cognitive_shift"),
                "behavioral_impact": learning_data.get("behavioral_impact", []),
                "internalization_level": learning_data.get("internalization", 0.5)
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )

        self.memory.store(entry)
        return learn_id

    def get_character_learning_history(
        self,
        world_id: str,
        character_id: str
    ) -> List[Dict[str, Any]]:
        """Get what a character has learned over time."""
        entries = self.memory.query({
            "world_id": world_id,
            "memory_type": "evolutionary"
        })

        learning = []
        for entry in entries:
            if (entry.content.get("type") == "learning" and
                entry.content.get("character_id") == character_id):
                learning.append(entry.content)

        learning.sort(key=lambda e: e.get("timestamp", ""))

        return learning

    def analyze_evolution_patterns(
        self,
        world_id: str,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze evolution patterns for world or specific entity.

        Returns statistical summary of changes.
        """
        entries = self.memory.query({
            "world_id": world_id,
            "memory_type": "evolutionary"
        })

        if entity_id:
            entries = [
                e for e in entries
                if (e.content.get("character_id") == entity_id or
                    e.content.get("entity_a") == entity_id or
                    e.content.get("entity_b") == entity_id)
            ]

        evolution_types = {}
        for entry in entries:
            evo_type = entry.content.get("type", "unknown")
            evolution_types[evo_type] = evolution_types.get(evo_type, 0) + 1

        return {
            "total_evolutions": len(entries),
            "by_type": evolution_types,
            "world_id": world_id,
            "entity_id": entity_id,
            "time_span": {
                "first": min((e.created_at for e in entries), default=None),
                "last": max((e.created_at for e in entries), default=None)
            }
        }

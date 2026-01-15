"""
Structural Memory: Worlds, characters, rules, archetypes.
Stores the STATIC STRUCTURE of narrative universes.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .base import MemorySystem, MemoryEntry
from ..core.types import WorldBible, Character


class StructuralMemory:
    """
    Manages structural memory: the skeleton of narrative worlds.
    - World definitions (WorldBible)
    - Character definitions (Character)
    - Rule systems
    - Archetypes
    """

    def __init__(self, memory_system: MemorySystem):
        self.memory = memory_system

    def store_world(self, world: WorldBible) -> bool:
        """Store complete world definition."""
        entry = MemoryEntry(
            entry_id=f"world_{world.world_id}",
            memory_type="structural",
            world_id=world.world_id,
            content={
                "type": "world",
                "name": world.name,
                "laws_of_reality": world.laws_of_reality,
                "boundaries": world.boundaries,
                "anomalies": world.anomalies,
                "core_conflict": world.core_conflict,
                "existential_theme": world.existential_theme,
                "archetype_system": world.archetype_system,
                "timeline": world.timeline,
                "current_state": world.current_state,
                "related_worlds": world.related_worlds,
                "isolation_level": world.isolation_level
            },
            created_at=world.created_at,
            updated_at=datetime.now(),
            metadata={"version": 1}
        )

        return self.memory.store(entry)

    def retrieve_world(self, world_id: str) -> Optional[WorldBible]:
        """Retrieve world definition."""
        entry = self.memory.retrieve(f"world_{world_id}")

        if not entry or entry.content.get("type") != "world":
            return None

        content = entry.content
        return WorldBible(
            world_id=world_id,
            name=content["name"],
            created_at=entry.created_at,
            laws_of_reality=content["laws_of_reality"],
            boundaries=content["boundaries"],
            anomalies=content["anomalies"],
            core_conflict=content["core_conflict"],
            existential_theme=content["existential_theme"],
            archetype_system=content["archetype_system"],
            timeline=content["timeline"],
            current_state=content["current_state"],
            related_worlds=content.get("related_worlds", []),
            isolation_level=content.get("isolation_level", "isolated")
        )

    def store_character(self, character: Character) -> bool:
        """Store character definition."""
        entry = MemoryEntry(
            entry_id=f"char_{character.character_id}",
            memory_type="structural",
            world_id=character.world_id,
            content={
                "type": "character",
                "name": character.name,
                "internal_trajectory": character.internal_trajectory,
                "contradictions": character.contradictions,
                "cognitive_limits": character.cognitive_limits,
                "evolution_capacity": character.evolution_capacity,
                "motivations": character.motivations,
                "fears": character.fears,
                "blind_spots": character.blind_spots,
                "relationships": character.relationships,
                "current_state": character.current_state,
                "evolution_history": character.evolution_history
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"version": 1}
        )

        return self.memory.store(entry)

    def retrieve_character(self, character_id: str, world_id: str) -> Optional[Character]:
        """Retrieve character definition."""
        entry = self.memory.retrieve(f"char_{character_id}")

        if not entry or entry.content.get("type") != "character":
            return None

        content = entry.content
        return Character(
            character_id=character_id,
            name=content["name"],
            world_id=world_id,
            internal_trajectory=content["internal_trajectory"],
            contradictions=content["contradictions"],
            cognitive_limits=content["cognitive_limits"],
            evolution_capacity=content["evolution_capacity"],
            motivations=content["motivations"],
            fears=content["fears"],
            blind_spots=content["blind_spots"],
            relationships=content["relationships"],
            current_state=content["current_state"],
            evolution_history=content.get("evolution_history", [])
        )

    def get_world_characters(self, world_id: str) -> List[Character]:
        """Get all characters in a world."""
        entries = self.memory.query({
            "world_id": world_id,
            "memory_type": "structural"
        })

        characters = []
        for entry in entries:
            if entry.content.get("type") == "character":
                char_id = entry.entry_id.replace("char_", "")
                char = self.retrieve_character(char_id, world_id)
                if char:
                    characters.append(char)

        return characters

    def store_rule_system(
        self,
        world_id: str,
        rule_name: str,
        rules: Dict[str, Any]
    ) -> bool:
        """Store a rule system for a world."""
        entry = MemoryEntry(
            entry_id=f"rules_{world_id}_{rule_name}",
            memory_type="structural",
            world_id=world_id,
            content={
                "type": "rule_system",
                "name": rule_name,
                "rules": rules
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"category": "rules"}
        )

        return self.memory.store(entry)

    def retrieve_rule_system(
        self,
        world_id: str,
        rule_name: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve rule system."""
        entry = self.memory.retrieve(f"rules_{world_id}_{rule_name}")

        if not entry or entry.content.get("type") != "rule_system":
            return None

        return entry.content["rules"]

    def store_archetype(
        self,
        world_id: str,
        archetype_name: str,
        archetype_data: Dict[str, Any]
    ) -> bool:
        """Store archetype definition."""
        entry = MemoryEntry(
            entry_id=f"arch_{world_id}_{archetype_name}",
            memory_type="structural",
            world_id=world_id,
            content={
                "type": "archetype",
                "name": archetype_name,
                "data": archetype_data
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"category": "archetypes"}
        )

        return self.memory.store(entry)

    def get_world_archetypes(self, world_id: str) -> List[Dict[str, Any]]:
        """Get all archetypes for a world."""
        entries = self.memory.query({
            "world_id": world_id,
            "memory_type": "structural"
        })

        archetypes = []
        for entry in entries:
            if entry.content.get("type") == "archetype":
                archetypes.append({
                    "name": entry.content["name"],
                    "data": entry.content["data"]
                })

        return archetypes

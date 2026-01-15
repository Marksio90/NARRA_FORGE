"""
Semantic Memory: Events, motifs, relationships.
Stores the DYNAMIC CONTENT of narratives.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .base import MemorySystem, MemoryEntry


class SemanticMemory:
    """
    Manages semantic memory: the living content of stories.
    - Events that happened
    - Motifs and themes
    - Relationships between entities
    - Narrative consequences
    """

    def __init__(self, memory_system: MemorySystem):
        self.memory = memory_system

    def store_event(
        self,
        world_id: str,
        event_data: Dict[str, Any]
    ) -> str:
        """
        Store a narrative event.

        Args:
            world_id: World where event occurred
            event_data: Event details (who, what, where, when, why, consequences)

        Returns:
            Event ID
        """
        event_id = str(uuid.uuid4())

        entry = MemoryEntry(
            entry_id=f"event_{event_id}",
            memory_type="semantic",
            world_id=world_id,
            content={
                "type": "event",
                "event_id": event_id,
                "timestamp": event_data.get("timestamp"),
                "location": event_data.get("location"),
                "participants": event_data.get("participants", []),
                "description": event_data.get("description"),
                "consequences": event_data.get("consequences", []),
                "narrative_weight": event_data.get("narrative_weight", 0.5)
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={
                "tags": event_data.get("tags", []),
                "chapter": event_data.get("chapter")
            }
        )

        self.memory.store(entry)
        return event_id

    def retrieve_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific event."""
        entry = self.memory.retrieve(f"event_{event_id}")

        if not entry or entry.content.get("type") != "event":
            return None

        return entry.content

    def get_world_events(
        self,
        world_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all events in a world, chronologically."""
        filters = {
            "world_id": world_id,
            "memory_type": "semantic"
        }

        if limit:
            filters["limit"] = limit

        entries = self.memory.query(filters)

        events = []
        for entry in entries:
            if entry.content.get("type") == "event":
                events.append(entry.content)

        # Sort by timestamp if available
        events.sort(
            key=lambda e: e.get("timestamp", ""),
            reverse=False
        )

        return events

    def store_motif(
        self,
        world_id: str,
        motif_name: str,
        motif_data: Dict[str, Any]
    ) -> bool:
        """
        Store a recurring motif/theme.

        Args:
            world_id: World ID
            motif_name: Motif identifier
            motif_data: Motif details (description, occurrences, significance)
        """
        entry = MemoryEntry(
            entry_id=f"motif_{world_id}_{motif_name}",
            memory_type="semantic",
            world_id=world_id,
            content={
                "type": "motif",
                "name": motif_name,
                "description": motif_data.get("description"),
                "occurrences": motif_data.get("occurrences", []),
                "thematic_significance": motif_data.get("thematic_significance"),
                "evolution": motif_data.get("evolution", [])
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"category": "theme"}
        )

        return self.memory.store(entry)

    def update_motif_occurrence(
        self,
        world_id: str,
        motif_name: str,
        occurrence: str
    ) -> bool:
        """Add new occurrence to motif."""
        entry = self.memory.retrieve(f"motif_{world_id}_{motif_name}")

        if not entry:
            return False

        content = entry.content
        content["occurrences"].append({
            "timestamp": datetime.now().isoformat(),
            "description": occurrence
        })

        return self.memory.update(entry.entry_id, content)

    def store_relationship(
        self,
        world_id: str,
        entity_a: str,
        entity_b: str,
        relationship_data: Dict[str, Any]
    ) -> bool:
        """
        Store relationship between entities (characters, locations, etc.).

        Args:
            world_id: World ID
            entity_a: First entity ID
            entity_b: Second entity ID
            relationship_data: Relationship details (type, strength, history)
        """
        rel_id = f"{entity_a}_{entity_b}"

        entry = MemoryEntry(
            entry_id=f"rel_{world_id}_{rel_id}",
            memory_type="semantic",
            world_id=world_id,
            content={
                "type": "relationship",
                "entity_a": entity_a,
                "entity_b": entity_b,
                "relationship_type": relationship_data.get("type"),
                "strength": relationship_data.get("strength", 0.5),
                "valence": relationship_data.get("valence", 0.0),  # -1 to 1
                "history": relationship_data.get("history", []),
                "current_state": relationship_data.get("current_state")
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"bidirectional": relationship_data.get("bidirectional", True)}
        )

        return self.memory.store(entry)

    def update_relationship(
        self,
        world_id: str,
        entity_a: str,
        entity_b: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """Update existing relationship."""
        rel_id = f"{entity_a}_{entity_b}"
        entry = self.memory.retrieve(f"rel_{world_id}_{rel_id}")

        if not entry:
            return False

        content = entry.content

        # Update fields
        if "strength" in update_data:
            content["strength"] = update_data["strength"]
        if "valence" in update_data:
            content["valence"] = update_data["valence"]
        if "current_state" in update_data:
            content["current_state"] = update_data["current_state"]

        # Add to history
        if "history_entry" in update_data:
            content["history"].append({
                "timestamp": datetime.now().isoformat(),
                "change": update_data["history_entry"]
            })

        return self.memory.update(entry.entry_id, content)

    def get_entity_relationships(
        self,
        world_id: str,
        entity_id: str
    ) -> List[Dict[str, Any]]:
        """Get all relationships involving an entity."""
        entries = self.memory.query({
            "world_id": world_id,
            "memory_type": "semantic"
        })

        relationships = []
        for entry in entries:
            if entry.content.get("type") == "relationship":
                if (entry.content.get("entity_a") == entity_id or
                    entry.content.get("entity_b") == entity_id):
                    relationships.append(entry.content)

        return relationships

    def store_consequence(
        self,
        world_id: str,
        source_event_id: str,
        consequence_data: Dict[str, Any]
    ) -> str:
        """
        Store a narrative consequence.

        Args:
            world_id: World ID
            source_event_id: Event that caused this consequence
            consequence_data: Consequence details
        """
        cons_id = str(uuid.uuid4())

        entry = MemoryEntry(
            entry_id=f"cons_{cons_id}",
            memory_type="semantic",
            world_id=world_id,
            content={
                "type": "consequence",
                "consequence_id": cons_id,
                "source_event": source_event_id,
                "description": consequence_data.get("description"),
                "affected_entities": consequence_data.get("affected_entities", []),
                "scope": consequence_data.get("scope", "local"),  # local, regional, global
                "permanence": consequence_data.get("permanence", "temporary")
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )

        self.memory.store(entry)
        return cons_id

    def get_event_consequences(self, event_id: str) -> List[Dict[str, Any]]:
        """Get all consequences of an event."""
        entries = self.memory.query({"memory_type": "semantic"})

        consequences = []
        for entry in entries:
            if (entry.content.get("type") == "consequence" and
                entry.content.get("source_event") == event_id):
                consequences.append(entry.content)

        return consequences

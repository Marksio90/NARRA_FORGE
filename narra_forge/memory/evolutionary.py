"""
Evolutionary Memory - CHANGE OVER TIME

Stores:
- How worlds evolve
- How characters transform
- How relationships shift
- How themes develop

This is the TEMPORAL layer - the dimension of change.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from narra_forge.core.types import EvolutionEntry
from narra_forge.memory.storage import MemoryStorage


class EvolutionaryMemory:
    """
    Evolutionary memory system.

    Tracks how entities change over time.
    """

    def __init__(self, storage: MemoryStorage):
        """
        Initialize evolutionary memory.

        Args:
            storage: MemoryStorage instance
        """
        self.storage = storage

    async def record_change(
        self,
        entity_id: str,
        entity_type: str,
        change_type: str,
        before_state: Dict[str, Any],
        after_state: Dict[str, Any],
        trigger: Optional[str] = None,
        significance: float = 0.5,
    ) -> EvolutionEntry:
        """
        Record a change in an entity.

        Args:
            entity_id: What changed
            entity_type: "character", "world", "relationship", etc.
            change_type: Type of change
            before_state: State before change
            after_state: State after change
            trigger: What caused the change
            significance: Importance (0.0-1.0)

        Returns:
            EvolutionEntry instance
        """
        entry = EvolutionEntry(
            entry_id=f"evol_{uuid4().hex[:12]}",
            entity_id=entity_id,
            entity_type=entity_type,
            timestamp=datetime.now(),
            change_type=change_type,
            before_state=before_state,
            after_state=after_state,
            trigger=trigger,
            significance=significance,
        )

        # Save to storage
        entry_dict = {
            "entry_id": entry.entry_id,
            "entity_id": entry.entity_id,
            "entity_type": entry.entity_type,
            "change_type": entry.change_type,
            "before_state": entry.before_state,
            "after_state": entry.after_state,
            "trigger": entry.trigger,
            "significance": entry.significance,
        }
        await self.storage.save_evolution_entry(entry_dict)

        return entry

    async def get_history(
        self, entity_id: str, limit: int = 100
    ) -> List[EvolutionEntry]:
        """
        Get evolution history for an entity.

        Args:
            entity_id: Entity ID
            limit: Max number of entries

        Returns:
            List of EvolutionEntry instances
        """
        import json

        entry_dicts = await self.storage.get_evolution_history(entity_id, limit)

        entries = []
        for ed in entry_dicts:
            entry = EvolutionEntry(
                entry_id=ed["entry_id"],
                entity_id=ed["entity_id"],
                entity_type=ed["entity_type"],
                timestamp=datetime.fromisoformat(ed["timestamp"]),
                change_type=ed["change_type"],
                before_state=json.loads(ed["before_state"]),
                after_state=json.loads(ed["after_state"]),
                trigger=ed.get("trigger"),
                significance=ed["significance"],
            )
            entries.append(entry)

        return entries

    async def record_character_evolution(
        self,
        character_id: str,
        change_type: str,
        before: Dict[str, Any],
        after: Dict[str, Any],
        trigger: str,
        significance: float = 0.7,
    ) -> EvolutionEntry:
        """Record character psychological evolution"""
        return await self.record_change(
            entity_id=character_id,
            entity_type="character",
            change_type=change_type,
            before_state=before,
            after_state=after,
            trigger=trigger,
            significance=significance,
        )

    async def record_world_event(
        self,
        world_id: str,
        event_type: str,
        before: Dict[str, Any],
        after: Dict[str, Any],
        trigger: Optional[str] = None,
        significance: float = 0.8,
    ) -> EvolutionEntry:
        """Record world-changing event"""
        return await self.record_change(
            entity_id=world_id,
            entity_type="world",
            change_type=event_type,
            before_state=before,
            after_state=after,
            trigger=trigger,
            significance=significance,
        )

    async def get_character_arc(self, character_id: str) -> List[EvolutionEntry]:
        """Get full character arc (all changes)"""
        return await self.get_history(character_id)

    async def get_world_timeline(self, world_id: str) -> List[EvolutionEntry]:
        """Get world timeline (all major events)"""
        return await self.get_history(world_id)

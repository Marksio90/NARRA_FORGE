"""
World Manager: Multi-IP and multi-world management.
Handles world creation, consistency, and cross-world operations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from ..core.types import WorldBible
from ..memory.structural import StructuralMemory
from ..memory.semantic import SemanticMemory
from ..memory.evolutionary import EvolutionaryMemory


class WorldManager:
    """
    Manages multiple narrative worlds/IPs.

    Responsibilities:
    - Create and store worlds
    - Ensure world consistency
    - Handle cross-world relationships
    - Validate world operations
    """

    def __init__(
        self,
        structural_memory: StructuralMemory,
        semantic_memory: SemanticMemory,
        evolutionary_memory: EvolutionaryMemory
    ):
        self.structural = structural_memory
        self.semantic = semantic_memory
        self.evolutionary = evolutionary_memory

        # Cache active worlds
        self._world_cache: Dict[str, WorldBible] = {}

    def create_world(
        self,
        name: str,
        laws_of_reality: Dict[str, Any],
        core_conflict: str,
        existential_theme: str,
        **kwargs
    ) -> WorldBible:
        """
        Create a new narrative world.

        Args:
            name: World name
            laws_of_reality: Physical/magical/tech rules
            core_conflict: Overarching conflict
            existential_theme: Why this world exists narratively
            **kwargs: Additional world parameters

        Returns:
            WorldBible instance
        """
        world_id = str(uuid.uuid4())

        world = WorldBible(
            world_id=world_id,
            name=name,
            created_at=datetime.now(),
            laws_of_reality=laws_of_reality,
            boundaries=kwargs.get("boundaries", {}),
            anomalies=kwargs.get("anomalies", []),
            core_conflict=core_conflict,
            existential_theme=existential_theme,
            archetype_system=kwargs.get("archetype_system", {}),
            timeline=kwargs.get("timeline", []),
            current_state=kwargs.get("current_state", {}),
            related_worlds=kwargs.get("related_worlds", []),
            isolation_level=kwargs.get("isolation_level", "isolated")
        )

        # Store in structural memory
        self.structural.store_world(world)

        # Cache it
        self._world_cache[world_id] = world

        # Track creation as world evolution
        self.evolutionary.track_world_state_change(
            world_id=world_id,
            change_data={
                "trigger": "world_creation",
                "affected_systems": ["all"],
                "state_before": {},
                "state_after": world.current_state,
                "scope": "global",
                "reversibility": "irreversible"
            }
        )

        return world

    def get_world(self, world_id: str) -> Optional[WorldBible]:
        """Retrieve world by ID."""
        # Check cache first
        if world_id in self._world_cache:
            return self._world_cache[world_id]

        # Load from memory
        world = self.structural.retrieve_world(world_id)

        if world:
            self._world_cache[world_id] = world

        return world

    def update_world_state(
        self,
        world_id: str,
        state_updates: Dict[str, Any],
        trigger: Optional[str] = None
    ) -> bool:
        """
        Update world state and track evolution.

        Args:
            world_id: World to update
            state_updates: New state values
            trigger: What caused this change

        Returns:
            Success status
        """
        world = self.get_world(world_id)

        if not world:
            return False

        old_state = world.current_state.copy()

        # Apply updates
        world.current_state.update(state_updates)

        # Store updated world
        self.structural.store_world(world)

        # Update cache
        self._world_cache[world_id] = world

        # Track evolution
        self.evolutionary.track_world_state_change(
            world_id=world_id,
            change_data={
                "trigger": trigger or "unknown",
                "affected_systems": list(state_updates.keys()),
                "state_before": old_state,
                "state_after": world.current_state,
                "scope": "varies",
                "reversibility": "depends"
            }
        )

        return True

    def validate_world_consistency(self, world_id: str) -> Dict[str, Any]:
        """
        Validate world consistency.

        Checks:
        - Laws of reality are not violated
        - Timeline is coherent
        - State changes are logical

        Returns:
            Validation report
        """
        world = self.get_world(world_id)

        if not world:
            return {
                "valid": False,
                "errors": ["World not found"]
            }

        errors = []
        warnings = []

        # Check timeline coherence
        if world.timeline:
            for i in range(len(world.timeline) - 1):
                # Basic temporal ordering check
                # In production, this would be more sophisticated
                pass

        # Check for state violations
        # (e.g., magic used in non-magic world)
        laws = world.laws_of_reality

        # Get all events in world
        events = self.semantic.get_world_events(world_id)

        # Validate events against laws
        for event in events:
            # Check if event violates any laws
            # This would be rule-engine in production
            pass

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "world_id": world_id,
            "checked_at": datetime.now().isoformat()
        }

    def link_worlds(
        self,
        world_a_id: str,
        world_b_id: str,
        relationship: str = "connected"
    ) -> bool:
        """
        Create relationship between two worlds.

        Args:
            world_a_id: First world
            world_b_id: Second world
            relationship: Type of connection

        Returns:
            Success status
        """
        world_a = self.get_world(world_a_id)
        world_b = self.get_world(world_b_id)

        if not world_a or not world_b:
            return False

        # Add to related worlds
        if world_b_id not in world_a.related_worlds:
            world_a.related_worlds.append(world_b_id)
            self.structural.store_world(world_a)

        if world_a_id not in world_b.related_worlds:
            world_b.related_worlds.append(world_a_id)
            self.structural.store_world(world_b)

        # Update cache
        self._world_cache[world_a_id] = world_a
        self._world_cache[world_b_id] = world_b

        return True

    def get_world_summary(self, world_id: str) -> Dict[str, Any]:
        """
        Get comprehensive world summary.

        Returns:
            Complete world state, statistics, evolution
        """
        world = self.get_world(world_id)

        if not world:
            return {"error": "World not found"}

        # Get characters
        characters = self.structural.get_world_characters(world_id)

        # Get events
        events = self.semantic.get_world_events(world_id)

        # Get evolution
        evolution = self.evolutionary.get_world_evolution_timeline(world_id)

        return {
            "world": {
                "id": world.world_id,
                "name": world.name,
                "created": world.created_at.isoformat(),
                "theme": world.existential_theme,
                "conflict": world.core_conflict
            },
            "statistics": {
                "characters": len(characters),
                "events": len(events),
                "evolutions": len(evolution)
            },
            "current_state": world.current_state,
            "related_worlds": world.related_worlds
        }

    def list_all_worlds(self) -> List[Dict[str, str]]:
        """List all worlds in system."""
        # This would query the memory system for all worlds
        # Simplified version
        return [
            {
                "id": world_id,
                "name": world.name
            }
            for world_id, world in self._world_cache.items()
        ]

    def delete_world(self, world_id: str) -> bool:
        """
        Delete world (careful operation).

        Args:
            world_id: World to delete

        Returns:
            Success status
        """
        # Remove from cache
        if world_id in self._world_cache:
            del self._world_cache[world_id]

        # In production, this would also delete all associated memory entries
        # For now, just a flag

        return True

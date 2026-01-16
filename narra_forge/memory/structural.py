"""
Structural Memory - SKELETON of universes

Stores:
- Worlds (IP-level entities)
- Characters (dynamic processes, not static descriptions)
- Rules, archetypes, constraints

This is the FOUNDATION layer - the unchanging structure.
"""
from typing import List, Optional
from uuid import uuid4

from narra_forge.core.types import Character, World
from narra_forge.memory.storage import MemoryStorage


class StructuralMemory:
    """
    Structural memory system.

    Manages worlds and characters as structured entities.
    """

    def __init__(self, storage: MemoryStorage):
        """
        Initialize structural memory.

        Args:
            storage: MemoryStorage instance
        """
        self.storage = storage

    async def create_world(
        self,
        name: str,
        genre: str,
        reality_laws: dict,
        boundaries: dict,
        core_conflict: str,
        existential_theme: str,
        **kwargs,
    ) -> World:
        """
        Create a new world (IP).

        Args:
            name: World name
            genre: Genre
            reality_laws: Laws governing this world
            boundaries: Spatial/temporal/dimensional boundaries
            core_conflict: Central tension of the world
            existential_theme: Deep philosophical theme
            **kwargs: Additional world properties

        Returns:
            World instance
        """
        from narra_forge.core.types import Genre, RealityLaws, WorldBoundaries

        world = World(
            world_id=f"world_{uuid4().hex[:12]}",
            name=name,
            genre=Genre(genre),
            reality_laws=RealityLaws(**reality_laws),
            boundaries=WorldBoundaries(**boundaries),
            anomalies=kwargs.get("anomalies", []),
            core_conflict=core_conflict,
            existential_theme=existential_theme,
            description=kwargs.get("description"),
            linked_worlds=kwargs.get("linked_worlds", []),
        )

        # Save to storage
        world_dict = {
            "world_id": world.world_id,
            "name": world.name,
            "genre": world.genre.value,
            "reality_laws": world.reality_laws.__dict__,
            "boundaries": world.boundaries.__dict__,
            "anomalies": world.anomalies,
            "core_conflict": world.core_conflict,
            "existential_theme": world.existential_theme,
            "description": world.description,
            "linked_worlds": world.linked_worlds,
        }
        await self.storage.save_world(world_dict)

        return world

    async def get_world(self, world_id: str) -> Optional[World]:
        """Get world by ID"""
        world_dict = await self.storage.get_world(world_id)
        if not world_dict:
            return None

        from narra_forge.core.types import Genre, RealityLaws, WorldBoundaries
        import json

        return World(
            world_id=world_dict["world_id"],
            name=world_dict["name"],
            genre=Genre(world_dict["genre"]),
            reality_laws=RealityLaws(**json.loads(world_dict["reality_laws"])),
            boundaries=WorldBoundaries(**json.loads(world_dict["boundaries"])),
            anomalies=json.loads(world_dict["anomalies"]),
            core_conflict=world_dict["core_conflict"],
            existential_theme=world_dict["existential_theme"],
            description=world_dict.get("description"),
            linked_worlds=json.loads(world_dict.get("linked_worlds", "[]")),
        )

    async def create_character(
        self,
        world_id: str,
        name: str,
        internal_trajectory: dict,
        contradictions: List[str],
        cognitive_limits: List[str],
        evolution_capacity: float,
        **kwargs,
    ) -> Character:
        """
        Create a character as a dynamic process.

        Args:
            world_id: World this character belongs to
            name: Character name
            internal_trajectory: Psychological journey
            contradictions: Internal conflicts
            cognitive_limits: What they can't perceive/understand
            evolution_capacity: How much they can change (0.0-1.0)
            **kwargs: Additional character properties

        Returns:
            Character instance
        """
        from narra_forge.core.types import InternalTrajectory

        character = Character(
            character_id=f"char_{uuid4().hex[:12]}",
            world_id=world_id,
            name=name,
            internal_trajectory=InternalTrajectory(**internal_trajectory),
            contradictions=contradictions,
            cognitive_limits=cognitive_limits,
            evolution_capacity=evolution_capacity,
            archetype=kwargs.get("archetype"),
            role=kwargs.get("role"),
        )

        # Save to storage
        char_dict = {
            "character_id": character.character_id,
            "world_id": character.world_id,
            "name": character.name,
            "internal_trajectory": character.internal_trajectory.__dict__,
            "contradictions": character.contradictions,
            "cognitive_limits": character.cognitive_limits,
            "evolution_capacity": character.evolution_capacity,
            "archetype": character.archetype,
            "role": character.role,
        }
        await self.storage.save_character(char_dict)

        return character

    async def get_characters_in_world(self, world_id: str) -> List[Character]:
        """Get all characters in a world"""
        from narra_forge.core.types import InternalTrajectory
        import json

        char_dicts = await self.storage.get_characters_by_world(world_id)

        characters = []
        for cd in char_dicts:
            character = Character(
                character_id=cd["character_id"],
                world_id=cd["world_id"],
                name=cd["name"],
                internal_trajectory=InternalTrajectory(**json.loads(cd["internal_trajectory"])),
                contradictions=json.loads(cd["contradictions"]),
                cognitive_limits=json.loads(cd["cognitive_limits"]),
                evolution_capacity=cd["evolution_capacity"],
                archetype=cd.get("archetype"),
                role=cd.get("role"),
            )
            characters.append(character)

        return characters

    async def save_world(self, world_dict: dict) -> None:
        """
        Save world directly (for agents that construct their own World objects).

        Args:
            world_dict: World data dictionary
        """
        await self.storage.save_world(world_dict)

    async def save_character(self, char_dict: dict) -> None:
        """
        Save character directly (for agents that construct their own Character objects).

        Args:
            char_dict: Character data dictionary
        """
        await self.storage.save_character(char_dict)

    async def link_worlds(self, world_id_a: str, world_id_b: str) -> None:
        """
        Link two worlds (multi-universe).

        Args:
            world_id_a: First world
            world_id_b: Second world
        """
        # Get both worlds
        world_a = await self.get_world(world_id_a)
        world_b = await self.get_world(world_id_b)

        if not world_a or not world_b:
            raise ValueError("One or both worlds not found")

        # Add links
        if world_id_b not in world_a.linked_worlds:
            world_a.linked_worlds.append(world_id_b)
            await self.storage.save_world(world_a.__dict__)

        if world_id_a not in world_b.linked_worlds:
            world_b.linked_worlds.append(world_id_a)
            await self.storage.save_world(world_b.__dict__)

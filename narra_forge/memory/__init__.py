"""
Triple Memory System for NARRA_FORGE V2

Three-layer architecture:
1. Structural Memory: Worlds, characters, rules (SKELETON)
2. Semantic Memory: Events, motifs, relationships (CONTENT)
3. Evolutionary Memory: How things change over time (TEMPORAL)

Usage:
    from narra_forge.memory import MemorySystem

    memory = MemorySystem(config)
    await memory.initialize()

    # Create world
    world = await memory.structural.create_world(...)

    # Add event
    event = await memory.semantic.add_event(...)

    # Record change
    change = await memory.evolutionary.record_change(...)
"""
from pathlib import Path

from narra_forge.core.config import NarraForgeConfig
from narra_forge.memory.evolutionary import EvolutionaryMemory
from narra_forge.memory.semantic import SemanticMemory
from narra_forge.memory.storage import MemoryStorage
from narra_forge.memory.structural import StructuralMemory


class MemorySystem:
    """
    Unified memory system.

    Combines all three memory types with shared storage.
    """

    def __init__(self, config: NarraForgeConfig):
        """
        Initialize memory system.

        Args:
            config: NarraForgeConfig instance
        """
        self.config = config

        # Shared storage
        self.storage = MemoryStorage(config.db_path)

        # Three memory types
        self.structural = StructuralMemory(self.storage)
        self.semantic = SemanticMemory(self.storage)
        self.evolutionary = EvolutionaryMemory(self.storage)

    async def initialize(self) -> None:
        """Initialize storage (create schemas)"""
        await self.storage.initialize()

    async def save_job(self, job_dict: dict) -> None:
        """Save production job"""
        await self.storage.save_job(job_dict)

    async def get_job(self, job_id: str) -> dict:
        """Get production job"""
        return await self.storage.get_job(job_id)

    async def list_jobs(self, status: str = None, limit: int = 100) -> list:
        """List production jobs"""
        return await self.storage.list_jobs(status, limit)


__all__ = [
    "MemorySystem",
    "MemoryStorage",
    "StructuralMemory",
    "SemanticMemory",
    "EvolutionaryMemory",
]

"""
Core module for NARRA_FORGE V2

Exports:
- NarraForgeConfig: Configuration
- BatchOrchestrator: Main production engine
- Types: All data types
"""
from narra_forge.core.config import NarraForgeConfig, get_config
from narra_forge.core.orchestrator import BatchOrchestrator, create_orchestrator
from narra_forge.core.types import (
    Genre,
    JobStatus,
    NarrativeOutput,
    PipelineStage,
    ProductionBrief,
    ProductionJob,
    ProductionType,
)

__all__ = [
    # Config
    "NarraForgeConfig",
    "get_config",
    # Orchestrator
    "BatchOrchestrator",
    "create_orchestrator",
    # Types
    "ProductionBrief",
    "ProductionType",
    "Genre",
    "ProductionJob",
    "JobStatus",
    "PipelineStage",
    "NarrativeOutput",
]

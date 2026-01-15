"""
NARRA_FORGE - Batch Production Engine for Publishing-Grade Narratives

This is NOT a chatbot. This is NOT a streaming system.
This is a BATCH PRODUCTION ENGINE.

Work mode: input → full analysis → full production → final output

Version: 2.0.0
Provider: OpenAI ONLY
"""

__version__ = "2.0.0"
__author__ = "NARRA_FORGE Team"
__license__ = "MIT"

from narra_forge.core.config import NarraForgeConfig
from narra_forge.core.orchestrator import BatchOrchestrator

__all__ = [
    "NarraForgeConfig",
    "BatchOrchestrator",
    "__version__",
]

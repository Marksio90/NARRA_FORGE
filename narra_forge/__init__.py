"""
NARRA_FORGE - Autonomiczny Wieloświatowy System Generowania Narracji Klasy Absolutnej

Synteza:
- Zaawansowanych modeli generatywnych
- Systemów pamięci długoterminowej
- Orkiestracji wieloagentowej
- Mechanizmów kontroli jakości
- Logiki wydawniczej
- Architektury narracyjnej na skalę uniwersów
"""

__version__ = "3.0.0"
__author__ = "NARRA_FORGE Team"

from narra_forge.core.orchestrator import NarrativeOrchestrator
from narra_forge.core.config import get_default_config, SystemConfig
from narra_forge.core.types import (
    NarrativeForm,
    Genre,
    ProjectBrief,
    WorldBible,
    Character,
    NarrativeSegment,
    GenerationResult
)

__all__ = [
    "NarrativeOrchestrator",
    "get_default_config",
    "SystemConfig",
    "NarrativeForm",
    "Genre",
    "ProjectBrief",
    "WorldBible",
    "Character",
    "NarrativeSegment",
    "GenerationResult"
]

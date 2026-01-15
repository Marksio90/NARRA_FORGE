"""
Etap 10: Agent Przetwarzania Wyjścia
Przygotowuje finalne wyjście gotowe do publikacji i audiobooka.
"""
from typing import Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

from .base_agent import BaseAgent, AgentResponse
from ..core.types import NarrativeSegment, ProjectBrief, WorldBible


class OutputProcessorAgent(BaseAgent):
    """
    Przetwarza finalne wyjście do różnych formatów.

    Tworzy:
    - Plik tekstowy gotowy do publikacji
    - Plik z znacznikami dla audiobooka
    - Metadane projektu
    - Strukturę do dalszej ekspansji
    """

    def get_system_prompt(self) -> str:
        return """Jesteś specjalistą od formatowania publikacyjnego.

ZADANIE:

Przygotuj finalne wyjścia:

1. TEKST PUBLIKACYJNY
   - Właściwe formatowanie
   - Podział na rozdziały
   - Elementy paratekstowe

2. FORMAT AUDIOBOOK
   - Znaczniki dla narratora
   - Wskazówki intonacyjne
   - Podział na pliki

3. METADANE
   - Kompletne informacje o projekcie
   - Statystyki
   - Struktura dla ekspansji

Finalizujesz produkt."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Waliduj dane wejściowe."""
        return (
            "edited_segments" in context and
            "brief" in context and
            "world" in context
        )

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Przetwórz finalne wyjście.

        Args:
            context: Musi zawierać edited_segments, brief, world

        Returns:
            AgentResponse z finalnymi plikami
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Brak wymaganych danych (edited_segments, brief, world)"
            )

        segments: List[NarrativeSegment] = context["edited_segments"]
        brief: ProjectBrief = context["brief"]
        world: WorldBible = context["world"]
        project_id: str = context.get("project_id", "unknown")

        self.log("Przetwarzanie finalnego wyjścia")

        # Utwórz katalog wyjściowy
        output_dir = Path("./output") / project_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Stwórz pełny tekst
        full_text = self._create_full_text(segments, brief, world)
        text_file = output_dir / "narracja.txt"
        text_file.write_text(full_text, encoding="utf-8")

        # 2. Stwórz format audiobook
        audiobook_text = self._create_audiobook_format(segments, brief)
        audiobook_file = output_dir / "narracja_audiobook.txt"
        audiobook_file.write_text(audiobook_text, encoding="utf-8")

        # 3. Stwórz metadane
        metadata = self._create_metadata(
            context, segments, project_id
        )
        metadata_file = output_dir / "metadata.json"
        metadata_file.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        # 4. Stwórz strukturę dla ekspansji
        expansion_data = self._create_expansion_structure(
            world, context
        )
        expansion_file = output_dir / "ekspansja.json"
        expansion_file.write_text(
            json.dumps(expansion_data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        self.log(f"Pliki zapisane w: {output_dir}")

        return AgentResponse(
            success=True,
            output={
                "text_file": str(text_file),
                "audiobook_file": str(audiobook_file),
                "metadata_file": str(metadata_file),
                "expansion_file": str(expansion_file),
                "full_text": full_text
            },
            metadata={
                "output_directory": str(output_dir),
                "total_words": len(full_text.split()),
                "total_characters": len(full_text)
            }
        )

    def _create_full_text(
        self,
        segments: List[NarrativeSegment],
        brief: ProjectBrief,
        world: WorldBible
    ) -> str:
        """Stwórz pełny, sformatowany tekst."""

        parts = []

        # Tytuł i informacje
        parts.append(f"# {world.name}")
        parts.append(f"\n_{brief.genre.value.upper()}_ | _{brief.form.value.upper()}_\n")
        parts.append("=" * 60)
        parts.append("\n\n")

        # Segmenty jako rozdziały
        for i, segment in enumerate(segments, 1):
            parts.append(f"\n\n## Rozdział {i}\n\n")
            parts.append(segment.content)
            parts.append("\n\n---\n")

        return "".join(parts)

    def _create_audiobook_format(
        self,
        segments: List[NarrativeSegment],
        brief: ProjectBrief
    ) -> str:
        """
        Stwórz format z oznaczeniami dla audiobooka.

        Oznaczenia:
        [ROZDZIAŁ X]
        [PAUZA KRÓTKA] / [PAUZA DŁUGA]
        [DIALOG: nazwa_postaci]
        [NARRATOR]
        """

        parts = []

        parts.append("[POCZĄTEK AUDIOBOOKA]\n\n")

        for i, segment in enumerate(segments, 1):
            parts.append(f"[ROZDZIAŁ {i}]\n")
            parts.append(f"[PAUZA DŁUGA]\n\n")

            # Treść z ewentualnymi znacznikami
            # (w pełnej implementacji: detekcja dialogów i oznaczanie)
            parts.append(segment.content)

            parts.append("\n\n[PAUZA DŁUGA]\n")
            parts.append("[KONIEC ROZDZIAŁU]\n\n")

        parts.append("[KONIEC AUDIOBOOKA]")

        return "".join(parts)

    def _create_metadata(
        self,
        context: Dict[str, Any],
        segments: List[NarrativeSegment],
        project_id: str
    ) -> Dict[str, Any]:
        """Stwórz kompletne metadane projektu."""

        brief: ProjectBrief = context["brief"]
        world: WorldBible = context["world"]
        characters = context.get("characters", [])

        # Oblicz statystyki
        total_words = sum(len(s.content.split()) for s in segments)
        total_chars = sum(len(s.content) for s in segments)

        metadata = {
            "project_id": project_id,
            "created_at": datetime.now().isoformat(),
            "form": brief.form.value,
            "genre": brief.genre.value,
            "world": {
                "id": world.world_id,
                "name": world.name,
                "theme": world.existential_theme,
                "conflict": world.core_conflict
            },
            "characters": [
                {
                    "id": c.character_id,
                    "name": c.name,
                    "trajectory": c.internal_trajectory
                }
                for c in characters
            ],
            "statistics": {
                "total_segments": len(segments),
                "total_words": total_words,
                "total_characters": total_chars,
                "avg_segment_words": total_words / len(segments) if segments else 0
            },
            "quality_metrics": {
                "coherence_score": context.get("coherence_report", {}).get("coherence_score", 0.0),
                "validated": all(s.validated for s in segments)
            }
        }

        return metadata

    def _create_expansion_structure(
        self,
        world: WorldBible,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stwórz strukturę dla potencjalnej ekspansji uniwersum.
        """

        characters = context.get("characters", [])

        expansion = {
            "universe_id": world.world_id,
            "universe_name": world.name,
            "expansion_potential": context.get("brief").expansion_potential,
            "world_state": world.current_state,
            "timeline": world.timeline,
            "active_characters": [
                {
                    "id": c.character_id,
                    "name": c.name,
                    "current_state": c.current_state,
                    "evolution_capacity": c.evolution_capacity,
                    "open_arcs": c.internal_trajectory
                }
                for c in characters
            ],
            "potential_storylines": [],  # Do wypełnienia przez użytkownika
            "unexplored_locations": [],  # Lokacje wspomniane ale niezbadane
            "open_questions": []  # Pytania pozostawione bez odpowiedzi
        }

        return expansion

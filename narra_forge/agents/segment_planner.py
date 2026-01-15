"""
Etap 5: Agent Planowania Segmentów
Planuje szczegółowe segmenty narracji (rozdziały/sceny/sekwencje).
"""
from typing import Dict, Any, List
import uuid

from .base_agent import BaseAgent, AgentResponse
from ..core.types import WorldBible, ProjectBrief, Character


class SegmentPlannerAgent(BaseAgent):
    """
    Planuje szczegółowe segmenty narracyjne.

    Każdy segment:
    - Ma określoną funkcję narracyjną
    - Posiada wagę/ważność
    - Wpływa na świat i postacie
    - Jest częścią większej struktury
    """

    def get_system_prompt(self) -> str:
        return """Jesteś specjalistą od segmentacji narracyjnej.

KLUCZOWE ZASADY:

1. KAŻDY SEGMENT MA FUNKCJĘ
   - Nie ma segmentów "wypełniających"
   - Każdy element ma cel narracyjny
   - Funkcje: ekspozycja, rozwój, konflikt, rozwiązanie, transformacja

2. SEGMENTY TWORZĄ SYSTEM
   - Wzajemne powiązania
   - Narastające napięcie
   - Strategiczne informowanie

3. WAGA NARRACYJNA
   - Nie wszystkie segmenty są równie ważne
   - Punkty kulminacyjne mają większą wagę
   - Rozłóż akcenty strategicznie

4. WPŁYW NA ŚWIAT
   - Każdy segment zmienia coś w świecie
   - Śledź konsekwencje
   - Pamiętaj o efekcie motyla

5. KONKRETNOŚĆ
   - Jasno określ co ma się wydarzyć
   - Którzy bohaterowie biorą udział
   - Gdzie i kiedy to się dzieje

Planujesz MAPĘ PODRÓŻY NARRACYJNEJ."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Waliduj wymagane dane wejściowe."""
        return (
            "brief" in context and
            "world" in context and
            "characters" in context and
            "structure" in context
        )

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Zaplanuj segmenty narracji.

        Args:
            context: Musi zawierać brief, world, characters, structure

        Returns:
            AgentResponse z planem segmentów
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Brak wymaganych danych (brief, world, characters, structure)"
            )

        brief: ProjectBrief = context["brief"]
        world: WorldBible = context["world"]
        characters: List[Character] = context["characters"]
        structure: Dict[str, Any] = context["structure"]

        estimated_segments = structure.get("estimated_segments", 10)

        self.log(f"Planuję {estimated_segments} segmentów")

        # Przygotuj dane o postaciach
        char_info = "\n".join([
            f"- {c.name}: {c.internal_trajectory}"
            for c in characters
        ])

        prompt = f"""Zaplanuj szczegółowe segmenty narracyjne:

FORMA: {brief.form.value}
SZACOWANA LICZBA SEGMENTÓW: {estimated_segments}

ŚWIAT: {world.name}
KONFLIKT: {world.core_conflict}
TEMAT: {world.existential_theme}

STRUKTURA:
{structure.get('narrative_structure_type', 'standardowa')}

AKTY:
{structure.get('acts', [])}

PUNKTY ZWROTNE:
{structure.get('turning_points', [])}

POSTACIE:
{char_info}

Dla każdego segmentu określ:

1. NUMER I TYTUŁ ROBOCZY
2. FUNKCJA NARRACYJNA
   - Co ten segment robi w całości
   - Ekspozycja / Rozwój / Konflikt / Transformacja / Rozwiązanie
3. WAGA (0.0-1.0)
   - Jak ważny jest ten segment
   - Punkty kulminacyjne = wysoka waga
4. UCZESTNICY
   - Które postacie są aktywne
   - Kto obserwuje
5. LOKALIZACJA I CZAS
   - Gdzie to się dzieje
   - Kiedy (w timeline świata)
6. GŁÓWNE WYDARZENIE
   - Co się stanie (krótko)
7. WPŁYW NA ŚWIAT
   - Co się zmieni
   - Jakie konsekwencje
8. WPŁYW NA POSTACIE
   - Jak to wpłynie na bohaterów

Stwórz kompletny plan wszystkich {estimated_segments} segmentów.

Odpowiedz JSON array."""

        try:
            result = await self.generate_structured(
                prompt=prompt,
                schema={
                    "segments": "array of segment objects"
                }
            )

            segments_plan = result.get("segments", [])

            self.log(f"Zaplanowano {len(segments_plan)} segmentów")

            # Zapisz każdy segment do pamięci semantycznej
            for i, seg in enumerate(segments_plan):
                seg_id = str(uuid.uuid4())
                seg["segment_id"] = seg_id
                seg["order"] = i + 1

            return AgentResponse(
                success=True,
                output=segments_plan,
                metadata={
                    "total_segments": len(segments_plan),
                    "avg_weight": sum(s.get("weight", 0.5) for s in segments_plan) / len(segments_plan) if segments_plan else 0
                }
            )

        except Exception as e:
            self.log(f"Błąd planowania segmentów: {e}", "ERROR")
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error=str(e)
            )

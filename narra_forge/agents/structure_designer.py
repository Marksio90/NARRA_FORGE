"""
Etap 4: Agent Projektowania Struktury Narracyjnej
Projektuje kompletną strukturę narracyjną dostosowaną do formy i skali.
"""
from typing import Dict, Any
import json

from .base_agent import BaseAgent, AgentResponse
from ..core.types import WorldBible, ProjectBrief, NarrativeForm


class StructureDesignerAgent(BaseAgent):
    """
    Projektuje strukturę narracyjną dla utworu.

    Decyduje o:
    - Strukturze fabularnej (liniowa, nieliniowa, wielowątkowa)
    - Liczbie aktów/części
    - Punktach zwrotnych
    - Tempie narracji
    - Perspektywie narracyjnej
    """

    def get_system_prompt(self) -> str:
        return """Jesteś architektem struktur narracyjnych wysokiego poziomu.

KLUCZOWE ZASADY:

1. STRUKTURA = ARCHITEKTURA
   - Struktura musi wspierać temat
   - Każdy element ma funkcję
   - Forma podąża za treścią

2. DOSTOSUJ DO SKALI:
   - Opowiadanie: kondensacja, pojedynczy łuk
   - Nowela: rozszerzone napięcie, głębszy rozwój
   - Powieść: wielowarstwowość, kompleksowa struktura
   - Saga: architektura wielotomowa, łuki nadrzędne

3. STRUKTURA MUSI ZAWIERAĆ:
   - Punkty zwrotne (turning points)
   - Tempo narracji (pacing)
   - Perspektywę narracyjną
   - Podział na segmenty
   - System napięcia

4. UNIKAJ SCHEMATÓW:
   - Nie kopiuj gotowych struktur
   - Dopasuj do specyfiki świata i postaci
   - Zaskakuj w ramach koherencji

Projektujesz ARCHITEKTURĘ DOŚWIADCZENIA."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Waliduj czy mamy brief i świat."""
        return (
            "brief" in context and
            "world" in context and
            isinstance(context["brief"], ProjectBrief) and
            isinstance(context["world"], WorldBible)
        )

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Zaprojektuj strukturę narracyjną.

        Args:
            context: Musi zawierać "brief", "world", "characters"

        Returns:
            AgentResponse ze strukturą narracyjną
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Brak wymaganych danych w kontekście (brief, world)"
            )

        brief: ProjectBrief = context["brief"]
        world: WorldBible = context["world"]
        characters = context.get("characters", [])

        self.log(f"Projektuję strukturę: {brief.form.value}, {brief.genre.value}")

        # Określ złożoność struktury
        structure_complexity = self._determine_complexity(brief)

        # Zaprojektuj strukturę
        prompt = f"""Zaprojektuj strukturę narracyjną dla tego utworu:

FORMA: {brief.form.value}
GATUNEK: {brief.genre.value}
SKALA ŚWIATA: {brief.world_scale}

ŚWIAT: {world.name}
TEMAT EGZYSTENCJALNY: {world.existential_theme}
KONFLIKT NADRZĘDNY: {world.core_conflict}

POSTACIE: {len(characters)}
TEMATY: {', '.join(brief.thematic_focus) if brief.thematic_focus else 'uniwersalne'}

Zaprojektuj:

1. STRUKTURA FABULARNA
   - Typ: liniowa / nieliniowa / wielowątkowa / rozgałęziona
   - Uzasadnienie wyboru

2. PODZIAŁ NA AKTY/CZĘŚCI
   - Liczba aktów
   - Funkcja każdego aktu
   - Proporcje (ile % narracji)

3. PUNKTY ZWROTNE (Turning Points)
   - Kluczowe punkty zwrotne
   - Gdzie powinny wystąpić
   - Jaki efekt wywołują

4. TEMPO NARRACJI (Pacing)
   - Strategia tempa
   - Gdzie przyspieszyć, gdzie zwolnić
   - Jak budować napięcie

5. PERSPEKTYWA NARRACYJNA
   - Typ narratora (pierwsza/trzecia osoba, wszechwiedzący/ograniczony)
   - Czy zmienia się perspektywa
   - Uzasadnienie

6. SYSTEM NAPIĘCIA
   - Jak budowane jest napięcie
   - Punkty kulminacyjne
   - Strategie rozładowania

7. SEGMENTACJA
   - Przybliżona liczba rozdziałów/scen
   - Logika podziału
   - Funkcja każdego typu segmentu

Odpowiedz szczegółowym JSON."""

        try:
            result = await self.generate_structured(
                prompt=prompt,
                schema={
                    "narrative_structure_type": "string",
                    "acts": "array",
                    "turning_points": "array",
                    "pacing_strategy": "object",
                    "narrative_perspective": "object",
                    "tension_system": "object",
                    "segmentation": "object",
                    "estimated_segments": "integer"
                }
            )

            self.log(f"Struktura zaprojektowana: {result['narrative_structure_type']}")

            return AgentResponse(
                success=True,
                output=result,
                metadata={
                    "complexity": structure_complexity,
                    "estimated_segments": result.get("estimated_segments", 0)
                }
            )

        except Exception as e:
            self.log(f"Błąd projektowania struktury: {e}", "ERROR")
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error=str(e)
            )

    def _determine_complexity(self, brief: ProjectBrief) -> str:
        """Określ złożoność struktury na podstawie brief."""
        if brief.form == NarrativeForm.SHORT_STORY:
            return "simple"
        elif brief.form == NarrativeForm.NOVELLA:
            return "moderate"
        elif brief.form == NarrativeForm.NOVEL:
            return "complex"
        else:  # EPIC_SAGA
            return "highly_complex"

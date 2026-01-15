"""
Etap 7: Agent Walidacji Koherencji
Sprawdza spójność logiczną, psychologiczną i czasową narracji.
"""
from typing import Dict, Any, List

from .base_agent import BaseAgent, AgentResponse
from ..core.types import NarrativeSegment, WorldBible, Character


class CoherenceValidatorAgent(BaseAgent):
    """
    Waliduje koherencję narracji na wszystkich poziomach.

    Sprawdza:
    - Spójność logiczną (prawa świata, przyczynowość)
    - Spójność psychologiczną (postacie działają konsekwentnie)
    - Spójność czasową (timeline się zgadza)
    - Spójność relacji (relacje ewoluują logicznie)
    """

    def get_system_prompt(self) -> str:
        return """Jesteś ekspertem od spójności narracyjnej.

ZADANIE:

Wykrywaj WSZYSTKIE niespójności:

1. LOGICZNE
   - Łamanie praw świata
   - Niemożliwe sytuacje
   - Pęknięcia przyczynowo-skutkowe
   - Magiczne rozwiązania

2. PSYCHOLOGICZNE
   - Postacie działają wbrew charakterowi
   - Nagłe, nieuzasadnione zmiany
   - Brak reakcji na traumy
   - Zapomniane motywacje

3. CZASOWE
   - Błędy w chronologii
   - Niemożliwe odległości/czasy podróży
   - Zapominanie o równoległych wydarzeniach

4. RELACYJNE
   - Zapominanie o relacjach
   - Niespójne reakcje między postaciami
   - Brak ciągłości emocjonalnej

Bądź BEZWZGLĘDNY, ale KONSTRUKTYWNY."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Waliduj dane wejściowe."""
        return (
            "world" in context and
            "characters" in context and
            "segments" in context
        )

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Waliduj koherencję narracji.

        Args:
            context: Musi zawierać world, characters, segments

        Returns:
            AgentResponse z raportem walidacji
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Brak wymaganych danych (world, characters, segments)"
            )

        world: WorldBible = context["world"]
        characters: List[Character] = context["characters"]
        segments: List[NarrativeSegment] = context["segments"]

        self.log(f"Walidacja koherencji {len(segments)} segmentów")

        # Przeprowadź walidację
        validation_report = await self._validate_coherence(
            world, characters, segments
        )

        # Oblicz wynik koherencji
        coherence_score = self._calculate_coherence_score(validation_report)

        self.log(f"Wynik koherencji: {coherence_score:.2f}")

        # Zapisz błędy do walidacji
        if validation_report["errors"]:
            self.log(f"Znaleziono {len(validation_report['errors'])} błędów", "WARNING")

        return AgentResponse(
            success=True,
            output=validation_report,
            metadata={
                "coherence_score": coherence_score,
                "total_errors": len(validation_report.get("errors", [])),
                "total_warnings": len(validation_report.get("warnings", []))
            }
        )

    async def _validate_coherence(
        self,
        world: WorldBible,
        characters: List[Character],
        segments: List[NarrativeSegment]
    ) -> Dict[str, Any]:
        """Przeprowadź kompletną walidację koherencji."""

        # Przygotuj pełny tekst do analizy
        full_narrative = "\n\n---\n\n".join([
            f"[SEGMENT {s.order}]\n{s.content}"
            for s in segments
        ])

        # Przygotuj specyfikację świata
        world_spec = f"""
ŚWIAT: {world.name}

PRAWA RZECZYWISTOŚCI:
{world.laws_of_reality}

GRANICE:
{world.boundaries}

ANOMALIE (dozwolone wyjątki):
{world.anomalies}

KONFLIKT NADRZĘDNY:
{world.core_conflict}
"""

        # Przygotuj specyfikację postaci
        character_spec = "\n\n".join([
            f"""POSTAĆ: {c.name}
Trajektoria: {c.internal_trajectory}
Motywacje: {', '.join(c.motivations)}
Lęki: {', '.join(c.fears)}
Zdolność ewolucji: {c.evolution_capacity}
Sprzeczności: {', '.join(c.contradictions)}
Martwe punkty: {', '.join(c.blind_spots)}
"""
            for c in characters
        ])

        prompt = f"""{world_spec}

{character_spec}

=== NARRACJA DO WALIDACJI ===

{full_narrative}

=== ZADANIE WALIDACJI ===

Przeanalizuj całą narrację i znajdź WSZYSTKIE niespójności:

1. BŁĘDY LOGICZNE
   - Łamanie ustalonych praw świata
   - Niemożliwe fizycznie/magicznie sytuacje
   - Pęknięcia w przyczynowości
   - Deus ex machina

2. BŁĘDY PSYCHOLOGICZNE
   - Postać działa wbrew swoim motywacjom
   - Nieuzasadnione zmiany charakteru
   - Brak reakcji na traumatyczne wydarzenia
   - Zapominanie o wcześniejszych doświadczeniach

3. BŁĘDY CZASOWE
   - Chronologia się nie zgadza
   - Niemożliwe czasy podróży/akcji
   - Zapominanie o równoległych wydarzeniach

4. BŁĘDY RELACYJNE
   - Niespójne relacje między postaciami
   - Zapominanie o wcześniejszych interakcjach

Dla każdego błędu podaj:
- TYP (logical/psychological/temporal/relational)
- SEGMENT (numer)
- OPIS (co jest nie tak)
- POWAGA (critical/major/minor)
- SUGESTIA POPRAWKI

Odpowiedz szczegółowym JSON."""

        try:
            result = await self.generate_structured(
                prompt=prompt,
                schema={
                    "errors": "array",
                    "warnings": "array",
                    "suggestions": "array"
                },
                temperature=0.3  # Niska temperatura dla precyzji
            )

            return result

        except Exception as e:
            self.log(f"Błąd walidacji: {e}", "ERROR")
            return {
                "errors": [],
                "warnings": [],
                "suggestions": [],
                "validation_failed": str(e)
            }

    def _calculate_coherence_score(self, report: Dict[str, Any]) -> float:
        """
        Oblicz wynik koherencji (0.0-1.0).

        Metoda:
        - Start: 1.0
        - Critical error: -0.15
        - Major error: -0.08
        - Minor error: -0.03
        - Warning: -0.01
        """
        score = 1.0

        errors = report.get("errors", [])
        warnings = report.get("warnings", [])

        for error in errors:
            severity = error.get("severity", "minor")
            if severity == "critical":
                score -= 0.15
            elif severity == "major":
                score -= 0.08
            else:  # minor
                score -= 0.03

        for warning in warnings:
            score -= 0.01

        return max(0.0, min(1.0, score))

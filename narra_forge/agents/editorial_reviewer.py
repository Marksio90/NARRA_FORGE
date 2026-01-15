"""
Etap 9: Agent Redakcji Wydawniczej
Finalna redakcja na poziomie wydawniczym.
"""
from typing import Dict, Any, List

from .base_agent import BaseAgent, AgentResponse
from ..core.types import NarrativeSegment, ProjectBrief


class EditorialReviewerAgent(BaseAgent):
    """
    Redakcja wydawnicza tekstu.

    Zadania:
    - Eliminacja zbędności
    - Wzmocnienie napięcia
    - Optymalizacja tempa
    - Finalne cięcia i poprawki
    - Przygotowanie do publikacji
    """

    def get_system_prompt(self) -> str:
        return """Jesteś redaktorem wydawniczym z wieloletnim doświadczeniem.

ZADANIE:

Przygotuj tekst do publikacji:

1. ELIMINACJA ZBĘDNOŚCI
   - Usuń wszystko co nie służy narracji
   - Niepotrzebne opisy
   - Zbędne dygresje
   - Powtórzenia informacji

2. WZMOCNIENIE NAPIĘCIA
   - Identyfikuj momenty słabsze
   - Zaproponuj wzmocnienia
   - Popraw pacing w kluczowych miejscach

3. PŁYNNOŚĆ NARRACJI
   - Przejścia między scenami
   - Ciągłość emocjonalna
   - Rytm całości

4. FINALNE CIĘCIA
   - Bezlitośnie tnij słabsze fragmenty
   - Każde słowo musi być uzasadnione

5. PRZYGOTOWANIE DO DRUKU
   - Spójność formatowania
   - Podział na rozdziały
   - Elementy paratekstowe

Jesteś OSTATNIĄ LINIĄ OBRONY przed publikacją."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Waliduj dane wejściowe."""
        return "stylized_segments" in context and "brief" in context

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Przeprowadź redakcję wydawniczą.

        Args:
            context: Musi zawierać stylized_segments, brief

        Returns:
            AgentResponse z wyredagowanymi segmentami
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Brak wymaganych danych (stylized_segments, brief)"
            )

        segments: List[NarrativeSegment] = context["stylized_segments"]
        brief: ProjectBrief = context["brief"]

        self.log(f"Redakcja wydawnicza {len(segments)} segmentów")

        # Analiza całości
        full_text = "\n\n".join([s.content for s in segments])
        editorial_analysis = await self._analyze_whole_narrative(full_text, brief)

        # Zredaguj każdy segment
        edited_segments = []

        for i, segment in enumerate(segments):
            self.log(f"  Redagowanie segmentu {i+1}/{len(segments)}")

            edited_content = await self._edit_segment(
                segment.content,
                brief,
                i + 1,
                len(segments),
                editorial_analysis
            )

            edited_segment = NarrativeSegment(
                segment_id=segment.segment_id,
                order=segment.order,
                narrative_function=segment.narrative_function,
                narrative_weight=segment.narrative_weight,
                world_impact=segment.world_impact,
                content=edited_content,
                involved_characters=segment.involved_characters,
                location=segment.location,
                timestamp=segment.timestamp,
                generated_at=segment.generated_at,
                validated=True  # Zatwierdzony przez redakcję
            )

            edited_segments.append(edited_segment)

        self.log("Redakcja zakończona")

        return AgentResponse(
            success=True,
            output=edited_segments,
            metadata={
                "total_segments": len(edited_segments),
                "editorial_notes": editorial_analysis
            }
        )

    async def _analyze_whole_narrative(
        self,
        full_text: str,
        brief: ProjectBrief
    ) -> Dict[str, Any]:
        """Przeanalizuj całość narracji przed redakcją."""

        prompt = f"""Przeanalizuj tę narrację z perspektywy redaktora wydawniczego:

FORMA: {brief.form.value}
GATUNEK: {brief.genre.value}
CEL: {brief.length_target} słów

=== PEŁNY TEKST ===

{full_text[:20000]}  # Pierwsze 20k znaków dla analizy

=== ZADANIE ===

Zidentyfikuj:

1. MOCNE STRONY
   - Co działa najlepiej
   - Które fragmenty są najsilniejsze

2. SŁABOŚCI
   - Zbędne fragmenty
   - Rozwlekłe opisy
   - Spadki napięcia

3. PROBLEMY PACING
   - Gdzie tempo spada
   - Gdzie można przyspieszyć
   - Gdzie zwolnić

4. SUGESTIE CIĘĆ
   - Co można bezpiecznie usunąć
   - Co wzmocnić

Odpowiedz JSON."""

        try:
            analysis = await self.generate_structured(
                prompt=prompt,
                schema={
                    "strengths": "array",
                    "weaknesses": "array",
                    "pacing_issues": "array",
                    "cut_suggestions": "array"
                },
                temperature=0.4
            )

            return analysis

        except Exception as e:
            self.log(f"Błąd analizy: {e}", "ERROR")
            return {}

    async def _edit_segment(
        self,
        content: str,
        brief: ProjectBrief,
        segment_num: int,
        total_segments: int,
        editorial_notes: Dict[str, Any]
    ) -> str:
        """Zredaguj pojedynczy segment."""

        prompt = f"""Zredaguj ten segment jako redaktor wydawniczy.

SEGMENT: {segment_num}/{total_segments}
FORMA: {brief.form.value}

NOTATKI REDAKCYJNE:
{editorial_notes}

=== TEKST DO REDAKCJI ===

{content}

=== INSTRUKCJE REDAKCYJNE ===

1. ELIMINUJ:
   - Zbędne słowa i frazy
   - Nadmiar przymiotników/przysłówków
   - Powtórzenia
   - Rozwlekłości

2. WZMACNIAJ:
   - Napięcie gdzie potrzeba
   - Obrazowość
   - Dynamikę

3. POPRAW:
   - Przejścia
   - Rytm
   - Płynność

4. ZACHOWAJ:
   - Wszystkie kluczowe elementy fabularne
   - Głębię postaci
   - Styl autora

Zwróć wyredagowany tekst BEZ komentarzy."""

        try:
            edited = await self.generate_text(
                prompt=prompt,
                temperature=0.6,
                max_tokens=4000
            )

            return edited.strip()

        except Exception as e:
            self.log(f"Błąd redakcji: {e}", "ERROR")
            return content

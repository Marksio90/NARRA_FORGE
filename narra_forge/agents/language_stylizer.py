"""
Etap 8: Agent Stylizacji Językowej
Dopracowuje język do najwyższego poziomu literackiego.
"""
from typing import Dict, Any, List

from .base_agent import BaseAgent, AgentResponse
from ..core.types import NarrativeSegment, ProjectBrief


class LanguageStylerAgent(BaseAgent):
    """
    Dopracowuje język narracji do poziomu publikacyjnego.

    Zadania:
    - Eliminacja banałów i klisz
    - Rytm i melodyka zdań
    - Precyzja słownictwa
    - Spójność stylistyczna
    - Dostosowanie do gatunku i formy
    """

    def get_system_prompt(self) -> str:
        return """Jesteś mistrzem języka polskiego na poziomie najwyższej klasy literatury.

ZADANIE:

Dopracuj tekst do poziomu publikacyjnego:

1. ELIMINACJA SŁABOŚCI
   - Banały i klisze
   - Nadużywane słowa
   - Zbędne przysłówki
   - Pasywne konstrukcje

2. RYTM I MELODYKA
   - Zróżnicowana długość zdań
   - Naturalny przepływ
   - Strategiczne pauzy
   - Akcenty w odpowiednich miejscach

3. PRECYZJA SŁOWNICTWA
   - Najdokładniejsze słowa
   - Unikanie powtórzeń (chyba że celowych)
   - Bogactwo językowe
   - Konkretność

4. SHOW, DON'T TELL
   - Emocje przez działania i szczegóły
   - Unikanie "był smutny", "była zła"
   - Szczegóły zmysłowe

5. DIALOGI
   - Naturalne, charakterystyczne
   - Każda postać ma swój sposób mówienia
   - Podteksty i niewypowiedziane

6. SPÓJNOŚĆ STYLISTYCZNA
   - Jednolity poziom przez cały tekst
   - Dostosowany do gatunku
   - Ton odpowiedni do sceny

NIE ZMIENIAJ TREŚCI - tylko język."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Waliduj dane wejściowe."""
        return "segments" in context and "brief" in context

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Dopracuj język segmentów.

        Args:
            context: Musi zawierać segments, brief

        Returns:
            AgentResponse z dopracowanymi segmentami
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Brak wymaganych danych (segments, brief)"
            )

        segments: List[NarrativeSegment] = context["segments"]
        brief: ProjectBrief = context["brief"]

        self.log(f"Stylizacja językowa {len(segments)} segmentów")

        stylized_segments = []

        for i, segment in enumerate(segments):
            self.log(f"  Stylizuję segment {i+1}/{len(segments)}")

            stylized_content = await self._stylize_segment(
                segment.content,
                brief,
                segment.narrative_function
            )

            # Utwórz nowy segment z dopracowaną treścią
            stylized_segment = NarrativeSegment(
                segment_id=segment.segment_id,
                order=segment.order,
                narrative_function=segment.narrative_function,
                narrative_weight=segment.narrative_weight,
                world_impact=segment.world_impact,
                content=stylized_content,
                involved_characters=segment.involved_characters,
                location=segment.location,
                timestamp=segment.timestamp,
                generated_at=segment.generated_at,
                validated=segment.validated
            )

            stylized_segments.append(stylized_segment)

        self.log("Stylizacja zakończona")

        return AgentResponse(
            success=True,
            output=stylized_segments,
            metadata={
                "total_segments": len(stylized_segments)
            }
        )

    async def _stylize_segment(
        self,
        content: str,
        brief: ProjectBrief,
        narrative_function: str
    ) -> str:
        """Dopracuj język pojedynczego segmentu."""

        style_guidance = self._get_style_guidance(brief)

        prompt = f"""Dopracuj ten fragment do najwyższego poziomu literackiego.

GATUNEK: {brief.genre.value}
FORMA: {brief.form.value}
FUNKCJA SEGMENTU: {narrative_function}

WSKAZÓWKI STYLISTYCZNE:
{style_guidance}

=== TEKST DO DOPRACOWANIA ===

{content}

=== INSTRUKCJE ===

Dopracuj tekst:
- Eliminuj banały, klisze, nadużywane słowa
- Popraw rytm i melodykę zdań
- Zwiększ precyzję słownictwa
- Wzmocnij "show, don't tell"
- Dopracuj dialogi (jeśli są)
- Zachowaj pełną spójność stylistyczną

KRYTYCZNIE WAŻNE:
- NIE ZMIENIAJ TREŚCI ani wydarzeń
- NIE DODAWAJ nowych scen
- TYLKO dopracuj język i styl

Zwróć TYLKO dopracowany tekst, bez komentarzy."""

        try:
            stylized = await self.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=4000
            )

            return stylized.strip()

        except Exception as e:
            self.log(f"Błąd stylizacji: {e}", "ERROR")
            return content  # Zwróć oryginalny w razie błędu

    def _get_style_guidance(self, brief: ProjectBrief) -> str:
        """Uzyskaj wskazówki stylistyczne dla gatunku/formy."""

        guidance = []

        # Wskazówki gatunkowe
        genre_styles = {
            "fantasy": "Bogaty, poetycki język. Szczegółowe opisy światów. Dostojność.",
            "sci_fi": "Precyzyjny, techniczny gdzie trzeba. Wizjonerski. Spekulatywny.",
            "horror": "Atmosferyczny. Szczegóły zmysłowe. Narastające napięcie. Niepokój.",
            "thriller": "Dynamiczny. Krótkie zdania w akcji. Tempo. Napięcie.",
            "mystery": "Precyzyjny. Szczegółowy. Śledzenie tropów. Inteligentny.",
            "literary": "Najwyższy poziom. Wielowarstwowość. Głębia. Subtelność.",
            "historical": "Autentyczny dla epoki. Staranny dobór słów. Immersja.",
            "romance": "Emocjonalny. Subtelny. Intymny. Napięcie uczuciowe."
        }

        genre_style = genre_styles.get(brief.genre.value, "Wysoki poziom literacki")
        guidance.append(f"Styl gatunkowy: {genre_style}")

        # Wskazówki formalne
        if brief.form.value == "short_story":
            guidance.append("Forma: Opowiadanie - każde słowo ma znaczenie. Kondensacja.")
        elif brief.form.value == "novella":
            guidance.append("Forma: Nowela - rozwinięcie, ale wciąż koncentracja.")
        elif brief.form.value == "novel":
            guidance.append("Forma: Powieść - przestrzeń na głębię i wielowarstwowość.")
        else:
            guidance.append("Forma: Saga - epickość, szeroki oddech, wielość płaszczyzn.")

        # Preferencje stylistyczne
        if brief.stylistic_preferences:
            for key, value in brief.stylistic_preferences.items():
                guidance.append(f"{key}: {value}")

        return "\n".join(guidance)

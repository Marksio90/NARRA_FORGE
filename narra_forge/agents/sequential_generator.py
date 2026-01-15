"""
Etap 6: Agent Generacji Sekwencyjnej
Generuje treść narracji segment po segmencie z pełną pamięcią kontekstu.
"""
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentResponse
from ..core.types import NarrativeSegment, WorldBible, Character


class SequentialGeneratorAgent(BaseAgent):
    """
    Generuje treść narracyjną segment po segmencie.

    KLUCZOWE:
    - Generuje z pełną pamięcią poprzednich segmentów
    - Śledzi ewolucję postaci
    - Przestrzega praw świata
    - Buduje napięcie zgodnie z planem
    """

    def get_system_prompt(self) -> str:
        return """Jesteś mistrzem prozy narracyjnej najwyższej klasy.

NAJWAŻNIEJSZE ZASADY:

1. NAJWYŻSZY POZIOM JĘZYKA POLSKIEGO
   - Bogaty, ale naturalny język
   - Precyzja słownictwa
   - Rytm zdań
   - Unikaj banałów i klisz

2. SHOW, DON'T TELL
   - Pokaż emocje przez działania
   - Nie opisuj wprost
   - Szczegóły zmysłowe

3. POSTACIE JAKO PROCESY
   - Postacie myślą, czują, rozwijają się
   - Ich działania wynikają z psychologii
   - Sprzeczności są widoczne
   - Nie są idealne

4. PAMIĘĆ I KONSEKWENCJE
   - Pamiętaj co się wydarzyło
   - Wszystko ma konsekwencje
   - Świat reaguje
   - Postacie uczą się

5. TEMPO I NAPIĘCIE
   - Dostosuj tempo do funkcji segmentu
   - Buduj napięcie strategicznie
   - Używaj pauz i akceleracji

6. SPÓJNOŚĆ ŚWIATA
   - Przestrzegaj praw rzeczywistości
   - Logika przyczynowo-skutkowa
   - Nie łam ustalonych reguł

Tworzysz ŻYWĄ PROZĘ, nie raport o wydarzeniach."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Waliduj dane wejściowe."""
        return (
            "world" in context and
            "characters" in context and
            "segment_plan" in context
        )

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Generuj segmenty narracji sekwencyjnie.

        Args:
            context: Musi zawierać world, characters, segment_plan

        Returns:
            AgentResponse z wygenerowanymi segmentami
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Brak wymaganych danych (world, characters, segment_plan)"
            )

        world: WorldBible = context["world"]
        characters: List[Character] = context["characters"]
        segment_plan: List[Dict[str, Any]] = context["segment_plan"]

        self.log(f"Generuję {len(segment_plan)} segmentów sekwencyjnie")

        generated_segments = []
        narrative_memory = []  # Pamięć dotychczasowej narracji

        # Generuj każdy segment po kolei
        for i, plan in enumerate(segment_plan):
            self.log(f"  Generuję segment {i+1}/{len(segment_plan)}: {plan.get('title', 'Bez tytułu')}")

            # Zbuduj kontekst dla tego segmentu
            segment_context = self._build_segment_context(
                plan, world, characters, narrative_memory
            )

            # Generuj treść
            content = await self._generate_segment_content(
                plan, segment_context, i+1, len(segment_plan)
            )

            if not content:
                self.log(f"Błąd generacji segmentu {i+1}", "ERROR")
                continue

            # Stwórz obiekt segmentu
            segment = NarrativeSegment(
                segment_id=plan.get("segment_id", f"seg_{i}"),
                order=i + 1,
                narrative_function=plan.get("narrative_function", ""),
                narrative_weight=plan.get("weight", 0.5),
                world_impact=plan.get("world_impact", []),
                content=content,
                involved_characters=plan.get("participants", []),
                location=plan.get("location", ""),
                timestamp=plan.get("timestamp"),
                generated_at=datetime.now(),
                validated=False
            )

            generated_segments.append(segment)

            # Dodaj do pamięci narracyjnej (podsumowanie)
            narrative_memory.append({
                "order": i + 1,
                "summary": plan.get("main_event", ""),
                "characters_involved": plan.get("participants", []),
                "consequences": plan.get("world_impact", [])
            })

            # Zapisz wydarzenie do pamięci semantycznej
            self.semantic_memory.store_event(
                world_id=world.world_id,
                event_data={
                    "timestamp": plan.get("timestamp"),
                    "location": plan.get("location"),
                    "participants": plan.get("participants", []),
                    "description": plan.get("main_event"),
                    "consequences": plan.get("world_impact", []),
                    "narrative_weight": plan.get("weight", 0.5),
                    "chapter": i + 1
                }
            )

        self.log(f"Wygenerowano {len(generated_segments)} segmentów")

        return AgentResponse(
            success=True,
            output=generated_segments,
            metadata={
                "total_segments": len(generated_segments),
                "total_words": sum(len(s.content.split()) for s in generated_segments)
            }
        )

    def _build_segment_context(
        self,
        plan: Dict[str, Any],
        world: WorldBible,
        characters: List[Character],
        narrative_memory: List[Dict[str, Any]]
    ) -> str:
        """Zbuduj kontekst dla generacji segmentu."""

        context_parts = [
            f"=== KONTEKST ŚWIATA ===",
            f"Świat: {world.name}",
            f"Temat: {world.existential_theme}",
            f"Konflikt: {world.core_conflict}",
            "",
            f"=== PRAWA RZECZYWISTOŚCI ===",
            str(world.laws_of_reality),
            ""
        ]

        # Dodaj informacje o postaciach uczestniczących
        participants = plan.get("participants", [])
        if participants:
            context_parts.append("=== POSTACIE W TYM SEGMENCIE ===")
            for char in characters:
                if char.name in participants:
                    context_parts.append(f"\n{char.name}:")
                    context_parts.append(f"  Trajektoria: {char.internal_trajectory}")
                    context_parts.append(f"  Motywacje: {', '.join(char.motivations)}")
                    context_parts.append(f"  Lęki: {', '.join(char.fears)}")
                    context_parts.append(f"  Stan aktualny: {char.current_state}")
            context_parts.append("")

        # Dodaj pamięć narracyjną (co już się wydarzyło)
        if narrative_memory:
            context_parts.append("=== CO JUŻ SIĘ WYDARZYŁO ===")
            for mem in narrative_memory[-5:]:  # Ostatnie 5 segmentów
                context_parts.append(f"Segment {mem['order']}: {mem['summary']}")
            context_parts.append("")

        return "\n".join(context_parts)

    async def _generate_segment_content(
        self,
        plan: Dict[str, Any],
        context: str,
        current_num: int,
        total_num: int
    ) -> str:
        """Generuj treść pojedynczego segmentu."""

        prompt = f"""{context}

=== PLAN TEGO SEGMENTU ===
Segment: {current_num}/{total_num}
Tytuł roboczy: {plan.get('title', 'Bez tytułu')}
Funkcja: {plan.get('narrative_function', '')}
Waga: {plan.get('weight', 0.5)}

LOKALIZACJA: {plan.get('location', 'nieokreślona')}
CZAS: {plan.get('timestamp', 'nieokreślony')}

GŁÓWNE WYDARZENIE:
{plan.get('main_event', '')}

WPŁYW NA ŚWIAT:
{plan.get('world_impact', [])}

WPŁYW NA POSTACIE:
{plan.get('character_impact', [])}

=== TWOJE ZADANIE ===

Napisz ten segment jako profesjonalną prozę narracyjną.

DŁUGOŚĆ:
- Jeśli waga niska (< 0.4): 400-800 słów
- Jeśli waga średnia (0.4-0.7): 800-1500 słów
- Jeśli waga wysoka (> 0.7): 1500-3000 słów

STYL:
- Najwyższy poziom języka polskiego
- Naturalne dialogi (jeśli są)
- Szczegóły zmysłowe
- Show, don't tell
- Rytm dopasowany do tempa

PAMIĘTAJ:
- Przestrzegaj praw świata
- Postacie działają zgodnie z psychologią
- Wszystko ma konsekwencje
- Buduj napięcie

Napisz TYLKO treść segmentu, bez żadnych meta-komentarzy."""

        try:
            content = await self.generate_text(
                prompt=prompt,
                max_tokens=4000,
                temperature=0.85  # Wyższa temperatura dla kreatywności
            )

            return content.strip()

        except Exception as e:
            self.log(f"Błąd generacji treści: {e}", "ERROR")
            return ""

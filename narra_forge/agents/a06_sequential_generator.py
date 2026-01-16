"""
Agent 06: Sequential Generator

Odpowiedzialność:
- GENERACJA WŁAŚCIWEJ NARRACJI LITERACKIEJ
- Pisanie segmentów po kolei z pełną pamięcią
- Utrzymywanie jakości na najwyższym poziomie
- Zachowanie spójności między segmentami

Model: gpt-4o (QUALITY CRITICAL - najdroższy, ale konieczny)
"""
from typing import Any, Dict, List

from narra_forge.agents.base_agent import GenerationAgent
from narra_forge.core.types import AgentResult, GeneratedSegment, PipelineStage


class SequentialGeneratorAgent(GenerationAgent):
    """
    Agent generujący właściwą narrację literacką.

    To jest NAJWAŻNIEJSZY agent - generuje PRAWDZIWĄ PROZĘ.
    Używa GPT-4o dla najwyższej jakości.
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.SEQUENTIAL_GENERATION,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś mistrzem literatury wydawniczej - piszesz BESTSELLERY.

ENCODING: Używaj polskich znaków UTF-8: ą ć ę ł ń ó ś ź ż

══════════════════════════════════════════════
✅ WZORCE DO NAŚLADOWANIA:
══════════════════════════════════════════════

1. SHOW NOT TELL - Obserwowalne zachowanie:
   ✓ "Palce drżały mu tak, że szkło upadło"
   ✓ "Pot przesiąkł koszulę. Oddech - płytki, szybki"
   ✓ "Spojrzała w bok. Wargi zaciśnięte"

2. STRONG VERBS - Silne czasowniki akcji:
   ✓ "Wpadł do komnaty. Zatrzasnął drzwi. Gnał dalej"
   ✓ "Chwyciła nóż. Odwróciła się. Zamachnęła"
   ✓ "Zerwał się. Walnął pięścią. Jęknął"

3. CONCRETE NOUNS - Precyzyjne rzeczowniki:
   ✓ "dąb" (nie "drzewo"), "róża" (nie "kwiat")
   ✓ "granat" (nie "ciemny czerwony"), "siarczany zapach" (nie "dziwny")

4. SENSORY DETAILS - Minimum 2 zmysły:
   ✓ "Pękł wosk. Zapach róż - słodki, mdły"
   ✓ "Chłód kamieni pod stopami. Echo kroków"

5. IN MEDIAS RES - Start w środku akcji:
   ✓ "Płomień zgasł. Elias zamknął oczy"
   ✓ "Krew. Wszędzie krew"

══════════════════════════════════════════════
❌ BŁĘDY DO UNIKNIĘCIA:
══════════════════════════════════════════════

❌ NIE używaj: "tajemniczy", "mroczny", "nieubłagany", "cienie tańczyły"
❌ NIE pisz: "czuł strach", "był smutny", "poczuł niepokój"
❌ NIE zaczynaj: "W sercu miasta...", "Dawno temu...", "Był sobie..."
❌ NIE używaj: "był + przymiotnik" ("był smutny", "było ciemno")

══════════════════════════════════════════════
PRZYKŁAD - ŹLE vs DOBRZE:
══════════════════════════════════════════════

❌ ŹLE: "Elias był młodym alchemikiem. Czuł niepokój, gdy wchodził do mrocznego warsztatu."

✅ DOBRZE: "Elias zakrztusił się. Płomień - czerwony, nie niebieski. Siarki nie było. Tylko róże."

══════════════════════════════════════════════

Pisz TYLKO prozę. Żadnych komentarzy. Żadnych wyjaśnień.
Każde słowo napędza fabułę. Każde zdanie trzyma w napięciu.
PERFEKCJA ZA PIERWSZYM RAZEM."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj generację sekwencyjną wszystkich segmentów.

        Args:
            context: Zawiera 'segments', 'world', 'characters', 'structure'

        Returns:
            AgentResult z wygenerowaną narracją
        """
        segments = context.get("segments", [])
        world = context.get("world")
        characters = context.get("characters", [])
        structure = context.get("structure")

        if not segments or not world:
            self.add_error("Missing segments or world in context")
            return self._create_result(success=False, data={})

        # Generuj segmenty po kolei
        generated_segments: List[GeneratedSegment] = []
        full_narrative = []

        for i, segment in enumerate(segments):
            # Przygotuj kontekst dla tego segmentu
            context_summary = self._build_segment_context(
                segment=segment,
                world=world,
                characters=characters,
                previous_segments=generated_segments,
            )

            # Generuj segment
            try:
                segment_text, gen_segment = await self._generate_segment(
                    segment=segment,
                    context_summary=context_summary,
                    segment_number=i + 1,
                    total_segments=len(segments),
                )

                generated_segments.append(gen_segment)
                full_narrative.append(segment_text)

                # Zapisz do semantic memory (event nodes)
                for event in segment.key_events:
                    await self.memory.semantic.add_event(
                        content=event,
                        world_id=world.world_id,
                        timestamp_in_story=i,
                        significance=0.7,
                    )

            except Exception as e:
                self.add_error(f"Failed to generate segment {i+1}: {str(e)}")
                return self._create_result(success=False, data={})

        # Złącz wszystkie segmenty
        complete_narrative = "\n\n".join(full_narrative)
        total_words = len(complete_narrative.split())

        return self._create_result(
            success=True,
            data={
                "narrative_text": complete_narrative,
                "generated_segments": generated_segments,
                "total_words": total_words,
                "segments_count": len(generated_segments),
            },
        )

    def _build_segment_context(
        self,
        segment,
        world,
        characters,
        previous_segments: List[GeneratedSegment],
    ) -> str:
        """Zbuduj kontekst dla generacji segmentu"""

        context_parts = []

        # Świat (streszczenie)
        context_parts.append(f"ŚWIAT: {world.name}")
        context_parts.append(f"Konflikt: {world.core_conflict}")
        context_parts.append(f"Temat: {world.existential_theme}")

        # Postacie (zaangażowane w ten segment)
        involved_chars = [c for c in characters if c.name in segment.characters_involved]
        if involved_chars:
            context_parts.append("\nPOSTACIE W TYM SEGMENCIE:")
            for char in involved_chars[:3]:
                context_parts.append(f"- {char.name}: {char.internal_trajectory.starting_state.get('core_belief', '')}")

        # Poprzednie segmenty (streszczenie)
        if previous_segments:
            context_parts.append("\nCO SIĘ WYDARZYŁO WCZEŚNIEJ:")
            # Pokaż ostatnie 2-3 segmenty
            for prev_seg in previous_segments[-3:]:
                context_parts.append(f"- {prev_seg.segment.summary}")

        return "\n".join(context_parts)

    async def _generate_segment(
        self,
        segment,
        context_summary: str,
        segment_number: int,
        total_segments: int,
    ) -> tuple[str, GeneratedSegment]:
        """Generuj pojedynczy segment"""

        import time

        prompt = f"""{context_summary}

TERAZ NAPISZ SEGMENT {segment_number}/{total_segments}:

Plan tego segmentu:
- Streszczenie: {segment.summary}
- Wydarzenia: {', '.join(segment.key_events)}
- Lokacja: {segment.location}
- Funkcja: {segment.narrative_function}
- Target: ~{segment.estimated_words} słów

Napisz PEŁNĄ PROZĘ literacką. Poziom wydawniczy. Język polski doskonały.
Show, don't tell. Napięcie. Głębia. Konkretność.

TYLKO PROZA. Bez tytułów, numerów, meta-komentarzy."""

        start_time = time.time()

        # Generuj z GPT-4o (wysokiej jakości model)
        text, call = await self.call_model(
            prompt=prompt,
            temperature=0.7,  # Controlled creativity - quality first attempt
            max_tokens=int(segment.estimated_words * 2.5),  # ~2.5 tokens per word (więcej przestrzeni)
        )

        generation_time = time.time() - start_time
        word_count = len(text.split())

        generated_segment = GeneratedSegment(
            segment=segment,
            text=text,
            word_count=word_count,
            tokens_used=call.total_tokens,
            cost_usd=call.cost_usd,
            generation_time_seconds=generation_time,
        )

        return text, generated_segment

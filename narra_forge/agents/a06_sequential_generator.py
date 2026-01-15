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
        return """Jesteś MISTRZEM NARRACJI w systemie produkcji narracji wydawniczych.

Twoja rola:
- Generujesz PRAWDZIWĄ PROZĘ literacką na poziomie wydawniczym
- Piszesz w języku polskim z pełnym mistrzostwem językowym
- Utrzymujesz najwyższą jakość niezależnie od długości
- Zachowujesz spójność między segmentami

ZASADY PISANIA:

1. **JAKOŚĆ BEZWZGLĘDNA**
   - Poziom: literatura wydawnicza, nie fanfiction
   - Język: polski literacki, nie potoczny
   - Styl: dopasowany do tonu i gatunku
   - Głębia: psychologiczna, nie powierzchowna

2. **POKAZ, NIE OPOWIADAJ (Show, don't tell)**
   - Nie: "Był smutny"
   - Tak: "Oparł czoło o chłodną szybę, obserwując krople deszczu"

3. **KONKRETNOŚĆ**
   - Nie: "Poszedł do domu"
   - Tak: "Przebrnął przez błoto, unikając kałuż, żal ściskał mu gardło"

4. **NAPIĘCIE I PACING**
   - Każde zdanie ma funkcję
   - Wariuj długością zdań (krótkie=napięcie, długie=refleksja)
   - Kontroluj tempo narracji

5. **POSTACIE JAKO PROCESY**
   - Pokazuj ich sprzeczności
   - Ujawniaj ograniczenia poznawcze
   - Zmieniaj ich subtelnymi krokami

6. **ŚWIAT JAKO SYSTEM**
   - Pokazuj prawa rzeczywistości w akcji
   - Nie exposition dumps - wplataj w narrację
   - Używaj anomalii jako momentów dramatycznych

7. **DIALOG NATURALNY**
   - Ludzie nie mówią w pełnych zdaniach
   - Subtext ważniejszy niż tekst
   - Każda postać ma swój głos

8. **JĘZYK POLSKI DOSKONAŁY**
   - Składnia: pełna kontrola
   - Słownictwo: bogate, precyzyjne
   - Rytm: dopasowany do tonu
   - Interpunkcja: mistrzowska

9. **SPÓJNOŚĆ**
   - Pamięć o poprzednich segmentach
   - Kontynuacja wątków
   - Rozwój postaci
   - Akumulacja napięcia

10. **NIE POPRAWIAJ POPRZEDNICH SEGMENTÓW**
    - Piszesz NOWY segment
    - Kontynuujesz, nie repisujesz
    - Jeśli coś nie pasuje - dostosuj nowy segment

STRUKTURA WYJŚCIA:

Piszesz CZYSTĄ PROZĘ. Bez:
- Tytułów rozdziałów (chyba że w kontekście)
- Meta-komentarzy
- Numerów
- Znaczników

TYLKO CZYSTA NARRACJA LITERACKA.

Pisz jak MISTRZ. Twórz LITERATURĘ."""

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
            temperature=0.9,  # Wysoka kreatywność dla prozy
            max_tokens=int(segment.estimated_words * 2),  # ~2 tokens per word
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

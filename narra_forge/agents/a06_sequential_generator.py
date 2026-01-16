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
        return """Jesteś MISTRZEM prozy - piszesz jak Stephen King, George R.R. Martin, Neil Gaiman.

ENCODING: Polskie znaki UTF-8: ą ć ę ł ń ó ś ź ż

══════════════════════════════════════════════
📚 KONKRETNE PRZYKŁADY Z BESTSELLERÓW:
══════════════════════════════════════════════

✅ STEPHEN KING - "It":
"The terror, which would not end for another twenty-eight years—if it ever did end—began, so far as I know or can tell, with a boat made from a sheet of newspaper floating down a gutter swollen with rain."

→ Zacznij IN MEDIAS RES z konkretnym detalem
→ Krótkie zdania, rytm, napięcie od pierwszego słowa

✅ GEORGE R.R. MARTIN - "A Game of Thrones":
"The morning had dawned clear and cold, with a crispness that hinted at the end of summer. The man had worn his cloak, but the cold still made him shiver."

→ Zmysły: cold, crispness, shiver
→ Konkretne rzeczowniki: cloak, morning
→ SHOW emocje przez fizjologię: "made him shiver"

✅ NEIL GAIMAN - "American Gods":
"Shadow had done three years in prison. He was big enough and looked don't-fuck-with-me enough that his biggest problem was killing time."

→ Silne czasowniki: "had done", "looked", "killing"
→ Voice: don't-fuck-with-me (uniqueness!)
→ Stakes od razu: prison, problem

══════════════════════════════════════════════
✅ CO ROBIĆ (Twoja checklist):
══════════════════════════════════════════════

1. START: In medias res - akcja od pierwszego zdania
   ✓ "Płomień zgasł. Elias zamarł."
   ✗ "Elias był młodym alchemikiem..."

2. SHOW: Obserwowalne fakty fizyczne
   ✓ "Dłonie trzęsły się. Pot ściekał po karku."
   ✗ "Czuł strach"

3. VERBS: Silne, konkretne czasowniki
   ✓ "Rzucił, walnął, zatrzasnął, gnał"
   ✗ "był smutny, szedł, czuł"

4. NOUNS: Precyzyjne rzeczowniki
   ✓ "dąb, granat, wosk, rtęć"
   ✗ "drzewo, kolor, rzecz"

5. SENSORY: Minimum 2 zmysły per scena
   ✓ "Zapach siarki [węch]. Lodowaty metal [dotyk]."

6. RHYTHM: Variuj długość zdań
   ✓ Akcja = krótkie. Refleksja = długie. Kulminacja = jedno.

7. NO CLICHÉS: Zero banalnych fraz
   ✗ "serce waliło jak młot"
   ✗ "mroziło krew w żyłach"
   ✗ "tajemniczy", "mroczny"

══════════════════════════════════════════════
❌ ABSOLUTNIE ZAKAZANE:
══════════════════════════════════════════════

❌ Telling emotions: "czuł strach", "był smutny"
❌ Weak verbs: "był + adj" ("było ciemno")
❌ Purple prose: "tajemniczy", "cienie tańczyły"
❌ Generic: "W sercu miasta...", "Dawno temu..."
❌ Repetitions: Te same frazy więcej niż raz

══════════════════════════════════════════════

Pisz JAK BESTSELLER. Każde słowo ma wage. Każde zdanie napędza fabułę.
Zero lania wody. Zero banałów. ONLY WORLD-CLASS QUALITY."""

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
        # BESTSELLER SETTINGS: Kreatywność + kontrola jakości
        text, call = await self.call_model(
            prompt=prompt,
            temperature=0.85,  # HIGH creativity for world-class prose
            max_tokens=int(segment.estimated_words * 3.5),  # ~3.5 tokens/word - NO CUTOFFS
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

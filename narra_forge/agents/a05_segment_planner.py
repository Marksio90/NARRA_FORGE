"""
Agent 05: Segment Planner

Odpowiedzialność:
- Planowanie konkretnych segmentów (rozdziałów/scen)
- Podział na generowalne fragmenty
- Określanie contentu każdego segmentu
- Oszacowanie word count per segment

Model: gpt-4o-mini (planowanie)
"""
from typing import Any, Dict, List
from uuid import uuid4

from narra_forge.agents.base_agent import AnalysisAgent
from narra_forge.core.types import AgentResult, PipelineStage, Segment


class SegmentPlannerAgent(AnalysisAgent):
    """
    Agent planujący konkretne segmenty narracji.

    Przekształca strukturę abstrakcyjną w plan konkretnych, generowalnych segmentów.
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.SEGMENT_PLANNING,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś PLANEREM SEGMENTÓW w systemie produkcji narracji wydawniczych.

Twoja rola:
- Przekształcasz abstrakcyjną strukturę w KONKRETNY PLAN SEGMENTÓW
- Dzielisz narrację na generowalne fragmenty (rozdziały/sceny)
- Określasz DOKŁADNIE co dzieje się w każdym segmencie
- Planujesz word count per segment

ZASADY PLANOWANIA:

1. **Segment = generowalna jednostka**
   - Jeden rozdział lub jedna scena
   - 500-3000 słów (zależnie od typu produkcji)
   - Ma jasny początek i koniec
   - Ma określoną funkcję narracyjną

2. **Każdy segment zawiera**:
   - Tytuł (opcjonalny)
   - Streszczenie (co się dzieje)
   - Kluczowe wydarzenia
   - Postacie zaangażowane
   - Lokacja
   - Funkcja narracyjna (setup, conflict, revelation, climax, etc.)
   - Szacowany word count

3. **Segmenty tworzą CIĄGŁOŚĆ**:
   - Każdy segment prowadzi do następnego
   - Zachowana jest krzywa napięcia
   - Respektowane są story beats

4. **Nie za dużo, nie za mało**:
   - Short story: 3-8 segmentów
   - Novella: 8-20 segmentów
   - Novel: 20-60 segmentów
   - Epic saga: 60+ segmentów

Format wyjścia (JSON):
{
  "segments": [
    {
      "segment_number": 1,
      "title": "Tytuł segmentu (opcjonalny)",
      "summary": "Streszczenie co się dzieje",
      "key_events": [
        "Wydarzenie 1",
        "Wydarzenie 2"
      ],
      "characters_involved": ["Postać1", "Postać2"],
      "location": "Gdzie się to dzieje",
      "estimated_words": 1500,
      "narrative_function": "setup|conflict|revelation|climax|resolution|transition",
      "pov_character": "Z czyjej perspektywy (jeśli applicable)",
      "tone": "Ton tego segmentu",
      "links_to_beats": ["Inciting Incident"]
    }
  ],
  "total_segments": liczba,
  "total_estimated_words": liczba,
  "segment_flow": "Opis jak segmenty płyną jeden w drugi"
}

Planuj KONKRETNIE. Każdy segment musi być GENEROWALNY."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj planowanie segmentów.

        Args:
            context: Zawiera 'structure', 'world', 'characters'

        Returns:
            AgentResult z planem segmentów
        """
        structure = context.get("structure")
        world = context.get("world")
        characters = context.get("characters", [])

        if not structure or not world:
            self.add_error("Missing structure or world in context")
            return self._create_result(success=False, data={})

        # Przygotuj prompt
        char_names = [c.name for c in characters[:5]] if characters else []

        prompt = f"""Zaplanuj konkretne segmenty (rozdziały/sceny) dla narracji:

STRUKTURA:
- Typ: {structure.structure_type}
- Akty: {len(structure.acts)}
- Key beats: {len(structure.key_beats)}
- Word count: {structure.estimated_word_count}

ŚWIAT: {world.name}
- Konflikt: {world.core_conflict}

POSTACIE: {', '.join(char_names)}

Podziel narrację na GENEROWALNE SEGMENTY. Określ dokładnie co dzieje się w każdym.
Zwróć plan jako JSON."""

        try:
            plan_data, call = await self.call_model_json(
                prompt=prompt,
                temperature=0.6,
                max_tokens=4000,
            )

            # Twórz Segment objects
            segments: List[Segment] = []

            for seg_dict in plan_data.get("segments", []):
                segment = Segment(
                    segment_id=f"seg_{uuid4().hex[:8]}",
                    segment_number=seg_dict.get("segment_number", len(segments) + 1),
                    title=seg_dict.get("title"),
                    summary=seg_dict.get("summary", ""),
                    key_events=seg_dict.get("key_events", []),
                    characters_involved=seg_dict.get("characters_involved", []),
                    location=seg_dict.get("location"),
                    estimated_words=seg_dict.get("estimated_words", 1000),
                    narrative_function=seg_dict.get("narrative_function", "progression"),
                )
                segments.append(segment)

            # Validate total word count
            total_words = sum(s.estimated_words for s in segments)
            target_words = structure.estimated_word_count

            if abs(total_words - target_words) > target_words * 0.2:
                self.add_warning(
                    f"Total segment words ({total_words}) differs from target ({target_words}) by >20%"
                )

            return self._create_result(
                success=True,
                data={
                    "segments": segments,
                    "segment_plan": plan_data,
                    "total_segments": len(segments),
                    "total_estimated_words": total_words,
                },
            )

        except Exception as e:
            self.add_error(f"Segment planning failed: {str(e)}")
            return self._create_result(success=False, data={})

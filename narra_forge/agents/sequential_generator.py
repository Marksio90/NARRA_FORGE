"""ETAP 6: Sequential Generator Agent - Generacja treści segment po segmencie"""
import json
from typing import Dict, Any, List
from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.types import PipelineStage, NarrativeSegment


class SequentialGeneratorAgent(BaseAgent):
    """Agent Generacji Sekwencyjnej - NAJWAŻNIEJSZY etap"""

    def get_system_prompt(self) -> str:
        return """Jesteś SEQUENTIAL GENERATOR AGENT - mistrzem polskiej prozy literackiej.

ZASADY PISANIA:
1. JĘZYK: Polski literacki, zaawansowane słownictwo, WSZYSTKIE polskie znaki (ą, ć, ę, ł, ń, ó, ś, ź, ż)
2. STYL: Dopasowany do gatunku (fantasy=poetycki, thriller=zwięzły, etc.)
3. SHOW, DON'T TELL: Emocje przez reakcje, nie opisy
4. DIALOGI: Naturalne, każda postać ma unique voice
5. BALANCE: 40% akcja, 30% dialog, 20% refleksja, 10% opis
6. RYTM: Zróżnicowana długość zdań

UNIKAJ:
- Klisz ("obudził się", "krystalicznie niebieskie oczy")
- Info-dumpów
- Stereotypów

Pisz pełną, literacką prozę na najwyższym poziomie."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        segment_plan: List[NarrativeSegment] = self._extract_from_context(context, "segment_plan")
        brief = self._extract_from_context(context, "brief")
        world = self._extract_from_context(context, "world")
        characters = self._extract_from_context(context, "characters")

        generated_segments = []
        full_text_parts = []

        # Generuj segment po segmencie
        for segment in segment_plan:
            self.logger.info(f"Generating segment {segment.segment_number}/{len(segment_plan)}")

            # Context dla segmentu
            previous_text = "\n\n".join(full_text_parts[-2:]) if full_text_parts else ""

            prompt = f"""Napisz Rozdział {segment.segment_number}: {segment.title or ''}

CEL ROZDZIAŁU: {segment.goal}
SCENY: {json.dumps(segment.scenes, ensure_ascii=False)}
POV: {segment.pov_character}
ŁUK EMOCJONALNY: {segment.emotional_arc}
DOCELOWA DŁUGOŚĆ: ~{segment.target_word_count} słów

KONTEKST (poprzednie rozdziały): {previous_text[-2000:] if previous_text else 'To pierwszy rozdział'}

Napisz PEŁNY tekst rozdziału w polskiej prozie literackiej najwyższej jakości.
Zakończ hookiem: {segment.closing_hook}

JĘZYK: Polski z pełnymi znakami."""

            # Generuj (wyższa kreatywność, więcej tokenów)
            chapter_text = await self._generate(
                prompt=prompt,
                temperature=0.85,
                max_tokens=segment.target_word_count * 2,  # Heurystyka: 1 słowo ≈ 2 tokeny
            )

            # Dodaj do segmentu
            segment.content = chapter_text
            segment.actual_word_count = len(chapter_text.split())

            generated_segments.append(segment)
            full_text_parts.append(f"# Rozdział {segment.segment_number}\n\n{chapter_text}")

        full_text = "\n\n---\n\n".join(full_text_parts)

        return {
            "segments": generated_segments,
            "full_text": full_text
        }

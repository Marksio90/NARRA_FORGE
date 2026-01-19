"""ETAP 5: Segment Planner Agent - Planowanie rozdziałów/segmentów"""
import json
from typing import Dict, Any, List
from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.types import PipelineStage, NarrativeSegment, ProjectBrief


class SegmentPlannerAgent(BaseAgent):
    """Agent Planowania Segmentów"""

    def get_system_prompt(self) -> str:
        return """Jesteś SEGMENT PLANNER AGENT - planujesz rozdziały/segmenty narracji.

Dla każdego rozdziału określ:
1. CEL: Co musi się wydarzyć
2. POV: Kto jest narratorem i dlaczego
3. SCENY: 2-4 sceny z celami
4. ŁUK EMOCJONALNY: Jak zmienia się ton
5. WORLDBUILDING: Co nowego wprowadzamy
6. CLOSING HOOK: Jak kończymy

Zwróć JSON ARRAY segmentów."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        brief: ProjectBrief = self._extract_from_context(context, "brief")
        structure = self._extract_from_context(context, "structure")

        prompt = f"""Zaplanuj {brief.target_chapter_count} rozdziałów (każdy ~{brief.target_word_count // brief.target_chapter_count} słów).

Zwróć JSON ARRAY z planem każdego rozdziału."""

        response = await self._generate(prompt=prompt, temperature=0.6, max_tokens=4096, json_mode=True)
        segments_data = json.loads(response)

        segments = []
        for i, seg_data in enumerate(segments_data):
            segment = NarrativeSegment(
                segment_id=f"seg_{i+1}",
                segment_number=i + 1,
                title=seg_data.get("title"),
                goal=seg_data["goal"],
                narrative_function=seg_data["narrative_function"],
                narrative_weight=seg_data.get("narrative_weight", 0.5),
                pov_character=seg_data["pov_character"],
                pov_rationale=seg_data["pov_rationale"],
                scenes=seg_data["scenes"],
                emotional_arc=seg_data["emotional_arc"],
                tone=seg_data.get("tone", "neutral"),
                worldbuilding_elements=seg_data.get("worldbuilding_elements", []),
                closing_hook=seg_data["closing_hook"],
                theme_development=seg_data["theme_development"],
                target_word_count=brief.target_word_count // brief.target_chapter_count,
                project_id=brief.project_id,
            )
            segments.append(segment)

        return {"segments": segments}

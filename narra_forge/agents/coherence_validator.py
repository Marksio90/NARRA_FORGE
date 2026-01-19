"""ETAP 7: Coherence Validator Agent - Walidacja spójności"""
import json
from typing import Dict, Any
from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.types import PipelineStage, CoherenceReport


class CoherenceValidatorAgent(BaseAgent):
    """Agent Walidacji Koherencji"""

    def get_system_prompt(self) -> str:
        return """Jesteś COHERENCE VALIDATOR AGENT - wykrywasz niespójności.

Sprawdź:
1. CHARACTER CONSISTENCY: Fizyka, psychologia, rozwój
2. WORLD CONSISTENCY: Geografia, zasady świata, timeline
3. PLOT CONSISTENCY: Cause-effect, brak plot holes
4. LANGUAGE CONSISTENCY: Terminologia, ton, POV voice

Dla każdej niespójności: type, severity (critical/major/minor), description, location, suggested_fix

Zwróć JSON z raportem i scores (0.0-1.0)."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        full_text = self._extract_from_context(context, "full_text")
        brief = self._extract_from_context(context, "brief")

        prompt = f"""Zwaliduj spójność tej narracji:

TEKST (pierwsze 3000 znaków): {full_text[:3000]}...
DŁUGOŚĆ CAŁKOWITA: {len(full_text)} znaków

Zwróć JSON raport walidacji ze scores i issues."""

        response = await self._generate(prompt=prompt, temperature=0.2, json_mode=True)
        data = json.loads(response)

        report = CoherenceReport(
            overall_score=data.get("overall_score", 0.85),
            passed=data.get("overall_score", 0.85) >= self.config.min_coherence_score,
            character_consistency=data.get("character_consistency", 0.9),
            world_consistency=data.get("world_consistency", 0.88),
            plot_consistency=data.get("plot_consistency", 0.85),
            language_consistency=data.get("language_consistency", 0.92),
            timeline_consistency=data.get("timeline_consistency", 0.9),
            issues=data.get("issues", []),
            recommendations=data.get("recommendations", []),
            project_id=brief.project_id,
        )

        self.logger.info(f"Coherence score: {report.overall_score:.2f} (passed: {report.passed})")

        return {"report": report}

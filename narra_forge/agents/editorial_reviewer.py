"""ETAP 9: Editorial Reviewer Agent - Redakcja wydawnicza"""
from typing import Dict, Any
from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.types import PipelineStage


class EditorialReviewerAgent(BaseAgent):
    """Agent Redakcji Wydawniczej"""

    def get_system_prompt(self) -> str:
        return """Jesteś EDITORIAL REVIEWER AGENT - profesjonalnym redaktorem.

STRUCTURAL EDIT:
1. Pacing audit: czy tempo jest odpowiednie?
2. Scene necessity: czy każda scena przesuwa fabułę?
3. Chapter balance: czy rozdziały są zbalansowane?

LINE EDIT:
1. Gramatyka
2. Interpunkcja (polskie cudzysłowy „...")
3. Ortografia

COPY EDIT:
1. Consistency nazw
2. Formatting

FINAL QUALITY GATES:
- Zero błędów
- Consistent POV
- Satisfying endings

Zwróć finałowy, publikowalny tekst."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        stylized_text = self._extract_from_context(context, "stylized_text")

        reviewed_text = await self._generate(
            prompt=f"""Wykonaj finalną redakcję wydawniczą:

{stylized_text}

Popraw wszelkie błędy, dopracuj pacing, upewnij się że jest gotowe do publikacji.

Zwróć TYLKO finalny tekst.""",
            temperature=0.5,
            max_tokens=len(stylized_text.split()) * 3,
        )

        return {"text": reviewed_text}

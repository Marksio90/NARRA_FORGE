"""ETAP 8: Language Stylizer Agent - Stylizacja językowa"""
from typing import Dict, Any
from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.types import PipelineStage


class LanguageStylerAgent(BaseAgent):
    """Agent Stylizacji Językowej"""

    def get_system_prompt(self) -> str:
        return """Jesteś LANGUAGE STYLIZER AGENT - mistrz polskiego języka literackiego.

SENTENCE-LEVEL REFINEMENT:
1. Usuń redundancje
2. Wzmocnij czasowniki
3. Zwiększ konkretność
4. Zmienność długości zdań

POLISH-SPECIFIC:
1. Bogate słownictwo (synonimy, idiomy)
2. Poprawna interpunkcja
3. Wszystkie polskie znaki

SENSORY ENHANCEMENT:
- Minimum 3 zmysły w każdej scenie

EMOTIONAL DEPTH:
- Layered experiences, nie płytkie "był smutny"

Zwróć tylko ulepszony tekst (bez dodatkowych komentarzy)."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        full_text = self._extract_from_context(context, "full_text")

        # Stylizuj w częściach (jeśli tekst długi)
        stylized_text = await self._generate(
            prompt=f"""Ulepsz stylizację tego tekstu zachowując treść:

{full_text}

Zwróć TYLKO ulepszony tekst.""",
            temperature=0.7,
            max_tokens=len(full_text.split()) * 3,  # Więcej tokenów
        )

        return {"text": stylized_text}

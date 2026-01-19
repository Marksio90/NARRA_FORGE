"""ETAP 4: Structure Designer Agent - Projektowanie struktury narracyjnej"""
import json
from typing import Dict, Any
from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.types import PipelineStage, NarrativeStructure, ProjectBrief, WorldBible, Character


class StructureDesignerAgent(BaseAgent):
    """Agent Struktury Narracyjnej"""

    def get_system_prompt(self) -> str:
        return """Jesteś STRUCTURE DESIGNER AGENT - architektem fabularnym.

Zaprojektuj wielowarstwową strukturę narracyjną używając 7-Point Story Structure:

1. HOOK: Status quo
2. PLOT POINT 1: Incydent rozpoczynający
3. PINCH POINT 1: Pierwsza komplikacja
4. MIDPOINT: Fałszywe zwycięstwo/porażka
5. PINCH POINT 2: Druga komplikacja
6. PLOT POINT 3: Moment decyzji
7. RESOLUTION: Rozwiązanie

SUBPLOTY (2-4): Każdy odbija główny temat z innej perspektywy

TEMAT: Centralny temat, pytanie tematyczne, teza

Zwróć JSON zgodnie z NarrativeStructure."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        brief: ProjectBrief = self._extract_from_context(context, "brief")
        world: WorldBible = self._extract_from_context(context, "world")
        characters = self._extract_from_context(context, "characters")

        prompt = f"""Zaprojektuj strukturę narracyjną (7-Point Structure) dla:

KONFLIKT: {brief.central_conflict}
TEMAT: {brief.thematic_question}
LICZBA SUBPLOTÓW: {brief.subplot_count}

Zwróć JSON z pełną strukturą."""

        response = await self._generate(prompt=prompt, temperature=0.7, json_mode=True)
        data = json.loads(response)

        structure = NarrativeStructure(
            structure_id=f"struct_{brief.project_id}",
            structure_type="7-point",
            hook=data["hook"],
            plot_point_1=data["plot_point_1"],
            pinch_point_1=data["pinch_point_1"],
            midpoint=data["midpoint"],
            pinch_point_2=data["pinch_point_2"],
            plot_point_3=data["plot_point_3"],
            resolution=data["resolution"],
            subplots=data.get("subplots", []),
            central_theme=data["central_theme"],
            thematic_question=data["thematic_question"],
            thesis=data["thesis"],
            pacing_map=data.get("pacing_map", []),
            plot_twists=data.get("plot_twists", []),
            project_id=brief.project_id,
        )

        return {"structure": structure}

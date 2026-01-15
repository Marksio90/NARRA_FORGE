"""
Agent 04: Structure Designer

Odpowiedzialność:
- Dobór optymalnej struktury narracyjnej
- Projektowanie aktów i beatów
- Mapowanie pacing i napięcia
- Oszacowanie word count

Model: gpt-4o-mini (planowanie)
"""
from typing import Any, Dict

from narra_forge.agents.base_agent import AnalysisAgent
from narra_forge.core.types import AgentResult, NarrativeStructure, PipelineStage


class StructureDesignerAgent(AnalysisAgent):
    """
    Agent projektujący strukturę narracyjną.

    Dobiera optymalną strukturę (three-act, hero's journey, kishotenketsu, etc.)
    i mapuje beats, pacing, napięcie.
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.STRUCTURE_DESIGN,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś PROJEKTANTEM STRUKTUR NARRACYJNYCH w systemie produkcji narracji wydawniczych.

Twoja rola:
- Dobierasz optymalną strukturę narracyjną dla danej historii
- Projektujesz akty i story beats
- Mapujesz pacing i krzywe napięcia
- Określasz dokładny word count i podział

DOSTĘPNE STRUKTURY:

1. **Three-Act Structure** (klasyczna)
   - Act 1: Setup (25%)
   - Act 2: Confrontation (50%)
   - Act 3: Resolution (25%)

2. **Hero's Journey** (Campbell)
   - 12 etapów: Ordinary World → Return with Elixir

3. **Kishotenketsu** (bez konfliktu)
   - Ki (introduction), Sho (development), Ten (twist), Ketsu (conclusion)

4. **Five-Act Structure** (Freytag)
   - Exposition, Rising Action, Climax, Falling Action, Denouement

5. **In Medias Res**
   - Start w środku akcji, flashbacki

6. **Non-linear**
   - Przeskoki czasowe, multiple timelines

ZASADY DOBORU:

- **Gatunek**: fantasy/scifi → hero's journey, three-act
- **Charakter**: character-driven → kishotenketsu możliwe
- **Pacing**: thriller → tight three-act
- **Temat**: philosophical → five-act lub kishotenketsu
- **Długość**: short story → three-act simplified

STORY BEATS (kluczowe punkty):
- Opening Image
- Inciting Incident
- First Plot Point
- Midpoint
- All Is Lost
- Climax
- Resolution

Format wyjścia (JSON):
{
  "structure_type": "three_act|hero_journey|kishotenketsu|five_act|custom",
  "structure_choice_reasoning": "Dlaczego ta struktura",
  "acts": [
    {
      "act_number": 1,
      "name": "Setup",
      "word_count": liczba,
      "percentage": 25,
      "purpose": "Cel tego aktu",
      "key_beats": ["beat1", "beat2"]
    }
  ],
  "key_beats": [
    {
      "name": "Inciting Incident",
      "position": "word position",
      "description": "Co się dzieje",
      "impact": "Wpływ na postacie/świat"
    }
  ],
  "pacing_map": {
    "opening": "slow|medium|fast",
    "act1_end": "medium|fast",
    "midpoint": "fast|explosive",
    "climax": "explosive",
    "ending": "slow|medium"
  },
  "tension_curve": [
    {"position": 0, "tension": 0.3},
    {"position": 25, "tension": 0.5},
    {"position": 50, "tension": 0.8},
    {"position": 75, "tension": 0.4},
    {"position": 100, "tension": 0.9}
  ],
  "estimated_word_count": liczba,
  "chapter_count": liczba,
  "average_chapter_length": liczba
}

Dobieraj strukturę OPTYMALNĄ dla historii. Mapuj PRECYZYJNIE."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj projektowanie struktury.

        Args:
            context: Zawiera 'analyzed_brief', 'world', 'characters'

        Returns:
            AgentResult ze strukturą narracyjną
        """
        analyzed_brief = context.get("analyzed_brief")
        world = context.get("world")
        characters = context.get("characters", [])

        if not analyzed_brief or not world:
            self.add_error("Missing analyzed_brief or world in context")
            return self._create_result(success=False, data={})

        # Przygotuj prompt
        char_summary = ", ".join([c.name for c in characters[:3]]) if characters else "Brak"

        prompt = f"""Zaprojektuj strukturę narracyjną dla:

BRIEF:
- Typ: {analyzed_brief.get('production_type')}
- Gatunek: {analyzed_brief.get('genre')}
- Szacowany word count: {analyzed_brief.get('estimated_word_count')}
- Focus: {analyzed_brief.get('narrative_focus')}
- Złożoność: {analyzed_brief.get('quality_requirements', {}).get('complexity')}

ŚWIAT:
- Konflikt: {world.core_conflict}
- Temat: {world.existential_theme}

POSTACIE: {char_summary}

Dobierz OPTYMALNĄ strukturę narracyjną i zaprojektuj beats, pacing, tension curve.
Zwróć kompletną strukturę jako JSON."""

        try:
            structure_data, call = await self.call_model_json(
                prompt=prompt,
                temperature=0.5,
                max_tokens=3000,
            )

            # Twórz NarrativeStructure object
            structure = NarrativeStructure(
                structure_type=structure_data.get("structure_type", "three_act"),
                acts=structure_data.get("acts", []),
                key_beats=structure_data.get("key_beats", []),
                pacing_map=structure_data.get("pacing_map", {}),
                estimated_word_count=structure_data.get("estimated_word_count", 5000),
            )

            return self._create_result(
                success=True,
                data={
                    "structure": structure,
                    "structure_data": structure_data,
                    "tension_curve": structure_data.get("tension_curve", []),
                },
            )

        except Exception as e:
            self.add_error(f"Structure design failed: {str(e)}")
            return self._create_result(success=False, data={})

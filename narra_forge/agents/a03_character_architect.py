"""
Agent 03: Character Architect

Odpowiedzialność:
- Projektowanie postaci jako PROCESÓW DYNAMICZNYCH
- Definiowanie trajektorii wewnętrznych
- Określanie sprzeczności i konfliktów
- Identyfikacja ograniczeń poznawczych
- Określanie zdolności ewolucji

Model: gpt-4o-mini (struktura)
"""
from typing import Any, Dict, List
from uuid import uuid4

from narra_forge.agents.base_agent import AnalysisAgent
from narra_forge.core.types import AgentResult, Character, InternalTrajectory, PipelineStage


class CharacterArchitectAgent(AnalysisAgent):
    """
    Agent projektujący postacie jako procesy dynamiczne.

    NIE tworzy statycznych opisów.
    Tworzy PROCESY z trajektoriami, sprzecznościami, ograniczeniami.
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.CHARACTER_ARCHITECTURE,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś ARCHITEKTEM POSTACI w systemie produkcji narracji wydawniczych.

Twoja rola:
- Projektujesz postacie jako PROCESY DYNAMICZNE, nie statyczne opisy
- Definiujesz trajektorie wewnętrzne (jak mogą się zmieniać)
- Określasz sprzeczności i konflikty wewnętrzne
- Identyfikujesz ograniczenia poznawcze (czego NIE mogą zrozumieć)
- Definiujesz zdolność ewolucji (jak bardzo mogą się zmienić)

ZASADY PROJEKTOWANIA POSTACI:

1. **Postać to PROCES, nie opis**
   - NIE: "Jest odważna i mądra"
   - TAK: "Udaje odwagę by ukryć lęk przed nieadekwatnością"

2. **Trajektoria wewnętrzna**
   - Stan początkowy (skąd zaczynają)
   - Potencjalne łuki (jak mogą się rozwinąć)
   - Triggery (co może je zmienić)
   - Punkty oporu (czemu będą się opierać)

3. **Sprzeczności wewnętrzne**
   - Każda postać ma konflikty w sobie
   - Pragnie A, ale boi się B
   - Wierzy w X, ale działa według Y

4. **Ograniczenia poznawcze**
   - Czego postać NIE MOŻE zrozumieć
   - Jakie ma cognitive blind spots
   - Co zawsze będzie interpretować błędnie

5. **Zdolność ewolucji**
   - 0.0-1.0 (jak bardzo może się zmienić)
   - Wysoka: postać może przejść transformację
   - Niska: postać jest w pewnym sensie "zamrożona"

Format wyjścia (JSON):
{
  "characters": [
    {
      "name": "Imię postaci",
      "role": "protagonist|antagonist|supporting|catalyst",
      "archetype": "opcjonalny archetyp",
      "internal_trajectory": {
        "starting_state": {
          "core_belief": "Co wierzą o sobie/świecie",
          "facade": "Co pokazują na zewnątrz",
          "hidden_truth": "Ukryta prawda o nich",
          "wound": "Psychologiczna rana"
        },
        "potential_arcs": [
          {
            "arc_type": "redemption|fall|growth|stasis|corruption",
            "direction": "Dokąd mogą zmierzać",
            "cost": "Co to będzie kosztować"
          }
        ],
        "triggers": ["Wydarzenie/osoba mogąca wywołać zmianę"],
        "resistance_points": ["Czemu będą się opierać"]
      },
      "contradictions": [
        "Sprzeczność wewnętrzna 1",
        "Sprzeczność wewnętrzna 2"
      ],
      "cognitive_limits": [
        "Czego nie mogą zrozumieć",
        "Co zawsze błędnie interpretują"
      ],
      "evolution_capacity": 0.0-1.0,
      "relationships": {
        "character_name": "natura relacji"
      }
    }
  ],
  "character_dynamics": {
    "primary_tension": "Główne napięcie między postaciami",
    "power_structure": "Kto ma władzę, kto jest uzależniony",
    "evolution_potential": "Jak relacje mogą ewoluować"
  }
}

Projektuj postacie jako PROCESY. Definiuj TRAJEKTORIE. Określaj OGRANICZENIA."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj projektowanie postaci.

        Args:
            context: Zawiera 'analyzed_brief', 'world'

        Returns:
            AgentResult z zaprojektowanymi postaciami
        """
        analyzed_brief = context.get("analyzed_brief")
        world = context.get("world")

        if not analyzed_brief or not world:
            self.add_error("Missing analyzed_brief or world in context")
            return self._create_result(success=False, data={})

        # Przygotuj prompt
        prompt = f"""Zaprojektuj postacie dla narracji w świecie "{world.name}":

ŚWIAT:
- Konflikt nadrzędny: {world.core_conflict}
- Temat egzystencjalny: {world.existential_theme}
- Prawa rzeczywistości: {world.reality_laws}

BRIEF:
- Gatunek: {analyzed_brief.get('genre')}
- Elementy kluczowe: {analyzed_brief.get('key_elements', {})}
- Focus: {analyzed_brief.get('narrative_focus')}
- Głębia: {analyzed_brief.get('quality_requirements', {}).get('depth')}

Zaprojektuj postacie jako PROCESY DYNAMICZNE z trajektoriami, sprzecznościami, ograniczeniami.
Zwróć strukturę jako JSON."""

        try:
            char_data, call = await self.call_model_json(
                prompt=prompt,
                temperature=0.8,
                max_tokens=4000,
            )

            # Twórz Character objects
            characters: List[Character] = []

            for char_dict in char_data.get("characters", []):
                char_id = f"char_{uuid4().hex[:12]}"

                character = Character(
                    character_id=char_id,
                    world_id=world.world_id,
                    name=char_dict.get("name", "Unknown"),
                    internal_trajectory=InternalTrajectory(
                        starting_state=char_dict.get("internal_trajectory", {}).get("starting_state", {}),
                        potential_arcs=char_dict.get("internal_trajectory", {}).get("potential_arcs", []),
                        triggers=char_dict.get("internal_trajectory", {}).get("triggers", []),
                        resistance_points=char_dict.get("internal_trajectory", {}).get("resistance_points", []),
                    ),
                    contradictions=char_dict.get("contradictions", []),
                    cognitive_limits=char_dict.get("cognitive_limits", []),
                    evolution_capacity=char_dict.get("evolution_capacity", 0.5),
                    archetype=char_dict.get("archetype"),
                    role=char_dict.get("role"),
                )

                # Zapisz do memory
                char_dict_save = {
                    "character_id": character.character_id,
                    "world_id": character.world_id,
                    "name": character.name,
                    "internal_trajectory": character.internal_trajectory.__dict__,
                    "contradictions": character.contradictions,
                    "cognitive_limits": character.cognitive_limits,
                    "evolution_capacity": character.evolution_capacity,
                    "archetype": character.archetype,
                    "role": character.role,
                }
                await self.memory.structural.save_character(char_dict_save)

                characters.append(character)

            return self._create_result(
                success=True,
                data={
                    "characters": characters,
                    "character_data": char_data,
                    "character_dynamics": char_data.get("character_dynamics", {}),
                },
            )

        except Exception as e:
            self.add_error(f"Character architecture failed: {str(e)}")
            return self._create_result(success=False, data={})

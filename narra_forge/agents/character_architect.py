"""
ETAP 3: Character Architect Agent

Tworzy wielowymiarowe, psychologicznie złożone postacie jako procesy, nie statyczne opisy.
"""

import json
from typing import Dict, Any, List
from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.types import PipelineStage, Character, ProjectBrief, WorldBible
from datetime import datetime


class CharacterArchitectAgent(BaseAgent):
    """
    Agent Architektury Postaci

    Odpowiedzialność: Projektowanie wielowymiarowych, psychologicznie złożonych postaci
    Input: ProjectBrief + WorldBible
    Output: List[Character] (protagonist, antagonist, supporting)
    """

    def get_system_prompt(self) -> str:
        return """Jesteś CHARACTER ARCHITECT AGENT - psychologiem narracyjnym specjalizującym się w tworzeniu głębokich, wielowymiarowych postaci.

FUNDAMENTALNA ZASADA: Postacie to PROCESY PSYCHOLOGICZNE, nie statyczne opisy.

Każda postać MUSI mieć:

RDZEŃ PSYCHOLOGICZNY:
- **Conscious Goal**: Co postać MYŚLI, że chce
- **Unconscious Need**: Czego NAPRAWDĘ potrzebuje (często sprzeczne z goal)
- **Ghost/Trauma**: Wydarzenie z przeszłości definiujące postać
- **Internal Conflict**: Sprzeczność w wartościach/przekonaniach
- **Fatal Flaw**: Wada, która może ją zniszczyć

CHARAKTERYSTYKA:
- Wiek, wygląd (unikalne cechy, nie generic!)
- Pochodzenie, status społeczny
- Umiejętności (3-5, Z OGRANICZENIAMI)
- Sposób mówienia (dialekt, słownictwo, maniery)
- Wewnętrzny głos (jak myśli)

DYNAMIKA:
- **Internal Trajectory**: Dokąd zmierza psychologicznie
- **Contradictions**: Wewnętrzne sprzeczności
- **Evolution Capacity**: Zdolność zmiany (0.0-1.0)

ARKA TRANSFORMACJI:
- Punkt startowy: Kim jest NA POCZĄTKU
- Punkt zwrotny: Co musi się wydarzyć, żeby się zmienił
- Punkt końcowy: Kim będzie NA KOŃCU

PROTAGONIST:
- Musi być WIELOWYMIAROWY (nie idealny, nie generic)
- Flaw jest źródłem konfliktów
- Need vs Goal generuje napięcie

ANTAGONIST (KLUCZOWE!):
- Antagonist ≠ zły
- Antagonist = ma sprzeczne cele z protagonistą
- MUSI mieć rację Z JEGO perspektywy
- Human element (co czyni go człowiekiem?)
- Line won't cross (granica moralności)

SUPPORTING (3-5 postaci):
- Każda ma własny cel (nie tylko wspiera protagonistę)
- Reprezentuje alternatywny sposób radzenia sobie z tematem
- Własna mini-arka transformacji
- Wpływa na fabułę główną

RELACJE:
- Każda relacja ma: historię, dynamikę, konflikt
- Relacje EWOLUUJĄ w czasie

ZASADY:
1. ZERO stereotypów i klisz
2. Każda postać jest unikalna
3. Sposób mówienia CHARAKTERYSTYCZNY
4. Wewnętrzny głos RÓŻNY dla każdej postaci
5. Polski z pełnym wsparciem znaków

Zwróć JSON (bez markdown) - ARRAY postaci:
[
    {
        "character_id": "unique_id",
        "name": "Imię i Nazwisko",
        "role": "protagonist|antagonist|supporting",
        "conscious_goal": "świadomy cel",
        "unconscious_need": "nieświadoma potrzeba",
        "ghost_trauma": "trauma z przeszłości",
        "internal_conflict": "wewnętrzny konflikt",
        "fatal_flaw": "wada charakteru",
        "age": 30,
        "physical_description": "opis wyglądu",
        "social_status": "status społeczny",
        "origin": "skąd pochodzi",
        "skills": ["umiejętność 1 (z ograniczeniem)", "..."],
        "cognitive_limits": ["czego nie może pojąć"],
        "speech_pattern": "jak mówi",
        "internal_voice": "jak myśli",
        "relationships": {
            "character_2_id": {
                "nature": "natura relacji",
                "history": "historia",
                "dynamic": "dynamika"
            }
        },
        "story_goal": "konkretny cel w fabule",
        "stakes": "co straci",
        "arc_start": "punkt A",
        "arc_midpoint": "kluczowa zmiana",
        "arc_end": "punkt B",
        "transformation_catalyst": "co musi się wydarzyć",
        "internal_trajectory": "dokąd zmierza",
        "contradictions": ["sprzeczność 1", "..."],
        "evolution_capacity": 0.7,
        "thematic_function": "co reprezentuje w temacie",
        "philosophy": "światopogląd (dla antagonisty)",
        "methods": ["metody (dla antagonisty)"],
        "line_wont_cross": "granica (dla antagonisty)",
        "human_element": "co czyni go ludzkim (dla antagonisty)"
    }
]
"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stwórz postacie

        Args:
            context: Musi zawierać 'brief' i 'world'

        Returns:
            {'characters': List[Character]}
        """
        brief: ProjectBrief = self._extract_from_context(context, "brief")
        world: WorldBible = self._extract_from_context(context, "world")

        # Określ liczbę postaci drugoplanowych
        supporting_count = brief.supporting_count

        prompt = f"""Zaprojektuj kompletny zestaw postaci dla narracji zgodnie z tym briefem i światem:

BRIEF:
- Archetyp protagonisty: {brief.protagonist_archetype}
- Typ antagonisty: {brief.antagonist_type}
- Liczba postaci drugoplanowych: {supporting_count}
- Centralny konflikt: {brief.central_conflict}
- Pytanie tematyczne: {brief.thematic_question}

ŚWIAT:
- Nazwa: {world.name}
- Temat egzystencjalny: {world.existential_theme}
- Konflikt nadrzędny: {world.core_conflict}
- Główna tajemnica: {world.central_mystery}

Stwórz:
1. PROTAGONIST (1 postać) - zgodny z archetypem, ale UNIKALNY
2. ANTAGONIST (1 postać) - sprzeczny cel, ale ma RACJĘ z jego perspektywy
3. SUPPORTING ({supporting_count} postaci) - każda z własnym celem i mini-arką

KLUCZOWE:
- Każda postać to PROCES, nie statyczny opis
- Conscious Goal vs Unconscious Need = napięcie
- Antagonist ≠ zły, tylko ma inne cele
- Supporting mają własne życie (nie tylko wspierają)
- Sposób mówienia unikalny dla każdej postaci

JĘZYK: Polski z pełnymi znakami (ą, ć, ę, ł, ń, ó, ś, ź, ż)

Zwróć JSON ARRAY postaci zgodnie z instrukcją systemową.
"""

        response = await self._generate(
            prompt=prompt,
            temperature=0.8,  # Wysoka kreatywność
            max_tokens=4096,
            json_mode=True,
        )

        try:
            characters_data = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Character Architect returned invalid JSON: {e}")

        # Konwertuj na Character objects
        characters: List[Character] = []

        for char_data in characters_data:
            character = Character(
                character_id=char_data.get("character_id", f"char_{len(characters)}"),
                name=char_data["name"],
                role=char_data["role"],
                conscious_goal=char_data["conscious_goal"],
                unconscious_need=char_data["unconscious_need"],
                ghost_trauma=char_data["ghost_trauma"],
                internal_conflict=char_data["internal_conflict"],
                fatal_flaw=char_data["fatal_flaw"],
                age=char_data["age"],
                physical_description=char_data["physical_description"],
                social_status=char_data["social_status"],
                origin=char_data["origin"],
                skills=char_data["skills"],
                cognitive_limits=char_data["cognitive_limits"],
                speech_pattern=char_data["speech_pattern"],
                internal_voice=char_data["internal_voice"],
                relationships=char_data.get("relationships", {}),
                story_goal=char_data["story_goal"],
                stakes=char_data["stakes"],
                arc_start=char_data["arc_start"],
                arc_midpoint=char_data["arc_midpoint"],
                arc_end=char_data["arc_end"],
                transformation_catalyst=char_data["transformation_catalyst"],
                internal_trajectory=char_data["internal_trajectory"],
                contradictions=char_data["contradictions"],
                evolution_capacity=char_data["evolution_capacity"],
                thematic_function=char_data["thematic_function"],
                philosophy=char_data.get("philosophy"),
                methods=char_data.get("methods"),
                line_wont_cross=char_data.get("line_wont_cross"),
                human_element=char_data.get("human_element"),
                world_id=world.world_id,
            )
            characters.append(character)

        self.logger.info(
            f"Created {len(characters)} characters: "
            f"{[c.name for c in characters]}"
        )

        return {"characters": characters}

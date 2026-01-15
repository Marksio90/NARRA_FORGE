"""
Stage 3: Character Architect Agent
Designs characters as PROCESSES, not static entities.
"""
from typing import Dict, Any, List
import uuid

from .base_agent import BaseAgent, AgentResponse
from ..core.types import Character, WorldBible, ProjectBrief


class CharacterArchitectAgent(BaseAgent):
    """
    Designs characters as dynamic, evolving entities.

    CRITICAL: Characters are PROCESSES, not descriptions.

    Each character has:
    - Internal trajectory (where they're going psychologically)
    - Contradictions (internal conflicts)
    - Cognitive limits (what they can't perceive/understand)
    - Evolution capacity (resistance to change)
    - Motivations, fears, blind spots
    """

    def get_system_prompt(self) -> str:
        return """Jesteś architektem postaci specjalizującym się w dynamicznych, psychologicznie złożonych bytach.

KRYTYCZNE ZASADY:

1. POSTACIE SĄ PROCESAMI
   - Nie statycznymi opisami
   - Mają wewnętrzne trajektorie
   - Ewoluują przez doświadczenie
   - Mają ograniczenia poznawcze

2. KAŻDA POSTAĆ POTRZEBUJE:
   - TRAJEKTORIA WEWNĘTRZNA: Dokąd zmierzają psychologicznie?
   - SPRZECZNOŚCI: Jakie konflikty istnieją w ich wnętrzu?
   - OGRANICZENIA POZNAWCZE: Czego nie mogą zobaczyć/zrozumieć?
   - ZDOLNOŚĆ EWOLUCJI: Jak bardzo są oporni/otwarci na zmianę?

3. GŁĘBIA ZAMIAST OPISU:
   - Nie opisuj wyglądu
   - Definiuj WEWNĘTRZNĄ STRUKTURĘ
   - Twórz ARCHITEKTURĘ PSYCHOLOGICZNĄ

4. MOTYWACJE VS LĘKI:
   - Co pcha ich do przodu?
   - Co ich powstrzymuje?
   - Jak te siły się ze sobą konfliktują?

5. MARTWE PUNKTY:
   - Jakich prawd nie mogą dostrzec?
   - Jakie uprzedzenia kształtują ich percepcję?

6. RELACYJNE:
   - Jak odnoszą się do innych?
   - Jakie wzorce się powtarzają?

ABSOLUTNIE WYMAGANE:
   - WSZYSTKIE imiona muszą być PO POLSKU lub brzmiące naturalnie po polsku
   - Opisy psychologiczne, motywacje, lęki - wszystko po polsku
   - Żadnych angielskich terminów ani imion

Projektuj postacie które się ZMIENIAJĄ, nie manekiny."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Validate inputs."""
        return (
            "world" in context and
            isinstance(context["world"], WorldBible) and
            "brief" in context
        )

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Design characters for the narrative.

        Args:
            context: Must contain "world" and "brief"
            **kwargs: Can specify "character_count" or "character_roles"

        Returns:
            AgentResponse with list of Characters
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Missing world or brief in context"
            )

        world: WorldBible = context["world"]
        brief: ProjectBrief = context["brief"]

        # Determine how many characters needed
        character_count = kwargs.get("character_count")
        if not character_count:
            character_count = self._estimate_character_count(brief)

        self.log(f"Designing {character_count} characters for {world.name}")

        # Design characters
        prompt = f"""Zaprojektuj {character_count} postaci dla tego świata narracyjnego:

ŚWIAT: {world.name}
TEMAT: {world.existential_theme}
KONFLIKT: {world.core_conflict}
GATUNEK: {brief.genre.value}
FORMA: {brief.form.value}

PRAWA ŚWIATA:
{world.laws_of_reality}

DOSTĘPNE ARCHETYPY:
{world.archetype_system}

Dla KAŻDEJ postaci podaj:

1. NAME: Imię odpowiednie dla świata (PO POLSKU lub brzmiące naturalnie po polsku!)
2. INTERNAL TRAJECTORY: Dokąd zmierzają psychologicznie?
3. CONTRADICTIONS: Jakie mają wewnętrzne konflikty? (lista)
4. COGNITIVE LIMITS: Czego nie mogą dostrzec/zrozumieć? (lista)
5. EVOLUTION CAPACITY: 0.0-1.0 (0=sztywni, 1=bardzo adaptatywni)
6. MOTIVATIONS: Co ich napędza? (lista)
7. FEARS: Czego się boją? (lista)
8. BLIND SPOTS: Jakich prawd nie widzą? (lista)
9. CURRENT STATE: Gdzie są TERAZ? (obiekt)
10. ARCHETYPE: Który archetypświata ucieleśniają/podważają?

Zaprojektuj postacie które są:
- Psychologicznie złożone
- Zdolne do ewolucji
- Wewnętrznie sprzeczne
- Odpowiednie dla {brief.form.value}

KRYTYCZNIE WAŻNE: Wszystkie imiona, opisy, terminy muszą być PO POLSKU!
Imiona postaci muszą brzmieć naturalnie po polsku (np. Tomasz, Maria, Krzysztof, Ada, etc.).

Odpowiedz tablicą JSON z postaciami."""

        try:
            result = await self.generate_structured(
                prompt=prompt,
                schema={
                    "characters": "array of character objects"
                }
            )

            characters = []

            for char_data in result.get("characters", []):
                char_id = str(uuid.uuid4())

                character = Character(
                    character_id=char_id,
                    name=char_data["name"],
                    world_id=world.world_id,
                    internal_trajectory=char_data["internal_trajectory"],
                    contradictions=char_data["contradictions"],
                    cognitive_limits=char_data["cognitive_limits"],
                    evolution_capacity=char_data["evolution_capacity"],
                    motivations=char_data["motivations"],
                    fears=char_data["fears"],
                    blind_spots=char_data["blind_spots"],
                    relationships={},
                    current_state=char_data["current_state"],
                    evolution_history=[]
                )

                # Store in structural memory
                self.structural_memory.store_character(character)

                characters.append(character)

                self.log(f"Created character: {character.name}")

            # Establish initial relationships
            if len(characters) > 1:
                await self._establish_relationships(world.world_id, characters)

            return AgentResponse(
                success=True,
                output=characters,
                metadata={
                    "character_count": len(characters),
                    "avg_evolution_capacity": sum(c.evolution_capacity for c in characters) / len(characters)
                }
            )

        except Exception as e:
            self.log(f"Error designing characters: {e}", "ERROR")
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error=str(e)
            )

    def _estimate_character_count(self, brief: ProjectBrief) -> int:
        """Estimate appropriate character count based on form."""
        form_counts = {
            "short_story": 2,
            "novella": 3,
            "novel": 5,
            "epic_saga": 8
        }
        return form_counts.get(brief.form.value, 3)

    async def _establish_relationships(
        self,
        world_id: str,
        characters: List[Character]
    ):
        """
        Establish initial relationships between characters.
        """
        if len(characters) < 2:
            return

        # Create relationship matrix prompt
        char_names = [c.name for c in characters]
        char_details = "\n".join([
            f"- {c.name}: {c.internal_trajectory}"
            for c in characters
        ])

        prompt = f"""Define initial relationships between these characters:

{char_details}

For each pair, define:
- relationship_type: (e.g., allies, enemies, family, strangers, etc.)
- strength: 0.0-1.0 (how strong is the connection)
- valence: -1.0 to 1.0 (negative=hostile, positive=supportive)

Create a relationship matrix. Some can be strangers (strength=0).

Respond with JSON array of relationships."""

        try:
            result = await self.generate_structured(
                prompt=prompt,
                schema={
                    "relationships": "array of relationship objects"
                }
            )

            for rel in result.get("relationships", []):
                self.semantic_memory.store_relationship(
                    world_id=world_id,
                    entity_a=rel["entity_a"],
                    entity_b=rel["entity_b"],
                    relationship_data={
                        "type": rel["relationship_type"],
                        "strength": rel["strength"],
                        "valence": rel["valence"],
                        "history": [],
                        "current_state": "initial"
                    }
                )

        except Exception as e:
            self.log(f"Error establishing relationships: {e}", "WARNING")

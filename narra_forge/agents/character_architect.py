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
        return """You are a character architect specializing in dynamic, psychologically complex entities.

CRITICAL PRINCIPLES:

1. CHARACTERS ARE PROCESSES
   - Not static descriptions
   - They have internal trajectories
   - They evolve through experience
   - They have cognitive limits

2. EVERY CHARACTER NEEDS:
   - INTERNAL TRAJECTORY: Where are they going psychologically?
   - CONTRADICTIONS: What conflicts exist within them?
   - COGNITIVE LIMITS: What can't they see/understand?
   - EVOLUTION CAPACITY: How resistant/open to change?

3. DEPTH OVER DESCRIPTION:
   - Don't describe appearance
   - Define INTERNAL STRUCTURE
   - Create PSYCHOLOGICAL ARCHITECTURE

4. MOTIVATIONS VS FEARS:
   - What drives them forward?
   - What holds them back?
   - How do these forces conflict?

5. BLIND SPOTS:
   - What truths can they not see?
   - What biases shape their perception?

6. RELATIONAL:
   - How do they relate to others?
   - What patterns repeat?

Design characters that CHANGE, not mannequins."""

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
        prompt = f"""Design {character_count} characters for this narrative world:

WORLD: {world.name}
THEME: {world.existential_theme}
CONFLICT: {world.core_conflict}
GENRE: {brief.genre.value}
FORM: {brief.form.value}

WORLD LAWS:
{world.laws_of_reality}

ARCHETYPES AVAILABLE:
{world.archetype_system}

For EACH character, provide:

1. NAME: Appropriate for world
2. INTERNAL TRAJECTORY: Where are they going psychologically?
3. CONTRADICTIONS: What internal conflicts do they have? (list)
4. COGNITIVE LIMITS: What can't they perceive/understand? (list)
5. EVOLUTION CAPACITY: 0.0-1.0 (0=rigid, 1=highly adaptive)
6. MOTIVATIONS: What drives them? (list)
7. FEARS: What terrifies them? (list)
8. BLIND SPOTS: What truths can't they see? (list)
9. CURRENT STATE: Where are they NOW? (object)
10. ARCHETYPE: Which world archetype do they embody/subvert?

Design characters that are:
- Psychologically complex
- Capable of evolution
- Internally contradictory
- Appropriate for {brief.form.value}

Respond with JSON array of characters."""

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

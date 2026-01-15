"""
Stage 2: World Architect Agent
Designs narrative worlds as complete systems.
"""
from typing import Dict, Any
from datetime import datetime
import uuid

from .base_agent import BaseAgent, AgentResponse
from ..core.types import WorldBible, ProjectBrief


class WorldArchitectAgent(BaseAgent):
    """
    Designs narrative worlds following NARRA_FORGE principles.

    Creates:
    - Laws of reality (physical, magical, technological)
    - Boundaries (spatial, temporal, dimensional)
    - Anomalies (exceptions to rules)
    - Core conflict
    - Existential theme
    - Archetype system
    """

    def get_system_prompt(self) -> str:
        return """You are a master world architect for narrative universes.

Your responsibility is to design COMPLETE, COHERENT worlds as SYSTEMS.

CRITICAL PRINCIPLES:

1. LAWS BEFORE STORIES
   - Define physical/magical/technological rules FIRST
   - Rules create constraints
   - Constraints create drama

2. EVERY WORLD MUST ANSWER:
   - What makes this world UNIQUE?
   - What is the CORE CONFLICT that defines it?
   - Why does this world exist NARRATIVELY?
   - What is its EXISTENTIAL THEME?

3. DESIGN FOR CONSISTENCY:
   - Laws must be internally consistent
   - Anomalies must be intentional and explained
   - Boundaries must be clear

4. SCALE APPROPRIATELY:
   - Intimate: small, personal world
   - Regional: cities, kingdoms
   - Global: planets, civilizations
   - Cosmic: galaxies, multiverses

5. AVOID CLICHÉS:
   - Don't copy existing worlds
   - Use archetypal STRUCTURES, not characters
   - Create unique rule systems

You design SYSTEMS that enable great stories."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Validate that we have a project brief."""
        return "brief" in context and isinstance(context["brief"], ProjectBrief)

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Design a narrative world.

        Args:
            context: Must contain "brief" (ProjectBrief)

        Returns:
            AgentResponse with WorldBible
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Missing or invalid brief in context"
            )

        brief: ProjectBrief = context["brief"]

        self.log(f"Architecting world: {brief.genre.value}, scale: {brief.world_scale}")

        # Construct world design prompt
        prompt = f"""Design a narrative world with these parameters:

FORM: {brief.form.value}
GENRE: {brief.genre.value}
SCALE: {brief.world_scale}
THEMATIC FOCUS: {', '.join(brief.thematic_focus)}
EXPANSION POTENTIAL: {brief.expansion_potential}

Your world design must include:

1. LAWS OF REALITY
   - Physical laws (how does nature work?)
   - Technological level (if applicable)
   - Magical/supernatural rules (if applicable)
   - Social/cultural rules

2. BOUNDARIES
   - Spatial: where does this world exist? limits?
   - Temporal: time period, time flow rules
   - Dimensional: single reality or multiverse?

3. ANOMALIES
   - What breaks the rules?
   - Why do these exceptions exist?

4. CORE CONFLICT
   - What is the fundamental tension in this world?
   - What drives all stories here?

5. EXISTENTIAL THEME
   - WHY does this world exist narratively?
   - What question does it explore?

6. ARCHETYPE SYSTEM
   - What archetypal roles exist here?
   - How do they function in this world?

7. CURRENT STATE
   - What is happening NOW in this world?
   - What tensions are active?

Design a world that is:
- Internally consistent
- Rich enough for {brief.form.value}
- Appropriate for {brief.genre.value}
- Unique and compelling

Respond with detailed JSON."""

        try:
            # Generate world design
            result = await self.generate_structured(
                prompt=prompt,
                schema={
                    "name": "string",
                    "laws_of_reality": "object",
                    "boundaries": "object",
                    "anomalies": "array",
                    "core_conflict": "string",
                    "existential_theme": "string",
                    "archetype_system": "object",
                    "current_state": "object"
                }
            )

            # Create WorldBible
            world_id = str(uuid.uuid4())

            world = WorldBible(
                world_id=world_id,
                name=result["name"],
                created_at=datetime.now(),
                laws_of_reality=result["laws_of_reality"],
                boundaries=result["boundaries"],
                anomalies=result["anomalies"],
                core_conflict=result["core_conflict"],
                existential_theme=result["existential_theme"],
                archetype_system=result["archetype_system"],
                timeline=[],
                current_state=result["current_state"],
                related_worlds=[],
                isolation_level="isolated"
            )

            # Store in structural memory
            self.structural_memory.store_world(world)

            self.log(f"World created: {world.name}")

            return AgentResponse(
                success=True,
                output=world,
                metadata={
                    "world_id": world_id,
                    "complexity_score": self._assess_complexity(world)
                }
            )

        except Exception as e:
            self.log(f"Error architecting world: {e}", "ERROR")
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error=str(e)
            )

    def _assess_complexity(self, world: WorldBible) -> float:
        """
        Assess world complexity (0.0-1.0).
        Used for determining generation parameters.
        """
        score = 0.0

        # More laws = more complex
        score += min(len(world.laws_of_reality), 5) * 0.1

        # Anomalies add complexity
        score += min(len(world.anomalies), 3) * 0.1

        # Archetype system depth
        score += min(len(world.archetype_system), 5) * 0.1

        # State complexity
        score += min(len(world.current_state), 5) * 0.1

        return min(score, 1.0)

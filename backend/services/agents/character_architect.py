"""Character Architect Agent - creates character profiles and arcs."""

import json
import logging
from datetime import datetime
from uuid import uuid4

from models.schemas.agent import CharacterRequest, CharacterResponse
from services.model_policy import ModelPolicy, PipelineStage
from services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class CharacterArchitect:
    """
    Character Architect Agent - creates character profiles with psychological depth.

    This agent uses gpt-4o-mini to:
    - Design character trajectories (transformation arcs)
    - Define relationships between characters
    - Establish psychological constraints and motivations
    - Create balanced casts with distinct voices

    Uses PipelineStage.CHARACTER_PROFILE for model selection.
    """

    SYSTEM_PROMPT = """You are the Character Architect for a literary production system.

Your role is to create psychologically complex characters with clear transformation arcs.

## Your responsibilities:
1. **Character Trajectory** - How the character changes from start to finish
2. **Relationships** - Connections with other characters (mentor, rival, love interest, etc.)
3. **Psychological Constraints** - Fears, traumas, beliefs that limit the character
4. **Motivations** - What drives the character forward

## Output Format:
Return ONLY a valid JSON object with this structure:
{
  "characters": [
    {
      "name": "string",
      "role": "protagonist|antagonist|supporting|mentor",
      "trajectory": [
        {"stage": "beginning", "state": "naive and idealistic"},
        {"stage": "challenge", "state": "tested and doubting"},
        {"stage": "transformation", "state": "hardened but wise"},
        {"stage": "resolution", "state": "balanced and mature"}
      ],
      "relationships": [
        {"character": "Character Name", "type": "mentor", "dynamic": "teaches protagonist magic"},
        {"character": "Character Name", "type": "antagonist", "dynamic": "represents protagonist's fears"}
      ],
      "constraints": [
        "Fear of abandonment prevents forming close bonds",
        "Oath of non-violence creates moral dilemmas",
        "Pride makes it hard to ask for help"
      ],
      "motivations": {
        "surface": "Find the lost artifact",
        "deeper": "Prove worth to distant father",
        "core": "Overcome feelings of inadequacy"
      }
    }
  ]
}

## Guidelines:
- Create characters equal to the requested count
- Each character should have 3-5 trajectory stages
- Define 2-4 key relationships per character
- Include 2-4 psychological constraints
- Make trajectories specific and measurable
- Ensure characters complement each other (avoid redundancy)
- Balance character types (not all protagonists)
- Create believable transformations (gradual, earned)

## Character Roles:
- **Protagonist**: Main character whose journey we follow (1-2 max)
- **Antagonist**: Opposition to protagonist's goals (1-2 max)
- **Supporting**: Help or hinder protagonist (majority)
- **Mentor**: Guide and teach protagonist (0-1)

## Trajectory Guidelines:
- Beginning: Establish normal state and core traits
- Challenge: What tests the character
- Transformation: How they change
- Resolution: Final state (changed but recognizable)

## Example (Fantasy - 3 characters):
{
  "characters": [
    {
      "name": "Kael Thornweave",
      "role": "protagonist",
      "trajectory": [
        {"stage": "beginning", "state": "disillusioned former mage, hiding from past"},
        {"stage": "call_to_action", "state": "reluctantly accepts mission to save apprentice"},
        {"stage": "trials", "state": "confronts failures, regains partial powers"},
        {"stage": "transformation", "state": "accepts responsibility for past mistakes"},
        {"stage": "resolution", "state": "mentor to new generation, at peace"}
      ],
      "relationships": [
        {"character": "Lyra", "type": "ward", "dynamic": "must save her, sees himself in her"},
        {"character": "The Shadowmancer", "type": "antagonist", "dynamic": "former friend turned enemy"},
        {"character": "Elder Moira", "type": "mentor", "dynamic": "guides his redemption"}
      ],
      "constraints": [
        "Guilt over past tragedy prevents using full power",
        "Fear of becoming like the Shadowmancer",
        "Vow to never lead others into danger"
      ],
      "motivations": {
        "surface": "Rescue Lyra from the Shadowmancer",
        "deeper": "Redeem past failure when he couldn't save his students",
        "core": "Prove he deserves a second chance"
      }
    },
    {
      "name": "Lyra Ashwind",
      "role": "supporting",
      "trajectory": [
        {"stage": "beginning", "state": "eager apprentice, over-confident"},
        {"stage": "captured", "state": "realizes she's outmatched, learns humility"},
        {"stage": "survival", "state": "uses cleverness to resist corruption"},
        {"stage": "resolution", "state": "tempered by experience, ready to learn properly"}
      ],
      "relationships": [
        {"character": "Kael", "type": "mentor", "dynamic": "idolizes him, doesn't know his past"},
        {"character": "The Shadowmancer", "type": "captor", "dynamic": "tries to turn her to darkness"}
      ],
      "constraints": [
        "Youthful arrogance leads to mistakes",
        "Lack of training makes her vulnerable",
        "Fear of disappointing Kael"
      ],
      "motivations": {
        "surface": "Become a powerful mage",
        "deeper": "Prove she's special, not ordinary",
        "core": "Earn recognition and belonging"
      }
    },
    {
      "name": "The Shadowmancer (Aldric Voss)",
      "role": "antagonist",
      "trajectory": [
        {"stage": "backstory", "state": "Kael's friend, idealistic about changing world"},
        {"stage": "corruption", "state": "embraces dark magic for 'greater good'"},
        {"stage": "present", "state": "believes ends justify means, corrupting Lyra"},
        {"stage": "climax", "state": "confronts Kael, forced to see what he's become"},
        {"stage": "resolution", "state": "defeated but offered chance at redemption"}
      ],
      "relationships": [
        {"character": "Kael", "type": "former_friend", "dynamic": "mirror of what Kael could become"},
        {"character": "Lyra", "type": "target", "dynamic": "sees her potential for darkness"}
      ],
      "constraints": [
        "Corrupted by dark magic, losing humanity",
        "Genuinely believes he's helping the world",
        "Can't admit he was wrong"
      ],
      "motivations": {
        "surface": "Recruit Lyra to his cause",
        "deeper": "Prove his path was right all along",
        "core": "Be validated that his sacrifices weren't in vain"
      }
    }
  ]
}
"""

    def __init__(self, openai_client: OpenAIClient | None = None) -> None:
        """
        Initialize Character Architect agent.

        Args:
            openai_client: OpenAI client for API calls (creates new if None)
        """
        self.client = openai_client or OpenAIClient()
        self.stage = PipelineStage.CHARACTER_PROFILE
        self.model = ModelPolicy.get_model_for_stage(self.stage)
        self.temperature = ModelPolicy.get_temperature_for_stage(self.stage)
        self.token_budget = ModelPolicy.get_token_budget_for_stage(self.stage)

    async def create_characters(self, request: CharacterRequest) -> CharacterResponse:
        """
        Create character profiles with trajectories and relationships.

        Args:
            request: CharacterRequest with world_id, character_count, types

        Returns:
            CharacterResponse with character_ids

        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        logger.info(
            "CharacterArchitect starting",
            extra={
                "job_id": str(request.job_id),
                "world_id": str(request.world_id),
                "character_count": request.character_count,
                "stage": self.stage.value,
            },
        )

        # Build user prompt
        user_prompt = f"""Create {request.character_count} characters for this story.
"""

        if request.character_types:
            user_prompt += f"\nRequested character types: {', '.join(request.character_types)}"

        if request.constraints:
            user_prompt += f"\nConstraints: {json.dumps(request.constraints)}"

        user_prompt += """

Ensure:
- Each character has a clear transformation arc
- Relationships form a coherent web
- Psychological constraints create genuine conflict
- Motivations operate on multiple levels (surface/deeper/core)
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        # Call OpenAI
        result = await self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            token_budget=self.token_budget,
        )

        # Parse JSON response
        try:
            char_data = json.loads(result["content"])
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse CharacterArchitect response",
                extra={"response": result["content"][:200]},
            )
            raise ValueError(f"Invalid JSON response from CharacterArchitect: {exc}") from exc

        # Validate structure
        if "characters" not in char_data or not isinstance(char_data["characters"], list):
            raise ValueError("CharacterArchitect response missing 'characters' list")

        characters = char_data["characters"]
        if len(characters) != request.character_count:
            logger.warning(
                "Character count mismatch",
                extra={
                    "requested": request.character_count,
                    "received": len(characters),
                },
            )

        # Generate character IDs
        character_ids = [uuid4() for _ in characters]

        logger.info(
            "CharacterArchitect completed",
            extra={
                "job_id": str(request.job_id),
                "characters_created": len(character_ids),
                "cost_usd": result["cost"],
            },
        )

        # Build response
        response = CharacterResponse(
            id=uuid4(),
            job_id=request.job_id,
            agent="architekt_postaci",
            stage=self.stage,
            character_ids=character_ids,
            character_count=len(character_ids),
            created_at=result.get("created_at") or datetime.utcnow(),
        )

        return response

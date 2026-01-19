"""World Architect Agent - creates world specifications."""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from models.schemas.agent import WorldRequest, WorldResponse
from models.schemas.domain import WorldSchema
from services.model_policy import ModelPolicy, PipelineStage
from services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class WorldArchitect:
    """
    World Architect Agent - creates detailed world specifications.

    This agent uses gpt-4o-mini to:
    - Design world rules (magic systems, technology levels, societal structures)
    - Define geography (continents, regions, key locations)
    - Establish history (major events, timeline)
    - Set themes and atmosphere

    Uses PipelineStage.STRUCTURE for model selection.
    """

    SYSTEM_PROMPT = """You are the World Architect for a literary production system.

Your role is to create rich, internally consistent world specifications for stories.

## Your responsibilities:
1. **World Rules** - Magic systems, technology level, physics, societal laws
2. **Geography** - Continents, regions, key locations, climate
3. **History** - Major historical events, timeline, world-shaping moments
4. **Themes** - Core themes that permeate the world

## Output Format:
Return ONLY a valid JSON object with this structure:
{
  "world_name": "string",
  "summary": "string (max 400 words - concise overview)",
  "rules": [
    "Rule 1: Magic requires personal sacrifice",
    "Rule 2: Technology is steam-powered only",
    "Rule 3: No faster-than-light travel"
  ],
  "geography": {
    "continents": ["Continent 1", "Continent 2"],
    "key_locations": ["Capital City", "Ancient Ruins"],
    "climate": "temperate with harsh winters"
  },
  "history": [
    {"year": -1000, "event": "The Great Sundering"},
    {"year": 0, "event": "Foundation of the Empire"},
    {"year": 523, "event": "The Long Night begins"}
  ],
  "themes": ["power and corruption", "hope vs despair", "technology vs nature"]
}

## Guidelines:
- Keep summary under 400 words (aim for 200-300)
- Define 3-7 clear, enforceable rules
- Create 2-4 major continents/regions
- Include 5-10 key historical events
- Extract 2-4 core themes
- Ensure internal consistency
- Make rules specific and actionable
- Avoid clichés unless specifically requested

## Genre-Specific Guidance:
- **Fantasy**: Magic systems, mythical creatures, ancient civilizations
- **Sci-Fi**: Technology level, FTL capability, alien contact, social structures
- **Thriller/Mystery**: Modern setting, institutions (police, government), social dynamics
- **Historical**: Accurate time period, real events blended with fiction
- **Horror**: Supernatural rules, sources of dread, boundaries between normal/abnormal

## Example (Fantasy):
{
  "world_name": "Aethermoor",
  "summary": "A post-apocalyptic fantasy world where magic once flourished but now lingers only in fragments. Three continents remain habitable after the Sundering, connected by sky-ships powered by rare aether crystals. Society has regressed to feudalism, with knowledge hoarded by mage-guilds.",
  "rules": [
    "Magic requires aether crystals, which are finite and irreplaceable",
    "Using magic drains the user's life force proportionally",
    "The Void between continents is impassable except by sky-ship",
    "Technology beyond Renaissance level fails near active magic"
  ],
  "geography": {
    "continents": ["Nordreach", "The Shattered Isles", "Sunward Territories"],
    "key_locations": ["Skyhaven (capital)", "Crystal Mines of Durn", "The Dead City"],
    "climate": "temperate with magical storm seasons"
  },
  "history": [
    {"year": -500, "event": "The Golden Age of magic reaches its zenith"},
    {"year": 0, "event": "The Sundering - continents torn apart by magical catastrophe"},
    {"year": 150, "event": "Discovery of aether crystals enables sky travel"},
    {"year": 300, "event": "Formation of the Mage Guilds"},
    {"year": 498, "event": "Present day - crystals running out"}
  ],
  "themes": ["scarcity and power", "knowledge vs wisdom", "rebuilding after collapse"]
}
"""

    def __init__(self, openai_client: OpenAIClient | None = None) -> None:
        """
        Initialize World Architect agent.

        Args:
            openai_client: OpenAI client for API calls (creates new if None)
        """
        self.client = openai_client or OpenAIClient()
        self.stage = PipelineStage.STRUCTURE
        self.model = ModelPolicy.get_model_for_stage(self.stage)
        self.temperature = ModelPolicy.get_temperature_for_stage(self.stage)
        self.token_budget = ModelPolicy.get_token_budget_for_stage(self.stage)

    async def create_world(self, request: WorldRequest) -> WorldResponse:
        """
        Create world specification based on genre and themes.

        Args:
            request: WorldRequest with genre, themes, constraints

        Returns:
            WorldResponse with world_id and specification

        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        logger.info(
            "WorldArchitect starting",
            extra={
                "job_id": str(request.job_id),
                "genre": request.genre,
                "themes_count": len(request.themes),
                "stage": self.stage.value,
            },
        )

        # Build user prompt
        user_prompt = f"""Create a world specification for a {request.genre} story.

Themes to incorporate: {", ".join(request.themes) if request.themes else "standard genre themes"}
"""

        if request.constraints:
            user_prompt += f"\nConstraints: {json.dumps(request.constraints)}"

        if request.summary:
            user_prompt += f"\nUser guidance: {request.summary}"

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
            world_data = json.loads(result["content"])
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse WorldArchitect response",
                extra={"response": result["content"][:200]},
            )
            raise ValueError(f"Invalid JSON response from WorldArchitect: {exc}") from exc

        # Validate required fields
        required = ["world_name", "summary", "rules"]
        missing = [f for f in required if f not in world_data]
        if missing:
            raise ValueError(f"WorldArchitect response missing fields: {', '.join(missing)}")

        # Generate world ID
        world_id = uuid4()

        # Extract data
        world_name = world_data["world_name"]
        summary = world_data["summary"]
        rules = world_data.get("rules", [])
        themes = world_data.get("themes", request.themes)

        logger.info(
            "WorldArchitect completed",
            extra={
                "job_id": str(request.job_id),
                "world_id": str(world_id),
                "world_name": world_name,
                "rules_count": len(rules),
                "cost_usd": result["cost"],
            },
        )

        # Build response
        response = WorldResponse(
            id=world_id,
            job_id=request.job_id,
            agent="architekt_swiata",
            stage=self.stage,
            world_id=world_id,
            world_name=world_name,
            summary=summary,
            rules=rules,
            themes=themes if isinstance(themes, list) else [themes],
            created_at=result.get("created_at") or datetime.utcnow(),
        )

        return response

    def create_world_schema(
        self, response: WorldResponse, world_data: dict[str, Any]
    ) -> WorldSchema:
        """
        Convert WorldResponse to WorldSchema for database storage.

        Args:
            response: WorldResponse from create_world
            world_data: Raw world data from OpenAI

        Returns:
            WorldSchema ready for database persistence
        """
        import datetime

        checksum = hashlib.sha256(json.dumps(world_data, sort_keys=True).encode()).hexdigest()

        return WorldSchema(
            id=response.world_id,
            name=response.world_name,
            rules=response.rules,
            geography=world_data.get("geography", {}),
            history=world_data.get("history", []),
            themes=response.themes,
            version=1,
            checksum=checksum,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )

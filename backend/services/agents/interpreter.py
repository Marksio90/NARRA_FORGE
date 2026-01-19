"""Interpreter Agent - analyzes user requests and extracts parameters."""

import json
import logging
from datetime import datetime

from models.schemas.agent import InterpretRequest, InterpretResponse
from services.model_policy import ModelPolicy, PipelineStage
from services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class Interpreter:
    """
    Interpreter Agent - analyzes user prompts and extracts structured parameters.

    This agent uses gpt-4o-mini to:
    - Identify genre (fantasy, sci-fi, thriller, etc.)
    - Determine work length (short_story, novella, novel, saga)
    - Extract themes and constraints
    - Validate and structure user intent

    Uses PipelineStage.STRUCTURE for model selection.
    """

    SYSTEM_PROMPT = """You are the Interpreter Agent for a literary production system.

Your role is to analyze user requests and extract structured parameters for story generation.

## Extract these parameters:
1. **genre** - One of: fantasy, sci-fi, thriller, mystery, horror, romance, historical, literary, dystopian, urban_fantasy
2. **length** - One of: short_story (5-15k words), novella (15-40k words), novel (40-120k words), saga (120k+ words)
3. **themes** - List of major themes (e.g., ["redemption", "power", "identity"])
4. **setting** - Time period and location
5. **tone** - Overall mood (dark, lighthearted, epic, intimate, etc.)
6. **target_audience** - Who is this for? (YA, adult, literary fiction readers, etc.)

## Output Format:
Return ONLY a valid JSON object with this structure:
{
  "genre": "string",
  "length": "string",
  "themes": ["string"],
  "setting": "string",
  "tone": "string",
  "target_audience": "string",
  "constraints": {
    "max_characters": number (optional),
    "setting": "string (optional)",
    "tone": "string (optional)"
  }
}

## Guidelines:
- If the user doesn't specify something, make an intelligent guess based on context
- Be conservative with length - default to shorter unless explicitly requested
- Extract 2-4 core themes maximum
- Keep constraints minimal and actionable
- Ensure genre is from the allowed list

## Example:
User: "I want an epic fantasy story about a reluctant hero in a steampunk world"
Output:
{
  "genre": "fantasy",
  "length": "novel",
  "themes": ["reluctant heroism", "technology and magic", "destiny"],
  "setting": "steampunk fantasy world",
  "tone": "epic",
  "target_audience": "adult fantasy readers",
  "constraints": {
    "setting": "steampunk",
    "tone": "epic"
  }
}
"""

    def __init__(self, openai_client: OpenAIClient | None = None) -> None:
        """
        Initialize Interpreter agent.

        Args:
            openai_client: OpenAI client for API calls (creates new if None)
        """
        self.client = openai_client or OpenAIClient()
        self.stage = PipelineStage.STRUCTURE
        self.model = ModelPolicy.get_model_for_stage(self.stage)
        self.temperature = ModelPolicy.get_temperature_for_stage(self.stage)
        self.token_budget = ModelPolicy.get_token_budget_for_stage(self.stage)

    async def interpret(self, request: InterpretRequest) -> InterpretResponse:
        """
        Interpret user prompt and extract structured parameters.

        Args:
            request: InterpretRequest with job_id and user_prompt

        Returns:
            InterpretResponse with extracted parameters

        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        logger.info(
            "Interpreter starting",
            extra={
                "job_id": str(request.job_id),
                "prompt_length": len(request.user_prompt),
                "stage": self.stage.value,
            },
        )

        # Build messages
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": request.user_prompt},
        ]

        # Add context if provided
        if request.context:
            context_msg = f"\nAdditional context: {json.dumps(request.context)}"
            messages.append({"role": "user", "content": context_msg})

        # Call OpenAI
        result = await self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            token_budget=self.token_budget,
        )

        # Parse JSON response
        try:
            parameters = json.loads(result["content"])
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse Interpreter response",
                extra={"response": result["content"]},
            )
            raise ValueError(f"Invalid JSON response from Interpreter: {exc}") from exc

        # Validate required fields
        if "genre" not in parameters or "length" not in parameters:
            raise ValueError("Interpreter response missing required fields: genre, length")

        # Extract themes
        themes = parameters.get("themes", [])
        if not isinstance(themes, list):
            themes = [str(themes)]

        logger.info(
            "Interpreter completed",
            extra={
                "job_id": str(request.job_id),
                "genre": parameters.get("genre"),
                "length": parameters.get("length"),
                "themes_count": len(themes),
                "cost_usd": result["cost"],
            },
        )

        # Build response
        response = InterpretResponse(
            id=request.job_id,  # Use job_id as response ID for now
            job_id=request.job_id,
            agent="interpreter",
            stage=self.stage,
            parameters=parameters,
            genre=parameters.get("genre"),
            length=parameters.get("length"),
            themes=themes,
            created_at=result.get("created_at") or datetime.utcnow(),
        )

        return response

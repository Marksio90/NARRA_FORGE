"""Plot Creator Agent - creates narrative structure and plot outlines."""

import json
import logging
from datetime import datetime
from uuid import uuid4

from models.schemas.agent import PlotRequest, PlotResponse
from services.model_policy import ModelPolicy, PipelineStage
from services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class PlotCreator:
    """
    Plot Creator Agent - creates detailed plot structures with acts and scenes.

    This agent uses gpt-4o-mini to:
    - Design plot structure (three-act, hero's journey, etc.)
    - Break down story into acts and scenes
    - Identify major conflicts and turning points
    - Ensure narrative coherence

    Uses PipelineStage.PLAN for model selection.
    """

    SYSTEM_PROMPT = """You are the Plot Creator for a literary production system.

Your role is to create detailed plot structures that guide narrative development.

## Your responsibilities:
1. **Plot Structure** - Overall narrative architecture (three-act, five-act, hero's journey, etc.)
2. **Acts** - Major story divisions with clear purposes
3. **Scenes** - Individual narrative units within acts
4. **Conflicts** - Central tensions that drive the story

## Output Format:
Return ONLY a valid JSON object with this structure:
{
  "plot_id": "generated-uuid",
  "structure": "three-act|five-act|heros-journey|kishōtenketsu",
  "summary": "string (max 400 words - plot overview)",
  "acts": [
    {
      "number": 1,
      "name": "Setup",
      "description": "Introduce protagonist, establish normal world, inciting incident",
      "scenes": [1, 2, 3, 4]
    },
    {
      "number": 2,
      "name": "Confrontation",
      "description": "Escalating challenges, midpoint revelation, darkest moment",
      "scenes": [5, 6, 7, 8, 9, 10]
    },
    {
      "number": 3,
      "name": "Resolution",
      "description": "Climax, final confrontation, resolution, denouement",
      "scenes": [11, 12, 13, 14]
    }
  ],
  "scenes": [
    {
      "number": 1,
      "act": 1,
      "description": "Protagonist's ordinary world - establish baseline",
      "characters": ["Kael"],
      "purpose": "introduction",
      "conflict": "none yet"
    },
    {
      "number": 2,
      "act": 1,
      "description": "Lyra goes missing - inciting incident",
      "characters": ["Kael", "Elder Moira"],
      "purpose": "call to action",
      "conflict": "Kael must choose: hide or help"
    }
  ],
  "conflicts": [
    "Man vs Self: Kael's guilt and fear of failure",
    "Man vs Man: Kael vs The Shadowmancer",
    "Man vs Society: Magic users hunted by fearful populace"
  ]
}

## Guidelines:
- Structure should match story length and genre
- Acts must have clear purposes (setup, escalation, resolution)
- Each scene should advance plot OR deepen character
- Include 10-30 scenes depending on length:
  * Short story: 8-12 scenes
  * Novella: 15-25 scenes
  * Novel: 30-60 scenes
- Scenes should be atomic narrative units
- Identify 2-5 major conflicts
- Ensure causality (each scene flows from previous)

## Structure Types:

**Three-Act Structure** (Western standard):
- Act 1 (25%): Setup, inciting incident, first plot point
- Act 2 (50%): Rising action, midpoint, darkest moment
- Act 3 (25%): Climax, resolution, denouement

**Five-Act Structure** (Shakespearean):
- Act 1: Exposition
- Act 2: Rising Action
- Act 3: Climax
- Act 4: Falling Action
- Act 5: Denouement

**Hero's Journey** (Campbell):
- Ordinary World → Call to Adventure → Refusal → Meeting Mentor
- Crossing Threshold → Tests → Approach → Ordeal
- Reward → Road Back → Resurrection → Return

**Kishōtenketsu** (Eastern, no conflict):
- Ki (introduction) → Shō (development) → Ten (twist) → Ketsu (conclusion)

## Scene Structure:
Each scene should have:
1. **Purpose**: What it accomplishes (introduction, revelation, confrontation, etc.)
2. **Characters**: Who appears
3. **Conflict**: What tension exists (can be "none" for breathers)
4. **Description**: 1-2 sentence summary

## Example (Fantasy, Three-Act, 14 scenes):
{
  "structure": "three-act",
  "summary": "Kael, a guilt-ridden former mage, must rescue his apprentice Lyra from his corrupted former friend. As he confronts his past failures, Kael must decide whether to embrace his power again or lose everything. The story explores redemption, the corrupting nature of power, and the courage to try again after failure.",
  "acts": [
    {
      "number": 1,
      "name": "The Reluctant Hero",
      "description": "Establish Kael's broken state, Lyra's capture, and the impossible choice to return to magic",
      "scenes": [1, 2, 3, 4, 5]
    },
    {
      "number": 2,
      "name": "Journey to Redemption",
      "description": "Kael's quest to save Lyra, confronting failures, regaining partial power, discovering the Shadowmancer's plan",
      "scenes": [6, 7, 8, 9, 10]
    },
    {
      "number": 3,
      "name": "The Final Confrontation",
      "description": "Kael vs Shadowmancer, Lyra's choice, resolution of Kael's arc",
      "scenes": [11, 12, 13, 14]
    }
  ],
  "scenes": [
    {
      "number": 1,
      "act": 1,
      "description": "Kael living in hiding, refusing to use magic, haunted by nightmares of past failure",
      "characters": ["Kael"],
      "purpose": "establish protagonist's broken state",
      "conflict": "Man vs Self: guilt and fear"
    },
    {
      "number": 2,
      "act": 1,
      "description": "Elder Moira arrives: Lyra has been captured by the Shadowmancer",
      "characters": ["Kael", "Elder Moira"],
      "purpose": "inciting incident",
      "conflict": "Man vs Self: face past or hide"
    },
    {
      "number": 3,
      "act": 1,
      "description": "Kael refuses, but memories of Lyra's enthusiasm haunt him",
      "characters": ["Kael"],
      "purpose": "refusal of call",
      "conflict": "Man vs Self: responsibility vs fear"
    },
    {
      "number": 4,
      "act": 1,
      "description": "Moira reveals the Shadowmancer is Aldric - Kael's former friend thought dead",
      "characters": ["Kael", "Elder Moira"],
      "purpose": "raise stakes, personal connection",
      "conflict": "Man vs Past: old wounds reopened"
    },
    {
      "number": 5,
      "act": 1,
      "description": "Kael accepts mission, begins journey, first tentative use of magic",
      "characters": ["Kael"],
      "purpose": "crossing threshold, commitment",
      "conflict": "Man vs Self: trusting power again"
    },
    {
      "number": 6,
      "act": 2,
      "description": "Travel montage, Kael gradually regaining skills",
      "characters": ["Kael"],
      "purpose": "character development",
      "conflict": "none (breather)"
    },
    {
      "number": 7,
      "act": 2,
      "description": "Encounter with Shadowmancer's minions, Kael hesitates at crucial moment",
      "characters": ["Kael", "Dark Mages"],
      "purpose": "test of progress",
      "conflict": "Man vs Man, Man vs Self"
    },
    {
      "number": 8,
      "act": 2,
      "description": "Discovers Lyra is being groomed as Shadowmancer's apprentice, not killed",
      "characters": ["Kael", "Informant"],
      "purpose": "midpoint revelation",
      "conflict": "Man vs Man: race against corruption"
    },
    {
      "number": 9,
      "act": 2,
      "description": "Kael infiltrates Shadowmancer's fortress, nearly succeeds",
      "characters": ["Kael", "Lyra"],
      "purpose": "false victory",
      "conflict": "Man vs Man: confrontation"
    },
    {
      "number": 10,
      "act": 2,
      "description": "Ambush: Kael is overpowered, Lyra doesn't recognize him as savior",
      "characters": ["Kael", "Lyra", "The Shadowmancer"],
      "purpose": "darkest moment, all is lost",
      "conflict": "Man vs Man, Man vs Self: total failure"
    },
    {
      "number": 11,
      "act": 3,
      "description": "Kael imprisoned, confronts Shadowmancer about their shared past",
      "characters": ["Kael", "The Shadowmancer"],
      "purpose": "revelation of antagonist motivation",
      "conflict": "Man vs Man: ideological clash"
    },
    {
      "number": 12,
      "act": 3,
      "description": "Lyra secretly visits Kael, seeds of doubt planted, Kael escapes",
      "characters": ["Kael", "Lyra"],
      "purpose": "turn Lyra back, preparation for climax",
      "conflict": "Man vs Man: battle for Lyra's soul"
    },
    {
      "number": 13,
      "act": 3,
      "description": "Final battle: Kael fully embraces power, defeats Shadowmancer, offers redemption",
      "characters": ["Kael", "The Shadowmancer", "Lyra"],
      "purpose": "climax, character transformation complete",
      "conflict": "Man vs Man: final confrontation"
    },
    {
      "number": 14,
      "act": 3,
      "description": "Aftermath: Kael becomes mentor to Lyra properly, at peace with past",
      "characters": ["Kael", "Lyra", "Elder Moira"],
      "purpose": "resolution, new normal",
      "conflict": "none (denouement)"
    }
  ],
  "conflicts": [
    "Man vs Self: Kael's guilt over past failure and fear of repeating it",
    "Man vs Man: Kael vs The Shadowmancer (former friend)",
    "Man vs Society: Magic users hunted and feared",
    "Man vs Nature: The corrupting influence of dark magic"
  ]
}
"""

    def __init__(self, openai_client: OpenAIClient | None = None) -> None:
        """
        Initialize Plot Creator agent.

        Args:
            openai_client: OpenAI client for API calls (creates new if None)
        """
        self.client = openai_client or OpenAIClient()
        self.stage = PipelineStage.PLAN
        self.model = ModelPolicy.get_model_for_stage(self.stage)
        self.temperature = ModelPolicy.get_temperature_for_stage(self.stage)
        self.token_budget = ModelPolicy.get_token_budget_for_stage(self.stage)

    async def create_plot(self, request: PlotRequest) -> PlotResponse:
        """
        Create plot structure with acts and scenes.

        Args:
            request: PlotRequest with world_id, character_ids, structure

        Returns:
            PlotResponse with plot_id and structure summary

        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        logger.info(
            "PlotCreator starting",
            extra={
                "job_id": str(request.job_id),
                "world_id": str(request.world_id),
                "character_count": len(request.character_ids),
                "stage": self.stage.value,
            },
        )

        # Build user prompt
        user_prompt = f"""Create a plot structure for a story.

Characters: {len(request.character_ids)} characters defined
World: Established world setting
"""

        if request.structure:
            user_prompt += f"\nPreferred structure: {request.structure}"

        if request.summary:
            user_prompt += f"\nPlot seed: {request.summary}"

        user_prompt += """

Requirements:
- Structure must fit the story scope
- Each scene must serve a purpose
- Ensure causality and logic
- Balance action, character development, and plot advancement
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
            plot_data = json.loads(result["content"])
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse PlotCreator response",
                extra={"response": result["content"][:200]},
            )
            raise ValueError(f"Invalid JSON response from PlotCreator: {exc}") from exc

        # Validate structure
        required = ["acts", "scenes", "summary"]
        missing = [f for f in required if f not in plot_data]
        if missing:
            raise ValueError(f"PlotCreator response missing fields: {', '.join(missing)}")

        # Generate plot ID
        plot_id = uuid4()

        # Extract data
        acts = plot_data.get("acts", [])
        scenes = plot_data.get("scenes", [])
        summary = plot_data.get("summary", "")

        logger.info(
            "PlotCreator completed",
            extra={
                "job_id": str(request.job_id),
                "plot_id": str(plot_id),
                "acts_count": len(acts),
                "scenes_count": len(scenes),
                "cost_usd": result["cost"],
            },
        )

        # Build response
        response = PlotResponse(
            id=plot_id,
            job_id=request.job_id,
            agent="kreator_fabuly",
            stage=self.stage,
            plot_id=plot_id,
            summary=summary,
            acts=len(acts),
            scenes=len(scenes),
            created_at=result.get("created_at") or datetime.utcnow(),
        )

        return response

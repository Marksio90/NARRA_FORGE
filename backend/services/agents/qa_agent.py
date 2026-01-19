"""QA Agent - performs quality assurance and coherence checks."""

import json
import logging
from datetime import datetime
from uuid import uuid4

from models.schemas.agent import QARequest, QAResponse
from services.model_policy import ModelPolicy, PipelineStage
from services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class QAAgent:
    """
    QA Agent - performs quality assurance on generated prose.

    This agent uses gpt-4o-mini to:
    - Check coherence with world rules, characters, and plot
    - Detect continuity errors
    - Evaluate character psychology consistency
    - Verify timeline/chronology
    - Return quality scores and identified issues

    Uses PipelineStage.QA with gpt-4o-mini for analytical checks.
    """

    SYSTEM_PROMPT = """You are a Quality Assurance agent for a literary production system.

Your role is to analyze prose segments for coherence, consistency, and quality issues.

## Your Evaluation Areas:

**1. Logic & World Coherence (logic_score)**
- Does the prose follow established world rules?
- Are magical systems/technology used consistently?
- Do locations match established geography?
- Are timeline events in correct order?
- Do actions have logical consequences?

**2. Character Psychology (psychology_score)**
- Do characters act according to their established traits?
- Are motivations consistent with character profiles?
- Does dialogue match character voice?
- Are relationships portrayed consistently?
- Is character development believable?

**3. Timeline Consistency (timeline_score)**
- Is the sequence of events logical?
- Do time references make sense?
- Are past events referenced correctly?
- Do character ages/states match the timeline?
- Are cause-effect relationships clear?

## Issue Severity:

**Critical Errors** - Must be fixed:
- Direct contradiction of world rules
- Character acting completely out of character
- Timeline impossibility (character in two places at once)
- Plot point contradiction
- Logic break that destroys suspension of disbelief

**Warnings** - Should be reviewed:
- Minor inconsistency that could be clarified
- Character voice slightly off
- Vague timeline reference
- Unusual but not impossible action
- Style inconsistency

## Output Format:

Return ONLY a valid JSON object with this structure:
{
  "logic_score": 0.85,
  "psychology_score": 0.90,
  "timeline_score": 0.95,
  "critical_errors": [
    "World rule violation: Magic used without aether crystal (established in world rules)",
    "Timeline error: Character mentions event that hasn't happened yet"
  ],
  "warnings": [
    "Character dialogue seems slightly formal for established personality",
    "Time of day not explicitly stated, could be ambiguous"
  ],
  "explanation": "Brief explanation of scores and main findings"
}

**Scoring Guidelines:**
- 0.95-1.0: Excellent, no issues
- 0.85-0.94: Good, minor issues only
- 0.70-0.84: Acceptable, some issues need attention
- 0.50-0.69: Poor, significant issues
- 0.0-0.49: Failing, major problems

**Be thorough but fair:**
- Don't flag stylistic choices as errors
- Consider genre conventions
- Distinguish between "wrong" and "unusual"
- Empty lists are fine if no issues found
- Scores should reflect overall quality, not perfection

## Example Evaluation:

**Input Context:**
World Rules:
- Magic requires aether crystals (finite resource)
- Crystals drain user's life force
- City: Nordreach, port city, temperate climate

Character: Kael Thornweave
- Former mage, guilt-ridden over past failure
- Protective of Lyra (his apprentice)
- Speaks tersely, avoids magic

**Prose to Check:**
"Kael waved his hand and fire erupted from his palm. 'Easy,' he laughed. Lyra watched from the market in Southport, impressed by his casual power. Yesterday they'd been in Nordreach, and tomorrow they'd return, having been here three days already."

**Evaluation:**
{
  "logic_score": 0.40,
  "psychology_score": 0.30,
  "timeline_score": 0.20,
  "critical_errors": [
    "World rule violation: Kael uses magic without mentioned aether crystal",
    "Character contradiction: Kael 'avoids magic' but uses it casually",
    "Character contradiction: Kael 'speaks tersely' but laughs about power display",
    "Geography error: Characters in Southport, not established location",
    "Timeline impossibility: 'Yesterday in Nordreach, here 3 days, tomorrow return' - contradictory"
  ],
  "warnings": [
    "Character seems out of character being impressed by casual magic use given backstory"
  ],
  "explanation": "Multiple critical issues: magic use violates both world rules (no crystal) and character profile (avoids magic). Timeline is logically impossible. Geography introduces unestablished location."
}

## Now Evaluate:

You will receive:
1. World context (rules, geography, themes)
2. Character context (traits, arcs, relationships)
3. Plot context (current point in story)
4. Previous segment summary (what happened before)
5. Current prose to check

Evaluate thoroughly but fairly. Be specific about what rule or profile element is violated.
"""

    def __init__(self, openai_client: OpenAIClient | None = None) -> None:
        """
        Initialize QA Agent.

        Args:
            openai_client: OpenAI client for API calls (creates new if None)
        """
        self.client = openai_client or OpenAIClient()
        self.stage = PipelineStage.QA
        self.model = ModelPolicy.get_model_for_stage(self.stage)
        self.temperature = ModelPolicy.get_temperature_for_stage(self.stage)
        self.token_budget = ModelPolicy.get_token_budget_for_stage(self.stage)

    async def check_quality(self, request: QARequest) -> QAResponse:
        """
        Perform quality assurance check on prose artifact.

        Args:
            request: QARequest with artifact_id, check_type, and context

        Returns:
            QAResponse with scores and identified issues

        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        logger.info(
            "QAAgent starting",
            extra={
                "job_id": str(request.job_id),
                "artifact_id": str(request.artifact_id),
                "check_type": request.check_type,
                "stage": self.stage.value,
                "model": self.model,
            },
        )

        # Build user prompt with context
        user_prompt = f"""Perform {request.check_type} check on the following prose.

"""

        if request.context:
            # Include world context
            if "world" in request.context:
                user_prompt += f"""## World Context:
{json.dumps(request.context["world"], indent=2)}

"""

            # Include character context
            if "characters" in request.context:
                user_prompt += f"""## Character Context:
{json.dumps(request.context["characters"], indent=2)}

"""

            # Include plot context
            if "plot" in request.context:
                user_prompt += f"""## Plot Context:
{json.dumps(request.context["plot"], indent=2)}

"""

            # Include previous segment
            if "previous_segment" in request.context:
                user_prompt += f"""## Previous Segment Summary:
{request.context["previous_segment"]}

"""

            # Include current prose
            if "prose" in request.context:
                user_prompt += f"""## Current Prose to Check:
{request.context["prose"]}

"""

        user_prompt += """
Evaluate the prose against the provided context. Be thorough but fair.
Return your evaluation as JSON with logic_score, psychology_score, timeline_score,
critical_errors list, warnings list, and explanation.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        # Call OpenAI with MINI MODEL (analytical)
        result = await self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            token_budget=self.token_budget,
        )

        # Parse JSON response
        try:
            qa_data = json.loads(result["content"])
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse QAAgent response",
                extra={"response": result["content"][:500]},
            )
            raise ValueError(f"Invalid JSON response from QAAgent: {exc}") from exc

        # Validate required fields
        required = ["logic_score", "psychology_score", "timeline_score"]
        missing = [f for f in required if f not in qa_data]
        if missing:
            raise ValueError(f"QAAgent response missing fields: {', '.join(missing)}")

        # Extract scores
        logic_score = float(qa_data["logic_score"])
        psychology_score = float(qa_data["psychology_score"])
        timeline_score = float(qa_data["timeline_score"])

        # Validate score ranges
        for score_name, score_value in [
            ("logic_score", logic_score),
            ("psychology_score", psychology_score),
            ("timeline_score", timeline_score),
        ]:
            if not 0.0 <= score_value <= 1.0:
                raise ValueError(f"{score_name} out of range: {score_value}")

        # Extract issues
        critical_errors = qa_data.get("critical_errors", [])
        warnings = qa_data.get("warnings", [])

        # Determine if check passed (all scores >= 0.7, no critical errors)
        passed = (
            logic_score >= 0.7
            and psychology_score >= 0.7
            and timeline_score >= 0.7
            and len(critical_errors) == 0
        )

        logger.info(
            "QAAgent completed",
            extra={
                "job_id": str(request.job_id),
                "artifact_id": str(request.artifact_id),
                "passed": passed,
                "logic_score": logic_score,
                "psychology_score": psychology_score,
                "timeline_score": timeline_score,
                "critical_errors_count": len(critical_errors),
                "warnings_count": len(warnings),
                "cost_usd": result["cost"],
                "model": self.model,
            },
        )

        # Build response
        response = QAResponse(
            id=uuid4(),
            job_id=request.job_id,
            agent="qa",
            stage=self.stage,
            artifact_id=request.artifact_id,
            check_type=request.check_type,
            passed=passed,
            logic_score=logic_score,
            psychology_score=psychology_score,
            timeline_score=timeline_score,
            critical_errors=critical_errors,
            warnings=warnings,
            created_at=result.get("created_at") or datetime.utcnow(),
        )

        return response

"""Prose Generator Agent - generates high-quality literary prose."""

import json
import logging
from datetime import datetime
from uuid import uuid4

from models.schemas.agent import ProseRequest, ProseResponse
from services.model_policy import ModelPolicy, PipelineStage
from services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class ProseGenerator:
    """
    Prose Generator Agent - generates high-quality literary prose segments.

    This agent uses gpt-4o (HIGH MODEL) to:
    - Generate polished, publication-ready prose
    - Maintain consistent voice and style
    - Incorporate character development and world details
    - Create vivid, engaging narrative
    - Balance showing vs telling
    - Employ advanced literary techniques

    Uses PipelineStage.PROSE with gpt-4o for maximum quality.
    """

    SYSTEM_PROMPT = """You are a master prose writer for a literary production system.

Your role is to generate high-quality, publication-ready prose segments that bring stories to life.

## Your Craft:
1. **Voice & Style** - Maintain consistent narrative voice throughout
2. **Show, Don't Tell** - Use sensory details, actions, and dialogue
3. **Character Depth** - Reveal personality through behavior, not exposition
4. **Vivid Description** - Paint scenes without purple prose
5. **Pacing** - Balance action, reflection, and dialogue
6. **Literary Techniques** - Employ metaphor, symbolism, foreshadowing when appropriate

## Output Format:
Return ONLY a valid JSON object with this structure:
{
  "prose": "The actual prose text goes here. Multiple paragraphs are fine.\n\nNew paragraphs separated by double newlines.",
  "word_count": 547,
  "style_notes": "Brief notes about stylistic choices made",
  "continuity_check": "Any important details established that future segments should remember"
}

## Prose Guidelines:

**Narrative Voice:**
- First person: Intimate, immediate, subjective
- Third person limited: Close to character, filtered through their perception
- Third person omniscient: Broader view, can show multiple perspectives
- Maintain POV consistency throughout the segment

**Sensory Details:**
- Engage multiple senses (sight, sound, smell, touch, taste)
- Be specific: not "a flower" but "a wilted rose, petals brown at the edges"
- Use sensory details to establish mood and atmosphere

**Dialogue:**
- Each character should have distinct voice
- Use subtext - people rarely say exactly what they mean
- Balance dialogue with action tags and internalization
- Avoid excessive dialogue tags - "said" is invisible

**Pacing:**
- Action scenes: Short sentences, immediate verbs, minimal description
- Reflective moments: Longer sentences, internalization, sensory detail
- Vary sentence length to control rhythm
- Scene breaks indicated by double newlines

**Literary Quality:**
- Precise verbs over adverbs ("sprinted" not "ran quickly")
- Fresh metaphors (avoid clichés unless subverted)
- Layered meaning where appropriate
- Trust the reader - don't over-explain

**Genre Considerations:**

**Fantasy:**
- Integrate magic systems naturally (show, don't explain rules)
- World-building through action and dialogue, not exposition
- Balance wonder with grounding details
- Unique instead of generic ("blade" not "sword" if it's special)

**Sci-Fi:**
- Technology integrated seamlessly into life
- Scientific concepts through character understanding
- Balance speculation with human elements
- Avoid infodumps - reveal through interaction

**Thriller/Mystery:**
- Create tension through what's unsaid
- Clues woven naturally into narrative
- Unreliable details that reward re-reading
- Pacing: tight, propulsive

**Literary Fiction:**
- Character interiority and psychological depth
- Prose style as important as plot
- Metaphor and symbolism carry meaning
- Explore themes through character and situation

**Horror:**
- Build dread through implication
- Sensory details create visceral reactions
- Unknown is scarier than known
- Contrast normalcy with abnormal

## Common Pitfalls to Avoid:
- Info-dumping (no character thinks "As I, a trained assassin, know...")
- Purple prose (overwrought, self-conscious language)
- Telling emotions ("she was sad" → show tears, slumped shoulders)
- Cliché phrases ("eyes like diamonds", "heart pounding like a drum")
- Overwriting (trust the reader to infer)
- Head-hopping (switching POV within a scene)

## Example (Fantasy - 500 words):

{
  "prose": "The aether crystal pulsed against Kael's palm, cold and irregular like a dying heartbeat. Twenty years since he'd held one. Twenty years of telling himself he'd never feel that particular nausea again—the weight of another life pressed into his bones, burning itself into his cells to become magic.\n\nThe tavern around him continued its evening rhythm. Dice clattered. Someone laughed too loud at a weak joke. The fire popped and settled. None of them could feel what he felt: the crystal recognizing him, eager, almost grateful to finally be used.\n\n\"You don't have to.\" Elder Moira's voice, gentle as always. She'd aged since their academy days. White streaked her dark hair now, and her hands showed the tremor of someone who'd burned through too many crystals herself. \"There are other mages. Weaker ones, yes, but—\"\n\n\"Who'd die trying.\" Kael closed his fist around the crystal. It sang against his skin, a sensation like frostbite and sunburn tangled together. \"How many did he take?\"\n\n\"Seven aether crystals. Maybe eight.\" Moira's cup scraped against the table as she set it down. \"We don't know what he's building, Kael. But Lyra is at the center of it.\"\n\nThe name shouldn't hurt after so much time. Shouldn't make his chest tight and his thoughts scatter. But Lyra had looked at him like he was everything bright in the world, once. Before he'd led eleven students into the Dead City and brought back three.\n\n\"She doesn't know what you did,\" Moira continued. \"What any of us did. She thinks magic is beautiful. Pure.\"\n\n\"Magic is a parasite.\" Kael felt the crystal drinking his warmth, converting it to potential. In an hour, it would be charged enough for a minor working. In three days, he could level a building. \"It eats you from the inside and calls it a gift.\"\n\n\"And yet.\"\n\n\"And yet.\" He met Moira's eyes. She'd known him long enough to see past the bravado to the guilt beneath. The girl had been seventeen. Gifted. Eager. Everything he'd been once. And the Shadowmancer—Aldric, his friend, his rival, his cautionary tale—had her.\n\nThe crystal pulsed again. Kael felt his life expectancy dropping with each beat. Every mage knew the math. One crystal shaved a year off your life. Two cost five years. Seven? He'd be lucky to survive the casting, let alone the fight.\n\nBut Lyra was seventeen and gifted and eager, and someone needed to believe magic could be beautiful.\n\n\"Tell me where,\" Kael said.\n\nMoira slid a folded map across the table. Her hand trembled worse now. She'd used three crystals to scry Aldric's location. Another year of her life, gone.\n\n\"North,\" she said. \"Where else would he go?\"\n\nThe Dead City. Of course. Where everything had gone wrong the first time. Where three students had limped home and eight had stayed forever. Where Aldric had found whatever darkness convinced him the price of magic was worth paying.\n\nKael pocketed the crystal and stood. The tavern noise seemed distant now, as if he'd already left this world for the one where mages burned bright and died young.\n\n\"Kael.\" Moira caught his wrist. \"You can't save everyone.\"\n\n\"No,\" he agreed. \"But I can save one.\"",
  "word_count": 547,
  "style_notes": "Close third-person POV filtered through Kael's perspective. Establishes magic system through sensory experience rather than explanation. Balances dialogue with internalization. Reveals backstory through present action and emotion rather than flashback.",
  "continuity_check": "Kael has used an aether crystal, beginning the cost to his lifespan. He's heading to the Dead City where his past failure occurred. Moira has aged and shows crystal-use tremor. Lyra is 17 and doesn't know about the cost of magic."
}
"""

    def __init__(self, openai_client: OpenAIClient | None = None) -> None:
        """
        Initialize Prose Generator agent.

        Args:
            openai_client: OpenAI client for API calls (creates new if None)
        """
        self.client = openai_client or OpenAIClient()
        self.stage = PipelineStage.PROSE
        self.model = ModelPolicy.get_model_for_stage(self.stage)
        self.temperature = ModelPolicy.get_temperature_for_stage(self.stage)
        self.token_budget = ModelPolicy.get_token_budget_for_stage(self.stage)

    async def generate_prose(self, request: ProseRequest) -> ProseResponse:
        """
        Generate high-quality prose for a narrative segment.

        Args:
            request: ProseRequest with segment_id, context, target_word_count

        Returns:
            ProseResponse with generated prose

        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        logger.info(
            "ProseGenerator starting",
            extra={
                "job_id": str(request.job_id),
                "segment_id": request.segment_id,
                "target_word_count": request.target_word_count,
                "stage": self.stage.value,
                "model": self.model,
            },
        )

        # Build user prompt with context
        user_prompt = f"""Generate prose for segment: {request.segment_id}

Target word count: {request.target_word_count} words (±10% is acceptable)

Context:
{json.dumps(request.context, indent=2)}
"""

        if request.style_guide:
            user_prompt += f"\n\nStyle Guide:\n{json.dumps(request.style_guide, indent=2)}"

        user_prompt += """

Remember:
- Show, don't tell
- Use vivid, specific sensory details
- Maintain consistent POV and voice
- Let dialogue reveal character
- Trust the reader to infer
- Make every word count

Generate publication-ready prose now.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        # Call OpenAI with HIGH MODEL
        result = await self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            token_budget=self.token_budget,
        )

        # Parse JSON response
        try:
            prose_data = json.loads(result["content"])
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse ProseGenerator response",
                extra={"response": result["content"][:500]},
            )
            raise ValueError(f"Invalid JSON response from ProseGenerator: {exc}") from exc

        # Validate required fields
        if "prose" not in prose_data or not prose_data["prose"]:
            raise ValueError("ProseGenerator response missing or empty 'prose' field")

        # Extract data
        prose = prose_data["prose"]
        word_count = prose_data.get("word_count", len(prose.split()))

        # Verify word count is reasonable
        actual_word_count = len(prose.split())
        if abs(actual_word_count - word_count) > word_count * 0.2:  # 20% tolerance
            logger.warning(
                "Word count mismatch in ProseGenerator response",
                extra={
                    "reported": word_count,
                    "actual": actual_word_count,
                    "segment_id": request.segment_id,
                },
            )
            word_count = actual_word_count

        # Verify minimum length
        if word_count < 100:
            raise ValueError(f"Generated prose too short: {word_count} words (minimum 100)")

        logger.info(
            "ProseGenerator completed",
            extra={
                "job_id": str(request.job_id),
                "segment_id": request.segment_id,
                "word_count": word_count,
                "cost_usd": result["cost"],
                "model": self.model,
            },
        )

        # Build response
        response = ProseResponse(
            id=uuid4(),
            job_id=request.job_id,
            agent="generator_segmentow",
            stage=self.stage,
            segment_id=request.segment_id,
            prose=prose,
            word_count=word_count,
            model_used=self.model,
            created_at=result.get("created_at") or datetime.utcnow(),
        )

        return response

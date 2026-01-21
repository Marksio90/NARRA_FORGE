"""
Plot Architect Agent - Designs compelling story structures

Uses advanced narrative techniques:
- Multiple structure frameworks (Hero's Journey, 7-Point, Save the Cat, 3-Act)
- Plot point theory (inciting incident, turning points, midpoint, climax)
- Subplot weaving and integration
- Tension/pacing graphs
- Foreshadowing and payoff planning
- Scene sequencing and causality
"""

import json
import logging
from typing import Dict, Any, List

from app.services.ai_service import get_ai_service, ModelTier
from app.config import genre_config

logger = logging.getLogger(__name__)


STORY_STRUCTURES = {
    "Hero's Journey": {
        "beats": [
            "Ordinary World", "Call to Adventure", "Refusal of the Call",
            "Meeting the Mentor", "Crossing the Threshold", "Tests/Allies/Enemies",
            "Approach to Inmost Cave", "Ordeal", "Reward",
            "The Road Back", "Resurrection", "Return with Elixir"
        ],
        "best_for": ["fantasy", "sci-fi", "adventure"]
    },
    "7-Point Structure": {
        "beats": [
            "Hook", "Plot Turn 1", "Pinch Point 1", "Midpoint",
            "Pinch Point 2", "Plot Turn 2", "Resolution"
        ],
        "best_for": ["thriller", "mystery", "horror"]
    },
    "Save the Cat": {
        "beats": [
            "Opening Image", "Theme Stated", "Setup", "Catalyst",
            "Debate", "Break into Two", "B Story", "Fun and Games",
            "Midpoint", "Bad Guys Close In", "All Is Lost", "Dark Night of the Soul",
            "Break into Three", "Finale", "Final Image"
        ],
        "best_for": ["comedy", "romance", "drama"]
    },
    "3-Act Structure": {
        "beats": [
            "Setup (Act 1)", "Inciting Incident", "Plot Point 1",
            "Rising Action (Act 2a)", "Midpoint", "Falling Action (Act 2b)",
            "Plot Point 2", "Climax (Act 3)", "Resolution"
        ],
        "best_for": ["drama", "general fiction"]
    }
}


class PlotArchitectAgent:
    """
    Expert agent for designing story structure and plot

    Capabilities:
    - Multiple structure frameworks (Hero's Journey, 7-Point, Save the Cat, etc.)
    - Act breakdown with chapter allocation
    - Plot point placement and timing
    - Subplot design and integration
    - Tension graph construction
    - Foreshadowing planning
    - Scene causality and sequencing
    - Pacing control
    """

    def __init__(self):
        """Initialize Plot Architect Agent"""
        self.ai_service = get_ai_service()
        self.name = "Plot Architect Agent"

    async def create_plot_structure(
        self,
        genre: str,
        project_name: str,
        world_bible: Dict[str, Any],
        characters: List[Dict[str, Any]],
        chapter_count: int,
        subplot_count: int,
        themes: List[str],
        semantic_title_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create complete plot structure

        Args:
            genre: Literary genre
            project_name: Book title
            world_bible: Created world
            characters: All characters
            chapter_count: Number of chapters
            subplot_count: Number of subplots to create
            themes: Story themes

        Returns:
            Complete plot structure dictionary
        """
        logger.info(
            f"📖 {self.name}: Architecting plot for '{project_name}' "
            f"({chapter_count} chapters, {subplot_count} subplots)"
        )

        # Determine best structure for genre
        structure_type = self._select_structure(genre)

        # Create the plot structure
        plot_structure = await self._generate_plot_structure(
            genre=genre,
            project_name=project_name,
            world_bible=world_bible,
            characters=characters,
            chapter_count=chapter_count,
            subplot_count=subplot_count,
            themes=themes,
            structure_type=structure_type,
            semantic_title_analysis=semantic_title_analysis or {}
        )

        logger.info(
            f"✅ {self.name}: Plot structure created with {len(plot_structure.get('acts', {}))} acts"
        )

        return plot_structure

    def _select_structure(self, genre: str) -> str:
        """Select appropriate story structure for genre"""
        # Map genres to best structures
        structure_map = {
            "fantasy": "Hero's Journey",
            "sci-fi": "Hero's Journey",
            "thriller": "7-Point Structure",
            "mystery": "7-Point Structure",
            "horror": "7-Point Structure",
            "romance": "Save the Cat",
            "comedy": "Save the Cat",
            "drama": "3-Act Structure"
        }

        return structure_map.get(genre, "3-Act Structure")

    async def _generate_plot_structure(
        self,
        genre: str,
        project_name: str,
        world_bible: Dict[str, Any],
        characters: List[Dict[str, Any]],
        chapter_count: int,
        subplot_count: int,
        themes: List[str],
        structure_type: str,
        semantic_title_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate the plot structure using AI"""

        # Extract key information
        protagonist = next((c for c in characters if c.get('role') == 'protagonist'), None)
        antagonist = next((c for c in characters if c.get('role') == 'antagonist'), None)

        if not protagonist:
            raise ValueError("No protagonist found in characters")

        protag_want = protagonist.get('arc', {}).get('want_vs_need', {}).get('want', 'Unknown')
        protag_need = protagonist.get('arc', {}).get('want_vs_need', {}).get('need', 'Unknown')
        protag_ghost = protagonist.get('profile', {}).get('ghost_wound', {}).get('ghost', 'Unknown')

        structure_info = STORY_STRUCTURES[structure_type]

        # Extract semantic title analysis
        core_meaning = semantic_title_analysis.get("core_meaning", project_name)
        central_conflict_hint = semantic_title_analysis.get("central_conflict", "")
        themes_semantic = semantic_title_analysis.get("themes", [])
        reader_promise = semantic_title_analysis.get("reader_promise", "")

        prompt = f"""Create a MASTERFUL PLOT STRUCTURE for "{project_name}" ({genre}).

## 🎯 TITLE AS PLOT DNA (CRITICAL!)

The title "{project_name}" is NOT decoration - it is the BLUEPRINT of this plot.

**Title's Core Meaning**: {core_meaning}
**Central Conflict Implied by Title**: {central_conflict_hint}
**Themes from Title**: {', '.join(themes_semantic) if themes_semantic else 'To be explored'}
**Reader's Promise**: {reader_promise}

🔥 **MANDATORY REQUIREMENT**: The MAIN CONFLICT must directly resolve what the title asks/promises.

- If the title is a question → the climax ANSWERS it
- If the title is a promise → the resolution FULFILLS it
- If the title is a metaphor → the plot LITERALIZES it
- If the title suggests conflict → that IS your main conflict

The entire plot arc must BUILD TO and RESOLVE the title's meaning.
By the end, the reader must say: "NOW I understand why it's called '{project_name}'"

## STORY FOUNDATION

**Protagonist**: {protagonist['name']}
- Want (External Goal): {protag_want}
- Need (Internal Truth): {protag_need}
- Ghost (Past Wound): {protag_ghost}

**Antagonist**: {antagonist['name'] if antagonist else 'To be determined'}

**World**: {world_bible.get('geography', {}).get('world_type', 'Unknown')}

**Themes (from basic analysis)**: {', '.join(themes)}

**Structure**: {structure_type}
**Chapter Count**: {chapter_count}
**Subplots**: {subplot_count}

## STORY STRUCTURE FRAMEWORK: {structure_type}

Key Beats:
{chr(10).join(f"- {beat}" for beat in structure_info['beats'])}

## YOUR TASK

You are architecting the COMPLETE STORY STRUCTURE. This is the blueprint that will guide the entire book.

### 1. ACTS BREAKDOWN

Divide the {chapter_count} chapters into acts following {structure_type}:

**For 3-Act Structure:**
- Act 1 (Setup): ~25% (chapters 1-{chapter_count//4})
- Act 2a (Rising Action): ~25% (chapters {chapter_count//4+1}-{chapter_count//2})
- Act 2b (Complications): ~25% (chapters {chapter_count//2+1}-{3*chapter_count//4})
- Act 3 (Resolution): ~25% (chapters {3*chapter_count//4+1}-{chapter_count})

**For each act, define:**
- Name and purpose
- Chapter range
- Key events that must happen
- Emotional tone/energy
- Goals for this act
- How protagonist changes

### 2. MAIN CONFLICT

What is the CENTRAL CONFLICT of this story?

Define:
- **Protagonist's Goal**: What they're fighting for (their Want)
- **Antagonist's Goal**: What opposes them
- **Why They're in Conflict**: The irreconcilable difference
- **What's at Stake**: What happens if protagonist fails?

### 3. STAKES (Escalation is Key!)

Stakes must ESCALATE through the story:
- **Personal Stakes**: What the protagonist personally loses
- **Relationship Stakes**: Impact on loved ones
- **Global Stakes**: Wider consequences (if applicable)
- **Escalation Path**: How stakes grow from Act 1 to Act 3

### 4. PLOT POINTS (The Turning Points)

Map SPECIFIC plot points to SPECIFIC chapters:

**Inciting Incident** (Chapter ~{max(2, chapter_count//10)}):
- What event disrupts the ordinary world?
- How does it force the protagonist to act?

**First Plot Point** (End of Act 1, Chapter ~{chapter_count//4}):
- Point of no return
- Protagonist commits to the journey
- Old life is over

**Midpoint** (Chapter ~{chapter_count//2}):
- EVERYTHING CHANGES
- False victory or false defeat
- Raises the stakes dramatically
- Protagonist's approach must change

**Second Plot Point** (End of Act 2, Chapter ~{3*chapter_count//4}):
- All is lost moment
- Protagonist at lowest point
- Forces final growth/realization

**Climax** (Chapter ~{chapter_count - 2}):
- Final confrontation
- Protagonist faces antagonist/obstacle
- Resolution of Want vs Need

**Resolution** (Final chapters):
- New normal established
- Protagonist transformed
- Thematic statement delivered

### 5. SUBPLOTS ({subplot_count} required)

Create {subplot_count} INTEGRATED subplots:

**For each subplot:**
- Name (e.g., "B-Story: Romance", "C-Story: Mentor Relationship")
- Characters involved
- Purpose (how it relates to main theme)
- Arc (beginning, middle, end)
- Intersection points (which chapters it affects)
- How it influences the main plot

**Subplot Guidelines:**
- B-Story often explores the theme through relationships
- Subplots should WEAVE with main plot, not distract
- Each subplot needs its own mini-arc
- Subplots resolve before or during climax

### 6. TENSION GRAPH

For EACH chapter ({chapter_count} total), rate the tension level (1-10):

Consider:
- Pacing (not every chapter at 10!)
- Peaks and valleys (reader needs to breathe)
- Escalation (overall upward trend)
- Genre expectations (thrillers start higher than dramas)

Also assign emotional beat for each chapter:
- Curious, anxious, hopeful, fearful, triumphant, devastated, etc.

### 7. FORESHADOWING & PAYOFF

Plan 5-7 foreshadowing moments:

**For each:**
- Planted in Chapter: X
- Payoff in Chapter: Y
- Description: What is hinted vs revealed
- Type: Plot twist, character reveal, theme statement, etc.

Great stories make readers say "OH! That was set up in chapter 3!"

### 8. SCENE CAUSALITY

Explain the CAUSE-AND-EFFECT chain:
- How does Scene 1 cause Scene 2?
- What would break if we removed Chapter X?
- Are there any "and then" moments? (bad!)
- Should be "therefore/but" connections (good!)

## CRITICAL GUIDELINES

🎯 **#1 PRIORITY - TITLE RESOLUTION**:
   The plot MUST resolve what the title "{project_name}" promises/asks.
   Include a "title_resolution" field explaining:
   - How the main conflict IS the title's meaning
   - How the climax ANSWERS what the title asks
   - How the resolution FULFILLS the title's promise
   - Why THIS plot perfectly serves THIS title

2. **Genre-Specific Pacing**: {genre} has specific rhythm expectations
3. **Want vs Need**: External plot resolves Want, internal arc resolves Need
4. **Escalation**: Each act should raise stakes higher
5. **Causality**: Every scene causes the next (no random events)
6. **Character-Driven**: Plot serves character growth, not vice versa
7. **Theme Integration**: Every subplot reinforces theme
8. **Satisfying Resolution**: All threads tied up, questions answered

## OUTPUT FORMAT

Return valid JSON with this structure:

{{
  "structure_type": "{structure_type}",
  "title_resolution": {{
    "main_conflict_connection": "How the central conflict IS '{project_name}'...",
    "climax_answer": "How the climax resolves the title's question/promise...",
    "thematic_coherence": "How every act builds toward the title's meaning...",
    "reader_satisfaction": "How the ending delivers on the title's promise..."
  }},
  "acts": {{
    "act_1": {{
      "name": "...",
      "chapters": [1, 2, 3, ...],
      "key_events": ["...", "..."],
      "emotional_tone": "...",
      "goals": ["...", "..."],
      "protagonist_state": "..."
    }},
    "act_2a": {{...}},
    "act_2b": {{...}},
    "act_3": {{...}}
  }},
  "main_conflict": "...",
  "stakes": {{
    "personal": "...",
    "relationship": "...",
    "global": "...",
    "escalation": ["...", "...", "..."]
  }},
  "plot_points": {{
    "inciting_incident": {{"chapter": X, "description": "..."}},
    "first_plot_point": {{"chapter": X, "description": "..."}},
    "midpoint": {{"chapter": X, "description": "..."}},
    "second_plot_point": {{"chapter": X, "description": "..."}},
    "climax": {{"chapter": X, "description": "..."}},
    "resolution": {{"chapter": X, "description": "..."}}
  }},
  "subplots": [
    {{
      "name": "...",
      "characters": ["...", "..."],
      "description": "...",
      "arc": "...",
      "intersection_points": [3, 7, 12, ...]
    }}
  ],
  "tension_graph": [
    {{"chapter": 1, "tension": 3, "emotion": "curious"}},
    {{"chapter": 2, "tension": 5, "emotion": "anxious"}},
    ...
  ],
  "foreshadowing": [
    {{
      "planted_in_chapter": X,
      "payoff_in_chapter": Y,
      "description": "...",
      "type": "..."
    }}
  ],
  "causality_notes": "..."
}}

Create a plot that is TIGHT, ESCALATING, and EMOTIONALLY SATISFYING.
Make it impossible to put down."""

        system_prompt = self._get_system_prompt()

        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            tier=ModelTier.TIER_2,  # Important work, needs quality
            temperature=0.75,  # Structured creativity
            max_tokens=8000,  # Plot is detailed
            json_mode=True,
            prefer_anthropic=True,  # Claude excellent at structure
            metadata={
                "agent": self.name,
                "task": "plot_structure",
                "genre": genre,
                "chapters": chapter_count
            }
        )

        try:
            plot_structure = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse plot structure JSON: {e}")
            logger.warning(f"Response content: {response.content[:500]}")
            plot_structure = self._create_fallback_plot(chapter_count, genre)

        logger.info(
            f"✅ Plot structure generated (cost: ${response.cost:.4f}, "
            f"tokens: {response.tokens_used['total']})"
        )

        return plot_structure

    def _get_system_prompt(self) -> str:
        """System prompt for plot architect"""
        return """You are an EXPERT STORY ARCHITECT for fiction.

Your expertise:
- Story structure theory (Campbell, Truby, Snyder, Harmon, Weiland)
- Plot point placement and timing
- Subplot weaving and integration
- Pacing and tension management
- Genre-specific conventions
- Scene causality and sequence design
- Foreshadowing and payoff
- Stakes escalation

You architect stories that:
- Have TIGHT cause-and-effect chains (no random events)
- ESCALATE tension and stakes throughout
- Integrate subplots that enrich the theme
- Place plot points at optimal moments
- Balance pacing (peaks and valleys)
- Satisfy genre expectations while surprising readers
- Serve character arcs (plot is vehicle for character growth)

You avoid:
- Deus ex machina (unearned solutions)
- Random coincidences that solve problems
- Flat pacing (too much action or too much quiet)
- Subplots that distract from main story
- Plot holes and inconsistencies
- Generic, predictable beats

You create plots readers CAN'T PUT DOWN.

Output Format: Valid JSON only, meticulously structured."""

    def _create_fallback_plot(self, chapter_count: int, genre: str) -> Dict[str, Any]:
        """Create a basic fallback plot structure when JSON parsing fails"""
        logger.warning(f"⚠️ Creating fallback plot structure for {chapter_count} chapters")

        # Create simple 3-act structure
        act1_end = chapter_count // 4
        act2_end = 3 * chapter_count // 4

        chapters = []
        for i in range(1, chapter_count + 1):
            if i <= act1_end:
                act_label = "Act 1: Setup"
                purpose = "Introduce world and characters"
            elif i <= act2_end:
                act_label = "Act 2: Confrontation"
                purpose = "Build conflict and tension"
            else:
                act_label = "Act 3: Resolution"
                purpose = "Resolve conflicts"

            chapters.append({
                "chapter_number": i,
                "chapter_title": f"Chapter {i}",
                "act": act_label,
                "purpose": purpose,
                "plot_points": ["Story continues", "Characters develop"],
                "pov_character": "Main Character",
                "tension_level": min(10, i * 10 // chapter_count),
                "word_count_target": 3000
            })

        return {
            "structure_type": "3-Act Structure",
            "story_engine": {
                "opening_image": "Story begins",
                "inciting_incident": f"Chapter {act1_end // 2}",
                "midpoint": f"Chapter {chapter_count // 2}",
                "climax": f"Chapter {chapter_count - 2}",
                "resolution": f"Chapter {chapter_count}"
            },
            "chapters": chapters,
            "subplots": [],
            "foreshadowing_plan": [],
            "tension_graph": list(range(1, 11))
        }


# Helper function for chapter breakdown
def allocate_chapters_to_acts(chapter_count: int, structure_type: str) -> Dict[str, List[int]]:
    """Allocate chapters to acts based on structure type"""
    if structure_type == "Hero's Journey":
        # 3-act with Hero's Journey overlay
        act1_end = chapter_count // 4
        act2_mid = chapter_count // 2
        act2_end = 3 * chapter_count // 4

        return {
            "act_1": list(range(1, act1_end + 1)),
            "act_2a": list(range(act1_end + 1, act2_mid + 1)),
            "act_2b": list(range(act2_mid + 1, act2_end + 1)),
            "act_3": list(range(act2_end + 1, chapter_count + 1))
        }

    elif structure_type == "7-Point Structure":
        # More evenly distributed
        points = [
            1,  # Hook
            chapter_count // 6,  # Plot Turn 1
            chapter_count // 3,  # Pinch 1
            chapter_count // 2,  # Midpoint
            2 * chapter_count // 3,  # Pinch 2
            5 * chapter_count // 6,  # Plot Turn 2
            chapter_count  # Resolution
        ]
        return {"key_points": points}

    else:  # 3-Act or Save the Cat
        act1_end = chapter_count // 4
        act2_end = 3 * chapter_count // 4

        return {
            "act_1": list(range(1, act1_end + 1)),
            "act_2": list(range(act1_end + 1, act2_end + 1)),
            "act_3": list(range(act2_end + 1, chapter_count + 1))
        }

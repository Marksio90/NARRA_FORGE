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

        # Extract ADVANCED analysis
        conflicts = semantic_title_analysis.get("conflicts", {})
        pacing_suggestions = semantic_title_analysis.get("pacing_suggestions", {})
        secondary_plots = semantic_title_analysis.get("secondary_plots", [])
        reader_expectations = semantic_title_analysis.get("reader_expectations", {})

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

## ⚔️ CONFLICT LAYERS (From Advanced Analysis)
"""

        if conflicts:
            if conflicts.get('external'):
                prompt += f"- **External**: {conflicts['external']}\n"
            if conflicts.get('internal'):
                prompt += f"- **Internal**: {conflicts['internal']}\n"
            if conflicts.get('philosophical'):
                prompt += f"- **Philosophical**: {conflicts['philosophical']}\n"
            if conflicts.get('moral'):
                prompt += f"- **Moral**: {conflicts['moral']}\n"

        if pacing_suggestions:
            prompt += "\n## ⏱️ PACING GUIDANCE\n"
            if pacing_suggestions.get('overall_pace'):
                prompt += f"- **Overall Pace**: {pacing_suggestions['overall_pace']}\n"
            if pacing_suggestions.get('structure_type'):
                prompt += f"- **Structure Type**: {pacing_suggestions['structure_type']}\n"
            if pacing_suggestions.get('darkest_act'):
                prompt += f"- **Darkest Act**: {pacing_suggestions['darkest_act']}\n"
            if pacing_suggestions.get('tension_curve'):
                prompt += f"- **Tension Curve**: {pacing_suggestions['tension_curve']}\n"

        if secondary_plots:
            prompt += "\n## 🧵 SUGGESTED SUBPLOTS\n"
            for sp in secondary_plots[:5]:  # Top 5
                prompt += f"- **{sp.get('type', 'Unknown')}**: {sp.get('description', '')}\n"

        if reader_expectations:
            if reader_expectations.get('expected_scenes'):
                prompt += "\n## 📖 READER EXPECTATIONS\n"
                prompt += f"- **Expected Scenes**: {', '.join(reader_expectations['expected_scenes'][:5])}\n"

        prompt += "\n## THEMES (from basic analysis)"
        prompt += f"""
{', '.join(themes)}

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

### 6. TENSION & EMOTIONAL ARC GRAPH (READER EXPERIENCE!)

For EACH chapter ({chapter_count} total), map the **READER'S** emotional journey:

**Tension Level** (1-10 scale):
- 1-3: Low tension (breather, world-building, character moments)
- 4-6: Medium tension (complications, discoveries, conflicts)
- 7-8: High tension (crises, confrontations, revelations)
- 9-10: Maximum tension (climax, life-or-death, point of no return)

**Tension Pacing Rules**:
✅ NOT every chapter at 10 (exhausting!)
✅ Peaks and valleys (reader needs breathers)
✅ Overall UPWARD trend (escalation to climax)
✅ Genre-appropriate baseline:
  - Thriller: Start ~6, climb to 10
  - Romance: Start ~3, peaks at 7-8
  - Horror: Start ~4, slow build to 9-10
  - Drama: Start ~2, gradual to 7-8

**Emotional Beat** (Primary emotion reader feels):

Map to specific emotions (not vague!):
- **Curiosity**: "What's happening? I need to know more."
- **Anticipation**: "Something big is about to happen!"
- **Anxiety**: "I'm worried for the character."
- **Fear**: "This is dangerous, they're in trouble!"
- **Hope**: "Maybe they can do this!"
- **Triumph**: "Yes! They did it!"
- **Devastation**: "Oh no... everything's falling apart."
- **Anger**: "That's not fair! How dare they!"
- **Grief**: "I'm sad for what they've lost."
- **Relief**: "Thank god, they're safe now."
- **Dread**: "Something terrible is coming..."
- **Joy**: "This is wonderful!"
- **Betrayal**: "They were deceived!"
- **Resolve**: "They've made their choice."

**Emotional Arc Pattern Examples**:

**Thriller Arc**:
```
Ch1: Curiosity (3) → Ch5: Anxiety (6) → Ch10: Fear (8) →
Ch15: Dread (9) → Ch18: Triumph (7) → Ch20: Devastation (10)
```

**Romance Arc**:
```
Ch1: Curiosity (2) → Ch5: Hope (4) → Ch10: Joy (6) →
Ch15: Betrayal (8) → Ch18: Grief (5) → Ch20: Triumph (9)
```

**Horror Arc**:
```
Ch1: Unease (3) → Ch5: Anxiety (5) → Ch10: Fear (7) →
Ch15: Dread (8) → Ch18: Terror (10) → Ch20: Relief (4)
```

**Emotional Pacing Guidelines**:
✅ Vary emotions (not all anxiety!)
✅ Earn big emotions with setup (can't go 0→10 instantly)
✅ Give breathers after intense chapters
✅ Build to emotional peaks strategically
✅ End acts on strong emotions (hooks!)
✅ Climax = maximum emotional + tension convergence

**Reader Investment Checkpoints**:

Ask for each act:
- **End of Act 1**: Does reader CARE about protagonist? (If NO, fix!)
- **Midpoint**: Is reader INVESTED in outcome? (If NO, raise stakes!)
- **End of Act 2**: Is reader DESPERATE to know what happens? (If NO, amp tension!)
- **Climax**: Does reader FEEL the emotional weight? (If NO, earn it better!)
- **Resolution**: Does reader feel SATISFIED? (If NO, deliver on promises!)

**Emotional Variety Rule**:
Within any 5-chapter span, use at LEAST 3 different emotions.
(Prevents monotony, keeps reader engaged)

### 7. FORESHADOWING & PAYOFF TRACKER (Chekhov's Gun Management!)

**CRITICAL RULE**: If you show a gun in Act 1, it MUST fire by Act 3!

Plan 5-10 foreshadowing moments with METICULOUS tracking:

**Types of Foreshadowing**:

1. **Direct Foreshadowing** - Obvious hint reader notices
2. **Subtle Foreshadowing** - Easy to miss first read, "OH!" on reread
3. **Red Herring** - False trail (Mystery/Thriller primarily)
4. **Symbolic Foreshadowing** - Thematic objects/images
5. **Chekhov's Gun** - Object mentioned early, crucial later
6. **Prophecy/Promise** - Explicit prediction that comes true
7. **Character Skill/Knowledge** - Ability shown early, used later

**For EACH Foreshadowing Element, Provide**:

- **Type**: (Direct/Subtle/Red Herring/Symbolic/Chekhov's Gun/Prophecy/Skill)
- **Setup Chapter**: X (where planted)
- **Setup Description**: What reader sees/hears (SPECIFIC!)
- **Subtlety Level**: 1-10 (1=obvious, 10=nearly invisible)
- **Payoff Chapter**: Y (where revealed/used)
- **Payoff Description**: How it becomes significant
- **Time Gap**: Y - X chapters (longer = more satisfying)
- **Reader Impact**: Emotion created (satisfaction, shock, "I knew it!", etc.)
- **Mandatory**: true/false (Mandatory MUST pay off!)

**Foreshadowing Rules**:
✅ Minimum 5, maximum 15 elements
✅ EVERY Mandatory setup MUST have explicit payoff
✅ Payoffs concentrated in last 25% (climax/resolution)
✅ Red herrings: 1-3 for mystery/thriller, 0-1 others
✅ Vary subtlety (some obvious=anticipation, some hidden=surprise)
✅ Spread setups in Acts 1-2, payoffs in Acts 2-3
✅ Bigger reveals need longer time gaps (minimum 5+ chapters)
✅ NO deus ex machina - crucial items/skills must be seeded early!

**Examples**:

Strong Chekhov's Gun:
```
Type: Chekhov's Gun
Setup Chapter: 3
Setup: "Anna notices father's old revolver in drawer while searching for keys. 'Should get rid of that someday.' Closes drawer."
Subtlety: 4/10
Payoff Chapter: 18
Payoff: "Intruder breaks in. Anna remembers gun, uses it in climactic self-defense."
Time Gap: 15 chapters
Impact: "Oh! The gun from chapter 3!" - earned, not deus ex machina
Mandatory: true
```

Subtle Symbolic:
```
Type: Symbolic
Setup Chapter: 1
Setup: "Protagonist's watch broken, stopped at 3:47. She keeps wearing it."
Subtlety: 8/10
Payoff Chapter: 20
Payoff: "At 3:47 PM, confronts past trauma. Removes watch, smashes it. 'Time to move forward.'"
Time Gap: 19 chapters
Impact: Thematic resonance - watch = stuck in past
Mandatory: false
```

**Validation** (Answer for each):
✅ All Mandatory setups have payoffs?
✅ All payoffs later than setups?
✅ Time gaps sufficient? (3-5+ chapters minimum)
✅ No deus ex machina? (Crucial items seeded early)
✅ Red herrings mislead fairly? (Real clues still exist)
✅ Readers will feel SMART noticing connections?

### 8. CHAPTER OUTLINES (CRITICAL - Scene Structure!)

For EVERY chapter ({chapter_count} total), provide a detailed outline following the **SCENE/SEQUEL** structure:

**Scene Structure (Action chapters)** - Goal → Conflict → Disaster:
1. **Goal**: What does the POV character want in this chapter?
2. **Conflict**: What obstacles prevent them from getting it?
3. **Disaster**: They fail OR succeed with unexpected bad consequences

**Sequel Structure (Reaction chapters)** - Reaction → Dilemma → Decision:
1. **Reaction**: Emotional response to disaster (fear, anger, grief)
2. **Dilemma**: What are their options now? (All bad!)
3. **Decision**: What do they choose to do? (Leads to next Scene)

**Alternate Scene/Sequel for pacing** - not every chapter same type!

**For each chapter outline, include**:
- **Chapter Number**: X
- **Type**: Scene (action) or Sequel (reflection)
- **POV Character**: Who's telling this chapter?
- **Setting**: Where does it take place?
- **Characters Present**: Who's in this chapter?
- **Goal** (Scene) or **Reaction** (Sequel): What character wants/feels
- **Conflict** (Scene) or **Dilemma** (Sequel): Obstacles/tough choices
- **Disaster** (Scene) or **Decision** (Sequel): Outcome/choice
- **Emotional Beat**: Primary emotion (curious, anxious, triumphant, devastated, etc.)
- **Tension Level**: 1-10 scale
- **Key Reveals**: What new information emerges?
- **Cliffhanger**: Yes/No - does it end on unresolved tension?
- **Purpose**: How does this chapter advance plot AND/OR develop character?

**Scene Purpose Validation** - Every chapter must answer YES to:
✅ Does this chapter advance the plot? (new information, events, decisions)
OR
✅ Does this chapter develop character? (reveal personality, growth, relationships)

If answer is NO to both → DELETE THIS CHAPTER (it's filler!)

**Example Strong Chapter Outline**:
```
Chapter 5:
- Type: Scene
- POV: Anna
- Setting: Abandoned warehouse, night
- Characters: Anna, Detective Kowalski, mysterious figure
- Goal: Anna wants to find evidence that clears her brother
- Conflict: Detective warns her off, warehouse is dangerous, figure attacks
- Disaster: She finds evidence BUT it implicates HER, not clears her brother
- Emotional Beat: Hope → Fear → Devastation
- Tension: 8/10
- Key Reveals: Anna's brother may have been framed, but Anna is now a suspect
- Cliffhanger: YES - police sirens approaching, she's holding murder weapon
- Purpose: Plot advancement (new suspect twist) + Character (Anna's loyalty tested)
```

**Example Strong Sequel Outline**:
```
Chapter 6:
- Type: Sequel
- POV: Anna
- Setting: Her apartment, dawn
- Characters: Anna alone
- Reaction: Panic, betrayal, grief - brother lied to her for years
- Dilemma: Turn herself in? Run? Confront brother? All options terrible.
- Decision: She decides to find brother and force truth, whatever cost
- Emotional Beat: Devastation → Resolve
- Tension: 4/10 (calm before storm)
- Key Reveals: Anna's internal strength, her wound (trust issues) triggered
- Cliffhanger: NO - ends on decision, ready for next action
- Purpose: Character development (shows her wound, choice reveals who she is)
```

### 9. SCENE CAUSALITY & NO FILLER

Explain the CAUSE-AND-EFFECT chain:
- Chapter 1 leads to Chapter 2 because... (use "therefore" or "but", never "and then")
- Every chapter must be NECESSARY - removing it breaks the story
- No "and then" moments - each event CAUSES the next
- No filler chapters - each earns its place through purpose

**Test**: "Can I remove this chapter without breaking the story?"
- If YES → Delete it or combine with another
- If NO → It's necessary, keep it

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
  "emotional_arc": {{
    "tension_graph": [
      {{
        "chapter": 1,
        "tension": 3,
        "primary_emotion": "Curiosity",
        "reader_feeling": "What's happening? Need to know more.",
        "justification": "Opening hook with mysterious event"
      }},
      {{
        "chapter": 2,
        "tension": 5,
        "primary_emotion": "Anxiety",
        "reader_feeling": "Worried for protagonist's safety",
        "justification": "First major obstacle, stakes established"
      }},
      ...for all {chapter_count} chapters
    ],
    "act_checkpoints": {{
      "end_of_act_1": {{
        "reader_cares": "YES - protagonist's vulnerability shown, relatable wound revealed",
        "emotional_peak": "Hope mixed with anxiety"
      }},
      "midpoint": {{
        "reader_invested": "YES - stakes raised dramatically, can't predict outcome",
        "emotional_peak": "Triumph turning to dread"
      }},
      "end_of_act_2": {{
        "reader_desperate": "YES - all is lost, protagonist at lowest point",
        "emotional_peak": "Devastation, desperate to see resolution"
      }},
      "climax": {{
        "reader_feels_weight": "YES - emotional journey earned this moment",
        "emotional_peak": "Maximum tension + cathartic release"
      }},
      "resolution": {{
        "reader_satisfied": "YES - promises fulfilled, arc complete",
        "emotional_peak": "Bittersweet triumph, satisfying closure"
      }}
    }},
    "emotional_variety_check": "Emotions used: Curiosity, Anxiety, Hope, Fear, Dread, Triumph, Devastation, Resolve, Joy (9 different - PASS)",
    "genre_appropriateness": "Tension baseline and peaks match {genre} expectations"
  }},
  "chapter_outlines": [
    {{
      "chapter": 1,
      "type": "Scene",
      "pov_character": "Anna",
      "setting": "...",
      "characters_present": ["Anna", "..."],
      "goal": "..." (for Scene) OR "reaction": "..." (for Sequel),
      "conflict": "..." (for Scene) OR "dilemma": "..." (for Sequel),
      "disaster": "..." (for Scene) OR "decision": "..." (for Sequel),
      "emotional_beat": "curious",
      "tension": 3,
      "key_reveals": ["...", "..."],
      "cliffhanger": true/false,
      "purpose": "Advances plot by... AND develops character by..."
    }},
    ...for all {chapter_count} chapters
  ],
  "foreshadowing": [
    {{
      "type": "Chekhov's Gun|Direct|Subtle|Red Herring|Symbolic|Prophecy|Skill",
      "setup_chapter": X,
      "setup_description": "Specific description of what reader sees/hears...",
      "subtlety_level": 1-10,
      "payoff_chapter": Y,
      "payoff_description": "How it becomes significant/pays off...",
      "time_gap": Y-X,
      "reader_impact": "Emotion/reaction created (satisfaction, shock, etc.)",
      "mandatory": true/false
    }},
    ...minimum 5, maximum 15 elements
  ],
  "foreshadowing_validation": {{
    "all_mandatory_have_payoffs": true,
    "payoffs_after_setups": true,
    "time_gaps_sufficient": "Minimum 3-5 chapters, longer for major reveals",
    "no_deus_ex_machina": "All crucial items/skills seeded in Acts 1-2",
    "red_herrings_fair": "Misleading but fair clues exist",
    "reader_satisfaction": "Connections reward attentive readers"
  }},
  "causality_notes": "Chapter 1 leads to Chapter 2 because... (therefore/but chains, never 'and then')"
}}

**CRITICAL REQUIREMENTS**:
✅ ALL {chapter_count} chapters must have detailed outlines
✅ Each chapter has clear Goal→Conflict→Disaster OR Reaction→Dilemma→Decision
✅ Every chapter has validated PURPOSE (advances plot OR develops character)
✅ Causality chain is tight ("therefore/but", never "and then")
✅ No filler chapters - each one is NECESSARY
✅ Scene/Sequel alternation for pacing variety

Create a plot that is TIGHT, ESCALATING, EMOTIONALLY SATISFYING, and IMPOSSIBLE TO PUT DOWN."""

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

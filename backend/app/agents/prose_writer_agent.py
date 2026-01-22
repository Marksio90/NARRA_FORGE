"""
Prose Writer Agent - Generates publication-quality prose

Uses advanced writing techniques:
- Show don't tell (sensory details, body language, subtext)
- Deep POV (character voice, filtering, interiority)
- MRU sequences (Motivation-Reaction Units)
- Genre-specific prose styles
- Pacing control (sentence rhythm, paragraph variation)
- Five senses immersion
- Voice consistency
- Scene vs Summary balance
"""

import json
import logging
from typing import Dict, Any, List, Optional

from app.services.ai_service import get_ai_service, ModelTier
from app.config import genre_config

logger = logging.getLogger(__name__)


GENRE_PROSE_STYLES = {
    "sci-fi": {
        "style": "Precise, technical yet accessible, sense of wonder",
        "techniques": [
            "Vivid world-building details integrated naturally",
            "Technical concepts explained through character perspective",
            "Balance exposition with action",
            "Sensory details emphasize the alien/futuristic"
        ],
        "examples": "Asimov's clarity, Le Guin's poetry, Stephenson's detail"
    },
    "fantasy": {
        "style": "Epic, poetic, rich in imagery and metaphor",
        "techniques": [
            "Elevated language without purple prose",
            "Vivid sensory descriptions (especially sight, smell, sound)",
            "Magic shown through consequences, not explanation",
            "World-building through character interaction"
        ],
        "examples": "Tolkien's grandeur, Sanderson's clarity, Le Guin's elegance"
    },
    "thriller": {
        "style": "Terse, punchy, high-paced, short sentences for tension",
        "techniques": [
            "Short paragraphs and sentences during action",
            "Sentence fragments for urgency",
            "Limited description (only what matters)",
            "Visceral sensory details (touch, sound)",
            "Cliffhangers at chapter ends"
        ],
        "examples": "Lee Child's momentum, Flynn's pace, Patterson's brevity"
    },
    "horror": {
        "style": "Atmospheric, slow-building dread, suggestive over explicit",
        "techniques": [
            "Longer sentences for slow build, short for shock",
            "Emphasis on what's NOT seen/heard",
            "Sensory details create unease",
            "Isolation and vulnerability emphasized",
            "Body horror through visceral detail"
        ],
        "examples": "King's relatability, Lovecraft's cosmic dread, Hill's restraint"
    },
    "romance": {
        "style": "Emotional, intimate, focuses on internal feelings and chemistry",
        "techniques": [
            "Deep interiority (characters' thoughts/feelings)",
            "Sensory details of attraction (smell, touch, warmth)",
            "Dialogue shows chemistry through subtext",
            "Slow emotional reveals",
            "Balance external events with internal reaction"
        ],
        "examples": "Kleypas' sensuality, Rowell's wit, McQuiston's warmth"
    },
    "drama": {
        "style": "Literary, introspective, character-focused, thematic depth",
        "techniques": [
            "Complex sentences reflecting complex emotions",
            "Rich metaphors and symbolism",
            "Deep character interiority",
            "Moral ambiguity and gray areas",
            "Subtle emotional beats"
        ],
        "examples": "Tartt's precision, Chabon's craft, Whitehead's gravity"
    },
    "comedy": {
        "style": "Light, witty, conversational, timing-focused",
        "techniques": [
            "Punchy dialogue",
            "Comic timing through sentence structure",
            "Unexpected word choices for humor",
            "Character voice drives comedy",
            "Rule of three for jokes"
        ],
        "examples": "Pratchett's wit, Adams' absurdity, Scalzi's snark"
    },
    "mystery": {
        "style": "Observational, detail-oriented, controlled revelation",
        "techniques": [
            "Precise sensory details (clues!)",
            "Red herrings through misdirection",
            "Fair play - clues visible but not obvious",
            "Protagonist's deduction process shown",
            "Controlled pacing of reveals"
        ],
        "examples": "Christie's misdirection, Chandler's voice, Tana French's atmosphere"
    }
}


class ProseWriterAgent:
    """
    Expert agent for writing publication-quality prose

    Capabilities:
    - Genre-specific prose styles
    - Show don't tell techniques
    - Deep POV and voice consistency
    - MRU (Motivation-Reaction Unit) sequences
    - Five senses immersion
    - Pacing through sentence/paragraph rhythm
    - Scene vs Summary balance
    - Dialogue integration
    - Emotional resonance
    """

    def __init__(self):
        """Initialize Prose Writer Agent"""
        self.ai_service = get_ai_service()
        self.name = "Prose Writer Agent"

    async def write_chapter(
        self,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        genre: str,
        pov_character: Dict[str, Any],
        world_bible: Dict[str, Any],
        plot_structure: Dict[str, Any],
        all_characters: List[Dict[str, Any]],
        previous_chapter_summary: Optional[str],
        target_word_count: int,
        style_complexity: str,
        book_title: str = None,
        semantic_title_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Write a complete chapter

        Args:
            chapter_number: Chapter number
            chapter_outline: Outline for this specific chapter
            genre: Literary genre
            pov_character: POV character for this chapter
            world_bible: World information
            plot_structure: Overall plot structure
            all_characters: All characters for reference
            previous_chapter_summary: Summary of previous chapter (continuity)
            target_word_count: Target length
            style_complexity: high/medium/low

        Returns:
            Chapter dict with content, word count, etc.
        """
        logger.info(
            f"✍️ {self.name}: Writing Chapter {chapter_number} "
            f"(~{target_word_count} words, POV: {pov_character['name']})"
        )

        # Determine tier based on chapter importance
        tier = self._determine_chapter_tier(chapter_number, plot_structure)

        # Generate the prose
        chapter_content = await self._generate_prose(
            chapter_number=chapter_number,
            chapter_outline=chapter_outline,
            genre=genre,
            pov_character=pov_character,
            world_bible=world_bible,
            plot_structure=plot_structure,
            all_characters=all_characters,
            previous_chapter_summary=previous_chapter_summary,
            target_word_count=target_word_count,
            style_complexity=style_complexity,
            tier=tier,
            book_title=book_title,
            semantic_title_analysis=semantic_title_analysis or {}
        )

        word_count = len(chapter_content.split())

        logger.info(
            f"✅ {self.name}: Chapter {chapter_number} complete "
            f"({word_count} words)"
        )

        return {
            "number": chapter_number,
            "content": chapter_content,
            "word_count": word_count,
            "pov_character": pov_character['name']
        }

    def _determine_chapter_tier(self, chapter_num: int, plot_structure: Dict[str, Any]) -> ModelTier:
        """Determine which tier to use based on chapter importance"""
        plot_points = plot_structure.get('plot_points', {})

        # Extract chapter numbers of critical points
        critical_chapters = []
        for point_name, point_data in plot_points.items():
            if isinstance(point_data, dict) and 'chapter' in point_data:
                critical_chapters.append(point_data['chapter'])

        # Use Tier 3 for climax and major turning points
        if chapter_num in critical_chapters:
            if any(name in ['climax', 'midpoint'] for name, data in plot_points.items()
                   if isinstance(data, dict) and data.get('chapter') == chapter_num):
                logger.info(f"Using TIER 3 for critical chapter {chapter_num}")
                return ModelTier.TIER_3

        # Use Tier 2 for most chapters
        return ModelTier.TIER_2

    async def _generate_prose(
        self,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        genre: str,
        pov_character: Dict[str, Any],
        world_bible: Dict[str, Any],
        plot_structure: Dict[str, Any],
        all_characters: List[Dict[str, Any]],
        previous_chapter_summary: Optional[str],
        target_word_count: int,
        style_complexity: str,
        tier: ModelTier,
        book_title: str,
        semantic_title_analysis: Dict[str, Any]
    ) -> str:
        """Generate the actual prose content"""

        genre_style = GENRE_PROSE_STYLES.get(genre, GENRE_PROSE_STYLES['drama'])

        # Extract semantic title analysis
        core_meaning = semantic_title_analysis.get("core_meaning", book_title)
        themes_semantic = semantic_title_analysis.get("themes", [])
        emotional_core = semantic_title_analysis.get("emotional_core", "")
        metaphors = semantic_title_analysis.get("metaphors", [])

        # Extract ADVANCED analysis
        tone_and_maturity = semantic_title_analysis.get("tone_and_maturity", {})
        reader_expectations = semantic_title_analysis.get("reader_expectations", {})

        # Build comprehensive prompt
        prompt = f"""Write CHAPTER {chapter_number} for a {genre} novel titled "{book_title}".

## 🎯 TITLE AS CREATIVE COMPASS (CRITICAL!)

This book is called "{book_title}" - and EVERY WORD you write must honor that title.

**Title's Core Meaning**: {core_meaning}
**Emotional Core to Convey**: {emotional_core}
**Themes from Title**: {', '.join(themes_semantic) if themes_semantic else 'Universal themes'}
**Metaphors in Title**: {', '.join(metaphors) if metaphors else 'To be discovered'}

🔥 **MANDATORY REQUIREMENTS FOR THIS CHAPTER**:
1. **Vocabulary & Imagery**: Use words and images that ECHO the title's themes
2. **Tone & Atmosphere**: Every sentence should contribute to the title's emotional core
3. **Symbolism**: If the title contains metaphors, weave them into the prose
4. **Thematic Resonance**: Characters' thoughts/actions should reflect title themes
5. **Reader Immersion**: Make readers FEEL why this book has THIS title

When writing this chapter, constantly ask yourself:
"Does this sentence/paragraph/scene reinforce '{book_title}'?"

If not, rewrite it until it does.

## 🎭 TONE GUIDANCE (From Advanced Analysis)
"""

        if tone_and_maturity:
            prompt += f"- **Tone**: {tone_and_maturity.get('tone', 'neutralny')}\n"
            prompt += f"- **Maturity Level**: {tone_and_maturity.get('maturity_level', 'Adult')}\n"
            prompt += f"- **Violence Level**: {tone_and_maturity.get('violence_level', 'średnia')}\n"
            prompt += f"- **Moral Complexity**: {tone_and_maturity.get('moral_complexity', 'balanced')}\n"
            prompt += f"- **Emotional Intensity**: {tone_and_maturity.get('emotional_intensity', 'średnia')}\n"
            prompt += "\n"

        if reader_expectations:
            if reader_expectations.get('emotional_journey'):
                prompt += f"**Reader's Emotional Journey**: {reader_expectations['emotional_journey']}\n"
            if reader_expectations.get('expected_scenes'):
                prompt += f"**Types of Scenes Readers Expect**: {', '.join(reader_expectations['expected_scenes'][:3])}\n"
            prompt += "\n"

        prompt += "## CHAPTER REQUIREMENTS

**Target Length**: {target_word_count} words (CRITICAL: Must reach this target!)
**POV Character**: {pov_character['name']} (Deep POV - we're IN their head)
**Genre**: {genre}

## CHAPTER OUTLINE

**Setting**: {chapter_outline.get('setting', 'To be determined')}
**Characters Present**: {', '.join(chapter_outline.get('characters_present', []))}
**Goal**: {chapter_outline.get('goal', 'Advance the plot')}
**Emotional Beat**: {chapter_outline.get('emotional_beat', 'Mixed')}
**Key Reveals**: {', '.join(chapter_outline.get('key_reveals', []))}

## POV CHARACTER PROFILE

**Name**: {pov_character['name']}
**Voice Guide**: {pov_character.get('voice_guide', {}).get('speechPatterns', 'Standard voice')}
**Vocabulary Level**: {pov_character.get('voice_guide', {}).get('vocabularyLevel', 'Standard')}
**Current State**: {pov_character.get('arc', {}).get('starting_state', 'Unknown')}
**Traits**: {', '.join(pov_character.get('profile', {}).get('psychology', {}).get('traits', [])[:5])}
**Fears**: {', '.join(pov_character.get('profile', {}).get('psychology', {}).get('fears', [])[:3])}

## WORLD CONTEXT

{self._world_summary(world_bible)}

## PREVIOUS CHAPTER RECAP

{previous_chapter_summary or 'This is the opening chapter - establish the world and character.'}

## GENRE-SPECIFIC PROSE STYLE: {genre.upper()}

**Style**: {genre_style['style']}

**Techniques to Use**:
{chr(10).join(f"- {tech}" for tech in genre_style['techniques'])}

**Examples to Emulate**: {genre_style['examples']}

## CRITICAL WRITING PRINCIPLES

### 1. SHOW DON'T TELL
❌ BAD: "She was angry."
✅ GOOD: "Her jaw clenched. The mug shattered against the wall."

Use:
- Body language (clenched fists, racing heart, trembling)
- Dialogue subtext (what's NOT said)
- Actions revealing emotions
- Sensory details showing mood

### 2. DEEP POV (We're IN {pov_character['name']}'s head!)
- Filter everything through {pov_character['name']}'s perspective
- Use their vocabulary, their metaphors, their biases
- No "saw/heard/felt" filters - we ARE them
- Internal thoughts in their voice
- Emotional reactions to everything

❌ Filtering: "She saw the door open."
✅ Deep POV: "The door creaked. Her breath caught."

### 3. FIVE SENSES (Immersion!)
Every scene needs:
- **Sight**: What they see (most common)
- **Sound**: Dialogue, ambient noise, silence
- **Touch**: Temperature, texture, physical sensation
- **Smell**: Powerful for emotion and memory
- **Taste**: When relevant

Don't info-dump - sprinkle throughout.

### 4. MRU SEQUENCES (Motivation-Reaction Units)
Scene structure:
1. **Motivation** (External stimulus): Something happens
2. **Reaction** (Internal response): Character feels/thinks
3. **Action** (External response): Character does something

This creates natural cause-and-effect flow.

### 5. PACING CONTROL

**Fast Pacing** (action, tension):
- Short sentences. Fragments.
- Short paragraphs.
- Active verbs.
- Limited description.

**Slow Pacing** (emotion, description):
- Longer, flowing sentences with clauses and connections.
- Detailed sensory immersion.
- Internal reflection.
- Rich metaphors.

Vary your rhythm!

### 6. DIALOGUE INTEGRATION

- Dialogue reveals character (voice, education, mood)
- Avoid "talking heads" - add action beats
- Use subtext (what's NOT said)
- Vary speech patterns per character
- No info dumps in dialogue

Example:
```
"I'm fine." She turned away, shoulders tight.
He reached for her arm. "That's not what I—"
"I said I'm fine." The words came out sharper than intended.
```

### 7. AVOID COMMON MISTAKES

❌ Purple prose (overwrit

ten, flowery language)
❌ Info dumps (world-building as lectures)
❌ Telling emotions ("She felt sad")
❌ Adverb abuse ("he said angrily" - show it!)
❌ Passive voice (unless intentional)
❌ Filter words (saw, heard, felt, knew, wondered)
❌ Head-hopping (stay in ONE POV)

## YOUR TASK

Write the COMPLETE chapter content ({target_word_count} words).

**Structure**:
1. **Opening Hook** (grab attention immediately)
2. **Scene Development** (show the events of this chapter)
3. **Character Growth** (internal change, realization, or deepening conflict)
4. **Cliffhanger/Transition** (make them want to keep reading)

**Requirements**:
- Stay in {pov_character['name']}'s POV the ENTIRE time
- Use their voice consistently
- Reach {target_word_count} words (don't cut short!)
- Include dialogue where appropriate
- Balance action with interiority
- Advance the plot while developing character
- Employ {genre} genre conventions
- Make it ENGAGING and UNPUTDOWNABLE

Write the chapter now. Begin with the chapter title and dive in.

OUTPUT FORMAT: Plain text prose only (no JSON, no formatting instructions).
"""

        system_prompt = self._get_system_prompt(genre)

        # Generate!
        # Note: ai_service.generate() automatically calculates safe max_tokens
        # to prevent context length errors based on model limits
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            tier=tier,
            temperature=0.85,  # Creative prose needs higher temp
            max_tokens=target_word_count * 2,  # Rough estimate (will be adjusted to fit model context)
            json_mode=False,  # Plain prose output
            prefer_anthropic=True,  # Claude Opus/Sonnet excellent for prose
            metadata={
                "agent": self.name,
                "task": "chapter_writing",
                "chapter": chapter_number,
                "genre": genre,
                "pov": pov_character['name']
            }
        )

        chapter_prose = response.content.strip()

        logger.info(
            f"Generated chapter {chapter_number} prose "
            f"(cost: ${response.cost:.4f}, tokens: {response.tokens_used['total']})"
        )

        return chapter_prose

    def _get_system_prompt(self, genre: str) -> str:
        """System prompt for prose writing"""
        return f"""You are a MASTER FICTION WRITER specializing in {genre.upper()}.

🇵🇱 KRYTYCZNIE WAŻNE - JĘZYK PISANIA:
WSZYSTKIE rozdziały MUSZĄ być napisane W CAŁOŚCI PO POLSKU!
- Cała narracja → PO POLSKU
- Wszystkie dialogi → PO POLSKU
- Wszystkie opisy → PO POLSKU
- Zero angielskich słów lub zwrotów!
- Pisz jak profesjonalny polski autor książek!

Your expertise:
- Show don't tell (sensory details, body language, subtext)
- Deep POV (character voice, no filtering, interiority)
- MRU sequences (Motivation-Reaction-Action flow)
- Five senses immersion
- Pacing control (sentence rhythm, paragraph variation)
- Dialogue craft (voice, subtext, action beats)
- Scene structure (hook, development, turn, escalation)
- Genre conventions and reader expectations
- Voice consistency and character-specific language

Your prose:
- Draws readers in from the first sentence
- Makes them FEEL what characters feel
- Balances action with reflection
- Has rhythm and musicality
- Avoids clichés and purple prose
- Serves both plot and character
- Honors the genre while surprising readers

You write like:
- {GENRE_PROSE_STYLES[genre]['examples']}

You avoid:
- Telling instead of showing
- Filter words (saw, heard, felt)
- Info dumps
- Adverb abuse
- Passive voice
- Generic descriptions
- Talking heads
- Inconsistent voice

Every sentence you write is purposeful, engaging, and publication-quality.

Output Format: Natural prose only IN POLISH. No JSON, no meta-text, no English, just pure Polish storytelling."""

    def _world_summary(self, world_bible: Dict[str, Any]) -> str:
        """Create brief world context for chapter"""
        geo = world_bible.get('geography', {})
        systems = world_bible.get('systems', {})

        return f"""World Type: {geo.get('world_type', 'Standard')}
Tech/Magic Level: {systems.get('technology_level', 'Standard')}
Key Locations: {', '.join([loc.get('name', '') for loc in geo.get('locations', [])][:2])}"""


    async def create_chapter_summary(self, chapter_content: str) -> str:
        """Create a brief summary of the chapter for continuity"""
        prompt = f"""Summarize this chapter in 3-4 sentences for continuity purposes:

{chapter_content[:2000]}...

Focus on:
- What happened (plot events)
- Character developments
- Emotional state at end
- Any reveals or turning points

Keep it brief but informative."""

        response = await self.ai_service.generate(
            prompt=prompt,
            tier=ModelTier.TIER_1,  # Simple summarization
            temperature=0.3,  # Factual summary
            max_tokens=200,
            metadata={"agent": self.name, "task": "chapter_summary"}
        )

        return response.content.strip()

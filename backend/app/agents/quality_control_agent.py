"""
Quality Control Agent - Validates consistency, continuity, and quality

Performs multi-level validation:
- Continuity checking (character consistency, plot holes, timeline)
- Genre compliance (does it feel like the genre?)
- Voice consistency (characters sound like themselves)
- World rules adherence (magic/tech systems consistent)
- Pacing analysis (too fast/slow?)
- Emotional resonance check
- Show vs Tell ratio
"""

import json
import logging
from typing import Dict, Any, List, Optional

from app.services.ai_service import get_ai_service, ModelTier

logger = logging.getLogger(__name__)


class QualityControlAgent:
    """
    Expert agent for quality control and validation

    Capabilities:
    - Continuity checking across chapters
    - Character consistency validation
    - Plot hole detection
    - Genre compliance verification
    - Voice consistency analysis
    - World rules adherence checking
    - Pacing evaluation
    - Show vs Tell analysis
    - Emotional resonance measurement
    """

    def __init__(self):
        """Initialize Quality Control Agent"""
        self.ai_service = get_ai_service()
        self.name = "Quality Control Agent"

    async def validate_chapter(
        self,
        chapter_content: str,
        chapter_number: int,
        genre: str,
        pov_character: Dict[str, Any],
        world_bible: Dict[str, Any],
        previous_chapters_summary: List[str],
        all_characters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate a single chapter for quality and consistency

        Args:
            chapter_content: The prose content
            chapter_number: Chapter number
            genre: Literary genre
            pov_character: POV character
            world_bible: World rules
            previous_chapters_summary: Summaries of previous chapters
            all_characters: All characters for reference

        Returns:
            Validation report with issues and quality score
        """
        logger.info(f"🔍 {self.name}: Validating Chapter {chapter_number}")

        validation_report = await self._perform_validation(
            chapter_content=chapter_content,
            chapter_number=chapter_number,
            genre=genre,
            pov_character=pov_character,
            world_bible=world_bible,
            previous_chapters_summary=previous_chapters_summary,
            all_characters=all_characters
        )

        quality_score = validation_report.get('overall_quality_score', 0)
        issues_found = len(validation_report.get('issues', []))

        logger.info(
            f"✅ {self.name}: Chapter {chapter_number} validated "
            f"(score: {quality_score}/100, issues: {issues_found})"
        )

        return validation_report

    async def validate_full_manuscript(
        self,
        all_chapters: List[Dict[str, Any]],
        world_bible: Dict[str, Any],
        plot_structure: Dict[str, Any],
        all_characters: List[Dict[str, Any]],
        genre: str
    ) -> Dict[str, Any]:
        """
        Validate the complete manuscript for global consistency

        Args:
            all_chapters: All chapter data
            world_bible: World rules
            plot_structure: Plot structure
            all_characters: All characters
            genre: Literary genre

        Returns:
            Complete validation report
        """
        logger.info(f"🔍 {self.name}: Validating full manuscript ({len(all_chapters)} chapters)")

        report = await self._perform_full_validation(
            all_chapters=all_chapters,
            world_bible=world_bible,
            plot_structure=plot_structure,
            all_characters=all_characters,
            genre=genre
        )

        logger.info(
            f"✅ {self.name}: Full manuscript validated "
            f"(score: {report.get('overall_score', 0)}/100)"
        )

        return report

    async def _perform_validation(
        self,
        chapter_content: str,
        chapter_number: int,
        genre: str,
        pov_character: Dict[str, Any],
        world_bible: Dict[str, Any],
        previous_chapters_summary: List[str],
        all_characters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform chapter-level validation using AI"""

        # Truncate chapter if too long for context window
        content_preview = chapter_content[:8000]  # ~6000 words max

        prompt = f"""QUALITY CONTROL CHECK for Chapter {chapter_number} ({genre}).

## CHAPTER CONTENT (Preview)

{content_preview}

{"[...content truncated...]" if len(chapter_content) > 8000 else ""}

## VALIDATION CHECKLIST

### 1. CONTINUITY CONSISTENCY

**Previous chapters context**:
{chr(10).join(f"Ch{i+1}: {summary}" for i, summary in enumerate(previous_chapters_summary[-3:])) if previous_chapters_summary else "This is the opening chapter."}

**Check**:
- Does this chapter contradict any previous events?
- Are character behaviors consistent with established personality?
- Are any plot threads broken or forgotten?
- Timeline makes sense?

### 2. CHARACTER VOICE CONSISTENCY

**POV Character**: {pov_character['name']}
**Expected Voice**: {pov_character.get('voice_guide', 'Not specified')}
**Traits**: {', '.join(pov_character.get('profile', {}).get('psychology', {}).get('traits', [])[:5])}

**Check**:
- Does the narration sound like {pov_character['name']}?
- Vocabulary matches their education/background?
- Emotional reactions fit their personality?
- Internal thoughts match their psychology?

### 3. WORLD RULES ADHERENCE

**World Type**: {world_bible.get('geography', {}).get('world_type', 'Unknown')}
**Tech/Magic**: {world_bible.get('systems', {}).get('technology_level', 'Unknown')}
**Rules**: {world_bible.get('rules', {}).get('physics', 'Standard')}

**Check**:
- Are world rules followed consistently?
- No magic/tech used that shouldn't exist?
- Geography and locations match world bible?
- Cultural elements consistent?

### 4. GENRE COMPLIANCE

**Genre**: {genre}
**Expected style**: {self._get_genre_expectations(genre)}

**Check**:
- Does the prose feel like authentic {genre}?
- Pacing appropriate for genre?
- Tone matches genre conventions?
- Reader expectations met?

### 5. PROSE QUALITY

**Check**:
- **Show vs Tell**: Are emotions shown through action/dialogue/body language, not told?
- **Sensory Details**: Are 5 senses used for immersion?
- **Deep POV**: Is filtering minimized? (avoid "saw/heard/felt")
- **Pacing**: Sentence/paragraph rhythm appropriate?
- **Dialogue**: Natural, character-specific, with action beats?
- **Clichés**: Any overused phrases or tired tropes?

### 6. EMOTIONAL RESONANCE

**Check**:
- Does the chapter evoke emotion?
- Are character struggles relatable?
- Are stakes clear and compelling?
- Does reader care what happens next?

### 7. PLOT ADVANCEMENT

**Check**:
- Does this chapter move the story forward?
- Or is it filler/treading water?
- Are there consequences to actions?
- Does it set up future events?

## YOUR TASK

Provide a DETAILED validation report in JSON format:

{{
  "overall_quality_score": <0-100>,
  "continuity": {{
    "score": <0-100>,
    "issues": ["...", "..."],
    "notes": "..."
  }},
  "voice_consistency": {{
    "score": <0-100>,
    "issues": ["...", "..."],
    "notes": "..."
  }},
  "world_rules": {{
    "score": <0-100>,
    "issues": ["...", "..."],
    "notes": "..."
  }},
  "genre_compliance": {{
    "score": <0-100>,
    "issues": ["...", "..."],
    "notes": "..."
  }},
  "prose_quality": {{
    "score": <0-100>,
    "show_vs_tell_ratio": <0-100>,
    "issues": ["...", "..."],
    "strengths": ["...", "..."],
    "notes": "..."
  }},
  "emotional_resonance": {{
    "score": <0-100>,
    "notes": "..."
  }},
  "plot_advancement": {{
    "score": <0-100>,
    "notes": "..."
  }},
  "issues": [
    {{
      "severity": "critical|major|minor",
      "type": "continuity|voice|world_rules|prose|other",
      "description": "...",
      "location": "paragraph/line reference",
      "suggestion": "how to fix"
    }}
  ],
  "strengths": ["...", "...", "..."],
  "recommendations": ["...", "...", "..."]
}}

Be thorough but fair. This is professional editorial feedback.
"""

        system_prompt = self._get_system_prompt()

        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            tier=ModelTier.TIER_2,  # Quality checking needs good model
            temperature=0.3,  # Analytical, not creative
            max_tokens=3000,
            json_mode=True,
            prefer_anthropic=False,  # GPT better for structured analysis
            metadata={
                "agent": self.name,
                "task": "chapter_validation",
                "chapter": chapter_number
            }
        )

        validation_report = json.loads(response.content)
        return validation_report

    async def _perform_full_validation(
        self,
        all_chapters: List[Dict[str, Any]],
        world_bible: Dict[str, Any],
        plot_structure: Dict[str, Any],
        all_characters: List[Dict[str, Any]],
        genre: str
    ) -> Dict[str, Any]:
        """Perform full manuscript validation"""

        # Create manuscript summary
        chapter_summaries = []
        for ch in all_chapters[:15]:  # Sample first 15 chapters
            chapter_summaries.append(f"Ch{ch['number']}: {ch.get('content', '')[:200]}...")

        prompt = f"""FULL MANUSCRIPT QUALITY CONTROL for {genre} novel.

## MANUSCRIPT INFO

**Total Chapters**: {len(all_chapters)}
**Genre**: {genre}
**Structure**: {plot_structure.get('structure_type', 'Unknown')}

## SAMPLE CHAPTERS

{chr(10).join(chapter_summaries)}

## VALIDATION AREAS

### 1. GLOBAL CONTINUITY
- Are there plot holes across the full story?
- Character arcs completed satisfyingly?
- All foreshadowing paid off?
- Timeline consistent throughout?

### 2. CHARACTER CONSISTENCY
- Do characters act consistently across all chapters?
- Are their voices distinct and maintained?
- Do their arcs feel earned and natural?

### 3. PLOT STRUCTURE
- Does the structure work? (setup, rising action, climax, resolution)
- Pacing consistent or does it drag/rush?
- All subplots resolved?
- Satisfying ending?

### 4. WORLD CONSISTENCY
- World rules followed throughout?
- Geography/locations consistent?
- Technology/magic used consistently?

### 5. GENRE COMPLIANCE
- Does it fulfill {genre} reader expectations?
- Appropriate tone maintained?
- Genre tropes used well or avoided appropriately?

Output JSON validation report with overall scores and critical issues."""

        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self._get_system_prompt(),
            tier=ModelTier.TIER_2,
            temperature=0.3,
            max_tokens=2500,
            json_mode=True,
            metadata={"agent": self.name, "task": "full_manuscript_validation"}
        )

        return json.loads(response.content)

    def _get_system_prompt(self) -> str:
        """System prompt for QC agent"""
        return """You are an EXPERT DEVELOPMENTAL EDITOR and QUALITY CONTROL SPECIALIST.

Your expertise:
- Continuity and consistency checking
- Character arc and voice analysis
- Plot structure evaluation
- Genre conventions and reader expectations
- Prose quality assessment (show vs tell, pacing, etc.)
- World-building consistency
- Emotional resonance measurement

You provide:
- Professional, constructive feedback
- Specific, actionable suggestions
- Fair scoring (not overly harsh or lenient)
- Both strengths and weaknesses
- Editorial wisdom from years of experience

You catch:
- Plot holes and continuity errors
- Character inconsistencies
- Voice breaks
- Pacing issues
- Genre compliance problems
- Prose weaknesses (telling, filtering, clichés)
- World rule violations

You recognize:
- Strong character work
- Effective prose techniques
- Engaging scenes
- Good pacing
- Emotional impact

You are thorough, professional, and focused on making the manuscript BETTER.

Output Format: Valid JSON only, structured and detailed."""

    def _get_genre_expectations(self, genre: str) -> str:
        """Get genre-specific expectations"""
        expectations = {
            "sci-fi": "Plausible tech, sense of wonder, world-building integrated naturally",
            "fantasy": "Rich world-building, magic with rules, epic scope",
            "thriller": "High tension, fast pacing, escalating stakes",
            "horror": "Atmosphere of dread, slow build to terror, visceral details",
            "romance": "Emotional intimacy, chemistry, satisfying relationship arc",
            "drama": "Character depth, moral complexity, thematic richness",
            "comedy": "Wit, timing, likeable characters, light tone",
            "mystery": "Fair play clues, misdirection, satisfying revelation"
        }
        return expectations.get(genre, "Professional prose, engaging story, satisfying resolution")

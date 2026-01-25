"""
Chapter Revision Agent - Improves first drafts to bestseller quality

Multi-draft revision system:
- Analyzes first draft for weaknesses
- Provides specific improvement feedback
- Rewrites chapter with enhancements
- Focuses on: hooks, cliffhangers, dialogue, pacing, show-don't-tell
"""

import json
import logging
from typing import Dict, Any, List, Optional

from app.services.ai_service import get_ai_service, ModelTier

logger = logging.getLogger(__name__)


class ChapterRevisionAgent:
    """
    Expert agent for revising and improving chapter drafts

    Capabilities:
    - Analyzes first draft for weaknesses
    - Provides targeted improvement feedback
    - Rewrites with focus on:
      * Opening hook strength
      * Cliffhanger effectiveness
      * Dialogue quality (subtext, unique voices)
      * Pacing variety (paragraph lengths)
      * Show-don't-tell ratio
      * Sensory immersion
      * Character voice consistency
      * Polish dialogue formatting (EM DASHES)
    """

    def __init__(self):
        """Initialize Chapter Revision Agent"""
        self.ai_service = get_ai_service()
        self.name = "Chapter Revision Agent"

    async def revise_chapter(
        self,
        first_draft: str,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        genre: str,
        pov_character: Dict[str, Any],
        target_word_count: int,
        book_title: str,
        quality_issues: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Revise a chapter from first draft to improved version

        Args:
            first_draft: Initial chapter content
            chapter_number: Chapter number
            chapter_outline: Original outline
            genre: Literary genre
            pov_character: POV character
            target_word_count: Target length
            book_title: Book title
            quality_issues: Optional list of specific issues to fix

        Returns:
            Dict with revised_content, improvements_made, and quality_delta
        """
        logger.info(
            f"✏️ {self.name}: Revising Chapter {chapter_number} "
            f"(Draft: {len(first_draft.split())} words)"
        )

        # Step 1: Analyze what needs improvement
        analysis = await self._analyze_draft(
            first_draft=first_draft,
            chapter_number=chapter_number,
            genre=genre,
            pov_character=pov_character,
            book_title=book_title,
            quality_issues=quality_issues
        )

        # Step 2: Rewrite with improvements
        revised_chapter = await self._rewrite_with_improvements(
            first_draft=first_draft,
            chapter_number=chapter_number,
            chapter_outline=chapter_outline,
            genre=genre,
            pov_character=pov_character,
            target_word_count=target_word_count,
            book_title=book_title,
            improvement_plan=analysis
        )

        revised_word_count = len(revised_chapter.split())

        logger.info(
            f"✅ {self.name}: Chapter {chapter_number} revised "
            f"(Revised: {revised_word_count} words, "
            f"Improvements: {len(analysis.get('critical_improvements', []))})"
        )

        return {
            "revised_content": revised_chapter,
            "original_word_count": len(first_draft.split()),
            "revised_word_count": revised_word_count,
            "improvements_made": analysis.get('critical_improvements', []),
            "analysis": analysis
        }

    async def _analyze_draft(
        self,
        first_draft: str,
        chapter_number: int,
        genre: str,
        pov_character: Dict[str, Any],
        book_title: str,
        quality_issues: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Analyze first draft and identify improvement opportunities"""

        prompt = f"""Analyze this FIRST DRAFT of Chapter {chapter_number} for a {genre} novel titled "{book_title}".

POV Character: {pov_character['name']}

## FIRST DRAFT:
{first_draft[:5000]}
{'[...truncated for analysis]' if len(first_draft) > 5000 else ''}

## YOUR TASK: Identify Critical Improvements

Analyze this draft and identify the TOP 5-10 improvements that would have MAXIMUM IMPACT on reader engagement.

Focus on these HIGH-IMPACT areas:

1. **Opening Hook** (First 50 words):
   - Is it a killer hook? (Action/Dialogue/Mystery/Conflict)
   - Or is it weak? (Weather/Waking up/Throat-clearing)
   - Specific improvement needed?

2. **Cliffhanger** (Last 50 words):
   - Does it force reader to next chapter?
   - Or does it resolve tension/end calmly?
   - What type of cliffhanger would work best?

3. **Dialogue Quality**:
   - Polish formatting: Uses EM DASHES (—)? No quotation marks?
   - Subtext present or too direct?
   - Characters sound distinct or all same?
   - Action beats integrated or talking heads?

4. **Show vs. Tell**:
   - Emotions shown through body language?
   - Or told directly ("was sad", "felt angry")?
   - Filter words present? (saw, heard, felt, knew)

5. **Pacing Variety**:
   - Paragraph lengths varied (single/short/medium/long)?
   - Or monotonous (all same length)?
   - Sentence rhythm varied or repetitive?

6. **Sensory Immersion**:
   - All 5 senses engaged (sight, sound, touch, smell, taste)?
   - Or just sight/sound?
   - Specific senses missing?

7. **Character Voice Consistency**:
   - POV character's voice consistent with their profile?
   - Internal thoughts match their vocabulary/education?
   - Biases and wounds color perception?

8. **Scene Structure**:
   - Clear Goal → Conflict → Disaster?
   - Or meandering without purpose?
   - Scene earns its place (advances plot/develops character)?

9. **Clichés & Repetitions**:
   - Fresh metaphors or clichés ("black as night")?
   - Word repetitions (same word 3+ times in paragraph)?
   - Adverb abuse ("said angrily")?

10. **Polish Language Quality**:
    - Natural Polish phrasing?
    - Or translated/English-influenced constructions?
    - Dialogue sounds like real Polish speakers?

{"KNOWN ISSUES from QC:\n" + chr(10).join(f"- {issue}" for issue in quality_issues) if quality_issues else ""}

## OUTPUT FORMAT (JSON):

{{
  "overall_assessment": "Brief summary (2-3 sentences)",
  "critical_improvements": [
    {{
      "area": "Opening Hook|Cliffhanger|Dialogue|Show-Tell|Pacing|Sensory|Voice|Structure|Clichés|Polish",
      "current_issue": "Specific problem in draft...",
      "improvement_needed": "Concrete fix to apply...",
      "impact": "high|medium|low",
      "example_fix": "Show how to fix it (if applicable)..."
    }}
  ],
  "strengths": ["What's already working well..."],
  "priority_order": ["Most important fix first", "Then this", "Then this..."]
}}

Be SPECIFIC and ACTIONABLE. No vague advice - give concrete fixes!"""

        system_prompt = """You are an ELITE FICTION EDITOR who works with bestselling authors.

You specialize in:
- Identifying high-impact improvements (20% effort, 80% results)
- Giving specific, actionable feedback (not vague!)
- Focusing on reader engagement and page-turning quality
- Understanding bestseller craft (hooks, cliffhangers, pacing)
- Polish language expertise for natural dialogue

You are CRITICAL but CONSTRUCTIVE. Find what needs fixing AND how to fix it.

Output valid JSON only."""

        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            tier=ModelTier.TIER_2,  # Important analysis
            temperature=0.4,  # Analytical, not too creative
            max_tokens=3000,
            json_mode=True,
            prefer_anthropic=True,
            metadata={
                "agent": self.name,
                "task": "draft_analysis",
                "chapter": chapter_number
            }
        )

        try:
            analysis = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse analysis JSON: {e}")
            # Fallback
            analysis = {
                "overall_assessment": "Analysis failed - proceeding with generic improvements",
                "critical_improvements": [],
                "strengths": [],
                "priority_order": []
            }

        return analysis

    async def _rewrite_with_improvements(
        self,
        first_draft: str,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        genre: str,
        pov_character: Dict[str, Any],
        target_word_count: int,
        book_title: str,
        improvement_plan: Dict[str, Any]
    ) -> str:
        """Rewrite chapter incorporating all improvements"""

        improvements_text = "\n".join([
            f"- **{imp['area']}**: {imp['improvement_needed']}"
            for imp in improvement_plan.get('critical_improvements', [])[:10]
        ])

        priority_text = "\n".join([
            f"{i+1}. {priority}"
            for i, priority in enumerate(improvement_plan.get('priority_order', [])[:5])
        ])

        prompt = f"""# REWIZJA: Rozdział {chapter_number} - "{book_title}" ({genre})

## WYMAGANIA
• POV: {pov_character['name']} | Długość: min. {target_word_count} słów
• Dialogi: PAUZA (—), nigdy cudzysłowy | Język: 100% polski

## PIERWSZY SZKIC DO ULEPSZENIA:
{first_draft}

## ULEPSZENIA DO WDROŻENIA:
{improvements_text if improvements_text else "• Wzmocnij hook otwierający\n• Dodaj magnetyczny cliffhanger\n• Show don't tell w emocjach"}

## ZACHOWAJ:
{chr(10).join(f"• {s}" for s in improvement_plan.get('strengths', ['Fabułę i głos postaci'])[:3])}

## WZMOCNIJ:
• Hook → natychmiast przyciąga
• Cliffhanger → zmusza do czytania
• Dialogi → subtext + unikalne głosy + pauzy (—)
• Emocje → przez ciało, nie etykiety
• Pacing → różne długości akapitów
• Zmysły → min. 3-4 na scenę

Napisz ULEPSZONĄ wersję rozdziału. Zacznij od "Rozdział {chapter_number}"."""

        system_prompt = f"""# ROLA: Profesjonalny Redaktor Powieści {genre.upper()}

Jesteś redaktorem z 20-letnim doświadczeniem w wydawnictwie literackim.
Twoi autorzy regularnie trafiają na listy bestsellerów.

## TWOJE ZADANIE: REWIZJA (nie przepisywanie!)

Ulepszasz pierwszy szkic zachowując:
✓ Te same wydarzenia fabularne
✓ Ten sam POV i głos postaci
✓ Kluczowe dialogi (ulepszone)

Wzmacniasz:
✓ Hook otwierający → natychmiast przyciąga
✓ Cliffhanger → zmusza do czytania dalej
✓ Dialogi → subtext, unikalne głosy, pauzy (—)
✓ Show don't tell → ciało zamiast etykiet emocji
✓ Pacing → różnorodność długości akapitów
✓ 5 zmysłów → pełna immersja

## FORMAT POLSKI
• Dialogi: PAUZA (—), nigdy cudzysłowy
• 100% polski, naturalny język

Dostarczaj profesjonalną rewizję gotową do publikacji."""

        # COST OPTIMIZED: Use TIER_2 with bulletproof prompt (saves 85% vs TIER_3)
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            tier=ModelTier.TIER_2,  # OPTIMIZED: GPT-4o instead of GPT-4
            temperature=0.85,
            max_tokens=target_word_count * 2,
            json_mode=False,
            prefer_anthropic=False,  # Stick with OpenAI for consistency
            metadata={
                "agent": self.name,
                "task": "chapter_rewrite",
                "chapter": chapter_number,
                "genre": genre
            }
        )

        revised_prose = response.content.strip()

        logger.info(
            f"Revised chapter {chapter_number} "
            f"(cost: ${response.cost:.4f}, tokens: {response.tokens_used['total']})"
        )

        return revised_prose

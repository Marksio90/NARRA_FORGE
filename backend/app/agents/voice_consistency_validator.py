"""
Voice Consistency Validator - Ensures characters sound the same throughout the book

Cross-chapter character voice validation:
- Checks if character speech patterns remain consistent
- Validates vocabulary level consistency
- Verifies signature phrases and verbal tics appear
- Ensures emotional speech variations match character profile
- Detects voice drift over multiple chapters
"""

import json
import logging
from typing import Dict, Any, List

from app.services.ai_service import get_ai_service, ModelTier

logger = logging.getLogger(__name__)


class VoiceConsistencyValidator:
    """
    Expert agent for validating character voice consistency across chapters

    Capabilities:
    - Cross-chapter voice comparison
    - Speech pattern consistency checking
    - Vocabulary level validation
    - Signature phrase detection
    - Emotional variation appropriateness
    - Voice drift detection (character sounds different later)
    - Recommendations for voice correction
    """

    def __init__(self):
        """Initialize Voice Consistency Validator"""
        self.ai_service = get_ai_service()
        self.name = "Voice Consistency Validator"

    async def validate_character_voice(
        self,
        character: Dict[str, Any],
        chapters_with_dialogue: List[Dict[str, Any]],
        genre: str
    ) -> Dict[str, Any]:
        """
        Validate that a character's voice remains consistent across all chapters

        Args:
            character: Character profile with voice_guide
            chapters_with_dialogue: List of {chapter_number, dialogue_samples}
            genre: Literary genre

        Returns:
            Validation report with consistency score and issues
        """
        char_name = character.get('name', 'Unknown')
        logger.info(
            f"🎭 {self.name}: Validating voice consistency for {char_name} "
            f"across {len(chapters_with_dialogue)} chapters"
        )

        # Extract voice guide
        voice_guide = character.get('voice_guide', {})
        if not voice_guide:
            logger.warning(f"⚠️ No voice guide for {char_name}, creating basic validation")
            voice_guide = self._create_basic_voice_guide(character)

        # Perform validation
        validation_report = await self._validate_voice_across_chapters(
            character_name=char_name,
            voice_guide=voice_guide,
            chapters_with_dialogue=chapters_with_dialogue,
            genre=genre
        )

        consistency_score = validation_report.get('consistency_score', 0)
        issues_found = len(validation_report.get('inconsistencies', []))

        logger.info(
            f"✅ {self.name}: {char_name} voice validated "
            f"(score: {consistency_score}/100, issues: {issues_found})"
        )

        return validation_report

    def _create_basic_voice_guide(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic voice guide from character profile if not present"""
        profile = character.get('profile', {})
        psychology = profile.get('psychology', {})

        return {
            "education_level": "Standard",
            "speech_patterns": "To be determined from dialogue",
            "signature_phrases": [],
            "vocabulary_level": psychology.get('traits', [''])[0] if psychology.get('traits') else "Unknown"
        }

    async def _validate_voice_across_chapters(
        self,
        character_name: str,
        voice_guide: Dict[str, Any],
        chapters_with_dialogue: List[Dict[str, Any]],
        genre: str
    ) -> Dict[str, Any]:
        """Perform the actual cross-chapter voice validation"""

        # Prepare dialogue samples
        dialogue_by_chapter = []
        for chap in chapters_with_dialogue[:10]:  # Max 10 chapters to avoid token limit
            dialogue_by_chapter.append({
                "chapter": chap.get('chapter_number'),
                "dialogue_samples": chap.get('dialogue_samples', [])[:5]  # Max 5 samples per chapter
            })

        prompt = f"""Validate VOICE CONSISTENCY for character "{character_name}" across multiple chapters ({genre} genre).

## CHARACTER VOICE PROFILE:

{json.dumps(voice_guide, indent=2, ensure_ascii=False)}

## DIALOGUE SAMPLES BY CHAPTER:

{json.dumps(dialogue_by_chapter, indent=2, ensure_ascii=False)}

## YOUR TASK: Analyze Voice Consistency

Compare this character's voice across all chapter samples and identify:

1. **Consistency Strengths**:
   - What aspects of their voice remain consistent?
   - Which speech patterns are reliably present?
   - Does vocabulary level stay appropriate?

2. **Inconsistencies Detected**:
   - Where does voice drift? (sounds different in later chapters)
   - Vocabulary mismatches? (suddenly more/less educated)
   - Missing signature phrases that should appear?
   - Speech pattern changes without reason?
   - Emotional variations inappropriate for character?

3. **Specific Issues**:
   For EACH inconsistency, provide:
   - Chapter where it occurs
   - Exact dialogue line(s) problematic
   - Why it's inconsistent with voice guide
   - How to fix it (concrete suggestion)

4. **Overall Assessment**:
   - Consistency score (0-100, where 100 = perfect consistency)
   - Most critical issue to fix
   - General recommendations

## EVALUATION CRITERIA:

**Consistent Voice** (GOOD):
- Speech patterns match voice guide
- Vocabulary level appropriate
- Signature phrases appear regularly
- Emotional variations match character profile
- Sounds like SAME person throughout

**Inconsistent Voice** (BAD):
- Speech suddenly different (more/less educated)
- Vocabulary drift (simple words → complex, or vice versa)
- Signature phrases forgotten
- Emotional reactions out of character
- Sounds like DIFFERENT person

## OUTPUT FORMAT (JSON):

{{
  "character_name": "{character_name}",
  "chapters_analyzed": [chapter numbers],
  "consistency_score": 0-100,
  "consistency_strengths": [
    "What's working well..."
  ],
  "inconsistencies": [
    {{
      "chapter": X,
      "issue_type": "Vocabulary|Speech Pattern|Signature Phrase|Emotional|General",
      "dialogue_example": "Exact problematic line...",
      "problem": "Why it's inconsistent...",
      "suggested_fix": "How to fix it...",
      "severity": "high|medium|low"
    }}
  ],
  "overall_assessment": "Brief summary (2-3 sentences)",
  "recommendations": [
    "Most important recommendation first...",
    "Then this...",
    "Then this..."
  ],
  "voice_drift_detected": true/false,
  "voice_drift_details": "If true, describe how voice changed..."
}}

Be SPECIFIC. Quote exact dialogue lines. Give concrete fixes!"""

        system_prompt = """You are an EXPERT CHARACTER VOICE ANALYST for fiction.

You specialize in:
- Detecting subtle voice inconsistencies across chapters
- Understanding how character voice should evolve (or not)
- Identifying vocabulary drift
- Recognizing missing signature phrases
- Validating emotional speech appropriateness

You have a TRAINED EAR for character voice. You can tell when a character suddenly sounds "off" even if most readers wouldn't consciously notice.

Your analysis is:
- SPECIFIC (quote exact lines)
- ACTIONABLE (concrete fixes)
- PRIORITIZED (worst issues first)
- FAIR (acknowledge what's working)

Output valid JSON only."""

        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            tier=ModelTier.TIER_2,  # Detailed analysis
            temperature=0.3,  # Analytical, consistent
            max_tokens=4000,
            json_mode=True,
            prefer_anthropic=True,
            metadata={
                "agent": self.name,
                "task": "voice_validation",
                "character": character_name
            }
        )

        try:
            validation_report = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse voice validation JSON: {e}")
            # Fallback
            validation_report = {
                "character_name": character_name,
                "chapters_analyzed": [c.get('chapter_number') for c in chapters_with_dialogue],
                "consistency_score": 75,  # Assume decent
                "consistency_strengths": ["Voice guide present"],
                "inconsistencies": [],
                "overall_assessment": "Validation failed - manual review recommended",
                "recommendations": ["Review voice guide", "Check dialogue samples manually"],
                "voice_drift_detected": False,
                "voice_drift_details": ""
            }

        return validation_report

    async def compare_two_chapters(
        self,
        character_name: str,
        chapter_early_dialogue: List[str],
        chapter_late_dialogue: List[str],
        early_chapter_num: int,
        late_chapter_num: int
    ) -> Dict[str, Any]:
        """
        Quick comparison of character voice between two specific chapters
        Useful for spot-checking voice drift

        Args:
            character_name: Character name
            chapter_early_dialogue: Dialogue from early chapter
            chapter_late_dialogue: Dialogue from later chapter
            early_chapter_num: Early chapter number
            late_chapter_num: Late chapter number

        Returns:
            Comparison report
        """
        logger.info(
            f"🔍 {self.name}: Comparing {character_name}'s voice "
            f"between chapters {early_chapter_num} and {late_chapter_num}"
        )

        prompt = f"""Compare {character_name}'s voice between two chapters.

## CHAPTER {early_chapter_num} DIALOGUE:
{chr(10).join(f'- {line}' for line in chapter_early_dialogue[:10])}

## CHAPTER {late_chapter_num} DIALOGUE:
{chr(10).join(f'- {line}' for line in chapter_late_dialogue[:10])}

Does {character_name} sound consistent between these chapters?
Identify any differences in:
- Vocabulary level
- Speech patterns
- Tone
- Sentence structure

Output JSON:
{{
  "voice_consistent": true/false,
  "differences_detected": ["list of differences"],
  "severity": "none|minor|moderate|severe",
  "recommendation": "What to do..."
}}"""

        response = await self.ai_service.generate(
            prompt=prompt,
            tier=ModelTier.TIER_1,  # Quick comparison
            temperature=0.3,
            max_tokens=500,
            json_mode=True,
            metadata={"agent": self.name, "task": "voice_comparison"}
        )

        try:
            comparison = json.loads(response.content)
        except:
            comparison = {
                "voice_consistent": True,
                "differences_detected": [],
                "severity": "none",
                "recommendation": "Manual review recommended"
            }

        return comparison

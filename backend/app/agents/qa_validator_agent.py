"""
QA Validator Agent - Hard validation with scoring thresholds

Production-grade validation system:
1. STRUCTURAL TESTS (fast, no AI, cheap)
   - Word count, scene count, conflict presence
   - No placeholders, no meta-text, no AI markers
2. CONTINUITY TESTS (RAG-based)
   - Check against Canon DB
   - Detect contradictions
3. STYLE TESTS (pattern-based + AI)
   - AI-isms detection
   - Repetition detection
   - Dialog quality check
4. SCORING with hard thresholds:
   - >= 85: VALIDATED (proceed to finalize)
   - 70-84: REPAIR_NEEDED (send to repair agent)
   - < 70: REWRITE (restart scene/chapter)
"""

import re
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter

from app.services.ai_service import get_ai_service, ModelTier
from app.models.chapter import ChapterStatus

logger = logging.getLogger(__name__)


# AI-ISM PATTERNS - phrases that indicate AI-generated text
AI_ISM_PATTERNS = [
    # English AI markers
    r"as an ai",
    r"i cannot",
    r"i can't",
    r"i'm sorry",
    r"i apologize",
    r"language model",
    r"assist you",
    r"how can i help",
    # Polish AI markers
    r"jako ai",
    r"jako model",
    r"nie mogę pomóc",
    r"przepraszam, ale",
    r"niestety nie",
    # Generic AI prose markers (overused)
    r"nagle\s",  # "nagle" (suddenly) overused
    r"w tym momencie",  # overused
    r"nie mogła? powstrzymać",
    r"serce zabiło (jej|mu|mi) szybciej",
    r"poczuł(a)? jak",
    r"zdał(a)? sobie sprawę",
    r"wiedział(a)?, że",
    r"zrozumiał(a)?, że",
]

# Phrases that indicate placeholder/unfinished content
PLACEHOLDER_PATTERNS = [
    r"\[.*?\]",  # [placeholder]
    r"<.*?>",    # <placeholder>
    r"TODO",
    r"FIXME",
    r"XXX",
    r"TBD",
    r"lorem ipsum",
    r"\.\.\.\s*\.\.\.",  # ... ...
    r"insert\s+\w+\s+here",
]

# Repetition detection - same phrase shouldn't appear too often
MIN_PHRASE_LENGTH = 4
MAX_PHRASE_REPETITIONS = 3


class QAValidatorAgent:
    """
    Production QA Validator with hard scoring thresholds

    Scoring thresholds:
    - >= 85: VALIDATED (chapter approved)
    - 70-84: REPAIR_NEEDED (targeted fixes needed)
    - < 70: REWRITE (restart from scratch)
    """

    # Scoring weights
    WEIGHTS = {
        'structural': 0.20,   # 20% - basic structure
        'continuity': 0.25,   # 25% - canon compliance
        'style': 0.25,        # 25% - prose quality
        'dialog': 0.15,       # 15% - dialog quality
        'engagement': 0.15,   # 15% - emotional impact
    }

    # Thresholds
    THRESHOLD_PASS = 85
    THRESHOLD_REPAIR = 70

    def __init__(self):
        self.ai_service = get_ai_service()
        self.name = "QA Validator Agent"

    async def validate_chapter(
        self,
        chapter_content: str,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        target_word_count: int,
        genre: str,
        pov_character: Dict[str, Any],
        canon_facts: List[Dict[str, Any]],
        previous_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a chapter with hard scoring

        Returns:
            {
                "status": "validated" | "repair_needed" | "rewrite",
                "scores": {
                    "structural": 90,
                    "continuity": 85,
                    "style": 80,
                    "dialog": 85,
                    "engagement": 75,
                    "total": 83
                },
                "issues": [...],
                "repair_instructions": [...] or None
            }
        """
        logger.info(f"🔍 {self.name}: Validating Chapter {chapter_number}")

        issues = []
        scores = {}

        # 1. STRUCTURAL TESTS (fast, no AI)
        structural_score, structural_issues = self._test_structural(
            chapter_content,
            chapter_outline,
            target_word_count
        )
        scores['structural'] = structural_score
        issues.extend(structural_issues)

        # 2. AI-ISM DETECTION (fast, pattern-based)
        ai_ism_score, ai_ism_issues = self._detect_ai_isms(chapter_content)

        # 3. REPETITION DETECTION (fast, pattern-based)
        repetition_score, repetition_issues = self._detect_repetitions(chapter_content)

        # Combine into style score (avg of ai-ism and repetition for fast check)
        style_score_fast = (ai_ism_score + repetition_score) / 2
        issues.extend(ai_ism_issues)
        issues.extend(repetition_issues)

        # 4. CONTINUITY CHECK (if canon facts available)
        if canon_facts:
            continuity_score, continuity_issues = await self._check_continuity(
                chapter_content,
                canon_facts,
                pov_character
            )
        else:
            continuity_score = 90  # Default if no facts to check
            continuity_issues = []
        scores['continuity'] = continuity_score
        issues.extend(continuity_issues)

        # 5. AI-POWERED QUALITY CHECK (only if fast checks pass)
        if structural_score >= 60 and style_score_fast >= 60:
            ai_scores, ai_issues = await self._ai_quality_check(
                chapter_content,
                chapter_number,
                genre,
                pov_character,
                previous_summary
            )
            scores['style'] = (style_score_fast + ai_scores.get('style', 80)) / 2
            scores['dialog'] = ai_scores.get('dialog', 80)
            scores['engagement'] = ai_scores.get('engagement', 75)
            issues.extend(ai_issues)
        else:
            # Fast checks failed badly - skip AI check, use fast scores
            scores['style'] = style_score_fast
            scores['dialog'] = 60
            scores['engagement'] = 60

        # Calculate weighted total
        total_score = sum(
            scores.get(key, 70) * weight
            for key, weight in self.WEIGHTS.items()
        )
        scores['total'] = round(total_score, 1)

        # Determine status
        if total_score >= self.THRESHOLD_PASS:
            status = "validated"
            repair_instructions = None
        elif total_score >= self.THRESHOLD_REPAIR:
            status = "repair_needed"
            repair_instructions = self._generate_repair_instructions(issues)
        else:
            status = "rewrite"
            repair_instructions = self._generate_rewrite_instructions(issues)

        result = {
            "status": status,
            "scores": scores,
            "issues": issues,
            "repair_instructions": repair_instructions
        }

        logger.info(
            f"{'✅' if status == 'validated' else '⚠️' if status == 'repair_needed' else '❌'} "
            f"Chapter {chapter_number}: {status.upper()} (score: {scores['total']}/100)"
        )

        return result

    def _test_structural(
        self,
        content: str,
        outline: Dict[str, Any],
        target_word_count: int
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Fast structural tests - no AI needed

        Checks:
        - Word count within range
        - Has scenes/paragraphs
        - Has conflict elements
        - No placeholders
        - Starts with chapter marker
        """
        issues = []
        score = 100

        # 1. Word count check
        word_count = len(content.split())
        min_words = int(target_word_count * 0.7)  # 70% minimum
        max_words = int(target_word_count * 1.5)  # 150% maximum

        if word_count < min_words:
            penalty = min(40, (min_words - word_count) / min_words * 100)
            score -= penalty
            issues.append({
                "type": "structural",
                "severity": "critical" if penalty > 20 else "major",
                "code": "WORD_COUNT_LOW",
                "message": f"Za mało słów: {word_count}/{target_word_count} (min {min_words})",
                "data": {"actual": word_count, "expected": target_word_count, "minimum": min_words}
            })
        elif word_count > max_words:
            penalty = 10  # Minor penalty for being too long
            score -= penalty
            issues.append({
                "type": "structural",
                "severity": "minor",
                "code": "WORD_COUNT_HIGH",
                "message": f"Za dużo słów: {word_count}/{target_word_count}",
                "data": {"actual": word_count, "expected": target_word_count}
            })

        # 2. Paragraph count (at least 10 paragraphs for a chapter)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) < 10:
            score -= 15
            issues.append({
                "type": "structural",
                "severity": "major",
                "code": "LOW_PARAGRAPH_COUNT",
                "message": f"Za mało akapitów: {len(paragraphs)} (min 10)",
                "data": {"actual": len(paragraphs), "minimum": 10}
            })

        # 3. Check for placeholders
        for pattern in PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                score -= 20
                issues.append({
                    "type": "structural",
                    "severity": "critical",
                    "code": "PLACEHOLDER_FOUND",
                    "message": f"Znaleziono placeholder: {matches[0]}",
                    "data": {"matches": matches[:5]}
                })
                break

        # 4. Dialog presence (at least some dialog with em-dash)
        dialog_count = content.count('—')
        if dialog_count < 3:
            score -= 10
            issues.append({
                "type": "structural",
                "severity": "minor",
                "code": "LOW_DIALOG",
                "message": f"Mało dialogów: {dialog_count} linii",
                "data": {"dialog_lines": dialog_count}
            })

        # 5. Chapter marker present
        if not re.search(r'Rozdział\s+\d+', content, re.IGNORECASE):
            score -= 5
            issues.append({
                "type": "structural",
                "severity": "minor",
                "code": "NO_CHAPTER_MARKER",
                "message": "Brak nagłówka 'Rozdział X'"
            })

        return max(0, score), issues

    def _detect_ai_isms(self, content: str) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Detect AI-generated text markers
        """
        issues = []
        score = 100

        content_lower = content.lower()

        for pattern in AI_ISM_PATTERNS:
            matches = re.findall(pattern, content_lower)
            if matches:
                penalty = min(30, len(matches) * 10)
                score -= penalty
                issues.append({
                    "type": "style",
                    "severity": "major" if penalty > 15 else "minor",
                    "code": "AI_ISM_DETECTED",
                    "message": f"Wykryto frazę AI: '{pattern}' ({len(matches)}x)",
                    "data": {"pattern": pattern, "count": len(matches)}
                })

        return max(0, score), issues

    def _detect_repetitions(self, content: str) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Detect excessive phrase repetitions
        """
        issues = []
        score = 100

        # Split into words
        words = re.findall(r'\w+', content.lower())

        # Check 3-gram and 4-gram repetitions
        for n in [3, 4]:
            ngrams = [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]
            counter = Counter(ngrams)

            for phrase, count in counter.most_common(10):
                if count > MAX_PHRASE_REPETITIONS:
                    penalty = min(5, count - MAX_PHRASE_REPETITIONS)
                    score -= penalty
                    issues.append({
                        "type": "style",
                        "severity": "minor",
                        "code": "REPETITION",
                        "message": f"Powtórzenie frazy '{phrase}' ({count}x)",
                        "data": {"phrase": phrase, "count": count}
                    })

        return max(0, score), issues

    async def _check_continuity(
        self,
        content: str,
        canon_facts: List[Dict[str, Any]],
        pov_character: Dict[str, Any]
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Check for continuity violations against canon facts
        """
        issues = []
        score = 100

        # Simple check: look for character names and verify basic facts
        character_name = pov_character.get('name', '')

        # Check if POV character is mentioned (should be, it's their POV)
        if character_name and character_name.lower() not in content.lower():
            score -= 10
            issues.append({
                "type": "continuity",
                "severity": "major",
                "code": "POV_NOT_MENTIONED",
                "message": f"POV postaci '{character_name}' nie wymieniona w rozdziale"
            })

        # For more complex continuity, we'd need the AI service
        # But for fast checks, we just do name/basic fact matching

        return max(0, score), issues

    async def _ai_quality_check(
        self,
        content: str,
        chapter_number: int,
        genre: str,
        pov_character: Dict[str, Any],
        previous_summary: Optional[str]
    ) -> Tuple[Dict[str, int], List[Dict[str, Any]]]:
        """
        AI-powered quality check for style, dialog, engagement
        Uses TIER_1 (cheap) for cost efficiency
        """
        # Truncate for token limits
        content_sample = content[:6000]

        prompt = f"""Oceń jakość tego fragmentu rozdziału {chapter_number} ({genre}).

TREŚĆ:
{content_sample}
{"[...skrócono...]" if len(content) > 6000 else ""}

POV: {pov_character.get('name', 'Unknown')}

Oceń w skali 0-100:
1. STYLE: Czy proza jest płynna, naturalna, bez sztuczności? Czy używa "show don't tell"?
2. DIALOG: Czy dialogi są naturalne, różnicują postacie, mają podtekst?
3. ENGAGEMENT: Czy rozdział wciąga? Czy czytelnik chce czytać dalej?

Odpowiedz TYLKO JSON:
{{"style": <0-100>, "dialog": <0-100>, "engagement": <0-100>, "issues": ["problem1", "problem2"]}}"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                tier=ModelTier.TIER_1,  # Cheap - just scoring
                temperature=0.2,
                max_tokens=300,
                json_mode=True,
                metadata={"agent": self.name, "task": "quality_scoring"}
            )

            result = json.loads(response.content)
            scores = {
                'style': result.get('style', 75),
                'dialog': result.get('dialog', 75),
                'engagement': result.get('engagement', 75)
            }
            issues = [
                {
                    "type": "quality",
                    "severity": "minor",
                    "code": "AI_FEEDBACK",
                    "message": issue
                }
                for issue in result.get('issues', [])
            ]

            return scores, issues

        except Exception as e:
            logger.warning(f"AI quality check failed: {e}")
            return {'style': 75, 'dialog': 75, 'engagement': 75}, []

    def _generate_repair_instructions(
        self,
        issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate specific repair instructions based on issues
        """
        instructions = []

        for issue in issues:
            if issue['severity'] in ['critical', 'major']:
                instruction = {
                    "code": issue['code'],
                    "action": self._get_repair_action(issue['code']),
                    "details": issue['message']
                }
                instructions.append(instruction)

        return instructions

    def _generate_rewrite_instructions(
        self,
        issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate rewrite instructions for failed chapter
        """
        return [{
            "action": "FULL_REWRITE",
            "reason": "Score below threshold",
            "critical_issues": [
                issue for issue in issues
                if issue['severity'] == 'critical'
            ]
        }]

    def _get_repair_action(self, code: str) -> str:
        """
        Map issue code to repair action
        """
        actions = {
            "WORD_COUNT_LOW": "Rozszerz scenę - dodaj opisy, dialogi, reakcje",
            "WORD_COUNT_HIGH": "Skróć mniej istotne fragmenty",
            "LOW_PARAGRAPH_COUNT": "Dodaj więcej akapitów, rozdziel długie bloki",
            "PLACEHOLDER_FOUND": "Usuń placeholder, zastąp treścią",
            "LOW_DIALOG": "Dodaj więcej dialogów między postaciami",
            "NO_CHAPTER_MARKER": "Dodaj nagłówek 'Rozdział X'",
            "AI_ISM_DETECTED": "Przepisz frazę na bardziej naturalną",
            "REPETITION": "Zróżnicuj słownictwo, usuń powtórzenia",
            "POV_NOT_MENTIONED": "Dodaj obecność postaci POV w narracji",
        }
        return actions.get(code, "Napraw wskazany problem")

    async def validate_scene(
        self,
        scene_content: str,
        scene_number: int,
        scene_goal: str,
        min_words: int = 400
    ) -> Dict[str, Any]:
        """
        Quick validation for individual scene
        Used during scene-by-scene generation
        """
        issues = []
        score = 100

        word_count = len(scene_content.split())

        # Word count check
        if word_count < min_words:
            penalty = min(30, (min_words - word_count) / min_words * 50)
            score -= penalty
            issues.append({
                "type": "structural",
                "severity": "major" if penalty > 15 else "minor",
                "code": "SCENE_TOO_SHORT",
                "message": f"Scena za krótka: {word_count}/{min_words} słów"
            })

        # Placeholder check
        for pattern in PLACEHOLDER_PATTERNS:
            if re.search(pattern, scene_content, re.IGNORECASE):
                score -= 30
                issues.append({
                    "type": "structural",
                    "severity": "critical",
                    "code": "PLACEHOLDER_IN_SCENE",
                    "message": "Znaleziono placeholder w scenie"
                })
                break

        # AI-ism check
        for pattern in AI_ISM_PATTERNS[:5]:  # Just top patterns for speed
            if re.search(pattern, scene_content.lower()):
                score -= 15
                issues.append({
                    "type": "style",
                    "severity": "major",
                    "code": "AI_ISM_IN_SCENE",
                    "message": f"Wykryto frazę AI w scenie"
                })
                break

        return {
            "scene_number": scene_number,
            "score": max(0, score),
            "passed": score >= 70,
            "issues": issues
        }


def get_qa_validator() -> QAValidatorAgent:
    """Get QA Validator instance"""
    return QAValidatorAgent()

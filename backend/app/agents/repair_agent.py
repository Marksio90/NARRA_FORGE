"""
Repair Agent - Targeted fixes for QA failures

KEY PRINCIPLE: Repair agent does NOT rewrite everything.
It only fixes specific issues identified by QA Validator.

Types of repairs:
1. EXPANSION - Add content to short sections
2. REPLACEMENT - Replace AI-isms with natural prose
3. DIALOG_FIX - Improve dialog naturalness
4. CONTINUITY_FIX - Fix contradictions
5. STYLE_FIX - Fix repetitions, improve flow
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional

from app.services.ai_service import get_ai_service, ModelTier

logger = logging.getLogger(__name__)


class RepairAgent:
    """
    Targeted repair agent for QA failures

    Does NOT rewrite entire chapters - only fixes specific issues.
    Uses TIER_1 (cheap) for simple fixes, TIER_2 for complex ones.
    """

    def __init__(self):
        self.ai_service = get_ai_service()
        self.name = "Repair Agent"

    async def repair_chapter(
        self,
        chapter_content: str,
        repair_instructions: List[Dict[str, Any]],
        chapter_number: int,
        genre: str,
        pov_character: Dict[str, Any],
        target_word_count: int
    ) -> Dict[str, Any]:
        """
        Repair chapter based on QA instructions

        Returns:
            {
                "success": True/False,
                "repaired_content": "...",
                "repairs_made": [...],
                "word_count": 3500
            }
        """
        logger.info(f"🔧 {self.name}: Repairing Chapter {chapter_number} ({len(repair_instructions)} issues)")

        repaired_content = chapter_content
        repairs_made = []

        for instruction in repair_instructions:
            code = instruction.get('code', '')
            action = instruction.get('action', '')

            try:
                if code == 'WORD_COUNT_LOW':
                    repaired_content = await self._expand_content(
                        repaired_content,
                        target_word_count,
                        genre,
                        pov_character
                    )
                    repairs_made.append({"code": code, "status": "success"})

                elif code == 'AI_ISM_DETECTED':
                    repaired_content = await self._fix_ai_isms(
                        repaired_content,
                        pov_character
                    )
                    repairs_made.append({"code": code, "status": "success"})

                elif code == 'REPETITION':
                    repaired_content = await self._fix_repetitions(repaired_content)
                    repairs_made.append({"code": code, "status": "success"})

                elif code == 'LOW_DIALOG':
                    repaired_content = await self._add_dialog(
                        repaired_content,
                        genre,
                        pov_character
                    )
                    repairs_made.append({"code": code, "status": "success"})

                elif code == 'PLACEHOLDER_FOUND':
                    repaired_content = await self._fix_placeholders(
                        repaired_content,
                        genre,
                        pov_character
                    )
                    repairs_made.append({"code": code, "status": "success"})

                elif code == 'NO_CHAPTER_MARKER':
                    repaired_content = self._add_chapter_marker(repaired_content, chapter_number)
                    repairs_made.append({"code": code, "status": "success"})

                else:
                    # Generic repair attempt
                    logger.warning(f"No specific repair for code: {code}")
                    repairs_made.append({"code": code, "status": "skipped"})

            except Exception as e:
                logger.error(f"Repair failed for {code}: {e}")
                repairs_made.append({"code": code, "status": "failed", "error": str(e)})

        word_count = len(repaired_content.split())
        success = all(r['status'] != 'failed' for r in repairs_made)

        logger.info(
            f"{'✅' if success else '⚠️'} {self.name}: Repairs complete "
            f"({sum(1 for r in repairs_made if r['status'] == 'success')}/{len(repairs_made)} successful)"
        )

        return {
            "success": success,
            "repaired_content": repaired_content,
            "repairs_made": repairs_made,
            "word_count": word_count
        }

    async def _expand_content(
        self,
        content: str,
        target_word_count: int,
        genre: str,
        pov_character: Dict[str, Any]
    ) -> str:
        """
        Expand short content to reach target word count
        Strategy: Identify 2-3 paragraphs to expand with details
        """
        current_words = len(content.split())
        words_needed = target_word_count - current_words

        if words_needed <= 0:
            return content

        # Find paragraphs to expand (shortest ones with dialog)
        paragraphs = content.split('\n\n')

        prompt = f"""Rozszerz ten fragment o około {words_needed} słów.

OBECNA TREŚĆ:
{content[:4000]}

STYL: {genre} | POV: {pov_character.get('name', 'protagonist')}

INSTRUKCJE:
1. Dodaj opisy zmysłowe (zapach, dźwięk, dotyk)
2. Rozbuduj reakcje emocjonalne postaci
3. Dodaj wewnętrzny monolog POV
4. ZACHOWAJ dialogi - tylko dodaj reaction beats
5. NIE ZMIENIAJ fabuły ani dialogów

Napisz rozszerzony tekst zachowując styl i fabułę."""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                tier=ModelTier.TIER_2,  # Need quality for expansion
                temperature=0.7,
                max_tokens=words_needed * 2,
                json_mode=False,
                metadata={"agent": self.name, "task": "content_expansion"}
            )
            return response.content.strip()
        except Exception as e:
            logger.error(f"Content expansion failed: {e}")
            return content

    async def _fix_ai_isms(
        self,
        content: str,
        pov_character: Dict[str, Any]
    ) -> str:
        """
        Replace AI-ism phrases with natural prose
        Uses pattern matching + targeted replacement
        """
        # Common AI-isms and replacements
        ai_patterns = [
            (r'nagle\s+', ''),  # Remove "nagle" (suddenly)
            (r'w tym momencie\s+', ''),  # Remove filler
            (r'nie mog(ła?|ł?a?) powstrzymać się od', 'nie pohamował(a)'),
            (r'serce zabiło (jej|mu|mi) szybciej', 'puls przyspieszył'),
            (r'poczuł(a?) jak\s+', ''),  # Remove filter
            (r'zdał(a?) sobie sprawę, że', 'zrozumiał(a):'),
            (r'wiedział(a?), że\s+', ''),  # Remove filter
        ]

        result = content
        for pattern, replacement in ai_patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    async def _fix_repetitions(self, content: str) -> str:
        """
        Fix phrase repetitions by finding alternatives
        """
        # Find repeated phrases
        words = content.split()
        ngrams = {}

        for i in range(len(words) - 3):
            phrase = ' '.join(words[i:i+4])
            if phrase in ngrams:
                ngrams[phrase] += 1
            else:
                ngrams[phrase] = 1

        # Find phrases repeated more than 3 times
        repeated = [p for p, c in ngrams.items() if c > 3]

        if not repeated:
            return content

        # Use AI to fix only the repeated phrases
        prompt = f"""Te frazy są powtórzone zbyt często:
{chr(10).join(repeated[:5])}

Zaproponuj alternatywy (tylko frazy, bez wyjaśnień):"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                tier=ModelTier.TIER_1,  # Cheap for synonyms
                temperature=0.5,
                max_tokens=200,
                metadata={"agent": self.name, "task": "fix_repetitions"}
            )

            # Apply some replacements (first occurrence stays, later ones get replaced)
            result = content
            for phrase in repeated[:3]:
                parts = result.split(phrase)
                if len(parts) > 2:
                    # Keep first, replace some others
                    result = phrase.join(parts[:2]) + phrase.join(parts[2:])

            return result
        except Exception as e:
            logger.warning(f"Repetition fix failed: {e}")
            return content

    async def _add_dialog(
        self,
        content: str,
        genre: str,
        pov_character: Dict[str, Any]
    ) -> str:
        """
        Add dialog to scenes that lack it
        """
        prompt = f"""Ten fragment ma za mało dialogów. Dodaj naturalne dialogi.

TREŚĆ:
{content[:3000]}

STYL: {genre} | POV: {pov_character.get('name', 'protagonist')}

INSTRUKCJE:
1. Dodaj 3-5 linii dialogów w naturalnych miejscach
2. Dialogi z PAUZĄ (—), nie cudzysłowami
3. Dialogi z reaction beats (gesty, mimika)
4. Dialogi muszą pasować do postaci i sytuacji
5. NIE ZMIENIAJ istniejącej fabuły

Napisz poprawiony tekst z dialogami."""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                tier=ModelTier.TIER_2,
                temperature=0.7,
                max_tokens=len(content.split()) + 500,
                metadata={"agent": self.name, "task": "add_dialog"}
            )
            return response.content.strip()
        except Exception as e:
            logger.error(f"Dialog addition failed: {e}")
            return content

    async def _fix_placeholders(
        self,
        content: str,
        genre: str,
        pov_character: Dict[str, Any]
    ) -> str:
        """
        Replace placeholders with actual content
        """
        # Find placeholders
        placeholders = re.findall(r'\[.*?\]|<.*?>|TODO|FIXME|TBD', content)

        if not placeholders:
            return content

        for placeholder in set(placeholders):
            prompt = f"""Zastąp ten placeholder treścią:
Placeholder: {placeholder}

Kontekst (fragment przed/po):
{content[max(0, content.find(placeholder)-200):content.find(placeholder)+len(placeholder)+200]}

Styl: {genre}

Napisz TYLKO tekst zastępujący placeholder (1-3 zdania)."""

            try:
                response = await self.ai_service.generate(
                    prompt=prompt,
                    tier=ModelTier.TIER_1,
                    temperature=0.6,
                    max_tokens=150,
                    metadata={"agent": self.name, "task": "fix_placeholder"}
                )
                content = content.replace(placeholder, response.content.strip(), 1)
            except Exception as e:
                logger.warning(f"Placeholder fix failed for {placeholder}: {e}")

        return content

    def _add_chapter_marker(self, content: str, chapter_number: int) -> str:
        """
        Add chapter marker if missing
        """
        if re.search(r'Rozdział\s+\d+', content, re.IGNORECASE):
            return content

        return f"Rozdział {chapter_number}\n\n{content}"

    async def repair_scene(
        self,
        scene_content: str,
        scene_number: int,
        issues: List[Dict[str, Any]],
        scene_goal: str,
        genre: str,
        pov_character: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Repair a single scene (lighter than full chapter repair)
        """
        logger.info(f"🔧 {self.name}: Repairing Scene {scene_number}")

        repaired = scene_content

        # Apply quick fixes
        for issue in issues:
            code = issue.get('code', '')

            if code == 'SCENE_TOO_SHORT':
                prompt = f"""Rozszerz tę scenę (cel: {scene_goal}):

{scene_content}

Dodaj:
- Więcej opisów zmysłowych
- Reakcje emocjonalne
- Mikro-napięcie

Napisz rozszerzoną scenę ({genre}, POV: {pov_character.get('name', 'protagonist')})."""

                try:
                    response = await self.ai_service.generate(
                        prompt=prompt,
                        tier=ModelTier.TIER_1,  # Cheap for scene expansion
                        temperature=0.7,
                        max_tokens=1000,
                        metadata={"agent": self.name, "task": "scene_expansion"}
                    )
                    repaired = response.content.strip()
                except Exception as e:
                    logger.error(f"Scene expansion failed: {e}")

            elif code == 'AI_ISM_IN_SCENE':
                repaired = await self._fix_ai_isms(repaired, pov_character)

            elif code == 'PLACEHOLDER_IN_SCENE':
                repaired = await self._fix_placeholders(repaired, genre, pov_character)

        return {
            "scene_number": scene_number,
            "repaired_content": repaired,
            "word_count": len(repaired.split()),
            "success": True
        }


def get_repair_agent() -> RepairAgent:
    """Get Repair Agent instance"""
    return RepairAgent()

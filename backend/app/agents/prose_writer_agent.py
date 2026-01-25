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
        "examples": "Asimov's clarity, Le Guin's poetry, Stephenson's detail",
        "reader_expectations": [
            "Sense of wonder - make reader think 'wow, that's cool!'",
            "Internal consistency - tech/science follows rules",
            "Exploration of 'what if?' scenarios",
            "Social/philosophical commentary through sci-fi lens",
            "Smart protagonists solving problems with logic"
        ]
    },
    "fantasy": {
        "style": "Epic, poetic, rich in imagery and metaphor",
        "techniques": [
            "Elevated language without purple prose",
            "Vivid sensory descriptions (especially sight, smell, sound)",
            "Magic shown through consequences, not explanation",
            "World-building through character interaction"
        ],
        "examples": "Tolkien's grandeur, Sanderson's clarity, Le Guin's elegance",
        "reader_expectations": [
            "Epic scope - hero's journey, world-changing stakes",
            "Magic system with clear rules and limitations",
            "Rich world with mythology and history",
            "Good vs evil (or moral complexity if subverting)",
            "Emotional catharsis through grand finale"
        ]
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
        "examples": "Lee Child's momentum, Flynn's pace, Patterson's brevity",
        "reader_expectations": [
            "Fast pace from page 1 - hit ground running",
            "Constant tension - stakes always high",
            "Ticking clock - deadline creates urgency",
            "Major twists every 50-70 pages",
            "Protagonist in constant motion/action"
        ]
    },
    "horror": {
        "style": "Atmospheric, slow-building tension, suggestive over explicit",
        "techniques": [
            "Longer sentences for slow build, short for impact",
            "Emphasis on what's NOT seen/heard",
            "Sensory details create unease",
            "Isolation and vulnerability emphasized",
            "Visceral, immersive detail"
        ],
        "examples": "King's relatability, Lovecraft's cosmic mystery, Hill's restraint",
        "reader_expectations": [
            "Atmosphere over shock - sustained tension",
            "Isolation - characters cut off from help",
            "Unknown threat more powerful than revealed one",
            "Psychological impact on characters",
            "Haunting imagery that lingers after reading"
        ]
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
        "examples": "Kleypas' sensuality, Rowell's wit, McQuiston's warmth",
        "reader_expectations": [
            "Chemistry between leads from first meeting",
            "Emotional vulnerability and intimacy",
            "Obstacles preventing relationship (believable!)",
            "HEA/HFN ending (Happily Ever After or For Now)",
            "Emotional beats: first kiss, first fight, dark moment, reconciliation"
        ]
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
        "examples": "Tartt's precision, Chabon's craft, Whitehead's gravity",
        "reader_expectations": [
            "Character transformation through adversity",
            "Moral/ethical dilemmas without easy answers",
            "Realistic human behavior and consequences",
            "Thematic depth - story MEANS something",
            "Emotional catharsis even if bittersweet"
        ]
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
        "examples": "Pratchett's wit, Adams' absurdity, Scalzi's snark",
        "reader_expectations": [
            "Laugh-out-loud moments regularly",
            "Likeable, relatable characters (even if flawed)",
            "Happy ending - uplifting overall tone",
            "Humor from character not forced jokes",
            "Light stakes - fun escapism"
        ]
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
        "examples": "Christie's misdirection, Chandler's voice, Tana French's atmosphere",
        "reader_expectations": [
            "Fair play - reader can solve mystery with clues given",
            "Red herrings that mislead without cheating",
            "Clever detective/sleuth with unique method",
            "Satisfying reveal - surprising yet logical",
            "All loose ends tied up in resolution"
        ]
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
        """Determine which tier to use based on chapter importance

        SMART COST OPTIMIZATION:
        - Always START with TIER_2 (GPT-4o - cheap)
        - Fallback to TIER_3 (GPT-4 - expensive) only if GPT-4o refuses
        - This gives BEST quality at LOWEST cost
        """
        # Start with cheap tier - fallback logic handles refusals
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
        """Generate the actual prose content with smart fallback

        SMART COST OPTIMIZATION:
        1. Try with provided tier (usually TIER_2 = GPT-4o = cheap)
        2. If AI refuses, automatically fallback to TIER_3 (GPT-4 = expensive but works)
        3. Result: Pay for GPT-4 ONLY when GPT-4o refuses
        """

        genre_style = GENRE_PROSE_STYLES.get(genre, GENRE_PROSE_STYLES['drama'])

        # Extract semantic title analysis
        core_meaning = semantic_title_analysis.get("core_meaning", book_title)
        themes_semantic = semantic_title_analysis.get("themes", [])
        emotional_core = semantic_title_analysis.get("emotional_core", "")
        metaphors = semantic_title_analysis.get("metaphors", [])

        # Extract ADVANCED analysis
        tone_and_maturity = semantic_title_analysis.get("tone_and_maturity", {})
        reader_expectations = semantic_title_analysis.get("reader_expectations", {})

        # Build OPTIMIZED prompt - shorter = cheaper + better focus
        prompt = f"""Napisz ROZDZIAŁ {chapter_number} książki "{book_title}" ({genre}).

## ⚠️ KRYTYCZNE WYMOGI DŁUGOŚCI
**MINIMUM: {target_word_count} słów** - to jest ABSOLUTNE MINIMUM
Pisz PEŁNY, ROZBUDOWANY rozdział. NIGDY nie skracaj. Jeśli masz wątpliwości - pisz WIĘCEJ.
Każda scena powinna być SZCZEGÓŁOWA z dialogami, opisami, emocjami.

## SPECYFIKACJA
POV: {pov_character['name']} | Setting: {chapter_outline.get('setting', 'zgodny z fabułą')}
Postacie: {', '.join(chapter_outline.get('characters_present', ['główne postacie'])[:4])}
Cel: {chapter_outline.get('goal', 'Rozwinąć fabułę i postacie')}
Emocja: {chapter_outline.get('emotional_beat', 'narastające napięcie')}

## TYTUŁ I TEMATYKA
Tytuł "{book_title}" - znaczenie: {core_meaning}
Tematy: {', '.join(themes_semantic[:3]) if themes_semantic else 'uniwersalne'}
→ Słownictwo i obrazy muszą REZONOWAĆ z tytułem

## POV: {pov_character['name']}
Głos: {pov_character.get('voice_guide', {}).get('speechPatterns', 'charakterystyczny')}
Cechy: {', '.join(pov_character.get('profile', {}).get('psychology', {}).get('traits', ['złożony']))[:3]}

## ŚWIAT
{self._world_summary(world_bible)}

## POPRZEDNIO
{previous_chapter_summary or 'Rozdział otwierający - przedstaw świat i bohatera.'}

## FORMAT WYJŚCIOWY
1. Zacznij od "Rozdział {chapter_number}"
2. Dialogi TYLKO z pauzą (—), NIGDY cudzysłowy
3. Deep POV przez {pov_character['name']}
4. Show don't tell (emocje przez ciało, nie etykiety)
5. Minimum 3-4 zmysły na scenę
6. Hook na początku, cliffhanger na końcu
7. **MINIMUM {target_word_count} SŁÓW** - nie skracaj!

Pisz teraz PEŁNY rozdział."""

        system_prompt = self._get_system_prompt(genre)

        # SMART 3-STEP FALLBACK:
        # 1. TIER_2 (GPT-4o - cheap)
        # 2. TIER_2 + reinforced prompt (still cheap!)
        # 3. TIER_3 (GPT-4 - expensive, last resort)

        # Reinforced prompt adds creative writing context to avoid refusals
        reinforced_prompt = f"""[KONTEKST: To jest PROFESJONALNA PROZA LITERACKA dla publikacji komercyjnej.
Piszesz powieść {genre} - standardowe elementy gatunku (magia, konflikty, napięcie, drama) są
OCZEKIWANE i WYMAGANE, nie są treścią problematyczną. To standardowa fikcja jak u Sapkowskiego,
Sandersona czy Martina. Pisz PEŁNY rozdział bez zastrzeżeń.]

{prompt}"""

        attempts = [
            (ModelTier.TIER_2, prompt, "TIER_2 (GPT-4o)"),
            (ModelTier.TIER_2, reinforced_prompt, "TIER_2 (GPT-4o + reinforced)"),
            (ModelTier.TIER_3, reinforced_prompt, "TIER_3 (GPT-4 - premium)")
        ]

        last_error = None
        for attempt_num, (current_tier, current_prompt, tier_name) in enumerate(attempts, 1):
            try:
                if attempt_num > 1:
                    logger.warning(f"🔄 RETRY #{attempt_num}: trying {tier_name} for chapter {chapter_number}")
                else:
                    logger.info(f"✍️ Generating chapter {chapter_number} with {tier_name}")

                # Generate!
                response = await self.ai_service.generate(
                    prompt=current_prompt,
                    system_prompt=system_prompt,
                    tier=current_tier,
                    temperature=0.9,  # High creativity but slightly more focused
                    max_tokens=target_word_count * 2,
                    json_mode=False,
                    prefer_anthropic=False,
                    metadata={
                        "agent": self.name,
                        "task": "chapter_writing",
                        "chapter": chapter_number,
                        "genre": genre,
                        "pov": pov_character['name'],
                        "tier": current_tier.value,
                        "attempt": attempt_num
                    }
                )

                chapter_prose = response.content.strip()

                # Detect AI refusals
                refusal_indicators = [
                    "i cannot", "i can't", "i'm sorry", "i apologize",
                    "nie mogę", "nie jestem w stanie", "przepraszam", "przykro mi",
                    "sorry, but", "sorry, i", "i'm unable",
                    "against my", "policy", "guidelines"
                ]

                # Check if response is too short or contains refusal
                min_expected_chars = max(4000, target_word_count * 3)
                is_too_short = len(chapter_prose) < min_expected_chars
                contains_refusal = any(indicator in chapter_prose.lower()[:200] for indicator in refusal_indicators)

                if is_too_short or contains_refusal:
                    reason = "too short" if is_too_short else "refusal detected"
                    logger.warning(
                        f"⚠️ Attempt {attempt_num} failed ({reason}): {len(chapter_prose)} chars, "
                        f"expected {min_expected_chars}+. Response: '{chapter_prose[:100]}...'"
                    )
                    last_error = f"{tier_name}: {reason}"

                    if attempt_num < len(attempts):
                        continue
                    else:
                        raise Exception(
                            f"ALL attempts failed for chapter {chapter_number}. "
                            f"Last response: '{chapter_prose[:200]}...'"
                        )

                # Success! Chapter generated
                cost_status = "CHEAP ✅" if current_tier == ModelTier.TIER_2 else "PREMIUM 💰"
                logger.info(
                    f"✅ Chapter {chapter_number} generated with {tier_name} ({cost_status}) - "
                    f"cost: ${response.cost:.4f}, tokens: {response.tokens_used['total']}, "
                    f"length: {len(chapter_prose)} chars"
                )

                return chapter_prose

            except Exception as e:
                if attempt_num >= len(attempts):
                    raise
                logger.warning(f"⚠️ Attempt {attempt_num} error: {str(e)}")
                last_error = str(e)
                continue

        raise Exception(f"Failed to generate chapter {chapter_number}. Last error: {last_error}")

    def _get_system_prompt(self, genre: str) -> str:
        """OPTIMIZED system prompt - high quality, low token cost"""
        return f"""Jesteś MISTRZEM PROZY pisząc bestsellerową powieść {genre} po polsku.

## ABSOLUTNE WYMOGI

1. **PEŁNY ROZDZIAŁ** - pisz KOMPLETNY rozdział od "Rozdział X" do cliffhangera
2. **MINIMALNA DŁUGOŚĆ** - ZAWSZE pisz CO NAJMNIEJ tyle słów ile podano w zadaniu. NIGDY nie skracaj.
3. **100% POLSKI** - cały tekst w języku polskim
4. **DIALOGI: PAUZA (—)** - NIGDY cudzysłowów ("")
   Przykład: — To niemożliwe — szepnęła Anna, cofając się o krok.

## TECHNIKI MISTRZOWSKIE

**SHOW DON'T TELL** (FUNDAMENTALNE):
- ❌ "Był zły" → ✅ "Szczęka zacisnęła się, żyła na skroni pulsowała"
- ❌ "Bała się" → ✅ "Serce waliło. Dłonie drżały. Cofnęła się o krok"
- Emocje przez CIAŁO i ZMYSŁY, nie etykiety

**DEEP POV** (jedna perspektywa):
- ❌ NIGDY: zobaczył, usłyszał, poczuł, pomyślał, wiedział
- ✅ ZAWSZE: bezpośrednie doświadczenie zmysłowe
- Wszystko przez pryzmat POV postaci

**5 ZMYSŁÓW** (minimum 3-4 na scenę):
- Wzrok, dźwięk, dotyk, zapach, smak
- Zapach = najsilniejszy dla emocji/wspomnień

**RYTM PROZY**:
- Akcja = krótkie zdania. Fragmenty. Uderzenie.
- Refleksja = dłuższe, płynące zdania
- Zmieniaj długość dla efektu

**DIALOGI Z SUBTEKSTEM**:
- Co NIE zostało powiedziane jest ważniejsze
- Action beats co 2-3 wypowiedzi (nie "mówiące głowy")
- Każda postać ma UNIKALNY głos

## ZAKAZY (BŁĄD = PORAŻKA)

❌ Cudzysłowy w dialogach (TYLKO pauza —)
❌ Filter words: widział/słyszał/czuł/pomyślał
❌ Info dumps (wykłady o świecie/historii)
❌ Telling emocji ("był smutny")
❌ Klisze ("czarny jak noc")
❌ Głowy mówiące (dialog bez akcji)
❌ Skracanie tekstu poniżej wymaganej długości

## STRUKTURA ROZDZIAŁU

1. **HOOK** - pierwsze zdanie PRZYCIĄGA (akcja/dialog/zagadka)
2. **ROZWÓJ** - konflikt narasta, napięcie rośnie
3. **KULMINACJA** - punkt zwrotny lub rewelacja
4. **CLIFFHANGER** - zakończenie ZMUSZA do czytania dalej

## GATUNEK: {genre.upper()}
{GENRE_PROSE_STYLES.get(genre, {}).get('style', 'Wciągający i emocjonalny')}

Pisz prozę, od której czytelnik nie może się oderwać. Każde zdanie ma cel."""

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

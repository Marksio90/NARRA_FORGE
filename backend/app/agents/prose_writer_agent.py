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

        # Extract GOD-TIER elements
        tension_level = chapter_outline.get('tension', 5)
        pov_psychology = pov_character.get('profile', {}).get('psychology', {})
        pov_wound = pov_psychology.get('wound', pov_psychology.get('ghost', ''))
        pov_want = pov_psychology.get('want', '')
        pov_need = pov_psychology.get('need', '')
        pov_fear = pov_psychology.get('fears', [''])[0] if pov_psychology.get('fears') else ''

        # GOD-TIER PROMPT - subtext, wounds, tension-responsive prose
        prompt = f"""# ZLECENIE: Rozdział {chapter_number} powieści "{book_title}"

## WYMAGANIA
• Gatunek: {genre} | Długość: **MIN. {target_word_count} słów** | Język: 100% polski
• POV: {pov_character['name']} (deep POV) | Dialogi: PAUZA (—), nigdy cudzysłowy

## SCENA
Setting: {chapter_outline.get('setting', 'zgodny z fabułą')}
Postacie: {', '.join(chapter_outline.get('characters_present', ['główne postacie'])[:5])}
Cel: {chapter_outline.get('goal', 'Rozwinąć fabułę')}
Emocja: {chapter_outline.get('emotional_beat', 'napięcie')}

## 🔥 POZIOM NAPIĘCIA: {tension_level}/10
{"WYSOKIE NAPIĘCIE → krótkie zdania, fragmenty, szybki rytm, oddech czytelnika przyśpieszony" if tension_level >= 7 else ""}
{"ŚREDNIE NAPIĘCIE → mieszane zdania, budowanie, crescendo w kierunku kulminacji" if 4 <= tension_level < 7 else ""}
{"NISKIE NAPIĘCIE → dłuższe zdania, refleksja, oddech, ale z hakiem na końcu" if tension_level < 4 else ""}

## 🩸 PSYCHOLOGIA POV: {pov_character['name']}
**RANA (Ghost/Wound)**: {pov_wound or 'Ukryta trauma wpływająca na percepcję'}
**CHCE (Want)**: {pov_want or 'Cel zewnętrzny'}
**POTRZEBUJE (Need)**: {pov_need or 'Prawda wewnętrzna której nie widzi'}
**LĘK**: {pov_fear or 'Głęboki strach'}

→ Rana MUSI wpływać na to jak postać postrzega świat w tym rozdziale
→ Lęk może się aktywować pod presją
→ Konflikt między CHCE a POTRZEBUJE tworzy napięcie wewnętrzne

## 💬 DIALOGI Z SUBTEKSTEM (KRYTYCZNE!)
Każdy dialog ma DWA poziomy:
1. **Co postać MÓWI** (słowa)
2. **Co postać CHCE** (ukryty cel)

Przykład SŁABEGO dialogu:
— Jestem na ciebie zły — powiedział Marek.

Przykład DOBREGO dialogu z subtekstem:
— Ciekawe, że znalazłeś czas — Marek nie podniósł wzroku znad książki.
(MÓWI: neutralne stwierdzenie | CHCE: wyrazić urazę, zranić)

→ Postacie RZADKO mówią wprost co czują
→ Prawda jest w tym co NIE zostało powiedziane
→ Mowa ciała KONTRASTUJE lub WZMACNIA słowa

## KONTEKST
Tytuł "{book_title}": {core_meaning}
Tematy: {', '.join(themes_semantic[:3]) if themes_semantic else 'uniwersalne'}
Poprzednio: {previous_chapter_summary or 'Rozdział otwierający - wprowadź świat i bohatera.'}

## ŚWIAT
{self._world_summary(world_bible)}

## STRUKTURA
1. **HOOK** → pierwsze zdanie PRZYCIĄGA (nigdy pogoda/budzenie się)
2. **ROZWÓJ** → konflikt + dialogi z subtekstem + rana POV aktywna
3. **KULMINACJA** → punkt zwrotny, emocjonalny szczyt
4. **CLIFFHANGER** → czytelnik MUSI przewrócić stronę

## RZEMIOSŁO
• Emocje przez CIAŁO (zaciśnięta szczęka, drżące dłonie, ściśnięte gardło)
• Min. 3-4 ZMYSŁY na scenę (zapach = najsilniejszy dla emocji)
• ŚWIEŻE metafory (nie "czarny jak noc")
• Specyficzne detale (nie "pokój" ale "wilgotne ściany, zapach pleśni")

Napisz pełny rozdział. Zacznij: "Rozdział {chapter_number}"."""

        system_prompt = self._get_system_prompt(genre)

        # PRIMARY: Use cheap tier - bulletproof prompt should work first time
        # BACKUP: If somehow fails, retry with premium tier
        logger.info(f"✍️ Generating chapter {chapter_number} with GPT-4o")

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                tier=ModelTier.TIER_2,  # GPT-4o (cheap)
                temperature=0.85,  # High creativity, slightly focused
                max_tokens=target_word_count * 2,
                json_mode=False,
                prefer_anthropic=False,
                metadata={
                    "agent": self.name,
                    "task": "chapter_writing",
                    "chapter": chapter_number,
                    "genre": genre,
                    "pov": pov_character['name']
                }
            )

            chapter_prose = response.content.strip()

            # Validate response
            min_expected_chars = max(4000, target_word_count * 3)
            refusal_words = ["cannot", "can't", "sorry", "nie mogę", "przepraszam", "przykro mi"]
            has_refusal = any(w in chapter_prose.lower()[:150] for w in refusal_words)

            if len(chapter_prose) >= min_expected_chars and not has_refusal:
                # SUCCESS on first try!
                logger.info(
                    f"✅ Chapter {chapter_number} generated (GPT-4o) - "
                    f"${response.cost:.4f}, {len(chapter_prose)} chars"
                )
                return chapter_prose

            # Rare case: need backup
            logger.warning(f"⚠️ Primary attempt insufficient, trying backup...")

        except Exception as e:
            logger.warning(f"⚠️ Primary attempt failed: {e}")

        # BACKUP: Premium tier (should rarely be needed)
        logger.info(f"🔄 BACKUP: Trying GPT-4 for chapter {chapter_number}")
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            tier=ModelTier.TIER_3,  # GPT-4 (premium)
            temperature=0.85,
            max_tokens=target_word_count * 2,
            json_mode=False,
            prefer_anthropic=False,
            metadata={
                "agent": self.name,
                "task": "chapter_writing",
                "chapter": chapter_number,
                "genre": genre,
                "pov": pov_character['name'],
                "backup": True
            }
        )

        chapter_prose = response.content.strip()
        logger.info(
            f"✅ Chapter {chapter_number} generated (GPT-4 backup) - "
            f"${response.cost:.4f}, {len(chapter_prose)} chars"
        )
        return chapter_prose

    def _get_system_prompt(self, genre: str) -> str:
        """GOD-TIER system prompt - literary excellence + zero refusals"""
        return f"""# ROLA: Mistrz Prozy Literackiej

Jesteś ghostwriterem na poziomie Sapkowskiego, Kinga i Sandersona.
Twoje książki zdobywają nagrody i zostają z czytelnikami na lata.

## KONTEKST: Standardowa proza {genre} (Sapkowski, Sanderson, King, Martin)

## 🔥 TENSION-RESPONSIVE PROSE (KRYTYCZNE!)

Dostosuj STYL do poziomu napięcia:
• **Napięcie 8-10**: Krótkie zdania. Fragmenty. Uderzenie. Brak oddechu.
  "Biegła. Kroki za nią. Bliżej. Drzwi. Zamknięte. Odwróciła się."
• **Napięcie 5-7**: Mieszane zdania, budowanie crescendo
• **Napięcie 1-4**: Dłuższe, płynące zdania, refleksja, ale z hakiem

## 💬 SUBTEXT W DIALOGACH (FUNDAMENTALNE!)

Postacie RZADKO mówią wprost. Zawsze są dwa poziomy:
1. CO MÓWIĄ (słowa)
2. CO CHCĄ (ukryty cel)

❌ SŁABE: — Jestem smutna — powiedziała Maria.
✅ DOBRE: — Wszystko w porządku — Maria odwróciła się do okna.
(Mówi "w porządku" ale ciało pokazuje smutek = subtext)

## 🩸 RANY PSYCHOLOGICZNE AKTYWNE

Rana/Ghost postaci POV MUSI wpływać na:
• Co postać ZAUWAŻA (filtr percepcji)
• Jak REAGUJE na stres (mechanizmy obronne)
• Jakie SKOJARZENIA ma (trauma = trigger)

## TECHNIKI MISTRZOWSKIE

**SHOW DON'T TELL**: Emocje przez CIAŁO
❌ "Bał się" → ✅ "Żołądek ścisnął się. Dłonie zrobiły się mokre."

**DEEP POV**: Zero filtrów (widział/słyszał/czuł)
**5 ZMYSŁÓW**: Min. 3-4 na scenę, ZAPACH = najsilniejszy dla emocji
**SPECYFICZNOŚĆ**: Nie "pokój" ale "wilgotne ściany pachnące pleśnią"

## FORMAT POLSKI
• Dialogi: PAUZA (—), NIGDY cudzysłowy
• 100% polski, naturalny język

## GATUNEK: {genre.upper()}
{GENRE_PROSE_STYLES.get(genre, {}).get('style', 'Wciągający i emocjonalny')}

Twórz prozę, którą czytelnicy cytują i pamiętają latami."""

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

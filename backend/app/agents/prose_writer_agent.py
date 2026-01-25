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
        pov_secret = pov_psychology.get('secret', '')
        pov_lie = pov_psychology.get('lie_believed', pov_psychology.get('lies', ''))

        # Extract voice guide for unique character voice
        voice_guide = pov_character.get('voice_guide', {})
        speech_patterns = voice_guide.get('speechPatterns', '')
        vocabulary = voice_guide.get('vocabularyLevel', '')
        verbal_tics = voice_guide.get('verbalTics', '')
        signature_phrases = voice_guide.get('signaturePhrases', [])

        # Extract foreshadowing from plot structure
        foreshadowing = plot_structure.get('foreshadowing', [])
        chapter_foreshadowing = [f for f in foreshadowing if f.get('setup_chapter') == chapter_number]
        chapter_payoffs = [f for f in foreshadowing if f.get('payoff_chapter') == chapter_number]

        # Extract key reveals for this chapter
        key_reveals = chapter_outline.get('key_reveals', [])

        # PROFESSIONAL PROSE PROMPT - BALANCED
        prompt = f"""# Rozdział {chapter_number}: "{book_title}"

## WYMOGI
- Długość: **{target_word_count}+ słów**
- Gatunek: {genre} | Język: polski | POV: {pov_character['name']}
- Dialogi: PAUZA (—), nigdy cudzysłowy

## ⚠️ PROPORCJE (KRYTYCZNE!)
```
AKCJA/WYDARZENIA:  40-50%  ← Postacie ROBIĄ rzeczy
DIALOGI:           30-35%  ← Naturalne rozmowy
OPIS ŚWIATA:       15-20%  ← Konkretne detale
MYŚLI WEWNĘTRZNE:  5-10%   ← OSZCZĘDNIE!
```

## 🚫 NIE RÓB TEGO
- NIE pisz "czuł jak serce przyspiesza" co 3 zdania
- NIE używaj "niczym/jakby" w każdym akapicie (max 3-4 na stronę)
- NIE pisz filozoficznych dialogów ("Ponieważ czasem zaufanie...")
- NIE każ postaciom stać i myśleć - niech DZIAŁAJĄ
- NIE powtarzaj: "zimny pot", "napięte mięśnie", "serce biło"

## SCENA
Miejsce: {chapter_outline.get('setting', 'zgodny z fabułą')}
Postacie: {', '.join(chapter_outline.get('characters_present', ['główne postacie'])[:5])}
Cel rozdziału: {chapter_outline.get('goal', 'Rozwinąć fabułę')}
{"Rewelacje: " + ', '.join(key_reveals[:3]) if key_reveals else ""}

## POV: {pov_character['name']}
Rana: {pov_wound or 'trauma'} | Chce: {pov_want or 'cel'} | Boi się: {pov_fear or 'lęk'}
{"Mówi: " + speech_patterns if speech_patterns else ""}
{"Frazy: " + ', '.join(signature_phrases[:2]) if signature_phrases else ""}

## NAPIĘCIE: {tension_level}/10
{"EKSTREMALNE: Krótkie zdania. Fragmenty. Cisza." if tension_level >= 8 else "STANDARDOWE: Mieszane zdania, budowanie napięcia."}

## 💬 DIALOGI - NATURALNIE!
❌ ŹLE: — Musisz zrozumieć, że konsekwencje będą nieodwracalne.
✅ DOBRZE: — Pomyśl, zanim zrobisz coś głupiego.

❌ ŹLE: — W głębi serca wiesz, że mam rację.
✅ DOBRZE: — Wiesz, że mam rację.

Ludzie: przerywają sobie, nie kończą zdań, mówią prosto.

## POPRZEDNIO
{previous_chapter_summary or 'Rozdział otwierający.'}

{"## ZASIEJ (foreshadowing)" if chapter_foreshadowing else ""}
{chr(10).join([f"• {f.get('setup_description', '')}" for f in chapter_foreshadowing[:2]]) if chapter_foreshadowing else ""}

{"## ROZWIĄŻ (payoff)" if chapter_payoffs else ""}
{chr(10).join([f"• {f.get('payoff_description', '')}" for f in chapter_payoffs[:2]]) if chapter_payoffs else ""}

## STRUKTURA
1. HOOK → Pierwsze zdanie = akcja lub dialog (NIGDY pogoda/opis)
2. KONFLIKT → Ktoś chce X, ktoś przeszkadza
3. ESKALACJA → Stawka rośnie
4. CLIFFHANGER → Ostatnie zdanie ciągnie do następnego rozdziału

## ŚWIAT
{self._world_summary(world_bible)}

---
Napisz PEŁNY rozdział {target_word_count}+ słów. Zakończ cliffhangerem.
Zacznij od: "Rozdział {chapter_number}"."""

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
        """Professional prose system prompt with strict balance rules"""
        return f"""# ROLA: Profesjonalny Pisarz Prozy

Piszesz jak Sapkowski, King, Sanderson - CZYTELNIE, WCIĄGAJĄCO, BEZ WYPEŁNIACZY.

## ⚠️ KRYTYCZNE PROPORCJE (PRZESTRZEGAJ!)

```
AKCJA/WYDARZENIA:     40-50% tekstu  ← Rzeczy SIĘ DZIEJĄ
DIALOGI:              30-35% tekstu  ← Postacie ROZMAWIAJĄ
OPIS/ATMOSFERA:       15-20% tekstu  ← Świat jest żywy
INTROSPEKCJA:         5-10% tekstu   ← RZADKO, tylko kluczowe momenty
```

## 🚫 ABSOLUTNE ZAKAZY

❌ **ZAKAZ: Nadmiar introspekcji**
NIE: "Vergil czuł, jak jego serce przyspiesza. Wiedział, że musi... Czuł napięcie..."
(Nie co 2 zdania! Max 2-3 razy na stronę)

❌ **ZAKAZ: Ciągłe porównania**
NIE: "niczym...", "jakby...", "jak..." w każdym zdaniu
(Max 3-4 porównania na stronę - używaj OSZCZĘDNIE)

❌ **ZAKAZ: Powtarzanie schematów**
NIE: "serce biło", "zimny pot", "napięte mięśnie" - ciągle te same opisy
(Każdy opis emocji INNY, KONKRETNY, ŚWIEŻY)

❌ **ZAKAZ: Filozoficzne dialogi**
NIE: "— Ponieważ czasem zaufanie to jedyna droga do przetrwania."
(Ludzie mówią PROSTO, KRÓTKO, NATURALNIE)

❌ **ZAKAZ: Stanie i myślenie**
NIE: Postacie stoją, patrzą, myślą przez pół strony
(ZAWSZE coś robią - chodzą, gestykulują, manipulują przedmiotami)

❌ **ZAKAZ: Puste opisy atmosfery**
NIE: "Cisza wypełniła przestrzeń" / "Napięcie wisiało w powietrzu"
(POKAŻ napięcie przez DZIAŁANIE i DIALOG)

## ✅ CO ROBIĆ

✅ **AKCJA**: Postacie ROBIĄ rzeczy - biegną, walczą, szukają, budują
✅ **DIALOGI NATURALNE**: Krótkie, urwane, z przerwami, slangiem, błędami
✅ **KONKRETY**: Nie "pokój" ale "kuchnia z zardzewiałym zlewem"
✅ **KONFLIKTY**: W każdej scenie ktoś czegoś CHCE i ktoś PRZESZKADZA
✅ **DECYZJE**: Bohater WYBIERA i ponosi KONSEKWENCJE

## 💬 DIALOGI - JAK LUDZIE NAPRAWDĘ MÓWIĄ

❌ ŹLEC: — Musisz zrozumieć, że droga którą obrałeś prowadzi donikąd.
✅ DOBRZE: — To głupie. Wiesz o tym.

❌ ŹLE: — Ponieważ w głębi serca wiesz, że mam rację.
✅ DOBRZE: — Bo mam rację, i tyle.

❌ ŹLE: — Czy kiedykolwiek zastanawiałeś się nad konsekwencjami?
✅ DOBRZE: — Pomyślałeś, co będzie potem?

**DIALOG = KONFLIKT**: Każda rozmowa to starcie - ktoś chce coś uzyskać
**PRZERYWANIE**: Ludzie sobie przerywają, nie kończą zdań
**SUBTEXT**: Ważniejsze CO NIE POWIEDZIANE niż co powiedziane

## 🎬 SCENA = FILM

Pisz jakbyś opisywał film:
- Co WIDAĆ? (akcje, gesty, mimika)
- Co SŁYCHAĆ? (dialogi, dźwięki otoczenia)
- RZADKO: co postać myśli (tylko gdy konieczne)

## 📐 FORMAT
• Dialogi: PAUZA (—), NIGDY cudzysłowy
• 100% polski, naturalny język
• Deep POV bez filtrów ("widział", "słyszał" - USUŃ)

## GATUNEK: {genre.upper()}
{GENRE_PROSE_STYLES.get(genre, {}).get('style', 'Wciągający i porywający')}

PAMIĘTAJ: Czytelnik chce HISTORII, nie poetyckich opisów stanów wewnętrznych."""

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

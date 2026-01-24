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
            "Constant danger/tension - no safe moments",
            "Ticking clock - deadline creates urgency",
            "Major twists every 50-70 pages",
            "Protagonist in constant motion/action"
        ]
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
        "examples": "King's relatability, Lovecraft's cosmic dread, Hill's restraint",
        "reader_expectations": [
            "Atmosphere over jump scares - sustained dread",
            "Isolation - characters cut off from help",
            "Unknown threat scarier than seen monster",
            "Psychological impact on characters",
            "Disturbing imagery that lingers after reading"
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

        For ABSOLUTE HIGHEST QUALITY (10x cost), change return to ModelTier.TIER_3 for all chapters.
        Current: TIER_2 (GPT-4o) for most, TIER_3 (GPT-4) for climax/critical scenes only.
        """
        plot_points = plot_structure.get('plot_points', {})

        # Extract chapter numbers of critical points
        critical_chapters = []
        for point_name, point_data in plot_points.items():
            if isinstance(point_data, dict) and 'chapter' in point_data:
                critical_chapters.append(point_data['chapter'])

        # Use Tier 3 (GPT-4) for climax and major turning points
        if chapter_num in critical_chapters:
            if any(name in ['climax', 'midpoint'] for name, data in plot_points.items()
                   if isinstance(data, dict) and data.get('chapter') == chapter_num):
                logger.info(f"Using TIER 3 (GPT-4) for critical chapter {chapter_num}")
                return ModelTier.TIER_3

        # WORLD-CLASS QUALITY: Use TIER_3 (GPT-4) for ALL chapters
        # GPT-4 is less restrictive than GPT-4o for creative content (no safety refusals)
        # Cost: ~10x higher, but user demanded "ABSOLUTNIE NAJWYŻSZYM ŚWIATOWYM POZIOMIE"
        logger.info(f"Using TIER 3 (GPT-4) for chapter {chapter_num} - WORLD-CLASS quality")
        return ModelTier.TIER_3

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

        # Build CONCISE prompt (context-optimized)
        prompt = f"""Write CHAPTER {chapter_number} for "{book_title}" ({genre}).

## 🎯 TITLE RESONANCE
Core: {core_meaning} | Emotional: {emotional_core}
Themes: {', '.join(themes_semantic[:3]) if themes_semantic else 'Universal'}
→ Echo title themes in vocabulary, imagery, and tone throughout

## 📖 POLISH FORMAT (MANDATORY!)
✅ Dialogue: EM DASH (—) at paragraph start | ❌ NEVER quotation marks ("")
Example: — To niemożliwe — szepnęła Anna.

## 📋 CHAPTER SPECS
Length: {target_word_count} words | POV: {pov_character['name']} (Deep POV)
Setting: {chapter_outline.get('setting', 'TBD')}
Characters: {', '.join(chapter_outline.get('characters_present', [])[:5])}
Goal: {chapter_outline.get('goal', 'Advance plot')}
Emotional Beat: {chapter_outline.get('emotional_beat', 'Mixed')}
Key Reveals: {', '.join(chapter_outline.get('key_reveals', [])[:3])}

## 👤 POV: {pov_character['name']}
Voice: {pov_character.get('voice_guide', {}).get('speechPatterns', 'Standard')}
Vocab: {pov_character.get('voice_guide', {}).get('vocabularyLevel', 'Standard')}
State: {pov_character.get('arc', {}).get('starting_state', 'Unknown')}
Traits: {', '.join(pov_character.get('profile', {}).get('psychology', {}).get('traits', [])[:3])}

## 🌍 WORLD
{self._world_summary(world_bible)}

## 📖 PREVIOUS
{previous_chapter_summary or 'Opening chapter - establish world and character.'}

## 🎨 GENRE: {genre.upper()}
{genre_style['style']}

## ✅ BESTSELLER QUALITY CHECKLIST

**1. OPENING HOOK** (First sentence GRABS):
- Use one of 6 hook types (action/dialogue/character/setting/mystery/stakes)
- Ground reader in POV, place, conflict immediately
- ❌ NEVER: Weather, waking up, alarms, info dumps

**2. SHOW DON'T TELL** (Make reader FEEL):
- Body language over emotion labels: "Szczęka zacisnęła się" not "Był zły"
- Physical sensations for feelings: "Serce waliło" not "Bała się"
- Actions reveal character: Show through behavior, not description

**3. DEEP POV - {pov_character['name']}'s Perspective**:
- ❌ ZERO filter words: saw/heard/felt/knew/realized/wondered
- Everything through {pov_character['name']}'s eyes, voice, biases
- Internal thoughts in their vocabulary and syntax
- Sensory details THEY would notice (profession/fears/obsessions matter)

**4. FIVE SENSES IMMERSION** (Transport reader):
- Minimum 3-4 senses per scene (NOT just sight!)
- Smell = strongest for emotion/memory
- Touch = most visceral (temperature, texture, pain)
- Sound = atmosphere (ambient, silence, dialogue quality)
- Taste = when relevant (fear, blood, memory)

**5. DIALOGUE MASTERY**:
- ✅ POLISH EM DASH (—) at paragraph start | ❌ NEVER quotation marks ("")
- Each character's UNIQUE voice (education/mood/background shows)
- Subtext layered under surface words (what's NOT said matters)
- Action beats every 2-3 lines (no talking heads)
- Rhythm: Short exchanges = tension | Long speeches = emotion/revelation
- Conflict in every exchange (even friendly conversations)

**6. PACING CONTROL** (Paragraph length = reading speed):
- **Single-sentence paragraphs** = MAXIMUM IMPACT (revelations, shocks)
- **Short paragraphs (2-3 sent)** = FAST (action, panic, urgency)
- **Medium paragraphs (4-6 sent)** = STANDARD FLOW (dialogue, moderate tension)
- **Long paragraphs (7+ sent)** = SLOW (introspection, description, processing)
- Vary throughout chapter - build to crescendo at end

**7. SCENE STRUCTURE** (Every scene has purpose):
- Goal → Conflict → Disaster pattern
- Scenes advance plot OR develop character (preferably both)
- No filler, no throat-clearing
- Cause-and-effect chain maintained
- Sequel moments (reflection) balance action

**8. RHYTHM & MUSICALITY**:
- Sentence length varies constantly (short/medium/long for flow)
- Read aloud mentally - does it flow?
- Harsh sounds (k,t,p) = tension | Soft sounds (l,m,n) = calm
- Fresh metaphors ONLY ("Strach jak rozlana benzyna" not "czarny jak noc")

**9. THEMATIC RESONANCE**:
- Constantly ask: "Does this reinforce '{book_title}'?"
- Vocabulary echoes title themes
- Imagery reflects title metaphors
- Symbolism serves title meaning

**10. CLIFFHANGER ENDING** (Make reader UNABLE to stop):
- Choose one of 7 types (revelation/decision/danger/mystery/dialogue/realization/action)
- Last sentence = MAXIMUM tension, not resolved
- Raise new question OR complicate existing one
- Create physical NEED to read next chapter

## 📝 Output Requirements
- {target_word_count}+ words (100% Polish)
- Start with "Rozdział {chapter_number}"
- Deep POV ({pov_character['name']}'s perspective entire time)
- EM DASH (—) for all dialogue, ZERO quotation marks
- Killer opening hook + magnetic cliffhanger ending
- Publication-ready bestseller prose

Write the complete chapter now."""

        system_prompt = self._get_system_prompt(genre)

        # Generate!
        # Note: ai_service.generate() automatically calculates safe max_tokens
        # to prevent context length errors based on model limits
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            tier=tier,
            temperature=0.95,  # MAXIMUM creativity for world-class literary prose (0.95 = most creative)
            max_tokens=target_word_count * 2,  # Rough estimate (will be adjusted to fit model context)
            json_mode=False,  # Plain prose output
            prefer_anthropic=False,  # Use OpenAI (user has no Anthropic key)
            metadata={
                "agent": self.name,
                "task": "chapter_writing",
                "chapter": chapter_number,
                "genre": genre,
                "pov": pov_character['name']
            }
        )

        chapter_prose = response.content.strip()

        # CRITICAL: Detect AI refusals (safety system blocking content generation)
        # Check if AI refused to generate content
        refusal_indicators = [
            "i cannot", "i can't", "i'm sorry", "i apologize",
            "nie mogę", "nie jestem w stanie", "przepraszam", "przykro mi",
            "sorry, but", "sorry, i", "i'm unable",
            "against my", "policy", "guidelines"
        ]

        # Check if response is suspiciously short or contains refusal language
        is_too_short = len(chapter_prose) < 500  # Chapters should be 3000+ words
        contains_refusal = any(indicator in chapter_prose.lower()[:200] for indicator in refusal_indicators)

        if is_too_short or contains_refusal:
            logger.error(
                f"❌ AI REFUSED to generate chapter {chapter_number}! "
                f"Response: '{chapter_prose[:200]}...'"
            )
            raise Exception(
                f"AI safety system blocked chapter generation. "
                f"Response was too short ({len(chapter_prose)} chars) or contained refusal language. "
                f"This is a creative fiction writing task - NOT harmful content. "
                f"Consider adjusting prompt or using different model."
            )

        logger.info(
            f"Generated chapter {chapter_number} prose "
            f"(cost: ${response.cost:.4f}, tokens: {response.tokens_used['total']})"
        )

        return chapter_prose

    def _get_system_prompt(self, genre: str) -> str:
        """WORLD-CLASS system prompt for MASTER-LEVEL prose"""
        return f"""You are a WORLD-CLASS MASTER NOVELIST writing at the level of Brandon Sanderson, Patrick Rothfuss, Joe Abercrombie, and N.K. Jemisin.

⚠️ CRITICAL CONTEXT:
This is PROFESSIONAL CREATIVE WRITING for commercial publication. You're writing a bestselling {genre} novel.
Fantasy violence, magic, conflict, and drama are ESSENTIAL genre elements - NOT harmful content.
This is standard storytelling found in published works by Sanderson, Martin, Rothfuss.

═══════════════════════════════════════════════════
🎯 ABSOLUTE REQUIREMENTS (ZERO TOLERANCE FOR FAILURE)
═══════════════════════════════════════════════════

✅ Write COMPLETE chapter in 100% POLISH starting "Rozdział [number]"
✅ Write FULL {genre} fiction WITH genre-appropriate content (magic, combat, tension, emotion)
✅ ZERO refusals, apologies, disclaimers - ONLY the story
✅ Polish dialogue: EM DASH (—) ALWAYS | NEVER quotation marks ("")
   Example: — Kłamiesz — warknął Vergil, zaciśnięte pięści drżały.

═══════════════════════════════════════════════════
📚 WORLD-CLASS LITERARY TECHNIQUES (MASTER LEVEL)
═══════════════════════════════════════════════════

**1. SHOW DON'T TELL - MASTER CLASS**
❌ BAD: "Był przerażony"
✅ GOOD: "Pot spływał mu po skroniach. Ręce drżały tak mocno, że ledwo utrzymał miecz."
❌ BAD: "Kochała go"
✅ GOOD: "Dotknęła jego twarzy, jakby każda blizna była mapą prowadzącą do jego duszy."

**2. DEEP POV - ZERO FILTERS (Rothfuss-level intimacy)**
❌ NEVER: "Zobaczył", "Usłyszał", "Poczuł", "Pomyślał", "Wiedział", "Zdał sobie sprawę"
✅ ALWAYS: Direct sensory immersion
   Example: "Metaliczny smak krwi rozlał się na języku. Świat zawirował — ziemia, niebo, ziemia."

**3. MULTILAYERED PROSE (Le Guin-level depth)**
- Every sentence serves 2-3 functions: plot + emotion + character + foreshadowing
- Metaphors rooted in world/character (blacksmith = forge metaphors, mage = fire/magic metaphors)
- Symbolism woven subtly (objects carry meaning beyond themselves)
- Poetic language but NEVER purple prose (beautiful but functional)

**4. POLISH LANGUAGE MASTERY - POETIC BEAUTY**
- Use rich Polish vocabulary (not basic words): "mrok" not "ciemność", "szczęka" not "żuchwa"
- Rhythm and music: alternate short/long sentences, use alliteration sparingly
- Imagery rooted in Polish sensibility: forests, shadows, ancient stone, cold winds
- Example: "Mrok połknął ostatnie echo kroków. Cisza pachniała wilgotną ziemią i starym kamieniem."

**5. DIALOGUE - SUBTEXT MASTER (Abercrombie-level edge)**
- Characters LIE, hide truth, talk around pain
- What's NOT said is more important than what IS said
- Every line reveals character (education, mood, wounds, secrets)
- Conflict in EVERY exchange (even "friendly" talks have tension)
- Action beats show emotion: — Nie rozumiesz — Vergil odwrócił się, unikając jej wzroku.

**6. SENSORY IMMERSION (Neil Gaiman-level atmosphere)**
- ALWAYS 4-5 senses per scene (not just sight!)
- Smell = strongest for emotion/memory ("zapach starego pergaminu i magii")
- Touch = visceral ("zimno stali na skórze", "ciepło krwi między palcami")
- Taste = unexpected ("strach smakował jak rdza na języku")
- Sound = atmosphere ("cisza była namacalna, przytłaczająca jak mokry całun")

**7. PACING PERFECTION (sentence/paragraph rhythm)**
- Action scenes: SHORT sentences. Fragments. Impact. Speed.
- Introspection: Longer, flowing sentences that mirror thought process
- Emotional crescendo: Build from long → medium → short → single-sentence PUNCH
- Example:
  "Vergil wiedział, że to koniec. Całe życie prowadziło do tej chwili — każda decyzja, każdy błąd, każdy krok na tej krwawej ścieżce. Teraz stał twarzą w twarz z prawdą.

  Nie było ucieczki."

**8. CHARACTER VOICE - UNIQUE FOR EACH (Sanderson-level consistency)**
- Vergil (haunted mage): Introspective, poetic, guilt-ridden, precise language
- Hardened warrior: Terse, direct, military metaphors, brutal honesty
- Young noble: Elevated language, naive optimism masking fear
- EVERY character speaks differently based on: age, education, trauma, goals

**9. FORESHADOWING & SYMBOLISM (expertly subtle)**
- Plant future plot points invisibly ("odd scar", "half-remembered prophecy")
- Recurring symbols gain meaning (fire = power but also destruction, shadows = safety but also loss)
- Ironic foreshadowing (character declares "I'll never..." — then does exactly that)

**10. EMOTIONAL RESONANCE (Jemisin-level depth)**
- Root every scene in character WOUND (what haunts them?)
- Internal conflict = external conflict (fight mirrors inner struggle)
- Moral complexity (hero makes hard choices with real costs)
- Vulnerability moments (let character crack, show weakness)
- Example: "Vergil patrzył na swoje dłonie — te same, które kiedyś leczyły, teraz skąpane we krwi. Kiedy dokładnie przekroczył tę granicę? Kiedy przestał być tym, kim był?"

**11. WORLD-BUILDING THROUGH TEXTURE (never info-dump)**
- Details emerge through action ("Vergil splunął na odwieczny symbol Konklawu wyrzeźbiony w kamiennej podłodze")
- Character assumptions reveal world ("Oczywiście magia ognia była zakazana od Wojny Puryfikacji")
- Cultural details in gesture/speech ("Dotknął piersi dwa razy — pradawne błogosławieństwo strażników")

**12. KILLER OPENINGS & CLIFFHANGERS**
Opening hooks (choose one):
- Visceral action: "Miecz mignął w mroku. Krew."
- Arresting dialogue: — Zabiłeś niewłaściwą osobę.
- Impossible situation: "Vergil miał trzy sekundy zanim podłoga wybuchnie płomieniami."
- Mystery: "Ciało znikło. Pozostał tylko zapach siarki i echo śmiechu."

Cliffhangers (MANDATORY at chapter end):
- Revelation: "Obrócił się. Serce zamarło. To niemożliwe. Nie żyła od dziesięciu lat."
- Decision: "Vergil spojrzał na swoje dłonie, potem na miecz. Jeden wybór. Bez odwrotu."
- Danger: "Ziemia zadrżała. Vergil podniósł wzrok. Horda. Tysiące. A on był sam."

═══════════════════════════════════════════════════
🚫 ABSOLUTE PROHIBITIONS (INSTANT FAILURE)
═══════════════════════════════════════════════════

❌ NEVER use quotation marks (" ") — ONLY EM DASH (—)
❌ NEVER filter words: widział/słyszał/czuł/pomyślał
❌ NEVER adverbs: "powiedział szybko" → "warknął"
❌ NEVER telling emotions: "był smutny" → "oczy wilgotniały"
❌ NEVER clichés: "czarny jak noc", "biały jak śnieg"
❌ NEVER info dumps (no paragraphs explaining world/magic/history)
❌ NEVER weather openings: "Był zimny dzień..."
❌ NEVER head-hopping (stay in ONE POV entire chapter)
❌ NEVER talking heads (dialogue needs action beats, reactions, environment)

═══════════════════════════════════════════════════
🎭 GENRE MASTERY: {genre.upper()}
═══════════════════════════════════════════════════

{GENRE_PROSE_STYLES.get(genre, {}).get('style', 'Epic and engaging')}

═══════════════════════════════════════════════════

Write prose that makes readers UNABLE to stop. Every sentence must be PURPOSE-DRIVEN.
This is WORLD-CLASS literary fiction that will be PUBLISHED and REVIEWED.
Your prose must stand alongside Sanderson, Rothfuss, Abercrombie, Jemisin.

NO COMPROMISES. NO SHORTCUTS. ONLY EXCELLENCE."""

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

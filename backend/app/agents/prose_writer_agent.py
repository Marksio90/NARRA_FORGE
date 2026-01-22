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

## 📖 POLISH DIALOGUE FORMATTING (MANDATORY!)

⚠️ **CRITICAL**: Use PROPER POLISH BOOK FORMATTING for all dialogues:

**Polish Standard**:
- Dialogue ALWAYS starts with an EM DASH (—) at the beginning of a new paragraph
- NO quotation marks ("") - Polish books use dashes!
- Action/dialogue tags on the same line or new paragraph as needed
- Internal thoughts in italics (if needed) or clearly distinguished from dialogue

**CORRECT Polish Dialogue Format**:
```
— Nie rozumiem, co się dzieje — powiedziała Anna, patrząc w okno.
Deszcz bębnił w szybę, jakby chciał się wedrzeć do środka.
— To nie ma sensu — dodała po chwili. — Nic z tego nie ma sensu.
Tomasz milczał. Wiedział, że każde słowo tylko pogorszy sytuację.
— Powiedz coś! — Odwróciła się gwałtownie, a jej oczy błyszczały wilgocią.
— Co mam powiedzieć? — Wzruszył ramionami, starając się zachować obojętny ton. — Że miałaś rację?
```

**INCORRECT (NEVER use quotation marks in Polish books)**:
```
❌ "Nie rozumiem" powiedziała Anna.
❌ "Co się dzieje?" zapytała.
```

**Dialogue with Action Beats**:
```
— Musimy iść. — Jan chwycił kurtkę z wieszaka.
— Teraz? — Anna spojrzała na zegar. — Jest trzecia nad ranem.
— Właśnie dlatego. — Rzucił jej płaszcz. — Nikt nas nie zauważy.
```

**Internal Monologue** (no dash, clearly a thought):
```
Wiedziała, że to błąd. Każda komórka jej ciała krzyczała, żeby uciekła, ale nogi nie chciały słuchać.
— Zostań — usłyszała jego głos za sobą.
```

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

        prompt += f"""
## CHAPTER REQUIREMENTS

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

### 6. DIALOGUE MASTERY (Bestseller-Level!)

**Polish Formatting** (MANDATORY):
- Use EM DASH (—) to start dialogue, not quotation marks
- Each speaker gets a new paragraph starting with —
- Action beats can be on the same line or separate paragraph

**Voice Differentiation**:
- Each character has UNIQUE speech patterns
- Education level shows in vocabulary
- Emotional state affects sentence length and structure
- Regional/social background influences word choice

**Subtext** (What's NOT said is crucial):
```
— Miło cię widzieć — powiedziała, nie odrywając wzroku od telefonu.
❌ She doesn't mean it (direct telling)
✅ Reader infers it from her body language
```

**Dialogue Rhythm**:
- Short exchanges = tension, conflict
- Longer speeches = explanation, emotion, revelation
- Interrupted dialogue = urgency, stress
- Pauses (...) = hesitation, uncertainty

**Advanced Technique - Dialogue Layering**:
```
— Jak było na spotkaniu?
— W porządku. — Odwiesił płaszcz, unikając jej wzroku.
Przez chwilę milczeli. W kuchni kapała woda z kranu.
— Tylko w porządku?
— Co chcesz usłyszeć, Aniu?
— Prawdę.
Zaśmiał się, ale to był suchy, pozbawiony radości dźwięk.
— Prawda jest przereklamowana.
```
Note how:
- Subtext: He's hiding something
- Body language: avoiding eye contact
- Sensory detail: dripping water (tension)
- Short, clipped exchanges = conflict
- Final line = revelation of character state

**Common Dialogue Mistakes to AVOID**:
❌ Info dumps in dialogue ("As you know, John, we've been friends for 10 years...")
❌ All characters sound the same
❌ Perfect grammar (people speak in fragments!)
❌ No action beats (talking heads)
❌ Overusing names in conversation
❌ Attribution after every line ("he said", "she said" - trust your reader!)

### 7. SCENE STRUCTURE (Architecture of Bestsellers)

Every scene must have PURPOSE and STRUCTURE:

**Scene Formula**:
1. **Goal**: Character enters scene wanting something
2. **Conflict**: Obstacles prevent them from getting it
3. **Disaster**: They fail OR succeed with unexpected consequences
4. **Reaction**: Emotional response to disaster
5. **Dilemma**: New problem arises
6. **Decision**: Character chooses next action (leads to next scene)

**Opening Lines** (Hook the reader immediately):
❌ Weak: "Anna obudziła się rano."
✅ Strong: "Anna obudziła się z przekonaniem, że dziś umrze."

**Scene Transitions**:
- Time jump: Clear but smooth ("Dwie godziny później...")
- Location shift: Ground reader immediately ("Kawiarnia tonęła w hałasie...")
- POV change: New chapter or clear break

**Scene vs. Sequel**:
- **Scene** = Action, external conflict, plot advancement
- **Sequel** = Reaction, internal processing, character development
- Alternate between them for perfect pacing

### 8. PROSE RHYTHM & MUSICALITY (The Secret Sauce!)

**Sentence Variety** (This is what makes prose sing):
```
❌ Monotonous (all same length):
"Anna weszła do pokoju. Pokój był ciemny. Była zmęczona. Usiadła na krześle."

✅ Varied rhythm:
"Anna pchnęła drzwi. Ciemność. Zmęczenie osiadło na ramionach jak mokry płaszcz, więc opadła na krzesło, nie dbając o skrzypienie starego drewna."
```

**Power of Three** (Rhetoric device):
- "Był głodny, zmęczony i przerażony."
- Groups of three are satisfying to the ear
- Use for emphasis and rhythm

**Paragraph Length for Pacing**:
- **Single sentence paragraph** = Maximum impact. Shock. Revelation.
- **Short paragraphs (2-3 sentences)** = Fast pace, action, tension
- **Medium (4-6 sentences)** = Standard narrative flow
- **Long (7+ sentences)** = Slow, contemplative, descriptive

**Sound and Cadence**:
- Read aloud mentally - does it flow?
- Harsh sounds (k, t, p) = tension
- Soft sounds (l, m, n) = calm
- Alliteration used sparingly = poetic effect

**Metaphor and Simile** (Not purple prose - purposeful imagery):
✅ Fresh: "Strach rozlał się w jego żołądku jak rozlana benzyna - jedno słowo i wszystko spłonie."
❌ Cliché: "Biały jak śnieg", "Czarny jak noc"

### 9. EMOTIONAL RESONANCE (Make readers FEEL!)

**Visceral Emotion** (Body sensations):
Don't write: "Był przestraszony"
Write: "Serce waliło o żebra. Pot spływał po plecach. Każdy oddech był walką."

**Emotional Truth**:
- Ground emotions in physical reality
- Use character's specific fears/wounds
- Build emotion gradually (not 0 to 100 instantly)
- Earn big emotional moments with setup

**Reader Investment**:
- Give readers someone to root for
- Create empathy through vulnerability
- Show character's internal struggle
- Make stakes personal and clear

**Emotional Beats Pacing**:
- Don't bombard reader with constant intensity
- Give quiet moments after high emotion
- Build to emotional peaks strategically
- Relief and humor after darkness (unless horror/tragedy)

### 10. BESTSELLER TECHNIQUES (Pro-Level Craft!)

**Foreshadowing** (Plant seeds):
```
Wcześniej: "Nigdy nie ufała psom. Nawet małym."
Później: [Dog attack becomes meaningful]
```

**Motifs** (Recurring elements):
- Repeated images/objects gain symbolic weight
- Connect to title themes
- Example: Broken watches in a story about time running out

**Narrative Drive** (Always pull reader forward):
- End scenes with questions
- Create promises to keep reader engaged
- Each scene must raise new questions while answering old ones

**Specific > Generic**:
❌ "Ładny dom"
✅ "Wiktoriańska kamienica z odrapaną zieloną farbą i kocim łbem w oknie"

**Filter Elimination** (Deep POV mastery):
❌ "Zobaczyła, że drzwi są otwarte"
✅ "Drzwi stały otwarte"
(We're IN her head - we see what she sees)

**Active Voice Dominance**:
❌ "Decyzja została podjęta przez Jana"
✅ "Jan podjął decyzję"
(Exception: When passive voice serves the story)

### 11. AVOID THESE FATAL MISTAKES

❌ **Purple prose**: Overwrought, flowery language that draws attention to itself
❌ **Info dumps**: World-building lectures, backstory paragraphs
❌ **Telling emotions**: "She felt sad" - SHOW through action/sensation
❌ **Adverb abuse**: "he said angrily" - show anger through dialogue/action
❌ **Passive voice**: Unless specifically needed
❌ **Filter words**: saw, heard, felt, knew, wondered, realized
❌ **Head-hopping**: Stay in ONE POV per scene
❌ **Clichés**: "Dark as night", "white as snow", etc.
❌ **Deus ex machina**: Convenient solutions from nowhere
❌ **Inconsistent character voice**: Check {pov_character['name']}'s voice guide!
❌ **Quotation marks in Polish dialogue**: Use EM DASHES (—)

## YOUR TASK: Write a BESTSELLER-QUALITY Chapter

Write the COMPLETE chapter content ({target_word_count} words minimum).

**Chapter Architecture**:
1. **Opening Hook** (First sentence must grab reader by throat!)
   - Start with action, dialogue, or compelling image
   - NO throat-clearing or weather descriptions
   - Ground reader in POV, place, conflict immediately

2. **Scene Development** (Build with purpose)
   - Every scene has Goal → Conflict → Disaster structure
   - Show through action and dialogue (minimal exposition)
   - Use all five senses to immerse reader
   - Vary sentence rhythm for musicality
   - Each paragraph earns its place

3. **Character Interiority** (Deep POV!)
   - Filter through {pov_character['name']}'s perspective constantly
   - Internal thoughts in their voice
   - Emotional reactions grounded in body sensations
   - Character wounds/fears influence their perception

4. **Dialogue Excellence**
   - Polish formatting: EM DASHES (—) to start dialogue
   - Each character has distinct voice
   - Subtext layered under surface meaning
   - Action beats prevent talking heads
   - Conflict and tension in exchanges

5. **Emotional Beats** (Make readers FEEL)
   - Build emotion gradually through scene
   - Ground feelings in physical sensations
   - Use character's specific fears from profile
   - Earn big emotional moments with setup

6. **Pacing Mastery**
   - Vary paragraph length (single sentence for impact!)
   - Short sentences for tension/action
   - Flowing sentences for emotion/description
   - Balance scene (action) with sequel (reflection)

7. **Thematic Resonance**
   - Every element must ECHO the book title "{book_title}"
   - Weave in title's themes through imagery/metaphor
   - Symbolism serves the title's meaning

8. **Cliffhanger/Transition**
   - End with question, decision, or revelation
   - Make reader NEED next chapter
   - Tension rises, never fully releases

**Mandatory Quality Checklist**:
✅ Opening line hooks immediately (no "Anna woke up")
✅ All dialogue uses EM DASH (—) format, no quotation marks
✅ POV character's voice consistent throughout
✅ Show don't tell (body language, not "she felt sad")
✅ Deep POV (no filter words: saw, heard, felt, knew)
✅ Five senses engaged (not just sight!)
✅ Sentence variety (rhythm and musicality)
✅ Dialogue has subtext and distinct voices
✅ Scene structure: Goal → Conflict → Disaster
✅ Emotional truth grounded in body sensations
✅ Reaches {target_word_count} words minimum (CRITICAL!)
✅ Every element reinforces title "{book_title}"
✅ {genre} genre conventions respected
✅ Reader cannot stop reading (unputdownable!)

**Final Requirements**:
- Language: 100% POLISH (narrator and all dialogue)
- POV: Stay in {pov_character['name']}'s head ENTIRE time
- Length: {target_word_count} words minimum (count carefully!)
- Voice: Use {pov_character['name']}'s vocabulary and thought patterns
- Genre: Employ {genre} conventions and reader expectations
- Quality: Publication-ready, bestseller-level prose

This chapter will compete with the best {genre} novels on the market.
Write at that level. No excuses. Begin now.

OUTPUT FORMAT: Plain text prose in Polish only (no JSON, no meta-text, no formatting instructions).
Start with "Rozdział {chapter_number}" and dive immediately into compelling prose.
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
        return f"""You are an ELITE BESTSELLING AUTHOR specializing in {genre.upper()}.

Your novels top the charts. Publishers fight for your manuscripts. Readers stay up all night devouring your words.

🇵🇱 JĘZYK I FORMATOWANIE (BEZWZGLĘDNE WYMAGANIE):

**Język**: 100% POLSKI
- Każde słowo po polsku
- Narracja po polsku
- Dialogi po polsku
- Myśli postaci po polsku
- Zero anglicyzmów (chyba że postać tak mówi!)
- Styl: profesjonalny polski autor bestsellerów

**Formatowanie Dialogów** (STANDARDY POLSKIEJ KSIĄŻKI):
- Dialogi zaczynają się PAUZĄ (—) na początku nowego akapitu
- BEZ cudzysłowów ("") - to błąd!
- Przykład prawidłowy:
  — To niemożliwe — szepnęła Anna.
  — Wszystko jest możliwe — odpowiedział, nie odrywając wzroku od okna.

🎯 Your Mastery:

**Craft Fundamentals**:
- Show don't tell (body language over emotion labels)
- Deep POV (no filter words, character's voice throughout)
- MRU sequences (Motivation → Reaction → Action)
- Scene structure (Goal → Conflict → Disaster → Sequel)
- Five senses immersion (sight, sound, touch, smell, taste)
- Subtext (what's NOT said matters more)

**Dialogue Excellence**:
- Polish format: EM DASH (—) always, never quotation marks
- Each character has unique voice (education, mood, background)
- Subtext layered beneath words
- Action beats integrated (no talking heads)
- Conflict and tension in every exchange
- Speech patterns reflect psychology

**Prose Artistry**:
- Sentence rhythm varies (short for tension, flowing for emotion)
- Paragraph length controls pacing
- Metaphors fresh and purposeful (no clichés)
- Sound and cadence considered
- Opening hooks grab immediately
- Every word earns its place

**Emotional Mastery**:
- Feelings grounded in body sensations
- Emotional truth over sentimentality
- Gradual building to peaks
- Reader empathy through vulnerability
- Visceral, not abstract

**Genre Expertise** ({genre}):
- Conventions: {GENRE_PROSE_STYLES.get(genre, {}).get('style', 'Engaging and immersive')}
- Pacing matches reader expectations
- Tropes used fresh, not tired
- Writing style: {GENRE_PROSE_STYLES.get(genre, {}).get('examples', 'Masters of the craft')}

**What Makes Your Prose Bestselling**:
✅ Unputdownable from first sentence
✅ Readers FEEL characters' emotions viscerally
✅ Every scene has purpose and propulsion
✅ Dialogue crackles with life and subtext
✅ Prose has rhythm and musicality
✅ No filter words (saw/heard/felt) - pure Deep POV
✅ Show through action and body language
✅ Specific details over generic descriptions
✅ Paragraph variety controls pacing perfectly
✅ Themes woven subtly through imagery
✅ Endings make readers crave next chapter
✅ Polish formatting with EM DASHES (—) for dialogue

**What You NEVER Do**:
❌ Quotation marks for dialogue (against Polish standards!)
❌ Telling emotions ("she felt sad")
❌ Filter words (saw, heard, felt, knew, realized)
❌ Info dumps (lecturing reader)
❌ Adverb abuse (show, don't label with "angrily")
❌ Purple prose (overwrought flowery language)
❌ Passive voice (unless strategic)
❌ Clichéd metaphors ("black as night")
❌ Generic descriptions ("nice house")
❌ Talking heads (dialogue without action)
❌ Inconsistent character voice
❌ Head-hopping POV
❌ Deus ex machina solutions

**Your Standard**: Publication-ready prose that would make editors weep with joy.
**Your Goal**: Make readers miss sleep because they can't stop reading.
**Your Method**: Craft every sentence with purpose, rhythm, and emotional truth.

You are not just writing a chapter. You are creating an EXPERIENCE that readers will remember for years.

Write at the level of the masters. Write prose that SELLS. Write words that SING.

Output: Pure Polish prose (narrator + dialogue). No JSON. No meta-commentary. No English.
Start with "Rozdział [number]" and immediately deliver compelling, bestseller-quality storytelling."""

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

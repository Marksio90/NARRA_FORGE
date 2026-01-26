"""
Character Creator Agent - Creates psychologically deep, memorable characters

Uses advanced character development techniques:
- Ghost/Wound/Want/Need framework (K.M. Weiland)
- Myers-Briggs and Enneagram psychology
- Character arc construction
- Voice differentiation
- Relationship dynamics
"""

import json
import logging
from typing import Dict, Any, List

from app.services.ai_service import get_ai_service, ModelTier
from app.config import genre_config

logger = logging.getLogger(__name__)


PROTAGONIST_ARCHETYPES = {
    "sci-fi": ["The Explorer", "The Scientist", "The Rebel", "The Survivor"],
    "fantasy": ["The Chosen One", "The Reluctant Hero", "The Warrior", "The Mage"],
    "thriller": ["The Detective", "The Wrongly Accused", "The Hunter", "The Protector"],
    "horror": ["The Survivor", "The Skeptic", "The Investigator", "The Cursed"],
    "romance": ["The Cynic", "The Optimist", "The Wounded", "The Dreamer"],
    "drama": ["The Struggling Artist", "The Parent", "The Outsider", "The Seeker"],
    "comedy": ["The Lovable Loser", "The Fish Out of Water", "The Schemer", "The Innocent"],
    "mystery": ["The Detective", "The Amateur Sleuth", "The Witness", "The Victim"]
}


class CharacterCreatorAgent:
    """
    Expert agent for creating deep, memorable characters

    Capabilities:
    - Psychological depth (MBTI, Enneagram, motivations)
    - Character arcs (transformation over story)
    - Distinct voices and speech patterns
    - Relationship dynamics
    - Ghost/Wound/Want/Need framework
    - Genre-appropriate characterization
    """

    def __init__(self):
        """Initialize Character Creator Agent"""
        self.ai_service = get_ai_service()
        self.name = "Character Creator Agent"

    async def create_characters(
        self,
        genre: str,
        project_name: str,
        world_bible: Dict[str, Any],
        title_analysis: Dict[str, Any],
        character_count: Dict[str, int],
        themes: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Create full cast of characters

        Args:
            genre: Literary genre
            project_name: Book title
            world_bible: World bible created by World Builder
            title_analysis: Insights from title
            character_count: Dict with main/supporting/minor counts
            themes: Story themes to reflect in characters

        Returns:
            List of complete character dictionaries
        """
        logger.info(
            f"👥 {self.name}: Creating {character_count['main']} main + "
            f"{character_count.get('supporting', 0)} supporting characters"
        )

        characters = []

        # Create protagonist first
        protagonist = await self._create_protagonist(
            genre, project_name, world_bible, title_analysis, themes
        )
        characters.append(protagonist)

        # Create antagonist
        antagonist = await self._create_antagonist(
            genre, project_name, world_bible, protagonist, themes, title_analysis
        )
        characters.append(antagonist)

        # Create supporting characters
        for i in range(character_count['main'] - 2):  # -2 for protag + antag
            supporting = await self._create_supporting_character(
                genre, project_name, world_bible, characters, i, themes
            )
            characters.append(supporting)

        logger.info(f"✅ {self.name}: Created {len(characters)} characters")
        return characters

    async def _create_protagonist(
        self,
        genre: str,
        project_name: str,
        world_bible: Dict[str, Any],
        title_analysis: Dict[str, Any],
        themes: List[str]
    ) -> Dict[str, Any]:
        """Create the protagonist"""

        # Extract semantic analysis
        semantic_analysis = title_analysis.get("semantic_title_analysis", {})
        char_implications = semantic_analysis.get("character_implications", {})
        protagonist_archetype = char_implications.get("protagonist_archetype", "")
        protagonist_journey = char_implications.get("protagonist_journey", "")
        suggested_names_semantic = char_implications.get("suggested_names", [])
        core_meaning = semantic_analysis.get("core_meaning", project_name)
        reader_promise = semantic_analysis.get("reader_promise", "")

        # Extract ADVANCED fields
        character_arc = semantic_analysis.get("character_arc", {})
        magic_system = semantic_analysis.get("magic_system", {})
        tone_and_maturity = semantic_analysis.get("tone_and_maturity", {})

        # Check if title suggests a name (basic analysis)
        suggested_name = None
        char_names = title_analysis.get("character_names", [])
        if char_names:
            suggested_name = char_names[0]["name"]

        archetypes = PROTAGONIST_ARCHETYPES.get(genre, ["The Hero"])

        prompt = f"""Create a COMPELLING PROTAGONIST for "{project_name}" ({genre}).

## 🎯 TITLE AS CHARACTER DNA (CRITICAL!)

The title "{project_name}" is not just the book's name - it is THIS CHARACTER'S DESTINY.

**Title's Core Meaning**: {core_meaning}
**Protagonist Archetype from Title**: {protagonist_archetype}
**Protagonist Journey Implied**: {protagonist_journey}
**Reader's Promise**: {reader_promise}

🔥 **MANDATORY REQUIREMENT**: This protagonist must EMBODY the title "{project_name}".
- Their name should resonate with the title (use: {suggested_names_semantic if suggested_names_semantic else suggested_name or 'create fitting name'})
- Their arc must RESOLVE what the title promises
- Their ghost/wound must relate to the title's themes
- Their transformation must ANSWER the title's question
- They ARE the personification of "{project_name}"

If the title asks a question, the protagonist's journey answers it.
If the title is a metaphor, the protagonist embodies it.
If the title is a promise, the protagonist fulfills it.

## 📈 CHARACTER ARC GUIDANCE (From Title Analysis)
"""

        if character_arc:
            prompt += f"- **Starting Point**: {character_arc.get('starting_point', 'Unknown')}\n"
            prompt += f"- **Midpoint Shift**: {character_arc.get('midpoint_shift', 'Unknown')}\n"
            prompt += f"- **Climax Challenge**: {character_arc.get('climax_challenge', 'Unknown')}\n"
            prompt += f"- **Transformation**: {character_arc.get('transformation', 'Unknown')}\n"
            prompt += f"- **Arc Type**: {character_arc.get('arc_type', 'positive')}\n"

        if magic_system and magic_system.get('present'):
            prompt += "\n## 🔥 MAGIC/POWER CONTEXT\n"
            prompt += f"- **Type**: {magic_system.get('type', 'unknown')}\n"
            prompt += f"- **Power Dynamics**: {magic_system.get('power_dynamics', 'unknown')}\n"
            if magic_system.get('elements'):
                prompt += f"- **Elements**: {', '.join(magic_system['elements'])}\n"

        if tone_and_maturity:
            prompt += "\n## 🎭 TONE GUIDANCE\n"
            prompt += f"- **Maturity Level**: {tone_and_maturity.get('maturity_level', 'Adult')}\n"
            prompt += f"- **Moral Complexity**: {tone_and_maturity.get('moral_complexity', 'balanced')}\n"

        prompt += f"""
## WORLD CONTEXT
{self._summarize_world(world_bible)}

## TITLE ANALYSIS (Basic)
- Suggested name: {suggested_name or "Choose an evocative name"}
- Themes: {', '.join(themes)}
- Character hints: {char_names}

## PROTAGONIST REQUIREMENTS

You are creating the MAIN CHARACTER - the heart of the story.

### 1. BASIC PROFILE
- Name: {f"Use or adapt: {suggested_name}" if suggested_name else "Create genre-appropriate name"}
- Age: Consider story needs
- Background: Specific, vivid, shapes who they are
- Occupation: Relevant to plot
- Current situation: Where they start

### 2. PSYCHOLOGY (Deep characterization)
- **MBTI Type**: Choose and explain
- **Enneagram**: Type and wing
- **Core Traits**: 5-7 specific personality traits
- **Fatal Flaw**: Their main weakness
- **Greatest Strength**: What they excel at
- **Fears**: 3-4 deep fears (not surface level)
- **Desires**: What they think they want
- **Secrets**: 2-3 things they hide

### 3. GHOST, WOUND, WANT, NEED
- **Ghost**: Past trauma/event that haunts them
- **Wound**: How the ghost damaged them psychologically
- **Want**: External goal (what they think will fix them)
- **Need**: Internal truth (what will actually heal them)
- **Lie They Believe**: False belief driving their choices

This is K.M. Weiland's framework - the foundation of character arc!

### 4. PHYSICAL APPEARANCE
- Description: Specific, not generic
- Distinctive features: 2-3 memorable traits
- How they carry themselves: Body language
- Style: How they dress and why

### 5. CHARACTER ARC
- **Starting State**: Who they are at the beginning (flawed, wounded)
- **Transformation Moments**: 3-5 key scenes where they grow
- **Ending State**: Who they become (healed, transformed)
- **Arc Type**: Positive change / Tragic fall / Flat (already knows truth)

### 6. VOICE & SPEECH (CRITICAL for Dialogue Authenticity!)

This character's voice must be SO DISTINCTIVE that readers could identify them by dialogue alone.

**Speech Patterns** (How they construct sentences):
- Long, flowing sentences vs. short, clipped phrases?
- Complete grammar vs. fragments and slang?
- Formal vs. casual register?
- Question frequency (insecure? curious? challenging?)
- Interrupting others vs. letting them finish?
- Example patterns:
  * Academic: "I would posit that..." "Arguably..." "One might say..."
  * Street-smart: "Nah, man." "You kidding me?" "Listen up."
  * Noble/Formal: "I should think..." "One must consider..." "Indeed."
  * Young: "Like, seriously?" "Whatever." "OMG."

**Vocabulary Level & Word Choice**:
- Education: University? High school? Self-taught? Street?
- Profession: Technical jargon? Medical terms? Military slang?
- Social class: Polished language? Working-class idioms?
- Reading habits: Literary references? Pop culture? None?
- Specific words they USE: List 5-7 favorite words/phrases
- Specific words they AVOID: List 3-5 words they'd never say

**Verbal Tics & Signature Phrases** (Make them memorable!):
- Repeated phrases: "You know what I mean?" "Honestly..." "Listen..."
- Filler words: "Um..." "Like..." "Well..." "So..."
- Oaths/Curses: Do they swear? Mild? Profane? Religious euphemisms?
- Catchphrases: Unique expressions others don't use
- Example: A detective might say "Facts are facts" when closing arguments
- Example: A nervous character might start every sentence with "Well..."

**Dialect & Regional Speech**:
- Accent indicators (if any): Regional pronunciations
- Local idioms or expressions
- Contractions: Do they use "don't" or "do not"?
- Dropping letters: "goin'" vs "going"

**Sentence Structure Preferences**:
- Declarative (statements): "The sky is blue."
- Interrogative (questions): "Is the sky blue?"
- Exclamatory: "The sky is so blue!"
- Imperative (commands): "Look at the blue sky!"
- Which do they favor?

**Emotional Speech Variations**:
How does their speech CHANGE under stress/emotion?
- Angry: Shorter? Louder? More profanity? Colder?
- Afraid: Stuttering? Faster? Higher pitch? Fragments?
- Happy: More rambling? Laughter mid-sentence? Exclamations?
- Sad: Quieter? Slower? Trailing off? Fewer words?

**Internal Voice** (For POV chapters - VERY DIFFERENT from dialogue!):
- Thinking vocabulary: More complex? More honest? More profane?
- Stream of consciousness: Organized? Chaotic? Poetic?
- Self-talk: Critical? Encouraging? Sarcastic?
- Metaphors in thought: What do they compare things to?
- Example: A soldier thinks in tactical terms; a poet thinks in metaphors

**Dialogue Examples** (MANDATORY - Write 5-7 lines showing DISTINCT voice):

Provide actual dialogue that shows:
1. Their typical speech pattern
2. How they respond to stress
3. How they express emotion
4. Their unique word choices
5. Their personality through words

Example format (Polish, using EM DASHES):
```
Conversation with stranger about danger:
— To niemożliwe — powiedział Jan, krzyżując ramiona. — Sprawdziłem dwukrotnie.
— Niemożliwe? — Kobieta zaśmiała się gorzko. — Panie, wszystko jest możliwe, gdy ktoś chce cię zabić.
— Hipotetycznie rzecz biorąc, gdyby pani twierdzenie było prawdziwe... — zaczął Jan, ale urwał. — Nie, to absurd.

When angry at friend who betrayed him:
— Wiedziałem! — krzyknął, uderzając pięścią w stół. — Kurwa, wiedziałem, że coś jest nie tak!
(Note: He abandons formal speech when emotional)

Internal thought after the conversation:
"Niemożliwe, powiedziałem. Jakbym był idiotą. A może nim jestem? Może wszyscy mieli rację..."
(Note: More self-critical, uses fragmented thoughts)
```

**Voice Consistency Rules for Writer**:
- These patterns should appear in EVERY dialogue scene
- Internal narration reflects thinking style
- Voice shifts appropriately with emotion
- Other characters react to their unique speech style
- Readers should "hear" this character's voice

**What Makes This Voice UNIQUE**:
Write 2-3 sentences explaining what makes this character's voice different from everyone else in the cast. What would a reader recognize even without dialogue tags?

### 7. RELATIONSHIPS
- **Allies**: Who supports them?
- **Rivals**: Who challenges them?
- **Love Interest**: If applicable
- **Mentor**: Who guides them?
- **Family**: Relationships that shaped them

## ARCHETYPE OPTIONS FOR THIS GENRE
{', '.join(archetypes)}

Choose or blend archetypes, but make the character UNIQUE and SPECIFIC.

## CRITICAL GUIDELINES

🎯 **#1 PRIORITY - TITLE EMBODIMENT**:
   This character MUST embody the title "{project_name}".
   Include a "title_connection" field explaining:
   - How their name relates to the title
   - How their arc resolves the title's promise
   - How their journey answers what the title asks
   - Why THEY are the perfect protagonist for THIS title

2. **Depth Over Surface**: Go deep psychologically
3. **Flawed But Likeable**: They must have weaknesses
4. **Agency**: They drive the plot, not reactive
5. **Growth Potential**: Room for transformation
6. **Genre-Authentic**: Fits the {genre} world
7. **Memorable**: Readers should care about them

Output valid JSON with this structure:

{{
  "name": "...",
  "role": "protagonist",
  "title_connection": {{
    "name_resonance": "How the name connects to '{project_name}'...",
    "arc_resolution": "How their arc resolves what the title promises...",
    "thematic_embodiment": "How they personify the title's meaning...",
    "reader_promise_fulfillment": "How they deliver on the title's promise..."
  }},
  "profile": {{
    "biography": {{...}},
    "psychology": {{...}},
    "physical": {{...}},
    "ghost_wound": {{...}}
  }},
  "arc": {{...}},
  "voice_guide": "...",
  "relationships": {{}}
}}

Create a character readers will NEVER FORGET."""

        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self._get_character_system_prompt(),
            tier=ModelTier.TIER_2,
            temperature=0.85,  # More creative for character creation
            max_tokens=5000,
            json_mode=True,
            prefer_anthropic=True,
            metadata={"agent": self.name, "task": "protagonist_creation"}
        )

        try:
            character = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse protagonist JSON: {e}")
            logger.warning(f"Response content: {response.content[:500]}")
            character = self._create_fallback_character("protagonist", "Hero")

        # Validate character has required fields
        if not self._validate_character(character):
            logger.warning(f"⚠️ Character missing required fields, using fallback")
            character = self._create_fallback_character("protagonist", "Hero")

        character['role'] = 'protagonist'
        logger.info(f"✅ Created protagonist: {character.get('name', 'Unknown')}")
        return character

    async def _create_antagonist(
        self,
        genre: str,
        project_name: str,
        world_bible: Dict[str, Any],
        protagonist: Dict[str, Any],
        themes: List[str],
        title_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create the antagonist as a mirror/foil to protagonist"""

        # Extract antagonist predictions from advanced title analysis
        semantic_analysis = title_analysis.get("semantic_title_analysis", {})
        antagonist_predictions = semantic_analysis.get("antagonist_predictions", [])
        conflicts = semantic_analysis.get("conflicts", {})

        prompt = f"""Create a COMPELLING ANTAGONIST for "{project_name}" ({genre}).

## THE PROTAGONIST (Your Opposite)
Name: {protagonist['name']}
Key Traits: {protagonist['profile']['psychology'].get('traits', [])}
Want: {protagonist['arc'].get('want_vs_need', {}).get('want', 'Unknown')}

## 🎯 ANTAGONIST GUIDANCE (From Title Analysis)
"""

        if antagonist_predictions:
            for i, pred in enumerate(antagonist_predictions[:3], 1):  # Top 3 predictions
                prompt += f"\n**Option {i}**: {pred.get('type', 'Unknown')}\n"
                prompt += f"- Motivation: {pred.get('motivation', 'Unknown')}\n"
                prompt += f"- Opposition: {pred.get('opposition_nature', 'Unknown')}\n"

        # Helper to extract conflict description (handles both string and object formats)
        def get_conflict_text(conflict_value):
            if isinstance(conflict_value, str):
                return conflict_value
            elif isinstance(conflict_value, dict):
                desc = conflict_value.get('description', conflict_value.get('question', conflict_value.get('dilemma', '')))
                extra = conflict_value.get('stakes', conflict_value.get('false_belief', conflict_value.get('both_sides', conflict_value.get('cost', ''))))
                return f"{desc} ({extra})" if extra else desc
            return str(conflict_value)

        if conflicts:
            prompt += "\n## ⚔️ CONFLICT DIMENSIONS TO EXPLORE\n"
            if conflicts.get('external'):
                prompt += f"- **External**: {get_conflict_text(conflicts['external'])}\n"
            if conflicts.get('internal'):
                prompt += f"- **Internal**: {get_conflict_text(conflicts['internal'])}\n"
            if conflicts.get('relational'):
                prompt += f"- **Relational**: {get_conflict_text(conflicts['relational'])}\n"
            if conflicts.get('philosophical'):
                prompt += f"- **Philosophical**: {get_conflict_text(conflicts['philosophical'])}\n"
            if conflicts.get('moral'):
                prompt += f"- **Moral**: {get_conflict_text(conflicts['moral'])}\n"

        prompt += """
## YOUR TASK

Create an antagonist who is a WORTHY OPPONENT.

Great antagonists:
- Believe they're the hero of their own story
- Have understandable (even sympathetic) motivations
- Challenge the protagonist's beliefs
- Are intelligent, not just evil
- Have their own arc and depth

### REQUIREMENTS

1. **Motivation**: Why do they oppose the protagonist? (Must be believable)
2. **Backstory**: What made them this way?
3. **Methodology**: How do they operate?
4. **Strengths**: What makes them dangerous?
5. **Weaknesses**: How can they be defeated?
6. **Relationship to Protagonist**: Are they similar? Opposites? Why the conflict?
7. **Redemption Potential**: Can they be saved, or are they beyond redemption?

Make them COMPLEX, not a cartoon villain.

Output JSON with same structure as protagonist.
"""

        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self._get_character_system_prompt(),
            tier=ModelTier.TIER_2,
            temperature=0.85,
            max_tokens=4000,
            json_mode=True,
            prefer_anthropic=True,
            metadata={"agent": self.name, "task": "antagonist_creation"}
        )

        try:
            character = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse antagonist JSON: {e}")
            logger.warning(f"Response content: {response.content[:500]}")
            character = self._create_fallback_character("antagonist", "Adversary")

        # Validate character has required fields
        if not self._validate_character(character):
            logger.warning(f"⚠️ Antagonist missing required fields, using fallback")
            character = self._create_fallback_character("antagonist", "Adversary")

        character['role'] = 'antagonist'
        logger.info(f"✅ Created antagonist: {character.get('name', 'Unknown')}")
        return character

    async def _create_supporting_character(
        self,
        genre: str,
        project_name: str,
        world_bible: Dict[str, Any],
        existing_characters: List[Dict],
        index: int,
        themes: List[str]
    ) -> Dict[str, Any]:
        """Create a supporting character"""

        roles = ["mentor", "ally", "love_interest", "comic_relief", "wildcard"]
        role = roles[index % len(roles)]

        existing_names = [c['name'] for c in existing_characters]

        prompt = f"""Create a SUPPORTING CHARACTER ({role}) for "{project_name}" ({genre}).

## EXISTING CHARACTERS (must be DIFFERENT from these!)
{', '.join(existing_names)}

## ROLE: {role.replace('_', ' ').title()}
{"Mentor: Wiser, experienced, guides protagonist but has own flaws/agenda" if role == "mentor" else ""}
{"Ally: Loyal friend, complements protagonist's weaknesses, own goals" if role == "ally" else ""}
{"Love Interest: Chemistry with protagonist, own arc, not just romantic prop" if role == "love_interest" else ""}
{"Comic Relief: Lightens tension, but has depth and moments of seriousness" if role == "comic_relief" else ""}
{"Wildcard: Unpredictable, own agenda, can help or hinder" if role == "wildcard" else ""}

## THEMES TO REFLECT
{', '.join(themes[:3]) if themes else 'Universal human themes'}

## REQUIRED JSON STRUCTURE (fill ALL fields!):
{{
  "name": "Unique Polish name fitting the world",
  "profile": {{
    "appearance": {{
      "age": "specific age or range",
      "physical": "distinctive physical traits",
      "style": "clothing, presentation"
    }},
    "psychology": {{
      "traits": ["3-5 key personality traits"],
      "fears": ["1-2 core fears"],
      "desires": ["1-2 core desires"],
      "wound": "formative trauma or ghost",
      "lie_believed": "false belief driving behavior"
    }},
    "background": "2-3 sentences on history"
  }},
  "arc": {{
    "starting_state": "who they are at start",
    "transformation": "how they change",
    "ending_state": "who they become"
  }},
  "voice_guide": {{
    "speechPatterns": "how they talk (formal/casual, long/short sentences)",
    "vocabularyLevel": "education level reflected in word choice",
    "verbalTics": "signature phrases or speech habits",
    "signaturePhrases": ["2-3 phrases they often say"]
  }},
  "relationship_to_protagonist": "how they connect to main character"
}}

Create a MEMORABLE character - not a cardboard cutout!"""

        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=self._get_character_system_prompt(),
            tier=ModelTier.TIER_1,  # Tier 1 for supporting chars (cheaper)
            temperature=0.8,
            max_tokens=3000,
            json_mode=True,
            metadata={"agent": self.name, "task": f"supporting_{role}_creation"}
        )

        try:
            character = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse supporting character JSON: {e}")
            logger.warning(f"Response content: {response.content[:500]}")
            character = self._create_fallback_character("supporting", f"Companion_{index}")

        # Validate character has required fields
        if not self._validate_character(character):
            logger.warning(f"⚠️ Supporting character missing required fields, using fallback")
            character = self._create_fallback_character("supporting", f"Companion_{index}")

        character['role'] = 'supporting'
        logger.info(f"✅ Created supporting character: {character.get('name', 'Unknown')} ({role})")
        return character

    def _get_character_system_prompt(self) -> str:
        """System prompt for character creation"""
        return """You are a MASTER CHARACTER ARCHITECT - the creator behind bestselling fiction's most memorable characters.

Your characters live in readers' minds long after they close the book. They feel like real people with depth, contradictions, and authentic voices.

🎯 Your Expertise:

**Psychological Mastery**:
- MBTI and Enneagram with deep understanding (not surface labels)
- Trauma psychology (Ghost/Wound theory by K.M. Weiland)
- Motivation layers (Want vs. Need - external vs. internal)
- Flaws that drive conflict (fatal flaws, blind spots, lies believed)
- Cognitive biases that shape perception
- Attachment styles affecting relationships
- Defense mechanisms and coping strategies

**Character Arc Theory**:
- K.M. Weiland's Ghost/Wound/Want/Need/Lie framework
- Positive change arcs (character grows, learns truth)
- Negative/tragic arcs (character succumbs to lie)
- Flat arcs (character already knows truth, changes world)
- Transformation moments and turning points
- Character arc integration with plot structure

**Voice Differentiation** (CRITICAL):
- Every character speaks DISTINCTLY
- Speech patterns reflect psychology, education, background
- Vocabulary choices reveal character depth
- Verbal tics and signature phrases for memorability
- Emotional speech variations (how voice changes under stress)
- Internal voice vs. external dialogue differences
- Regional/social dialects where appropriate
- Age-appropriate speech patterns

**Relationship Dynamics**:
- Character chemistry (allies, rivals, romance)
- Power dynamics (mentor/student, boss/employee)
- Family systems and formative relationships
- Conflict sources in every relationship
- How characters bring out different sides of each other

**Archetype Transcendence**:
- Start with archetype, make it SPECIFIC
- Add contradictions and surprises
- Ground in unique psychology and background
- Universal recognition + specific individuality

**What Makes Your Characters BESTSELLING**:
✅ Psychological depth readers recognize as TRUE
✅ Flaws that make them human and relatable
✅ Distinct voices - reader knows who's talking without tags
✅ Transformative arcs with earned emotional payoffs
✅ Contradictions that make them complex (kind but vengeful, brave but afraid)
✅ Secrets and wounds that drive behavior
✅ Relationships that feel authentic and dynamic
✅ Agency - they DRIVE the plot, not passive victims
✅ Specific sensory details (how they move, smell, sound)
✅ Unique perspective that colors their world view

**What You NEVER Create**:
❌ Mary Sues / Gary Stus (perfect, flawless characters)
❌ Generic "chosen one" without depth or cost
❌ Characters who all sound the same
❌ Inconsistent behavior (without psychological reason)
❌ Stereotypes (ethnic, gender, professional clichés)
❌ Flat personalities (all angry, all nice, one-note)
❌ Characters who exist only to serve plot (they must live!)
❌ Motivations that don't make psychological sense
❌ Trauma without lasting psychological impact
❌ Relationships without complexity or conflict

**Voice Guide Creation** (Your Secret Weapon):

For EVERY character, you create a comprehensive VOICE GUIDE including:
- Speech patterns (sentence structure, length, complexity)
- Vocabulary level and favorite words
- Verbal tics and signature phrases
- How speech changes under emotion (anger, fear, joy, sadness)
- Specific dialogue examples (5-7 lines in Polish with EM DASHES)
- Internal voice style (for POV chapters)
- What makes this voice UNIQUE from all other characters

This ensures the prose writer can write authentic, differentiated dialogue.

**Your Standard**: Characters worthy of fan fiction, cosplay, and lifelong reader devotion.

**Your Method**:
1. Start with psychology (trauma, fears, desires, lies)
2. Build appearance and voice from psychology
3. Create arc that challenges their lie and forces growth
4. Ensure they're flawed, specific, and ALIVE
5. Make their voice so distinct it's unmistakable

You are creating PEOPLE, not chess pieces. Every detail has psychological truth.

**Output Format**:
- Valid JSON with ALL fields filled richly
- Specific details, never generic
- Voice guide with actual dialogue examples in POLISH using EM DASHES (—)
- Psychological depth in every section
- No placeholder text or "TBD" - complete every field thoughtfully"""

    def _summarize_world(self, world_bible: Dict[str, Any]) -> str:
        """Create brief world summary for context"""
        geography = world_bible.get('geography', {})
        systems = world_bible.get('systems', {})

        summary = f"""World Type: {geography.get('world_type', 'Unknown')}
Technology/Magic: {systems.get('technology_level', 'Unknown')}
Key Locations: {', '.join([loc.get('name', '') for loc in geography.get('locations', [])][:3])}
"""
        return summary

    def _validate_character(self, character: Dict[str, Any]) -> bool:
        """
        Validate that character has all required fields

        Args:
            character: Character dictionary from AI

        Returns:
            True if valid, False if missing required fields
        """
        required_fields = ['name', 'profile', 'arc']

        # Check top-level required fields
        for field in required_fields:
            if field not in character or not character[field]:
                logger.warning(f"⚠️ Character missing required field: {field}")
                return False

        # Check profile has required nested fields
        if not isinstance(character['profile'], dict):
            logger.warning(f"⚠️ Character profile is not a dict")
            return False

        # Check arc has required nested fields
        if not isinstance(character['arc'], dict):
            logger.warning(f"⚠️ Character arc is not a dict")
            return False

        return True

    def _create_fallback_character(self, role: str, name: str) -> Dict[str, Any]:
        """Create a basic fallback character when JSON parsing fails"""
        logger.warning(f"⚠️ Creating fallback character for role: {role}")
        return {
            "name": name,
            "role": role,
            "profile": {
                "biography": {
                    "age": 30,
                    "background": "A mysterious character with an unknown past.",
                    "occupation": "Unknown",
                    "current_situation": "Appears at a critical moment in the story."
                },
                "psychology": {
                    "traits": ["Mysterious", "Determined", "Complex"],
                    "mbti": "INTJ",
                    "enneagram": "5w4",
                    "fatal_flaw": "Trust issues",
                    "greatest_strength": "Adaptability",
                    "fears": ["Betrayal", "Failure", "Loss of control"],
                    "desires": ["Truth", "Justice", "Purpose"],
                    "secrets": ["Hidden past", "Secret abilities"]
                },
                "physical": {
                    "description": "Average height and build with distinctive features",
                    "distinctive_features": ["Intense gaze", "Unique mannerisms"],
                    "body_language": "Confident yet cautious",
                    "style": "Practical and functional"
                },
                "ghost_wound": {
                    "ghost": "A traumatic event from their past",
                    "wound": "Deep psychological scars",
                    "want": "External validation",
                    "need": "Inner peace",
                    "lie_believed": "Control equals safety"
                }
            },
            "arc": {
                "starting_state": "Guarded and isolated",
                "transformation_moments": [
                    "First moment of vulnerability",
                    "Facing their greatest fear",
                    "Ultimate choice"
                ],
                "ending_state": "Transformed and whole",
                "arc_type": "Positive change"
            },
            "voice_guide": {
                "speechPatterns": "Speaks with measured words and hidden depths",
                "vocabularyLevel": "Standard",
                "signature_phrases": []
            },
            "relationships": {
                "allies": [],
                "rivals": [],
                "mentor": None,
                "family": "Unknown"
            }
        }

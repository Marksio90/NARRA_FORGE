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
            genre, project_name, world_bible, protagonist, themes
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

        # Check if title suggests a name
        suggested_name = None
        char_names = title_analysis.get("character_names", [])
        if char_names:
            suggested_name = char_names[0]["name"]

        archetypes = PROTAGONIST_ARCHETYPES.get(genre, ["The Hero"])

        prompt = f"""Create a COMPELLING PROTAGONIST for "{project_name}" ({genre}).

## WORLD CONTEXT
{self._summarize_world(world_bible)}

## TITLE ANALYSIS
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

### 6. VOICE & SPEECH
- **Speech Patterns**: How do they talk?
- **Vocabulary Level**: Educated? Street-smart? Technical?
- **Verbal Tics**: Repeated phrases or habits
- **Internal Voice**: How do they think? (For POV narration)
- **Example Dialogue**: 2-3 lines showing their voice

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

1. **Depth Over Surface**: Go deep psychologically
2. **Flawed But Likeable**: They must have weaknesses
3. **Agency**: They drive the plot, not reactive
4. **Growth Potential**: Room for transformation
5. **Genre-Authentic**: Fits the {genre} world
6. **Memorable**: Readers should care about them

Output valid JSON with this structure:

{{
  "name": "...",
  "role": "protagonist",
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
        themes: List[str]
    ) -> Dict[str, Any]:
        """Create the antagonist as a mirror/foil to protagonist"""

        prompt = f"""Create a COMPELLING ANTAGONIST for "{project_name}" ({genre}).

## THE PROTAGONIST (Your Opposite)
Name: {protagonist['name']}
Key Traits: {protagonist['profile']['psychology'].get('traits', [])}
Want: {protagonist['arc'].get('want_vs_need', {}).get('want', 'Unknown')}

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

Output JSON with same structure as protagonist."""

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

        prompt = f"""Create a SUPPORTING CHARACTER ({role}) for "{project_name}".

## EXISTING CHARACTERS
{', '.join(existing_names)}

## ROLE: {role.replace('_', ' ').title()}

Create a character who:
1. Complements the existing cast
2. Serves a clear narrative function
3. Has their own personality and goals
4. Is distinct from other characters
5. Adds depth to the story

Keep it focused - this is NOT the protagonist. But make them memorable!

Output JSON matching character structure."""

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
        return """You are an EXPERT CHARACTER CREATOR for fiction.

Your expertise:
- Psychology (MBTI, Enneagram, trauma, motivation)
- Character arc theory (K.M. Weiland, John Truby, Save the Cat)
- Voice differentiation and dialogue
- Character relationships and dynamics
- Archetypes and how to transcend them

You create characters that:
- Feel REAL and three-dimensional
- Have psychological depth and complexity
- Undergo meaningful transformation
- Have distinct, memorable voices
- Serve the story while feeling authentic

You avoid:
- Generic "chosen one" tropes without depth
- Mary Sues / Gary Stus (characters without flaws)
- Flat, one-dimensional personalities
- Inconsistent character behavior
- Stereotypes and clichés

Output Format: Valid JSON only, rich with specific details."""

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

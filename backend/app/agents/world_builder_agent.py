"""
World Builder Agent - Creates rich, consistent fictional worlds

Uses advanced techniques:
- Chain-of-thought reasoning
- Genre-specific world building patterns
- Consistency checking
- Multi-layered world construction (geography -> history -> culture -> systems)
"""

import json
import logging
from typing import Dict, Any

from app.services.ai_service import get_ai_service, ModelTier
from app.config import genre_config

logger = logging.getLogger(__name__)


class WorldBuilderAgent:
    """
    Expert agent for creating detailed fictional worlds

    Capabilities:
    - Genre-appropriate world building (sci-fi, fantasy, etc.)
    - Layered construction: geography, history, cultures, systems
    - Internal consistency validation
    - Rich, immersive details
    - Integration with title/theme analysis
    """

    def __init__(self):
        """Initialize World Builder Agent"""
        self.ai_service = get_ai_service()
        self.name = "World Builder Agent"

    async def create_world_bible(
        self,
        genre: str,
        project_name: str,
        title_analysis: Dict[str, Any],
        target_word_count: int,
        style_complexity: str
    ) -> Dict[str, Any]:
        """
        Create comprehensive World Bible

        Args:
            genre: Literary genre (sci-fi, fantasy, etc.)
            project_name: Title of the book
            title_analysis: Insights from title analysis
            target_word_count: Target length of the book
            style_complexity: high/medium/low

        Returns:
            Complete world bible dictionary
        """
        logger.info(f"🌍 {self.name}: Creating world for '{project_name}' ({genre})")

        # Get genre-specific configuration
        genre_cfg = genre_config.get_genre_config(genre)

        # Build comprehensive prompt
        prompt = self._build_world_prompt(
            genre=genre,
            project_name=project_name,
            title_analysis=title_analysis,
            genre_config=genre_cfg,
            target_word_count=target_word_count,
            style_complexity=style_complexity
        )

        system_prompt = self._get_system_prompt()

        # Generate world bible using Tier 2 (balanced quality)
        response = await self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            tier=ModelTier.TIER_2,
            temperature=0.8,  # Creative but not random
            max_tokens=6000,
            json_mode=True,
            prefer_anthropic=True,  # Claude excels at world building
            metadata={
                "agent": self.name,
                "task": "world_building",
                "genre": genre
            }
        )

        # Parse and validate response
        try:
            world_bible = json.loads(response.content)
            logger.info(
                f"✅ {self.name}: World created successfully "
                f"(cost: ${response.cost:.4f}, tokens: {response.tokens_used['total']})"
            )
            return world_bible

        except json.JSONDecodeError as e:
            logger.error(f"❌ {self.name}: Failed to parse world bible JSON: {e}")
            # Fallback to structured but empty world
            return self._create_fallback_world(genre)

    def _get_system_prompt(self) -> str:
        """Get system prompt for world builder"""
        return """You are an EXPERT WORLD BUILDER for literary fiction.

Your expertise:
- Deep knowledge of world-building principles (Tolkien, Sanderson, Le Guin)
- Genre-specific conventions and expectations
- Internal consistency and logic
- Cultural anthropology and sociology
- Geography, history, and systems thinking

Your approach:
1. THINK DEEPLY about the genre requirements
2. CREATE layered, interconnected world elements
3. ENSURE internal consistency
4. PROVIDE rich, specific details (not generic)
5. GROUND everything in believable logic

You generate worlds that feel REAL, LIVED-IN, and PURPOSEFUL.
Every detail serves the story and enhances immersion.

Output Format: Valid JSON only, following the exact schema provided."""

    def _build_world_prompt(
        self,
        genre: str,
        project_name: str,
        title_analysis: Dict[str, Any],
        genre_config: Dict[str, Any],
        target_word_count: int,
        style_complexity: str
    ) -> str:
        """Build comprehensive world building prompt"""

        # Extract title insights
        setting_hints = title_analysis.get("setting_hints", [])
        themes = title_analysis.get("themes", [])
        character_names = title_analysis.get("character_names", [])

        scope = "epic" if target_word_count > 100000 else "focused"

        prompt = f"""Create a COMPLETE WORLD BIBLE for a {genre} novel titled "{project_name}".

## BOOK DETAILS
- Genre: {genre} ({genre_config['name']})
- Style: {genre_config['style']}
- Scope: {scope} ({target_word_count:,} words)
- Complexity: {style_complexity}

## TITLE ANALYSIS INSIGHTS
"""

        if setting_hints:
            prompt += f"- Setting hints from title: {', '.join(setting_hints)}\n"
        if themes:
            prompt += f"- Themes suggested: {', '.join(themes)}\n"
        if character_names:
            names = [c['name'] for c in character_names]
            prompt += f"- Character names to consider: {', '.join(names)}\n"

        prompt += f"""
## GENRE REQUIREMENTS
{genre_config['description']}

Key elements to include:
{', '.join(genre_config['key_elements'])}

## YOUR TASK

Create a world bible with these sections. Think step-by-step:

### 1. GEOGRAPHY & LOCATIONS
- World type (planet/galaxy/realm/etc.)
- 3-5 key locations with:
  * Name (evocative, genre-appropriate)
  * Type (city/space station/forest/etc.)
  * Description (vivid, specific details)
  * Population/size
  * Strategic importance to story
  * Unique features

### 2. HISTORY & TIMELINE
- Current year/date system
- 2-3 historical eras with:
  * Name and time period
  * Key events that shaped the world
  * How it affects the present
- Major turning points in history

### 3. SYSTEMS
- Technology level (or magic system for fantasy)
- Economic system (how trade/currency works)
- Political system (governance, power structures)
- Social structure (classes, hierarchies)
- Each system should have RULES and LOGIC

### 4. CULTURES & SOCIETIES
- 2-3 distinct cultures with:
  * Name and population
  * Core values and beliefs
  * Customs and traditions
  * Language/dialect notes
  * Relationship with other cultures
- Make cultures DIFFERENT and BELIEVABLE

### 5. RULES & PHYSICS
- Physical laws (standard/modified/magic-enhanced)
- Magic rules (if fantasy) with limitations
- Technology limitations (if sci-fi)
- What is possible vs impossible
- INTERNAL CONSISTENCY is crucial

### 6. GLOSSARY
- 5-10 unique terms/concepts specific to this world
- Each with:
  * Term name
  * Clear definition
  * Usage in context
  * Cultural significance

### 7. NOTES
- Additional world-building notes
- Secrets/mysteries to be revealed
- Potential for sequels
- Cultural touchstones or inspirations

## CRITICAL GUIDELINES

1. **Genre Authenticity**: This MUST feel like an authentic {genre} world
2. **Internal Logic**: Everything connects and makes sense
3. **Specificity**: Avoid generic names/concepts - be creative and specific
4. **Story Service**: Every element should serve potential story needs
5. **Depth**: Rich enough to feel real, not just surface details
6. **Consistency**: All elements harmonize with each other

## OUTPUT FORMAT

Return a valid JSON object with this exact structure:

{{
  "geography": {{
    "world_type": "...",
    "locations": [
      {{
        "name": "...",
        "type": "...",
        "description": "...",
        "population": 0,
        "strategic_importance": "...",
        "unique_features": ["...", "..."]
      }}
    ]
  }},
  "history": {{
    "eras": [
      {{
        "name": "...",
        "start_year": 0,
        "end_year": 0,
        "key_events": ["...", "...", "..."],
        "impact_on_present": "..."
      }}
    ],
    "current_year": 0
  }},
  "systems": {{
    "technology_level": "...",
    "magic_system": {{...}},
    "economic_system": {{...}},
    "political_system": {{...}},
    "social_structure": {{...}}
  }},
  "cultures": {{
    "cultures": [
      {{
        "name": "...",
        "population": 0,
        "values": ["...", "...", "..."],
        "customs": ["...", "...", "..."],
        "language": "...",
        "relationships": {{...}}
      }}
    ]
  }},
  "rules": {{
    "physics": "...",
    "magic_rules": ["...", "..."],
    "technology_limitations": ["...", "..."],
    "impossibilities": ["...", "..."]
  }},
  "glossary": {{
    "terms": [
      {{
        "term": "...",
        "definition": "...",
        "usage": "...",
        "significance": "..."
      }}
    ]
  }},
  "notes": "..."
}}

Think deeply. Create a world readers will want to live in. Make it UNFORGETTABLE.
"""

        return prompt

    def _create_fallback_world(self, genre: str) -> Dict[str, Any]:
        """Create basic fallback world if AI generation fails"""
        logger.warning(f"{self.name}: Using fallback world structure")

        return {
            "geography": {
                "world_type": "standard for genre",
                "locations": [
                    {
                        "name": "The Capital",
                        "type": "city",
                        "description": "Main setting for the story",
                        "population": 1000000,
                        "strategic_importance": "Central to plot",
                        "unique_features": ["To be developed"]
                    }
                ]
            },
            "history": {
                "eras": [
                    {
                        "name": "The Founding",
                        "start_year": -100,
                        "end_year": 0,
                        "key_events": ["Establishment of civilization"],
                        "impact_on_present": "Foundation of current society"
                    }
                ],
                "current_year": 100
            },
            "systems": {
                "technology_level": "appropriate for " + genre,
                "economic_system": {"type": "market-based"},
                "political_system": {"type": "to be determined"},
                "social_structure": {"type": "layered"}
            },
            "cultures": {
                "cultures": [
                    {
                        "name": "Main Culture",
                        "population": 1000000,
                        "values": ["honor", "duty"],
                        "customs": ["traditional greetings"],
                        "language": "Common",
                        "relationships": {}
                    }
                ]
            },
            "rules": {
                "physics": "standard",
                "magic_rules": [],
                "technology_limitations": [],
                "impossibilities": []
            },
            "glossary": {
                "terms": []
            },
            "notes": "Fallback world - requires AI generation for full detail"
        }

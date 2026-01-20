"""
Character Agent - creates multi-dimensional, evolving characters.
"""
from app.core.openai_client import OpenAIClient
from app.core.cost_optimizer import CostOptimizer
from app.core.cost_tracker import CostTracker
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)


class CharacterAgent:
    """
    Character Agent - Kreator Dusz.
    Tworzy postacie tak prawdziwe, że czytelnik czuje, jakby znał je osobiście.
    """

    def __init__(self):
        self.openai = OpenAIClient()

    async def create_characters(
        self,
        genre: str,
        world: Dict[str, Any],
        cost_optimizer: CostOptimizer,
        cost_tracker: CostTracker,
    ) -> List[Dict[str, Any]]:
        """
        Create characters for the book.

        Args:
            genre: Book genre
            world: World data
            cost_optimizer: Cost optimizer
            cost_tracker: Cost tracker

        Returns:
            List of character data dictionaries
        """
        logger.info(f"Creating characters for genre: {genre}")

        # Determine number of characters based on genre
        character_counts = {
            'scifi': 6, 'fantasy': 8, 'thriller': 5,
            'horror': 4, 'romance': 4, 'mystery': 6,
            'drama': 5, 'comedy': 5, 'dystopia': 6,
            'historical': 7
        }
        num_characters = character_counts.get(genre, 5)

        # Select model
        model = cost_optimizer.select_model_for_task('character_creation', genre=genre)

        # Generate characters
        prompt = self._build_characters_prompt(genre, world, num_characters)

        response = await self.openai.complete(
            model=model.value['model'],
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.85,
        )

        # Log cost
        cost_tracker.log_usage(
            model=model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            phase='character_creation'
        )

        # Parse response
        characters = self._parse_characters_response(response.content)

        logger.info(f"Created {len(characters)} characters")

        return characters

    SYSTEM_PROMPT = """Jesteś KREATOREM DUSZ - każda postać którą tworzysz
ma głębię, historię i własny głos.

ZASADY TWORZENIA POSTACI:
- Wady czynią bohaterów interesującymi
- Każda postać ma własny idiolekt (sposób mówienia)
- Łuki rozwojowe są kluczowe
- Motywacje muszą być jasne i wiarygodne
- Relacje między postaciami tworzą dynamikę

ODPOWIEDZ W FORMACIE JSON:
{
    "characters": [
        {
            "name": "imię",
            "full_name": "pełne imię",
            "role": "protagonist/antagonist/supporting/minor",
            "appearance": {
                "physical": "opis fizyczny",
                "distinctive_features": "charakterystyczne cechy",
                "style": "styl ubierania"
            },
            "personality": {
                "traits": ["cecha1", "cecha2"],
                "strengths": ["siła1", "siła2"],
                "weaknesses": ["słabość1", "słabość2"],
                "secrets": ["sekret1", "sekret2"]
            },
            "backstory": {
                "origin": "pochodzenie",
                "key_events": ["wydarzenie1", "wydarzenie2"],
                "traumas": ["trauma1"],
                "relationships": "relacje rodzinne"
            },
            "motivations": {
                "main_goal": "główny cel",
                "secondary_goals": ["cel1", "cel2"],
                "fears": ["lęk1", "lęk2"]
            },
            "voice": {
                "speech_pattern": "sposób mówienia",
                "favorite_expressions": ["wyrażenie1", "wyrażenie2"],
                "formality_level": "poziom formalności",
                "humor": "poczucie humoru"
            },
            "arc": {
                "starting_point": "kim jest na początku",
                "transformation": "jak się zmienia",
                "end_point": "kim się staje"
            }
        }
    ]
}"""

    def _build_characters_prompt(self, genre: str, world: Dict[str, Any], num: int) -> str:
        """Build character generation prompt."""
        world_summary = f"{world.get('name', 'Unknown')}: {world.get('description', '')}"

        return f"""Stwórz {num} postaci dla książki w gatunku {genre.upper()}.

ŚWIAT: {world_summary}

WYMAGANIA:
- 1-2 protagonistów (główni bohaterowie)
- 1 antagonista (przeciwnik)
- Reszta to postacie wspierające

PAMIĘTAJ:
- Każda postać musi mieć wady
- Imiona muszą pasować do świata
- Głosy muszą być różne
- Łuki rozwojowe muszą być jasne

Stwórz postacie w formacie JSON."""

    def _parse_characters_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse characters response from AI."""
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data.get('characters', [])
            else:
                data = json.loads(response)
                return data.get('characters', [])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse characters response: {e}")
            return []

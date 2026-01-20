"""
World Agent - creates immersive, consistent worlds.
"""
from app.core.openai_client import OpenAIClient
from app.core.cost_optimizer import CostOptimizer
from app.core.cost_tracker import CostTracker
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class WorldAgent:
    """
    World Agent - Architekt Światów.
    Tworzy żywy, oddychający świat z własną historią, kulturą i zasadami.
    """

    def __init__(self):
        self.openai = OpenAIClient()

    async def create_world(
        self,
        genre: str,
        cost_optimizer: CostOptimizer,
        cost_tracker: CostTracker,
    ) -> Dict[str, Any]:
        """
        Create a complete world for the book.

        Args:
            genre: Book genre
            cost_optimizer: Cost optimizer
            cost_tracker: Cost tracker

        Returns:
            World data dictionary
        """
        logger.info(f"Creating world for genre: {genre}")

        # Select model
        model = cost_optimizer.select_model_for_task(
            'world_building',
            genre=genre
        )

        # Generate world
        prompt = self._build_world_prompt(genre)

        response = await self.openai.complete(
            model=model.value['model'],
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.8,
        )

        # Log cost
        cost_tracker.log_usage(
            model=model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            phase='world_building'
        )

        # Parse response
        world_data = self._parse_world_response(response.content)
        world_data['genre'] = genre

        logger.info(f"World created: {world_data.get('name', 'Unknown')}")

        return world_data

    SYSTEM_PROMPT = """Jesteś ARCHITEKTEM ŚWIATÓW - tworzysz uniwersa tak bogate i spójne,
że czytelnicy chcą w nich zamieszkać.

Każdy świat który tworzysz ma:
- Własną historię i mitologię
- Spójne zasady funkcjonowania
- Żywe kultury i społeczeństwa
- Detale które budują immersję

WAŻNE:
- Każdy szczegół musi służyć historii
- Zasady świata muszą być konsekwentne
- Geografia musi wspierać fabułę
- Kultury muszą być wiarygodne

ODPOWIEDZ W FORMACIE JSON:
{
    "name": "nazwa świata",
    "description": "krótki opis (2-3 zdania)",
    "geography": {
        "regions": ["region1", "region2"],
        "key_locations": ["location1", "location2"],
        "climate": "opis klimatu"
    },
    "history": {
        "key_events": ["event1", "event2"],
        "conflicts": ["conflict1", "conflict2"],
        "legends": ["legend1", "legend2"]
    },
    "rules": {
        "physics_magic_tech": "jak działa świat",
        "limitations": "ograniczenia",
        "special_elements": "unikalne elementy"
    },
    "societies": {
        "cultures": ["culture1", "culture2"],
        "power_structures": "struktury władzy",
        "conflicts": "konflikty społeczne"
    },
    "details": {
        "food": ["typical dishes"],
        "traditions": ["customs"],
        "language_elements": ["slang", "expressions"]
    }
}"""

    def _build_world_prompt(self, genre: str) -> str:
        """Build world generation prompt."""
        genre_guidance = {
            'scifi': 'Wizjonerski świat przyszłości z zaawansowaną technologią',
            'fantasy': 'Epickie uniwersum z magią i mitycznymi elementami',
            'thriller': 'Realistyczny współczesny świat z ukrytymi zagrożeniami',
            'horror': 'Mroczny świat gdzie kryje się coś przerażającego',
            'romance': 'Romantyczny świat sprzyjający budowaniu relacji',
            'mystery': 'Świat pełen tajemnic i zagadek',
            'drama': 'Realistyczny świat z głębią społeczną',
            'comedy': 'Absurdalny lub satyryczny świat',
            'dystopia': 'Postnuklearny lub totalitarny świat przyszłości',
            'historical': 'Autentyczna historyczna epoka',
        }

        guidance = genre_guidance.get(genre, 'Fascynujący, immersyjny świat')

        return f"""Stwórz kompletny świat dla książki w gatunku: {genre.upper()}

KIERUNEK: {guidance}

Pamiętaj:
1. Świat musi być spójny i logiczny
2. Geografia wspiera fabułę
3. Historia daje głębię
4. Zasady są konsekwentne
5. Detale budują immersję

Stwórz świat teraz w formacie JSON."""

    def _parse_world_response(self, response: str) -> Dict[str, Any]:
        """Parse world response from AI."""
        try:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                # Fallback to whole response
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse world response: {e}")
            # Return minimal world
            return {
                'name': 'Unknown World',
                'description': 'A mysterious world awaits...',
                'geography': {},
                'history': {},
                'rules': {},
                'societies': {},
                'details': {}
            }

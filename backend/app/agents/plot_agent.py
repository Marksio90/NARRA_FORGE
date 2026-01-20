"""
Plot Agent - creates engaging, multi-threaded plots.
"""
from app.core.openai_client import OpenAIClient
from app.core.cost_optimizer import CostOptimizer
from app.core.cost_tracker import CostTracker
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)


class PlotAgent:
    """
    Plot Agent - Mistrz Fabuły.
    Snuje opowieści, które nie pozwalają odłożyć książki.
    """

    def __init__(self):
        self.openai = OpenAIClient()

    async def create_plot(
        self,
        genre: str,
        world: Dict[str, Any],
        characters: List[Dict[str, Any]],
        cost_optimizer: CostOptimizer,
        cost_tracker: CostTracker,
    ) -> Dict[str, Any]:
        """
        Create plot outline for the book.

        Args:
            genre: Book genre
            world: World data
            characters: Characters data
            cost_optimizer: Cost optimizer
            cost_tracker: Cost tracker

        Returns:
            Plot data dictionary with chapter outlines
        """
        logger.info(f"Creating plot for genre: {genre}")

        # Determine target length based on genre
        chapter_counts = {
            'scifi': 25, 'fantasy': 30, 'thriller': 22,
            'horror': 20, 'romance': 24, 'mystery': 22,
            'drama': 20, 'comedy': 18, 'dystopia': 25,
            'historical': 28
        }
        num_chapters = chapter_counts.get(genre, 22)

        # Select model
        model = cost_optimizer.select_model_for_task('plot_outline', genre=genre)

        # Generate plot
        prompt = self._build_plot_prompt(genre, world, characters, num_chapters)

        response = await self.openai.complete(
            model=model.value['model'],
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.75,
        )

        # Log cost
        cost_tracker.log_usage(
            model=model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            phase='plot_generation'
        )

        # Parse response
        plot_data = self._parse_plot_response(response.content)
        plot_data['num_chapters'] = num_chapters

        logger.info(f"Plot created with {len(plot_data.get('chapters', []))} chapters")

        return plot_data

    SYSTEM_PROMPT = """Jesteś MISTRZEM FABUŁY - tworzysz historie,
które pozostają z czytelnikiem na zawsze.

ZASADY FABUŁY:
- Każda scena ma cel (rozwój postaci LUB posuw fabuły)
- Setup i payoff - każde oczekiwanie musi być zaspokojone
- Napięcie narasta stopniowo
- Twisty są zasłużone, nie nagłe
- Wątki poboczne wzbogacają główną historię

STRUKTURA (3 akty):
- AKT I (25%): Setup, wprowadzenie, inciting incident
- AKT II (50%): Konfrontacja, komplikacje, midpoint twist
- AKT III (25%): Kulminacja, klimaks, rozwiązanie

ODPOWIEDZ W FORMACIE JSON:
{
    "structure_type": "three_act",
    "theme": "główny temat",
    "hook": "intrygujące otwarcie",
    "inciting_incident": "wydarzenie inicjujące",
    "midpoint": "twist w połowie",
    "climax": "kulminacja",
    "resolution": "rozwiązanie",
    "chapters": [
        {
            "number": 1,
            "title": "tytuł rozdziału",
            "act": 1,
            "goal": "cel rozdziału",
            "summary": "streszczenie (3-4 zdania)",
            "characters": ["postać1", "postać2"],
            "location": "lokacja",
            "pov": "punkt widzenia",
            "plot_points": ["punkt1", "punkt2"],
            "cliffhanger": "czy jest cliffhanger"
        }
    ],
    "subplots": [
        {
            "name": "nazwa wątku",
            "description": "opis",
            "resolution": "rozwiązanie"
        }
    ]
}"""

    def _build_plot_prompt(
        self,
        genre: str,
        world: Dict[str, Any],
        characters: List[Dict[str, Any]],
        num_chapters: int
    ) -> str:
        """Build plot generation prompt."""
        world_summary = f"{world.get('name', '')}: {world.get('description', '')}"
        char_summary = ", ".join([c.get('name', 'Unknown') for c in characters[:5]])

        return f"""Stwórz fabułę dla książki w gatunku {genre.upper()}.

ŚWIAT: {world_summary}
POSTACIE: {char_summary}
LICZBA ROZDZIAŁÓW: {num_chapters}

WYMAGANIA:
- Struktura 3-aktowa
- Minimum 2-3 wątki poboczne
- Punkty zwrotne w kluczowych momentach
- Cliffhangery co kilka rozdziałów

PAMIĘTAJ:
- Każdy rozdział to mini-historia
- Napięcie narasta stopniowo
- Twisty są zasłużone
- Wszystkie wątki muszą się połączyć

Stwórz fabułę w formacie JSON."""

    def _parse_plot_response(self, response: str) -> Dict[str, Any]:
        """Parse plot response from AI."""
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plot response: {e}")
            return {
                'structure_type': 'three_act',
                'theme': 'Unknown',
                'chapters': []
            }

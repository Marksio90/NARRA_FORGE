"""
Publisher Agent - prepares book for publication.
"""
from app.core.openai_client import OpenAIClient
from app.core.cost_optimizer import CostOptimizer
from app.core.cost_tracker import CostTracker
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class PublisherAgent:
    """
    Publisher Agent - Agent Wydawniczy.
    Przygotowuje książkę do spotkania z czytelnikiem.
    """

    def __init__(self):
        self.openai = OpenAIClient()

    async def finalize(
        self,
        book: Any,
        cost_optimizer: CostOptimizer,
        cost_tracker: CostTracker,
    ) -> Any:
        """
        Finalize book - generate metadata, title, blurb.

        Args:
            book: Book object with chapters
            cost_optimizer: Cost optimizer
            cost_tracker: Cost tracker

        Returns:
            Finalized book
        """
        logger.info("Finalizing book")

        # Select model
        model = cost_optimizer.select_model_for_task('extract_metadata')

        # Generate metadata
        metadata = await self._generate_metadata(book, model, cost_tracker)

        # Update book
        book.title = metadata.get('title')
        book.subtitle = metadata.get('subtitle')
        book.tagline = metadata.get('tagline')
        book.blurb = metadata.get('blurb')

        # Calculate stats
        total_words = sum(c.get('word_count', 0) for c in book.chapters)
        book.word_count = total_words
        book.chapter_count = len(book.chapters)
        book.estimated_reading_time = total_words // 250  # avg reading speed

        logger.info(
            f"Book finalized: '{book.title}' - "
            f"{book.word_count:,} words, {book.chapter_count} chapters"
        )

        return book

    async def _generate_metadata(
        self,
        book: Any,
        model: Any,
        cost_tracker: CostTracker
    ) -> Dict[str, Any]:
        """Generate book metadata."""

        # Build context
        context = f"""GATUNEK: {book.genre}

ŚWIAT: {book.world.name if book.world else 'Unknown'}
{book.world.description if book.world else ''}

POSTACIE GŁÓWNE:
{chr(10).join([f"- {c.name}" for c in book.characters[:3]])}

FABUŁA:
{book.plot.hook if book.plot else ''}

PIERWSZY ROZDZIAŁ (fragment):
{book.chapters[0].content[:1000] if book.chapters else ''}

Wygeneruj metadane książki w formacie JSON."""

        response = await self.openai.complete(
            model=model.value['model'],
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=context,
            temperature=0.7,
        )

        # Log cost
        cost_tracker.log_usage(
            model=model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            phase='publishing'
        )

        # Parse response
        try:
            start = response.content.find('{')
            end = response.content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response.content[start:end]
                return json.loads(json_str)
            else:
                return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse metadata: {e}")
            return {
                'title': 'Untitled',
                'subtitle': None,
                'tagline': '',
                'blurb': ''
            }

    SYSTEM_PROMPT = """Jesteś AGENTEM WYDAWNICZYM - przygotowujesz książkę
do publikacji.

Wygeneruj metadane książki:

1. TYTUŁ
   - Chwytliwy, zapadający w pamięć
   - Adekwatny do gatunku
   - Nie za długi (2-5 słów)

2. TAGLINE
   - Jedno zdanie, które sprzedaje książkę
   - Hook + konflikt
   - Intrygujący

3. BLURB (opis na okładkę)
   - 150-200 słów
   - Hook, konflikt, stawki
   - BEZ SPOILERÓW!
   - Wciągający

ODPOWIEDZ W FORMACIE JSON:
{
    "title": "Tytuł Książki",
    "subtitle": "Podtytuł (opcjonalnie)",
    "tagline": "Intrygujący tagline",
    "blurb": "Opis na okładkę (150-200 słów)",
    "keywords": ["słowo1", "słowo2", "słowo3"],
    "categories": ["kategoria1", "kategoria2"]
}"""

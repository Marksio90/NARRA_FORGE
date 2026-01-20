"""
Director Agent - final polish and pacing.
"""
from app.core.openai_client import OpenAIClient
from app.core.cost_optimizer import CostOptimizer
from app.core.cost_tracker import CostTracker
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DirectorAgent:
    """
    Director Agent - Reżyser Literacki.
    Ostatnie szlify przed publikacją. Zamienia dobrą książkę w wybitną.
    """

    def __init__(self):
        self.openai = OpenAIClient()

    async def polish_book(
        self,
        chapters: List[Dict[str, Any]],
        genre: str,
        cost_optimizer: CostOptimizer,
        cost_tracker: CostTracker,
    ) -> List[Dict[str, Any]]:
        """
        Polish all chapters - pacing, flow, emotional beats.

        Args:
            chapters: All chapters
            genre: Book genre
            cost_optimizer: Cost optimizer
            cost_tracker: Cost tracker

        Returns:
            Polished chapters
        """
        logger.info(f"Polishing {len(chapters)} chapters")

        polished = []

        for i, chapter in enumerate(chapters):
            logger.info(f"Polishing chapter {i+1}/{len(chapters)}")

            # Select model
            model = cost_optimizer.select_model_for_task('complex_scene')

            # Build context
            prev_chapter = chapters[i-1] if i > 0 else None
            next_chapter = chapters[i+1] if i < len(chapters)-1 else None

            prompt = self._build_polish_prompt(
                chapter, prev_chapter, next_chapter, i+1, len(chapters)
            )

            response = await self.openai.complete(
                model=model.value['model'],
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=prompt,
                temperature=0.6,
            )

            # Log cost
            cost_tracker.log_usage(
                model=model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                phase='polish_and_edit'
            )

            # Update chapter
            chapter['content'] = response.content
            chapter['word_count'] = len(response.content.split())
            polished.append(chapter)

        logger.info(f"Polishing complete")

        return polished

    SYSTEM_PROMPT = """Jesteś REŻYSEREM LITERACKIM - patrzysz na całość
i dbasz, by każdy element grał swoją rolę perfekcyjnie.

OCEŃ I POPRAW:

1. TEMPO
   - Czy nie jest za wolno/za szybko?
   - Czy są właściwe momenty oddechu?
   - Czy kulminacje są wzmocnione?

2. EMOCJE
   - Czy czytelnik czuje to, co powinien?
   - Czy emocje są zasłużone (earned)?
   - Czy nie ma emotional whiplash?

3. PRZEJŚCIA
   - Czy sceny płynnie się łączą?
   - Czy zmiany punktu widzenia są jasne?
   - Czy timeline jest czytelny?

4. HOOK I CLIFFHANGER
   - Czy początek wciąga?
   - Czy koniec zachęca do czytania dalej?

5. DETALE
   - Powtórzenia słów/fraz
   - Zbyt długie akapity
   - Niejasne zaimki

ZWRÓĆ POPRAWIONY TEKST.
Zachowaj długość i styl, popraw tylko co wymaga poprawy."""

    def _build_polish_prompt(
        self,
        chapter: Dict[str, Any],
        prev_chapter: Dict[str, Any] | None,
        next_chapter: Dict[str, Any] | None,
        position: int,
        total: int
    ) -> str:
        """Build polish prompt."""

        context = f"""ROZDZIAŁ DO POLEROWANIA:
---
{chapter.get('content', '')}
---

POZYCJA W KSIĄŻCE: {position}/{total}
CEL ROZDZIAŁU: {chapter.get('outline_goal', '')}

"""

        if prev_chapter:
            context += f"POPRZEDNI ROZDZIAŁ (koniec): ...{prev_chapter.get('content', '')[-500:]}\n\n"

        if next_chapter:
            context += f"NASTĘPNY ROZDZIAŁ (początek): {next_chapter.get('content', '')[:500]}...\n\n"

        context += """Polerujesz ten rozdział pod kątem:
- Tempo i flow
- Emocje i napięcie
- Przejścia między scenami
- Powtórzenia i niejasności

Zwróć poprawiony tekst rozdziału."""

        return context

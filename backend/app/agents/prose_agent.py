"""
Prose Agent - writes the actual book text.
"""
from app.core.openai_client import OpenAIClient
from app.core.cost_optimizer import CostOptimizer
from app.core.cost_tracker import CostTracker
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ProseAgent:
    """
    Prose Agent - Mistrz Słowa.
    Zamienia zarys w magię słowa. Każde zdanie ma znaczenie.
    """

    def __init__(self):
        self.openai = OpenAIClient()

    async def write_chapter(
        self,
        chapter_outline: Dict[str, Any],
        genre: str,
        world: Dict[str, Any],
        characters: List[Dict[str, Any]],
        previous_chapters: List[Dict[str, Any]],
        cost_optimizer: CostOptimizer,
        cost_tracker: CostTracker,
    ) -> Dict[str, Any]:
        """
        Write a chapter based on outline.

        Args:
            chapter_outline: Chapter outline from plot
            genre: Book genre
            world: World data
            characters: Characters data
            previous_chapters: Previously written chapters
            cost_optimizer: Cost optimizer
            cost_tracker: Cost tracker

        Returns:
            Chapter data with content
        """
        chapter_num = chapter_outline.get('number', 1)
        logger.info(f"Writing chapter {chapter_num}")

        # Determine if this is a critical chapter
        is_turning_point = chapter_outline.get('plot_points', []) != []
        is_finale = chapter_num > (chapter_outline.get('total_chapters', 22) * 0.9)

        # Select model
        model = cost_optimizer.select_model_for_task(
            'finale_writing' if is_finale else 'complex_scene' if is_turning_point else 'scene_description',
            is_plot_turning_point=is_turning_point,
            is_finale=is_finale,
            genre=genre
        )

        # Build context
        context = self._build_context(
            chapter_outline, world, characters, previous_chapters
        )

        # Generate chapter
        response = await self.openai.complete(
            model=model.value['model'],
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=context,
            temperature=0.8,
        )

        # Log cost
        cost_tracker.log_usage(
            model=model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            phase='prose_writing'
        )

        # Count words
        word_count = len(response.content.split())

        chapter_data = {
            'number': chapter_num,
            'title': chapter_outline.get('title'),
            'content': response.content,
            'word_count': word_count,
            'outline_goal': chapter_outline.get('goal'),
            'outline_summary': chapter_outline.get('summary'),
            'location': chapter_outline.get('location'),
            'pov': chapter_outline.get('pov'),
        }

        logger.info(f"Chapter {chapter_num} written: {word_count} words")

        return chapter_data

    SYSTEM_PROMPT = """Jesteś MISTRZEM SŁOWA - piszesz tak, że czytelnik
zapomina, że czyta.

ZASADY PISANIA:

1. SHOW, DON'T TELL
   ❌ "Jan był zły"
   ✅ "Jan zacisnął szczęki. Żyła na jego skroni pulsowała."

2. DIALOG MUSI BRZMIEĆ NATURALNIE
   - Każda postać ma własny głos
   - Ludzie przerywają sobie
   - Nie wszystko jest powiedziane wprost

3. OPISY SŁUŻĄ HISTORII
   - Opisuj to, co ważne
   - Używaj zmysłów (nie tylko wzroku!)
   - Atmosfera przed szczegółami

4. KONTROLUJ TEMPO
   - Krótkie zdania = napięcie, akcja
   - Długie zdania = refleksja, opis
   - Mieszaj dla dynamiki

5. KAŻDY ROZDZIAŁ TO MINI-HISTORIA
   - Własny cel
   - Własna struktura
   - Hook na końcu

PISZ W JĘZYKU POLSKIM.
Pisz pełny rozdział (3000-5000 słów).
Używaj bogatego języka i buduj immersję."""

    def _build_context(
        self,
        outline: Dict[str, Any],
        world: Dict[str, Any],
        characters: List[Dict[str, Any]],
        previous_chapters: List[Dict[str, Any]]
    ) -> str:
        """Build context for chapter writing."""

        # Previous chapter summary
        prev_summary = ""
        if previous_chapters:
            last = previous_chapters[-1]
            prev_summary = f"\nPOPRZEDNI ROZDZIAŁ:\n{last.get('outline_summary', '')}"

        # Characters in scene
        char_names = outline.get('characters', [])
        chars_in_scene = [c for c in characters if c.get('name') in char_names]
        char_info = "\n".join([
            f"- {c.get('name')}: {c.get('personality', {}).get('traits', [])[:3]}"
            for c in chars_in_scene
        ])

        return f"""ROZDZIAŁ {outline.get('number')}: {outline.get('title', '')}

CEL ROZDZIAŁU: {outline.get('goal')}
STRESZCZENIE: {outline.get('summary')}

LOKACJA: {outline.get('location')}
PUNKT WIDZENIA: {outline.get('pov')}

POSTACIE W SCENIE:
{char_info}

ŚWIAT: {world.get('name')} - {world.get('description')}
{prev_summary}

PUNKTY FABULARNE DO UWZGLĘDNIENIA:
{chr(10).join(f"- {p}" for p in outline.get('plot_points', []))}

Napisz pełny rozdział (3000-5000 słów) w języku polskim.
Pamiętaj o atmosferze, dialogach i tempo."""

    async def repair_chapter(
        self,
        chapter: Dict[str, Any],
        issues: List[Any],
        world: Dict[str, Any],
        characters: List[Dict[str, Any]],
        cost_optimizer: CostOptimizer,
        cost_tracker: CostTracker,
    ) -> Dict[str, Any]:
        """
        Repair chapter based on consistency issues.

        Args:
            chapter: Chapter with issues
            issues: List of consistency issues
            world: World data
            characters: Characters data
            cost_optimizer: Cost optimizer
            cost_tracker: Cost tracker

        Returns:
            Repaired chapter
        """
        logger.info(f"Repairing chapter {chapter.get('number')}")

        # Select model (repairs need higher tier)
        model = cost_optimizer.select_model_for_task('critical_repair')

        # Build repair instructions
        issues_text = "\n".join([
            f"{i+1}. [{issue.severity.value.upper()}] {issue.description}\n"
            f"   Lokalizacja: \"{issue.location}\"\n"
            f"   Naprawa: {issue.suggestion}"
            for i, issue in enumerate(issues)
        ])

        prompt = f"""ORYGINALNY TEKST:
---
{chapter['content']}
---

PROBLEMY DO NAPRAWIENIA:
{issues_text}

KONTEKST ŚWIATA:
{world.get('name')}: {world.get('description')}

Napraw wszystkie problemy zachowując styl i ton.
Zwróć KOMPLETNY naprawiony tekst."""

        response = await self.openai.complete(
            model=model.value['model'],
            system_prompt=self.REPAIR_SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.7,
        )

        # Log cost
        cost_tracker.log_usage(
            model=model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            phase='consistency_checks'
        )

        chapter['content'] = response.content
        chapter['word_count'] = len(response.content.split())

        logger.info(f"Chapter {chapter.get('number')} repaired")

        return chapter

    REPAIR_SYSTEM_PROMPT = """Jesteś CHIRURGIEM TEKSTU - naprawiasz błędy precyzyjnie,
zachowując wszystko co jest poprawne.

ZASADY:
1. Napraw TYLKO zgłoszone problemy
2. Zachowaj styl, ton i długość
3. Nie dodawaj nowych elementów
4. Nie usuwaj poprawnych fragmentów
5. Zachowaj strukturę rozdziału

Zwróć KOMPLETNY naprawiony tekst rozdziału."""

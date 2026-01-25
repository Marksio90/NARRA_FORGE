"""
Scene Writer Agent - SIMPLIFIED scene-by-scene chapter generation

ZASADA: PROSTOTA = NIEZAWODNOŚĆ
- Generuj sceny jedna po drugiej
- Każda scena to jedno wywołanie AI
- BEZ QA w trakcie generacji
- BEZ repair w trakcie generacji
- ZAWSZE zwróć content
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from app.services.ai_service import get_ai_service, ModelTier
from app.models.chapter import ChapterStatus

logger = logging.getLogger(__name__)


@dataclass
class SceneResult:
    """Result of scene generation"""
    scene_number: int
    content: str
    word_count: int
    cost: float
    model_used: str


@dataclass
class ChapterResult:
    """Result of chapter generation"""
    chapter_number: int
    scenes: List[SceneResult]
    full_content: str
    total_word_count: int
    status: ChapterStatus
    qa_scores: Dict[str, float]
    total_cost: float
    repair_count: int


class SceneWriterAgent:
    """
    SIMPLIFIED Scene Writer - generuje sceny BEZ dodatkowej walidacji

    Zasada: Wygeneruj content, zwróć content. Koniec.
    QA i repair to osobne kroki PO generacji.
    """

    def __init__(self):
        self.ai_service = get_ai_service()
        self.name = "Scene Writer Agent"

    async def write_chapter(
        self,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        genre: str,
        pov_character: Dict[str, Any],
        context_pack: Any,  # ContextPack - but we just use it for formatting
        target_word_count: int,
        book_title: str,
        tier: ModelTier = ModelTier.TIER_2,  # Default to GPT-4o for quality
        on_scene_complete: Optional[callable] = None
    ) -> ChapterResult:
        """
        Generuj rozdział scena po scenie - PROSTO i NIEZAWODNIE
        """
        logger.info(f"✍️ {self.name}: Generating Chapter {chapter_number} (~{target_word_count} words)")

        # Plan scenes - 4-5 scen na rozdział
        num_scenes = 5
        words_per_scene = target_word_count // num_scenes

        scene_results: List[SceneResult] = []
        total_cost = 0.0

        # Extract context for prompt
        context_text = self._format_context(context_pack, pov_character)

        # Previous scene content for continuity
        previous_content = ""

        for scene_num in range(1, num_scenes + 1):
            logger.info(f"🎬 Generating scene {scene_num}/{num_scenes}...")

            # Generate scene
            scene_result = await self._generate_scene(
                chapter_number=chapter_number,
                scene_number=scene_num,
                total_scenes=num_scenes,
                genre=genre,
                pov_character=pov_character,
                book_title=book_title,
                target_words=words_per_scene,
                context_text=context_text,
                previous_content=previous_content,
                chapter_outline=chapter_outline,
                tier=tier
            )

            scene_results.append(scene_result)
            total_cost += scene_result.cost
            previous_content = scene_result.content[-500:]  # Last 500 chars for continuity

            logger.info(f"✅ Scene {scene_num}: {scene_result.word_count} words, ${scene_result.cost:.4f}")

            # Progress callback
            if on_scene_complete:
                try:
                    await on_scene_complete(scene_num, num_scenes, scene_result)
                except:
                    pass  # Don't let callback errors break generation

        # Assemble full chapter
        full_content = self._assemble_chapter(chapter_number, scene_results)
        total_words = sum(s.word_count for s in scene_results)

        logger.info(f"✅ Chapter {chapter_number} COMPLETE: {total_words} words, ${total_cost:.4f}")

        return ChapterResult(
            chapter_number=chapter_number,
            scenes=scene_results,
            full_content=full_content,
            total_word_count=total_words,
            status=ChapterStatus.DRAFTED,
            qa_scores={"total": 85.0},  # Default - QA happens later
            total_cost=total_cost,
            repair_count=0
        )

    async def _generate_scene(
        self,
        chapter_number: int,
        scene_number: int,
        total_scenes: int,
        genre: str,
        pov_character: Dict[str, Any],
        book_title: str,
        target_words: int,
        context_text: str,
        previous_content: str,
        chapter_outline: Dict[str, Any],
        tier: ModelTier
    ) -> SceneResult:
        """Generate a single scene - SIMPLE and RELIABLE"""

        # Determine scene type based on position
        if scene_number == 1:
            scene_type = "OTWARCIE - mocny hook, wprowadzenie konfliktu"
        elif scene_number == total_scenes:
            scene_type = "FINAŁ - kulminacja, cliffhanger na koniec rozdziału"
        elif scene_number == total_scenes // 2:
            scene_type = "PUNKT ZWROTNY - zmiana kierunku, rewelacja"
        else:
            scene_type = "ROZWÓJ - pogłębienie konfliktu, napięcie rośnie"

        # Get character info
        char_name = pov_character.get('name', 'protagonist')
        char_wound = pov_character.get('wound', '')
        char_voice = pov_character.get('speechPatterns', '')

        prompt = f"""# SCENA {scene_number}/{total_scenes} - Rozdział {chapter_number}

## KSIĄŻKA: "{book_title}" ({genre})

## TYP SCENY: {scene_type}

## POV: {char_name}
Rana wewnętrzna: {char_wound}
Sposób mówienia: {char_voice}

## CEL SCENY
{chapter_outline.get('goal', 'Rozwinąć fabułę i pogłębić postacie')}

## KONTEKST
{context_text}

{f"## POPRZEDNIA SCENA (kontynuuj)" if previous_content else ""}
{previous_content if previous_content else ""}

## WYMAGANIA TECHNICZNE
• **MINIMUM {target_words} słów** - to absolutny wymóg!
• Dialogi z PAUZĄ (—), nigdy cudzysłowami
• 100% po polsku
• Deep POV przez {char_name}
• Min. 3 zmysły (zapach, dźwięk, dotyk)
• Mikro-napięcie w każdym akapicie
• Dialog = 3 warstwy (słowa / intencja / ciało)

## STRUKTURA SCENY
1. Mocne otwarcie (akcja/dialog/obraz - NIE opis pogody!)
2. Rozwój z napięciem w każdym akapicie
3. Punkt kulminacyjny sceny
4. Hak na następną scenę

Napisz scenę. MINIMUM {target_words} słów. Zacznij od akcji lub dialogu."""

        system_prompt = f"""Jesteś mistrzem prozy {genre} na poziomie Sapkowskiego, Kinga, Sandersona.

TWOJE ZASADY:
• ZAWSZE piszesz PEŁNE sceny - nigdy nie skracasz
• Deep POV przez {char_name} - świat widziany JEGO oczami
• Rana postaci KOLORUJE percepcję
• Ciało = emocje (zaciśnięte pięści, suche gardło, zimny pot)
• Dialogi z PODTEKSTEM - co NIE jest powiedziane
• Każdy akapit ma mikro-napięcie
• Zmysły budują atmosferę (szczególnie ZAPACH = pamięć)

FORMAT:
• Dialogi z pauzą (—), nigdy cudzysłowy
• 100% po polsku
• Naturalny, płynny język"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                tier=tier,
                temperature=0.85,
                max_tokens=target_words * 2,  # Double for safety
                json_mode=False,
                prefer_anthropic=False,
                metadata={
                    "agent": self.name,
                    "task": "scene_generation",
                    "chapter": chapter_number,
                    "scene": scene_number
                }
            )

            content = response.content.strip()
            word_count = len(content.split())

            return SceneResult(
                scene_number=scene_number,
                content=content,
                word_count=word_count,
                cost=response.cost,
                model_used=response.model
            )

        except Exception as e:
            logger.error(f"❌ Scene {scene_number} generation FAILED: {e}", exc_info=True)
            # NIGDY nie zwracaj pustego contentu - rzuć wyjątek!
            raise RuntimeError(f"Scene {scene_number} generation failed: {e}")

    def _format_context(self, context_pack: Any, pov_character: Dict[str, Any]) -> str:
        """Format context for prompt"""
        if context_pack is None:
            return f"POV: {pov_character.get('name', 'protagonist')}"

        try:
            # Try to use context_pack's format method if available
            if hasattr(context_pack, 'previous_chapter_summary'):
                parts = []
                if context_pack.previous_chapter_summary:
                    parts.append(f"Poprzednio: {context_pack.previous_chapter_summary[:300]}")
                if hasattr(context_pack, 'plot_context') and context_pack.plot_context:
                    pc = context_pack.plot_context
                    parts.append(f"Napięcie: {pc.get('tension_level', 5)}/10")
                return "\n".join(parts) if parts else ""
            else:
                return str(context_pack)[:500]
        except:
            return ""

    def _assemble_chapter(self, chapter_number: int, scenes: List[SceneResult]) -> str:
        """Assemble full chapter from scenes"""
        parts = [f"Rozdział {chapter_number}\n"]

        for scene in scenes:
            parts.append(scene.content)
            parts.append("")  # Empty line between scenes

        return "\n\n".join(parts)


def get_scene_writer() -> SceneWriterAgent:
    """Get Scene Writer instance"""
    return SceneWriterAgent()

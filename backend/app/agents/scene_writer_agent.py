"""
Scene Writer Agent - Scene-by-scene chapter generation

KEY ARCHITECTURE:
- Chapter = 3-6 scenes
- Each scene generated separately (300-800 words)
- Mini-QA after each scene
- Checkpoint after each scene (can resume)
- Scene fails → repair just that scene, not whole chapter

BENEFITS:
1. Cost control (can stop mid-chapter if budget exceeded)
2. Quality control (validate each scene before moving on)
3. Resume capability (restart from last good scene)
4. Targeted repair (fix just broken scene)
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from app.services.ai_service import get_ai_service, ModelTier
from app.services.context_pack_builder import ContextPackBuilder, ContextPack
from app.agents.qa_validator_agent import QAValidatorAgent
from app.agents.repair_agent import RepairAgent
from app.models.chapter import ChapterStatus

logger = logging.getLogger(__name__)


@dataclass
class SceneResult:
    """Result of scene generation"""
    scene_number: int
    content: str
    word_count: int
    status: str  # "success", "needs_repair", "failed"
    qa_score: float
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


# Scene type templates for variety
SCENE_TYPES = {
    "action": {
        "rhythm": "Krótkie zdania. Fragmenty. Szybkie cięcia. Napięcie.",
        "focus": "Ruch, reakcje fizyczne, czas kurczy się",
        "dialog_style": "Urwane. Ostrzegawcze. Zero ozdobników."
    },
    "dialog": {
        "rhythm": "Naturalne tempo rozmowy, pauzy, reakcje",
        "focus": "Subtext, co NIE jest powiedziane, napięcie między postaciami",
        "dialog_style": "Charakterystyczne głosy, tiki werbalne, przerywanie"
    },
    "introspection": {
        "rhythm": "Dłuższe, płynące zdania, refleksja, cisza",
        "focus": "Wewnętrzny świat POV, wspomnienia, emocje",
        "dialog_style": "Minimalne lub wewnętrzny monolog"
    },
    "revelation": {
        "rhythm": "Build-up → uderzenie → cisza → reakcja",
        "focus": "Moment prawdy, maska opada, konsekwencje",
        "dialog_style": "Ciężkie słowa, znaczące pauzy"
    },
    "tension": {
        "rhythm": "Crescendo - coraz krótsze zdania do wybuchu",
        "focus": "Mikro-napięcie w każdym detalu, coś jest NIE TAK",
        "dialog_style": "Podwójne znaczenia, ukryte groźby"
    }
}


class SceneWriterAgent:
    """
    Scene-by-scene chapter writer with quality gates

    Process:
    1. Plan scenes from chapter outline (3-6 scenes)
    2. For each scene:
       a. Generate scene (TIER_1 or TIER_2)
       b. Quick QA validation
       c. If fails → repair scene
       d. Checkpoint (save progress)
    3. Assemble chapter from scenes
    4. Full chapter QA
    5. Chapter-level repair if needed
    """

    def __init__(self):
        self.ai_service = get_ai_service()
        self.context_builder = ContextPackBuilder()
        self.qa_validator = QAValidatorAgent()
        self.repair_agent = RepairAgent()
        self.name = "Scene Writer Agent"

    async def write_chapter(
        self,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        genre: str,
        pov_character: Dict[str, Any],
        context_pack: ContextPack,
        target_word_count: int,
        book_title: str,
        tier: ModelTier = ModelTier.TIER_1,
        on_scene_complete: Optional[callable] = None  # Callback for progress
    ) -> ChapterResult:
        """
        Write a chapter scene by scene

        Args:
            chapter_number: Chapter number
            chapter_outline: Outline with scenes planned
            genre: Literary genre
            pov_character: POV character (trimmed)
            context_pack: Context pack from builder
            target_word_count: Target total words
            book_title: Book title for context
            tier: Starting tier (will escalate if needed)
            on_scene_complete: Optional callback after each scene

        Returns:
            ChapterResult with all scenes and metadata
        """
        logger.info(f"✍️ {self.name}: Starting Chapter {chapter_number} (scene-by-scene)")

        # 1. Plan scenes
        scenes_plan = self._plan_scenes(chapter_outline, target_word_count)
        logger.info(f"📝 Planned {len(scenes_plan)} scenes")

        # 2. Generate each scene
        scene_results: List[SceneResult] = []
        total_cost = 0.0
        repair_count = 0
        current_tier = tier

        for scene_plan in scenes_plan:
            scene_num = scene_plan['number']
            scene_goal = scene_plan['goal']
            scene_words = scene_plan['target_words']
            scene_type = scene_plan.get('type', 'dialog')

            logger.info(f"🎬 Scene {scene_num}/{len(scenes_plan)}: {scene_goal[:50]}...")

            # Generate scene
            scene_result = await self._generate_scene(
                scene_number=scene_num,
                scene_plan=scene_plan,
                genre=genre,
                pov_character=pov_character,
                context_pack=context_pack,
                previous_scenes=scene_results,
                tier=current_tier,
                book_title=book_title
            )

            total_cost += scene_result.cost

            # Quick QA
            qa_result = await self.qa_validator.validate_scene(
                scene_content=scene_result.content,
                scene_number=scene_num,
                scene_goal=scene_goal,
                min_words=int(scene_words * 0.7)
            )

            scene_result.qa_score = qa_result['score']

            # Repair if needed
            if not qa_result['passed']:
                logger.warning(f"⚠️ Scene {scene_num} needs repair (score: {qa_result['score']})")
                repair_result = await self.repair_agent.repair_scene(
                    scene_content=scene_result.content,
                    scene_number=scene_num,
                    issues=qa_result['issues'],
                    scene_goal=scene_goal,
                    genre=genre,
                    pov_character=pov_character
                )

                if repair_result['success']:
                    scene_result.content = repair_result['repaired_content']
                    scene_result.word_count = repair_result['word_count']
                    scene_result.status = "repaired"
                    repair_count += 1
                else:
                    scene_result.status = "needs_repair"
            else:
                scene_result.status = "success"

            scene_results.append(scene_result)

            # Callback for progress updates
            if on_scene_complete:
                await on_scene_complete(scene_num, len(scenes_plan), scene_result)

        # 3. Assemble chapter
        full_content = self._assemble_chapter(chapter_number, scene_results)
        total_word_count = sum(s.word_count for s in scene_results)

        # 4. Determine final status
        failed_scenes = [s for s in scene_results if s.status == "needs_repair"]
        if failed_scenes:
            status = ChapterStatus.REPAIR_NEEDED
        else:
            status = ChapterStatus.DRAFTED

        # Calculate aggregate QA scores
        qa_scores = {
            "scene_average": sum(s.qa_score for s in scene_results) / len(scene_results) if scene_results else 0,
            "min_scene_score": min(s.qa_score for s in scene_results) if scene_results else 0,
            "scenes_passed": len([s for s in scene_results if s.status in ["success", "repaired"]])
        }

        logger.info(
            f"✅ Chapter {chapter_number} complete: "
            f"{total_word_count} words, {len(scene_results)} scenes, "
            f"${total_cost:.4f}, {repair_count} repairs"
        )

        return ChapterResult(
            chapter_number=chapter_number,
            scenes=scene_results,
            full_content=full_content,
            total_word_count=total_word_count,
            status=status,
            qa_scores=qa_scores,
            total_cost=total_cost,
            repair_count=repair_count
        )

    def _plan_scenes(
        self,
        chapter_outline: Dict[str, Any],
        target_word_count: int
    ) -> List[Dict[str, Any]]:
        """
        Plan scenes from chapter outline

        Returns list of scene plans:
        [
            {"number": 1, "goal": "...", "target_words": 500, "type": "action", ...},
            ...
        ]
        """
        # Check if outline already has scenes
        existing_scenes = chapter_outline.get('scenes', [])

        if existing_scenes:
            # Use existing scene plans, add word targets
            scenes_count = len(existing_scenes)
            words_per_scene = target_word_count // scenes_count

            return [
                {
                    "number": i + 1,
                    "goal": scene.get('goal', scene.get('description', '')),
                    "conflict": scene.get('conflict', ''),
                    "characters": scene.get('characters', chapter_outline.get('characters_present', [])),
                    "setting": scene.get('setting', chapter_outline.get('setting', '')),
                    "type": self._infer_scene_type(scene),
                    "target_words": words_per_scene
                }
                for i, scene in enumerate(existing_scenes)
            ]

        # Generate scene plans from outline
        # Default: 4 scenes for standard chapter
        num_scenes = 4
        words_per_scene = target_word_count // num_scenes

        # Create scene breakdown
        goal = chapter_outline.get('goal', '')
        conflict = chapter_outline.get('conflict', '')
        turning_point = chapter_outline.get('turning_point', '')
        cliffhanger = chapter_outline.get('cliffhanger', '')

        scenes = [
            {
                "number": 1,
                "goal": f"Opening: Set scene, introduce conflict ({goal})",
                "type": "tension",
                "target_words": words_per_scene
            },
            {
                "number": 2,
                "goal": f"Development: Deepen conflict ({conflict})",
                "type": "dialog",
                "target_words": words_per_scene
            },
            {
                "number": 3,
                "goal": f"Turning point: {turning_point or 'Change direction'}",
                "type": "revelation",
                "target_words": words_per_scene
            },
            {
                "number": 4,
                "goal": f"Climax/Cliffhanger: {cliffhanger or 'Leave reader wanting more'}",
                "type": "action",
                "target_words": words_per_scene
            }
        ]

        return scenes

    def _infer_scene_type(self, scene: Dict[str, Any]) -> str:
        """Infer scene type from its description"""
        goal = (scene.get('goal', '') + scene.get('description', '')).lower()

        if any(w in goal for w in ['fight', 'chase', 'escape', 'walka', 'ucieczka', 'pościg']):
            return 'action'
        elif any(w in goal for w in ['reveal', 'secret', 'truth', 'odkrycie', 'sekret', 'prawda']):
            return 'revelation'
        elif any(w in goal for w in ['think', 'reflect', 'remember', 'myśl', 'wspomn', 'refleks']):
            return 'introspection'
        elif any(w in goal for w in ['tension', 'suspense', 'danger', 'napięcie', 'niebezp']):
            return 'tension'
        else:
            return 'dialog'  # Default

    async def _generate_scene(
        self,
        scene_number: int,
        scene_plan: Dict[str, Any],
        genre: str,
        pov_character: Dict[str, Any],
        context_pack: ContextPack,
        previous_scenes: List[SceneResult],
        tier: ModelTier,
        book_title: str
    ) -> SceneResult:
        """Generate a single scene"""

        scene_type = scene_plan.get('type', 'dialog')
        scene_style = SCENE_TYPES.get(scene_type, SCENE_TYPES['dialog'])
        target_words = scene_plan.get('target_words', 500)

        # Build previous scenes summary for continuity
        prev_summary = ""
        if previous_scenes:
            last_scene = previous_scenes[-1]
            prev_summary = f"Poprzednia scena: {last_scene.content[-500:]}"

        # Get character voice
        voice = pov_character.get('speechPatterns', '')
        wound = pov_character.get('wound', '')

        prompt = f"""# SCENA {scene_number} - "{book_title}"

## CEL SCENY
{scene_plan.get('goal', '')}

## WYMAGANIA
• Gatunek: {genre} | POV: {pov_character.get('name', 'protagonist')}
• Długość: **{target_words} słów** (minimum!)
• Dialogi: PAUZA (—), nigdy cudzysłowy
• 100% po polsku

## TYP SCENY: {scene_type.upper()}
Rytm: {scene_style['rhythm']}
Focus: {scene_style['focus']}
Dialogi: {scene_style['dialog_style']}

## PSYCHOLOGIA POV
Rana: {wound}
Głos: {voice}

## KONTEKST
{self.context_builder.format_for_prompt(context_pack)[:2000]}

{prev_summary}

## INSTRUKCJE
1. Zacznij od mocnego otwarcia (akcja/dialog/obraz)
2. Każdy akapit = mikro-napięcie
3. Dialog = 3 warstwy (słowa / intencja / ciało)
4. Końcówka = hak na kolejną scenę
5. Min. 3 zmysły (zapach, dźwięk, dotyk)

Napisz scenę. Minimum {target_words} słów."""

        system_prompt = f"""Jesteś mistrzem prozy {genre}. Piszesz scenami które nie puszczają czytelnika.

ZASADY:
• Deep POV przez {pov_character.get('name', 'protagonist')}
• Rana koloruje percepcję
• Napięcie w każdym akapicie
• Ciało = emocje (nie "czuł", ale fizyczne reakcje)
• Dialogi z podtekstem"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                tier=tier,
                temperature=0.8,
                max_tokens=target_words * 2,
                json_mode=False,
                metadata={
                    "agent": self.name,
                    "task": "scene_generation",
                    "scene": scene_number,
                    "type": scene_type
                }
            )

            content = response.content.strip()
            word_count = len(content.split())

            return SceneResult(
                scene_number=scene_number,
                content=content,
                word_count=word_count,
                status="generated",
                qa_score=0.0,  # Will be set after QA
                cost=response.cost,
                model_used=response.model
            )

        except Exception as e:
            logger.error(f"Scene generation failed: {e}")
            return SceneResult(
                scene_number=scene_number,
                content=f"[SCENE {scene_number} GENERATION FAILED: {e}]",
                word_count=0,
                status="failed",
                qa_score=0.0,
                cost=0.0,
                model_used="none"
            )

    def _assemble_chapter(
        self,
        chapter_number: int,
        scenes: List[SceneResult]
    ) -> str:
        """Assemble full chapter from scenes"""
        parts = [f"Rozdział {chapter_number}\n"]

        for scene in scenes:
            if scene.status != "failed":
                parts.append(scene.content)
                parts.append("")  # Empty line between scenes

        return "\n\n".join(parts)


def get_scene_writer() -> SceneWriterAgent:
    """Get Scene Writer instance"""
    return SceneWriterAgent()

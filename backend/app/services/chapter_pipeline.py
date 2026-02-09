"""
Chapter Pipeline - SIMPLIFIED chapter generation

ZASADA: PROSTOTA = NIEZAWODNOŚĆ
1. Zbuduj kontekst
2. Wygeneruj sceny
3. Zapisz do bazy
4. KONIEC

Żadnych fallbacków, żadnych pętli naprawczych.
Jeśli generacja się nie uda - rzuć wyjątek.
"""

import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.chapter import Chapter, ChapterStatus
from app.services.ai_service import get_ai_service, ModelTier
from app.services.context_pack_builder import ContextPackBuilder, get_context_pack_builder
from app.agents.scene_writer_agent import SceneWriterAgent, get_scene_writer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Semantic Router – dynamiczny dobór tier modelu na podstawie złożoności sceny
# ---------------------------------------------------------------------------

class SemanticRouter:
    """
    Analyzes chapter/scene complexity to route to the optimal model tier.

    Instead of always using TIER_2 (GPT-4o), this router:
    - Uses TIER_1 (GPT-4o-mini) for simple exposition, short dialogues
    - Uses TIER_2 (GPT-4o) for standard narrative scenes
    - Uses TIER_3 (GPT-4-turbo / o1) for climaxes, complex multi-POV scenes

    Classification is based on structural signals (no AI call needed):
    - Number of characters in scene
    - Tension level from plot structure
    - Scene type (dialogue, action, introspection)
    - Position in chapter (first/last scenes often more important)
    - Whether it's a climax, turning point, or resolution
    """

    # Complexity signals and their weights
    TIER_3_KEYWORDS = {
        "kulminacja", "climax", "zwrot akcji", "turning_point",
        "rozwiązanie", "resolution", "konfrontacja", "finał",
        "objawienie", "revelation", "śmierć", "death",
        "zdrada", "betrayal", "point_of_no_return",
    }
    TIER_1_KEYWORDS = {
        "ekspozycja", "exposition", "opis", "description",
        "podróż", "travel", "przejście", "transition",
        "sen", "poranek", "rutyna", "monolog",
    }

    def route_chapter(
        self,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        plot_structure: Dict[str, Any],
        total_chapters: int,
    ) -> ModelTier:
        """Determine optimal model tier for a chapter."""
        score = self._compute_complexity_score(
            chapter_number, chapter_outline, plot_structure, total_chapters
        )

        if score >= 7:
            tier = ModelTier.TIER_3
        elif score >= 4:
            tier = ModelTier.TIER_2
        else:
            tier = ModelTier.TIER_1

        logger.info(
            f"SemanticRouter: Chapter {chapter_number} complexity={score}/10 -> {tier.name}"
        )
        return tier

    def _compute_complexity_score(
        self,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        plot_structure: Dict[str, Any],
        total_chapters: int,
    ) -> int:
        """Compute complexity score 0-10 from structural signals."""
        score = 0

        # 1. Tension level from plot structure (0-10 directly)
        tension = self._get_tension(chapter_number, plot_structure)
        if tension >= 8:
            score += 3
        elif tension >= 5:
            score += 2
        else:
            score += 1

        # 2. Number of characters (more characters = more complex dialogue)
        num_chars = len(chapter_outline.get("characters_present", []))
        if num_chars >= 5:
            score += 2
        elif num_chars >= 3:
            score += 1

        # 3. Position: first chapter, last chapter, and midpoint are critical
        if chapter_number == 1 or chapter_number == total_chapters:
            score += 2
        elif total_chapters > 5 and abs(chapter_number - total_chapters // 2) <= 1:
            score += 1  # midpoint

        # 4. Keyword signals from outline text
        outline_text = " ".join([
            chapter_outline.get("goal", ""),
            chapter_outline.get("emotional_beat", ""),
            chapter_outline.get("summary", ""),
            chapter_outline.get("setting", ""),
        ]).lower()

        if any(kw in outline_text for kw in self.TIER_3_KEYWORDS):
            score += 2
        if any(kw in outline_text for kw in self.TIER_1_KEYWORDS):
            score -= 1

        # 5. Act position (Act 3 is usually most complex)
        acts = plot_structure.get("acts", [])
        for act in acts:
            if not isinstance(act, dict):
                continue
            if chapter_number in act.get("chapters", []):
                act_name = act.get("name", "").lower()
                if "iii" in act_name or "3" in act_name or "trzeci" in act_name:
                    score += 1
                break

        return max(0, min(10, score))

    def _get_tension(self, chapter_number: int, plot_structure: Dict[str, Any]) -> int:
        """Extract tension level for a chapter."""
        tension_graph = plot_structure.get("tension_graph", [])
        for idx, point in enumerate(tension_graph):
            if isinstance(point, dict) and point.get("chapter") == chapter_number:
                return point.get("tension", 5)
            elif isinstance(point, (int, float)) and idx + 1 == chapter_number:
                return int(point)
        return 5  # default


# Module-level instance
_semantic_router = SemanticRouter()


@dataclass
class PipelineConfig:
    """Configuration for chapter pipeline"""
    target_tier: ModelTier = ModelTier.TIER_2  # GPT-4o for quality (default/fallback)
    use_semantic_router: bool = True  # Enable dynamic tier selection
    cost_limit_per_chapter: float = 1.00  # USD - generous limit


@dataclass
class PipelineResult:
    """Result of chapter pipeline execution"""
    success: bool
    chapter_number: int
    status: ChapterStatus
    content: str
    word_count: int
    qa_scores: Dict[str, float]
    total_cost: float
    retries: int
    repairs: int
    tier_used: str
    escalated: bool
    error: Optional[str] = None


class ChapterPipeline:
    """
    SIMPLIFIED Chapter Pipeline

    Flow:
    1. Build context pack
    2. Generate scenes with SceneWriter
    3. Save to database
    4. Return result

    NO FALLBACKS - if generation fails, throw exception.
    """

    def __init__(
        self,
        db: Session,
        config: Optional[PipelineConfig] = None
    ):
        self.db = db
        self.config = config or PipelineConfig()

        # Initialize agents
        self.context_builder = get_context_pack_builder()
        self.scene_writer = get_scene_writer()

        logger.info(f"📦 ChapterPipeline initialized (tier={self.config.target_tier.name})")

    async def process_chapter(
        self,
        chapter: Chapter,
        genre: str,
        pov_character: Dict[str, Any],
        all_characters: List[Dict[str, Any]],
        world_bible: Dict[str, Any],
        plot_structure: Dict[str, Any],
        canon_facts: List[Dict[str, Any]],
        chapter_summaries: Dict[int, str],
        target_word_count: int,
        book_title: str,
        on_progress: Optional[callable] = None
    ) -> PipelineResult:
        """
        Generate chapter - SIMPLE and RELIABLE

        No fallbacks. No retries. Just generate.
        If it fails - throw exception.
        """
        chapter_number = chapter.number
        logger.info(f"🚀 Pipeline: Chapter {chapter_number} (~{target_word_count} words)")

        # Update status
        chapter.status = ChapterStatus.DRAFTING
        self.db.commit()

        # Build context pack
        context_pack = self.context_builder.build_chapter_context(
            chapter_number=chapter_number,
            chapter_outline=chapter.outline or {},
            all_characters=all_characters,
            world_bible=world_bible,
            plot_structure=plot_structure,
            canon_facts=canon_facts,
            chapter_summaries=chapter_summaries
        )

        logger.info(f"📦 Context pack: ~{context_pack.estimated_tokens} tokens")

        # Trim POV character for generation
        pov_trimmed = self.context_builder._trim_character(pov_character)

        # Semantic Router: dynamically select model tier based on chapter complexity
        if self.config.use_semantic_router:
            total_chapters = max(len(chapter_summaries) + 1, chapter_number)
            selected_tier = _semantic_router.route_chapter(
                chapter_number=chapter_number,
                chapter_outline=chapter.outline or {},
                plot_structure=plot_structure,
                total_chapters=total_chapters,
            )
        else:
            selected_tier = self.config.target_tier

        # Generate chapter with SceneWriter
        draft_result = await self.scene_writer.write_chapter(
            chapter_number=chapter_number,
            chapter_outline=chapter.outline or {},
            genre=genre,
            pov_character=pov_trimmed,
            context_pack=context_pack,
            target_word_count=target_word_count,
            book_title=book_title,
            tier=selected_tier,
            on_scene_complete=on_progress
        )

        # Validate result
        if draft_result.total_word_count < 500:
            raise RuntimeError(
                f"Chapter {chapter_number} generation failed: "
                f"only {draft_result.total_word_count} words generated. "
                f"Expected ~{target_word_count} words."
            )

        # Save to database
        chapter.content = draft_result.full_content
        chapter.word_count = draft_result.total_word_count
        chapter.status = ChapterStatus.DRAFTED
        chapter.generation_meta = {
            "model_tier": selected_tier.name,
            "cost": draft_result.total_cost,
            "scenes": len(draft_result.scenes),
            "generated_at": datetime.utcnow().isoformat()
        }
        chapter.is_complete = 1

        self.db.commit()

        logger.info(
            f"✅ Chapter {chapter_number} COMPLETE: "
            f"{draft_result.total_word_count} words, ${draft_result.total_cost:.4f}"
        )

        return PipelineResult(
            success=True,
            chapter_number=chapter_number,
            status=ChapterStatus.DRAFTED,
            content=draft_result.full_content,
            word_count=draft_result.total_word_count,
            qa_scores={"total": 85.0},  # Default score
            total_cost=draft_result.total_cost,
            retries=0,
            repairs=0,
            tier_used=selected_tier.name,
            escalated=(selected_tier != self.config.target_tier)
        )


def get_chapter_pipeline(db: Session, config: Optional[PipelineConfig] = None) -> ChapterPipeline:
    """Get Chapter Pipeline instance"""
    return ChapterPipeline(db, config)

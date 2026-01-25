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


@dataclass
class PipelineConfig:
    """Configuration for chapter pipeline"""
    target_tier: ModelTier = ModelTier.TIER_2  # GPT-4o for quality
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

        # Generate chapter with SceneWriter
        draft_result = await self.scene_writer.write_chapter(
            chapter_number=chapter_number,
            chapter_outline=chapter.outline or {},
            genre=genre,
            pov_character=pov_trimmed,
            context_pack=context_pack,
            target_word_count=target_word_count,
            book_title=book_title,
            tier=self.config.target_tier,
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
            "model_tier": self.config.target_tier.name,
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
            tier_used=self.config.target_tier.name,
            escalated=False
        )


def get_chapter_pipeline(db: Session, config: Optional[PipelineConfig] = None) -> ChapterPipeline:
    """Get Chapter Pipeline instance"""
    return ChapterPipeline(db, config)

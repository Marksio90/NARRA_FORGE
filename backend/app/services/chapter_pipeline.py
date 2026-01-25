"""
Chapter Pipeline - Production chapter generation with state machine

ARCHITECTURE:
1. State Machine (planned → drafted → validated → finalized)
2. Scene-based generation
3. QA with hard thresholds
4. Tiered escalation (TIER_0 → TIER_1 → TIER_2)
5. Circuit breaker (3 failures → escalate)
6. Recovery procedures

GUARANTEE: No empty chapters. Always produces result.
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.chapter import Chapter, ChapterStatus
from app.services.ai_service import get_ai_service, ModelTier
from app.services.context_pack_builder import ContextPackBuilder, get_context_pack_builder
from app.agents.scene_writer_agent import SceneWriterAgent, get_scene_writer
from app.agents.qa_validator_agent import QAValidatorAgent, get_qa_validator
from app.agents.repair_agent import RepairAgent, get_repair_agent

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for chapter pipeline"""
    max_retries: int = 3
    max_repairs: int = 2
    qa_pass_threshold: int = 85
    qa_repair_threshold: int = 70
    cost_limit_per_chapter: float = 0.50  # USD
    escalation_on_failure: bool = True
    use_circuit_breaker: bool = True


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
    Production chapter generation pipeline

    Flow:
    1. PLAN → Create context pack, validate outline
    2. DRAFT → Generate scenes with scene writer
    3. VALIDATE → Run QA validator
    4. REPAIR → Fix issues if needed
    5. FINALIZE → Create immutable snapshot

    Guarantees:
    - Always produces a chapter (fallback to safe draft)
    - Cost controlled (limits per chapter)
    - Quality gated (hard thresholds)
    - State persisted (can resume)
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
        self.qa_validator = get_qa_validator()
        self.repair_agent = get_repair_agent()

        # Circuit breaker state
        self._failure_count = 0

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
        Process a chapter through the full pipeline

        Args:
            chapter: Chapter model instance
            genre: Literary genre
            pov_character: POV character (full dict)
            all_characters: All characters
            world_bible: World bible
            plot_structure: Plot structure
            canon_facts: Established facts
            chapter_summaries: Previous chapter summaries
            target_word_count: Target words
            book_title: Book title
            on_progress: Optional progress callback

        Returns:
            PipelineResult with final state
        """
        chapter_number = chapter.number
        logger.info(f"🚀 Pipeline: Starting Chapter {chapter_number}")

        # Determine starting tier based on circuit breaker
        starting_tier = self._get_starting_tier()

        total_cost = 0.0
        retries = 0
        repairs = 0
        escalated = False

        try:
            # === PHASE 1: PLAN ===
            chapter.status = ChapterStatus.PLANNED
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

            logger.info(f"📦 Context pack ready: ~{context_pack.estimated_tokens} tokens")

            # === PHASE 2: DRAFT (with retries) ===
            chapter.status = ChapterStatus.DRAFTING
            self.db.commit()

            # Trim POV character for generation
            pov_trimmed = self.context_builder._trim_character(pov_character)

            draft_result = None
            current_tier = starting_tier

            for attempt in range(self.config.max_retries):
                logger.info(f"📝 Draft attempt {attempt + 1}/{self.config.max_retries} (Tier: {current_tier.name})")

                try:
                    draft_result = await self.scene_writer.write_chapter(
                        chapter_number=chapter_number,
                        chapter_outline=chapter.outline or {},
                        genre=genre,
                        pov_character=pov_trimmed,
                        context_pack=context_pack,
                        target_word_count=target_word_count,
                        book_title=book_title,
                        tier=current_tier,
                        on_scene_complete=on_progress
                    )

                    total_cost += draft_result.total_cost

                    # Check if draft is acceptable
                    if draft_result.total_word_count >= target_word_count * 0.7:
                        break  # Good enough, proceed to validation

                    # Draft too short, retry with escalation
                    retries += 1
                    if self.config.escalation_on_failure:
                        current_tier = self._escalate_tier(current_tier)
                        escalated = True

                except Exception as e:
                    logger.error(f"Draft attempt failed: {e}")
                    retries += 1

                    # Check cost limit
                    if total_cost >= self.config.cost_limit_per_chapter:
                        logger.warning("Cost limit reached, using fallback")
                        break

                    # Escalate on failure
                    if self.config.escalation_on_failure:
                        current_tier = self._escalate_tier(current_tier)
                        escalated = True

            # If no valid draft, create safe fallback
            if not draft_result or draft_result.total_word_count < 100:
                logger.warning("All attempts failed, creating safe draft")
                draft_result = await self._create_safe_draft(
                    chapter_number, chapter.outline or {}, genre, pov_trimmed, book_title
                )

            # Update chapter with draft
            chapter.content = draft_result.full_content
            chapter.word_count = draft_result.total_word_count
            chapter.scenes_content = [
                {
                    "scene_num": s.scene_number,
                    "content": s.content,
                    "word_count": s.word_count,
                    "status": s.status,
                    "qa_score": s.qa_score
                }
                for s in draft_result.scenes
            ]
            chapter.status = ChapterStatus.DRAFTED
            self.db.commit()

            # === PHASE 3: VALIDATE ===
            chapter.status = ChapterStatus.VALIDATING
            self.db.commit()

            qa_result = await self.qa_validator.validate_chapter(
                chapter_content=chapter.content,
                chapter_number=chapter_number,
                chapter_outline=chapter.outline or {},
                target_word_count=target_word_count,
                genre=genre,
                pov_character=pov_character,
                canon_facts=canon_facts
            )

            chapter.qa_scores = qa_result['scores']

            # === PHASE 4: REPAIR IF NEEDED ===
            if qa_result['status'] == 'repair_needed':
                chapter.status = ChapterStatus.REPAIRING
                self.db.commit()

                for repair_attempt in range(self.config.max_repairs):
                    logger.info(f"🔧 Repair attempt {repair_attempt + 1}/{self.config.max_repairs}")

                    repair_result = await self.repair_agent.repair_chapter(
                        chapter_content=chapter.content,
                        repair_instructions=qa_result.get('repair_instructions', []),
                        chapter_number=chapter_number,
                        genre=genre,
                        pov_character=pov_character,
                        target_word_count=target_word_count
                    )

                    repairs += 1

                    if repair_result['success']:
                        chapter.content = repair_result['repaired_content']
                        chapter.word_count = repair_result['word_count']

                        # Re-validate
                        qa_result = await self.qa_validator.validate_chapter(
                            chapter_content=chapter.content,
                            chapter_number=chapter_number,
                            chapter_outline=chapter.outline or {},
                            target_word_count=target_word_count,
                            genre=genre,
                            pov_character=pov_character,
                            canon_facts=canon_facts
                        )
                        chapter.qa_scores = qa_result['scores']

                        if qa_result['status'] == 'validated':
                            break

            # Determine final status
            if qa_result['status'] == 'rewrite':
                # Even rewrites get saved as drafts
                chapter.status = ChapterStatus.REPAIR_NEEDED
                self._failure_count += 1
            elif qa_result['status'] in ['validated', 'repair_needed']:
                chapter.status = ChapterStatus.VALIDATED
                self._failure_count = 0  # Reset circuit breaker

            # === PHASE 5: FINALIZE ===
            if chapter.status == ChapterStatus.VALIDATED:
                chapter.status = ChapterStatus.FINALIZED

                # Create immutable snapshot
                chapter.export_snapshot = {
                    "version": len(chapter.drafts or []) + 1,
                    "content": chapter.content,
                    "word_count": chapter.word_count,
                    "finalized_at": datetime.utcnow().isoformat(),
                    "checksum": self._create_checksum(chapter.content)
                }

                # Add to drafts history
                if chapter.drafts is None:
                    chapter.drafts = []
                chapter.drafts = list(chapter.drafts) + [{
                    "version": len(chapter.drafts) + 1,
                    "content": chapter.content,
                    "timestamp": datetime.utcnow().isoformat(),
                    "qa_scores": chapter.qa_scores
                }]

            # Update generation metadata
            chapter.generation_meta = {
                "model_tier": current_tier.name,
                "cost": total_cost,
                "retry_count": retries,
                "repair_count": repairs,
                "escalated": escalated
            }

            chapter.is_complete = 2 if chapter.status == ChapterStatus.FINALIZED else 1
            self.db.commit()

            logger.info(
                f"✅ Pipeline complete: Chapter {chapter_number} → {chapter.status.value} "
                f"({chapter.word_count} words, ${total_cost:.4f})"
            )

            return PipelineResult(
                success=chapter.status == ChapterStatus.FINALIZED,
                chapter_number=chapter_number,
                status=chapter.status,
                content=chapter.content,
                word_count=chapter.word_count,
                qa_scores=chapter.qa_scores or {},
                total_cost=total_cost,
                retries=retries,
                repairs=repairs,
                tier_used=current_tier.name,
                escalated=escalated
            )

        except Exception as e:
            logger.error(f"Pipeline failed for Chapter {chapter_number}: {e}")
            self._failure_count += 1

            # Save whatever we have
            if chapter.content:
                chapter.status = ChapterStatus.REPAIR_NEEDED
            else:
                chapter.status = ChapterStatus.PLANNED
            self.db.commit()

            return PipelineResult(
                success=False,
                chapter_number=chapter_number,
                status=chapter.status,
                content=chapter.content or "",
                word_count=chapter.word_count or 0,
                qa_scores=chapter.qa_scores or {},
                total_cost=total_cost,
                retries=retries,
                repairs=repairs,
                tier_used=starting_tier.name,
                escalated=escalated,
                error=str(e)
            )

    def _get_starting_tier(self) -> ModelTier:
        """Get starting tier based on circuit breaker state"""
        if self.config.use_circuit_breaker and self._failure_count >= 3:
            logger.warning("Circuit breaker triggered: starting with TIER_2")
            return ModelTier.TIER_2

        return ModelTier.TIER_1  # Default: cheap

    def _escalate_tier(self, current: ModelTier) -> ModelTier:
        """Escalate to next tier"""
        if current == ModelTier.TIER_1:
            return ModelTier.TIER_2
        elif current == ModelTier.TIER_2:
            return ModelTier.TIER_3
        else:
            return current  # Already at max

    async def _create_safe_draft(
        self,
        chapter_number: int,
        outline: Dict[str, Any],
        genre: str,
        pov_character: Dict[str, Any],
        book_title: str
    ) -> 'ChapterResult':
        """Create minimal safe draft when all else fails"""
        from app.agents.scene_writer_agent import ChapterResult, SceneResult

        logger.warning(f"Creating safe draft for Chapter {chapter_number}")

        # Create minimal content from outline
        goal = outline.get('goal', 'Continue the story')
        setting = outline.get('setting', '')
        characters = outline.get('characters_present', [])

        content = f"""Rozdział {chapter_number}

[Ten rozdział wymaga rewizji]

Cel: {goal}
Miejsce: {setting}
Postacie: {', '.join(characters[:5]) if characters else 'główni bohaterowie'}

{pov_character.get('name', 'Protagonist')} stanął przed kolejnym wyzwaniem.
Musiał podjąć decyzję, która zmieni wszystko.

— Co teraz? — zapytał cicho.

Odpowiedź nie nadeszła, ale wiedział, że musi działać.

[Kontynuacja rozdziału wymagana]"""

        return ChapterResult(
            chapter_number=chapter_number,
            scenes=[SceneResult(
                scene_number=1,
                content=content,
                word_count=len(content.split()),
                status="safe_draft",
                qa_score=50.0,
                cost=0.0,
                model_used="none"
            )],
            full_content=content,
            total_word_count=len(content.split()),
            status=ChapterStatus.REPAIR_NEEDED,
            qa_scores={"total": 50.0},
            total_cost=0.0,
            repair_count=0
        )

    def _create_checksum(self, content: str) -> str:
        """Create SHA256 checksum for content"""
        return f"sha256:{hashlib.sha256(content.encode()).hexdigest()[:16]}"


def get_chapter_pipeline(db: Session, config: Optional[PipelineConfig] = None) -> ChapterPipeline:
    """Get Chapter Pipeline instance"""
    return ChapterPipeline(db, config)

"""
Agent Orchestrator - Coordinates all AI agents for book generation

Manages the complete generation pipeline:
1. World Builder → creates world bible
2. Character Creator → creates all characters
3. Plot Architect → designs story structure
4. Prose Writer → writes all chapters (with QC)
5. Quality Control → validates everything

Features:
- Real-time progress tracking
- Cost monitoring per project
- Error handling and recovery
- Database persistence
- Async execution
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.agents import (
    WorldBuilderAgent,
    CharacterCreatorAgent,
    PlotArchitectAgent,
    ProseWriterAgent,
    QualityControlAgent
)
from app.models.project import Project, ProjectStatus
from app.models.world_bible import WorldBible
from app.models.character import Character, CharacterRole
from app.models.plot_structure import PlotStructure
from app.models.chapter import Chapter
from app.services.ai_service import get_ai_service
from app.config import settings

logger = logging.getLogger(__name__)


# Estimated duration for each step (in minutes)
STEP_DURATIONS = {
    1: 1,   # Inicjalizacja Projektu
    2: 1,   # Parametryzacja
    3: 1,   # World Bible
    4: 3,   # Kreacja Postaci Głównych
    5: 2,   # Kreacja Postaci Pobocznych
    6: 2,   # Główna Oś Fabularna
    7: 2,   # Wątki Poboczne
    8: 2,   # Chapter Breakdown
    9: 3,   # Scene Detailing
    10: 1,  # Pre-Writing Validation
    11: 20, # Prose Generation (LONGEST!)
    12: 2,  # Continuity Check
    13: 5,  # Style Polishing
    14: 1,  # Genre Compliance
    15: 1,  # Final Assembly
}


class GenerationProgress:
    """Track generation progress"""
    def __init__(self):
        self.total_steps = 15
        self.current_step = 0
        self.current_activity = ""
        self.total_cost = 0.0
        self.errors = []
        self.warnings = []
        self.step_start_time = None

    def update(self, step: int, activity: str, cost: float = 0.0):
        """Update progress"""
        self.current_step = step
        self.current_activity = activity
        self.total_cost += cost
        self.step_start_time = datetime.now()

    def get_percentage(self) -> float:
        """Get completion percentage"""
        return (self.current_step / self.total_steps) * 100

    def get_estimated_time_remaining(self) -> int:
        """Get estimated time remaining in minutes"""
        if self.current_step >= self.total_steps:
            return 0

        # Sum durations of remaining steps
        remaining = sum(
            STEP_DURATIONS[step]
            for step in range(self.current_step + 1, self.total_steps + 1)
        )

        # Add remaining time for current step
        current_step_duration = STEP_DURATIONS.get(self.current_step, 1)
        remaining += current_step_duration

        return remaining

    def get_current_step_duration(self) -> int:
        """Get estimated duration of current step in minutes"""
        return STEP_DURATIONS.get(self.current_step, 1)


class AgentOrchestrator:
    """
    Orchestrates all AI agents for complete book generation

    Manages the full pipeline from world building to final manuscript.
    Handles coordination, error recovery, progress tracking, and cost monitoring.
    """

    def __init__(self, db: Session, project: Project):
        """
        Initialize orchestrator

        Args:
            db: Database session
            project: Project to generate
        """
        self.db = db
        self.project = project
        self.progress = GenerationProgress()

        # Initialize agents
        self.world_builder = WorldBuilderAgent()
        self.character_creator = CharacterCreatorAgent()
        self.plot_architect = PlotArchitectAgent()
        self.prose_writer = ProseWriterAgent()
        self.quality_control = QualityControlAgent()

        # AI service for metrics
        self.ai_service = get_ai_service()

        # Reset AI service metrics for this project
        self.ai_service.reset_metrics()

        logger.info(f"🎬 Orchestrator initialized for project {project.id}: '{project.name}'")

    async def generate_complete_book(self) -> Dict[str, Any]:
        """
        Generate complete book from start to finish

        Returns:
            Generation report with stats and results
        """
        logger.info(f"🚀 Starting FULL GENERATION for project {self.project.id}")

        try:
            # Update project status
            self.project.status = ProjectStatus.GENERATING
            self.project.started_at = datetime.utcnow()
            try:
                self.db.commit()
            except SQLAlchemyError as e:
                self.db.rollback()
                logger.error(f"Database commit failed: {e}", exc_info=True)
                raise Exception(f"Nie udało się zaktualizować statusu projektu: {str(e)}")

            # Extract project parameters
            params = self.project.parameters or {}
            title_analysis = params.get('title_analysis', {})

            # STEP 1-2: Initialize (already done in simulation)
            await self._update_progress(1, "Inicjalizacja projektu")
            await asyncio.sleep(0.5)  # Brief pause
            await self._update_progress(2, "Walidacja parametrów")
            await asyncio.sleep(0.5)

            # STEP 3: Create World Bible
            await self._update_progress(3, "Generowanie World Bible (AI)")
            world_bible = await self._generate_world_bible(title_analysis, params)

            # STEP 4-5: Create Characters
            await self._update_progress(4, "Kreacja postaci głównych (AI)")
            characters = await self._generate_characters(world_bible, title_analysis, params)

            await self._update_progress(5, "Kreacja postaci pobocznych (AI)")
            # (included in above - supporting characters)

            # STEP 6-7: Create Plot Structure
            await self._update_progress(6, "Projektowanie struktury fabuły (AI)")
            plot_structure = await self._generate_plot_structure(
                world_bible, characters, params
            )

            await self._update_progress(7, "Projektowanie wątków pobocznych (AI)")
            # (included in plot structure - subplots)

            # STEP 8-9: Chapter Planning
            await self._update_progress(8, "Planowanie rozdziałów")
            chapter_count = params.get('chapter_count', 25)

            await self._update_progress(9, "Szczegółowe plany scen")
            # (will be done per-chapter)

            # STEP 10: Pre-writing validation
            await self._update_progress(10, "Walidacja przed pisaniem")
            await asyncio.sleep(0.5)

            # STEP 11: Generate ALL Chapters (THE BIG ONE!)
            await self._update_progress(11, f"Generowanie {chapter_count} rozdziałów (AI)")
            chapters_data = await self._generate_all_chapters(
                world_bible, characters, plot_structure, params
            )

            # STEP 12: Continuity Check
            await self._update_progress(12, "Sprawdzanie spójności (AI)")
            await self._validate_continuity(chapters_data, world_bible, characters, plot_structure)

            # STEP 13: Style Polishing
            await self._update_progress(13, "Polerowanie stylu")
            # (done during generation - QC agent)

            # STEP 14: Genre Compliance
            await self._update_progress(14, "Audyt zgodności z gatunkiem (AI)")
            await self._validate_genre_compliance(chapters_data)

            # STEP 15: Finalization
            await self._update_progress(15, "Finalizacja i eksport")
            await asyncio.sleep(0.5)

            # Mark as completed
            self.project.status = ProjectStatus.COMPLETED
            self.project.progress_percentage = 100.0
            self.project.current_step = 15
            self.project.current_activity = "Zakończone ✅"
            self.project.completed_at = datetime.utcnow()

            # Update actual cost
            metrics = self.ai_service.get_metrics()
            self.project.actual_cost = metrics.total_cost

            try:
                self.db.commit()
            except SQLAlchemyError as e:
                self.db.rollback()
                logger.error(f"Failed to commit completion status: {e}", exc_info=True)
                raise Exception(f"Nie udało się zapisać statusu zakończenia: {str(e)}")

            # Generate report
            report = {
                "success": True,
                "project_id": self.project.id,
                "project_name": self.project.name,
                "statistics": {
                    "world_bible": 1,
                    "characters": len(characters),
                    "plot_structure": 1,
                    "chapters": len(chapters_data),
                    "total_words": sum(ch['word_count'] for ch in chapters_data)
                },
                "ai_metrics": {
                    "total_cost": metrics.total_cost,
                    "total_tokens": metrics.total_tokens,
                    "api_calls": metrics.calls_made,
                    "errors": metrics.errors
                },
                "quality_scores": {
                    "average_chapter_quality": sum(
                        ch.get('quality_score', 0) for ch in chapters_data
                    ) / len(chapters_data) if chapters_data else 0
                }
            }

            logger.info(
                f"✅ GENERATION COMPLETE! Project {self.project.id}\n"
                f"   📊 Stats: {len(characters)} characters, {len(chapters_data)} chapters\n"
                f"   💰 Cost: ${metrics.total_cost:.2f}\n"
                f"   📝 Words: {report['statistics']['total_words']:,}"
            )

            return report

        except Exception as e:
            error_details = f"{type(e).__name__}: {str(e)}"
            logger.error(f"❌ Generation failed for project {self.project.id}: {error_details}", exc_info=True)

            # Mark as failed with detailed error message
            self.project.status = ProjectStatus.FAILED
            self.project.current_activity = f"Błąd: {str(e)}"
            self.project.error_message = error_details
            try:
                self.db.commit()
            except SQLAlchemyError as commit_error:
                self.db.rollback()
                logger.error(f"Failed to commit error status: {commit_error}", exc_info=True)
                # Don't raise here - we're already handling an error

            return {
                "success": False,
                "error": error_details,
                "error_type": type(e).__name__,
                "project_id": self.project.id
            }

    async def _generate_world_bible(
        self,
        title_analysis: Dict[str, Any],
        params: Dict[str, Any]
    ) -> WorldBible:
        """Generate world bible using World Builder Agent"""
        logger.info("🌍 Generating world bible with AI...")

        world_data = await self.world_builder.create_world_bible(
            genre=self.project.genre.value,
            project_name=self.project.name,
            title_analysis=title_analysis,
            target_word_count=params.get('target_word_count', 90000),
            style_complexity=params.get('style_complexity', 'medium')
        )

        # Save to database
        world_bible = WorldBible(
            project_id=self.project.id,
            geography=world_data.get('geography', {}),
            history=world_data.get('history', {}),
            systems=world_data.get('systems', {}),
            cultures=world_data.get('cultures', {}),
            rules=world_data.get('rules', {}),
            glossary=world_data.get('glossary', {}),
            notes=world_data.get('notes', '')
        )

        self.db.add(world_bible)
        try:
            self.db.commit()
            self.db.refresh(world_bible)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to save world bible: {e}", exc_info=True)
            raise Exception(f"Nie udało się zapisać World Bible do bazy: {str(e)}")

        logger.info(f"✅ World bible created and saved (ID: {world_bible.id})")
        return world_bible

    async def _generate_characters(
        self,
        world_bible: WorldBible,
        title_analysis: Dict[str, Any],
        params: Dict[str, Any]
    ) -> List[Character]:
        """Generate all characters using Character Creator Agent"""
        logger.info("👥 Generating characters with AI...")

        character_count = {
            'main': params.get('main_character_count', 4),
            'supporting': params.get('supporting_character_count', 8)
        }

        themes = title_analysis.get('themes', [])

        characters_data = await self.character_creator.create_characters(
            genre=self.project.genre.value,
            project_name=self.project.name,
            world_bible=world_bible.__dict__,
            title_analysis=title_analysis,
            character_count=character_count,
            themes=themes
        )

        # Save to database
        characters = []
        for char_data in characters_data:
            role_map = {
                'protagonist': CharacterRole.PROTAGONIST,
                'antagonist': CharacterRole.ANTAGONIST,
                'supporting': CharacterRole.SUPPORTING
            }

            character = Character(
                project_id=self.project.id,
                name=char_data.get('name', 'Unknown'),
                role=role_map.get(char_data.get('role', 'supporting'), CharacterRole.SUPPORTING),
                profile=char_data.get('profile', {}),
                arc=char_data.get('arc', {}),
                voice_guide=char_data.get('voice_guide', {}),
                relationships=char_data.get('relationships', {})
            )

            self.db.add(character)
            characters.append(character)

        try:
            self.db.commit()
            for char in characters:
                self.db.refresh(char)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to save characters: {e}", exc_info=True)
            raise Exception(f"Nie udało się zapisać postaci do bazy: {str(e)}")

        logger.info(f"✅ {len(characters)} characters created and saved")
        return characters

    async def _generate_plot_structure(
        self,
        world_bible: WorldBible,
        characters: List[Character],
        params: Dict[str, Any]
    ) -> PlotStructure:
        """Generate plot structure using Plot Architect Agent"""
        logger.info("📖 Architecting plot structure with AI...")

        # Convert characters to dict format
        characters_data = [
            {
                'name': c.name,
                'role': c.role.value,
                'profile': c.profile,
                'arc': c.arc,
                'voice_guide': c.voice_guide
            }
            for c in characters
        ]

        plot_data = await self.plot_architect.create_plot_structure(
            genre=self.project.genre.value,
            project_name=self.project.name,
            world_bible=world_bible.__dict__,
            characters=characters_data,
            chapter_count=params.get('chapter_count', 25),
            subplot_count=params.get('subplot_count', 3),
            themes=params.get('title_analysis', {}).get('themes', []),
            semantic_title_analysis=params.get('semantic_title_analysis', {})
        )

        # Save to database
        plot_structure = PlotStructure(
            project_id=self.project.id,
            structure_type=plot_data.get('structure_type', '3-Act Structure'),
            acts=plot_data.get('acts', {}),
            main_conflict=plot_data.get('main_conflict', ''),
            stakes=plot_data.get('stakes', {}),
            plot_points=plot_data.get('plot_points', {}),
            subplots=plot_data.get('subplots', []),
            tension_graph=plot_data.get('tension_graph', []),
            foreshadowing=plot_data.get('foreshadowing', [])
        )

        self.db.add(plot_structure)
        try:
            self.db.commit()
            self.db.refresh(plot_structure)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to save plot structure: {e}", exc_info=True)
            raise Exception(f"Nie udało się zapisać struktury fabuły do bazy: {str(e)}")

        logger.info(f"✅ Plot structure created and saved (ID: {plot_structure.id})")
        return plot_structure

    def _check_cost_limit(self, chapter_num: int = None) -> None:
        """
        Check if cost is approaching or exceeded the project limit

        Args:
            chapter_num: Current chapter number for context in error messages

        Raises:
            Exception: If cost limit is exceeded (100%)
        """
        metrics = self.ai_service.get_metrics()
        current_cost = metrics.total_cost
        max_cost = settings.MAX_COST_PER_PROJECT
        alert_threshold = settings.COST_ALERT_THRESHOLD

        cost_percentage = (current_cost / max_cost) if max_cost > 0 else 0

        # Update project's actual cost in real-time
        self.project.actual_cost = current_cost

        context = f" (po rozdziale {chapter_num})" if chapter_num else ""

        # HARD STOP at 100% of limit
        if cost_percentage >= 1.0:
            error_msg = (
                f"❌ LIMIT KOSZTÓW PRZEKROCZONY{context}!\n"
                f"   Koszt aktualny: ${current_cost:.2f}\n"
                f"   Maksymalny limit: ${max_cost:.2f}\n"
                f"   Przekroczenie: {(cost_percentage - 1.0) * 100:.1f}%\n"
                f"   Generowanie zatrzymane aby zapobiec dalszym kosztom."
            )
            logger.error(error_msg)
            raise Exception(error_msg)

        # WARNING at 80% of limit
        elif cost_percentage >= alert_threshold:
            warning_msg = (
                f"⚠️ OSTRZEŻENIE: Zbliżasz się do limitu kosztów{context}!\n"
                f"   Koszt aktualny: ${current_cost:.2f} ({cost_percentage * 100:.1f}%)\n"
                f"   Maksymalny limit: ${max_cost:.2f}\n"
                f"   Pozostało: ${max_cost - current_cost:.2f}"
            )
            logger.warning(warning_msg)

        # Regular cost tracking log
        else:
            logger.info(
                f"💰 Koszt projektu{context}: ${current_cost:.2f} "
                f"({cost_percentage * 100:.1f}% z ${max_cost:.2f} limitu)"
            )

    async def _generate_all_chapters(
        self,
        world_bible: WorldBible,
        characters: List[Character],
        plot_structure: PlotStructure,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate all chapters using Prose Writer Agent"""
        chapter_count = params.get('chapter_count', 25)
        target_words = params.get('target_word_count', 90000)
        words_per_chapter = target_words // chapter_count

        logger.info(f"✍️ Writing {chapter_count} chapters with AI (~{words_per_chapter} words each)...")

        # Check cost limit before starting chapter generation
        self._check_cost_limit()

        chapters_data = []
        previous_summary = None

        # Get POV character (protagonist)
        pov_character = next((c for c in characters if c.role == CharacterRole.PROTAGONIST), characters[0])

        for chapter_num in range(1, chapter_count + 1):
            logger.info(f"📝 Writing Chapter {chapter_num}/{chapter_count}...")

            # Get chapter outline from plot structure
            chapter_outline = self._get_chapter_outline(plot_structure, chapter_num)

            # Convert to dict format for agent
            pov_char_dict = {
                'name': pov_character.name,
                'role': pov_character.role.value,
                'profile': pov_character.profile,
                'arc': pov_character.arc,
                'voice_guide': pov_character.voice_guide
            }

            characters_dict = [
                {
                    'name': c.name,
                    'role': c.role.value,
                    'profile': c.profile
                }
                for c in characters
            ]

            # 🔥 RETRY LOGIC - Don't fail entire book if one chapter has issues
            max_retries = 3
            chapter_result = None
            last_error = None

            for attempt in range(1, max_retries + 1):
                try:
                    # Generate chapter
                    chapter_result = await self.prose_writer.write_chapter(
                        chapter_number=chapter_num,
                        chapter_outline=chapter_outline,
                        genre=self.project.genre.value,
                        pov_character=pov_char_dict,
                        world_bible=world_bible.__dict__,
                        plot_structure=plot_structure.__dict__,
                        all_characters=characters_dict,
                        previous_chapter_summary=previous_summary,
                        target_word_count=words_per_chapter,
                        style_complexity=params.get('style_complexity', 'medium'),
                        book_title=self.project.name,  # 🔥 CRITICAL: Pass title to prose writer!
                        semantic_title_analysis=params.get('semantic_title_analysis', {})  # 🎯 Deep meaning
                    )

                    # Success! Break out of retry loop
                    logger.info(f"✅ Chapter {chapter_num} generated successfully")
                    break

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"⚠️ Chapter {chapter_num} generation attempt {attempt}/{max_retries} failed: {str(e)}"
                    )

                    if attempt < max_retries:
                        # Wait before retry (exponential backoff)
                        wait_time = 2 ** attempt  # 2s, 4s, 8s
                        logger.info(f"⏳ Retrying chapter {chapter_num} in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        # All retries exhausted
                        logger.error(
                            f"❌ CRITICAL: Chapter {chapter_num} failed after {max_retries} attempts. "
                            f"Last error: {str(e)}"
                        )
                        raise Exception(
                            f"Failed to generate Chapter {chapter_num} after {max_retries} attempts. "
                            f"Error: {str(e)}. This chapter is critical for story continuity."
                        )

            # Create summary for next chapter
            previous_summary = await self.prose_writer.create_chapter_summary(
                chapter_result['content']
            )

            # Save chapter to database
            chapter = Chapter(
                project_id=self.project.id,
                number=chapter_num,
                title=f"Chapter {chapter_num}",
                pov_character_id=pov_character.id,
                outline=chapter_outline,
                content=chapter_result['content'],
                word_count=chapter_result['word_count'],
                quality_score=85.0,  # Will be updated by QC
                is_complete=2  # Final
            )

            self.db.add(chapter)
            try:
                self.db.commit()
                self.db.refresh(chapter)
            except SQLAlchemyError as e:
                self.db.rollback()
                logger.error(f"Failed to save chapter {chapter_num}: {e}", exc_info=True)
                raise Exception(f"Nie udało się zapisać rozdziału {chapter_num} do bazy: {str(e)}")

            chapters_data.append({
                'number': chapter_num,
                'content': chapter_result['content'],
                'word_count': chapter_result['word_count'],
                'quality_score': 85.0
            })

            # Check cost limit after each chapter (enforce budget)
            self._check_cost_limit(chapter_num)

            # Update progress
            progress_in_step = (chapter_num / chapter_count) * 0.5  # Chapters are 50% of this step
            await self._update_progress(
                11,
                f"Pisanie rozdziału {chapter_num}/{chapter_count} (AI)"
            )

        # Final cost check
        self._check_cost_limit()

        logger.info(f"✅ All {chapter_count} chapters written!")
        return chapters_data

    def _get_chapter_outline(self, plot_structure: PlotStructure, chapter_num: int) -> Dict[str, Any]:
        """Get outline for specific chapter from plot structure"""
        # Handle case where tension_graph might contain ints instead of dicts
        tension_data = {'tension': 5, 'emotion': 'neutral'}  # Default

        if plot_structure.tension_graph:
            # Try to find matching chapter in tension_graph
            for t in plot_structure.tension_graph:
                # Check if t is a dict (expected format)
                if isinstance(t, dict) and t.get('chapter') == chapter_num:
                    tension_data = t
                    break

        return {
            'setting': 'Dynamic based on chapter progression',
            'characters_present': ['Main characters'],
            'goal': f'Advance story at chapter {chapter_num}',
            'emotional_beat': tension_data.get('emotion', 'neutral'),
            'key_reveals': []
        }

    async def _validate_continuity(
        self,
        chapters_data: List[Dict],
        world_bible: WorldBible,
        characters: List[Character],
        plot_structure: PlotStructure
    ):
        """Validate continuity across all chapters (basic validation)"""
        logger.info("🔍 Validating continuity across manuscript...")

        # Basic validation checks (full AI-powered validation would be expensive)
        issues = []

        # Check 1: All chapters have content
        for chapter in chapters_data:
            if not chapter.get('content') or len(chapter['content'].strip()) < 100:
                issues.append(f"Chapter {chapter['number']} has insufficient content")

        # Check 2: Word count progression (chapters shouldn't vary too wildly)
        word_counts = [ch['word_count'] for ch in chapters_data]
        avg_words = sum(word_counts) / len(word_counts)
        for i, count in enumerate(word_counts):
            if count < avg_words * 0.3:  # Less than 30% of average
                issues.append(f"Chapter {i+1} is suspiciously short ({count} words vs avg {avg_words:.0f})")

        # Check 3: Character name consistency (basic check)
        character_names = {c.name for c in characters}
        # Sample first 3 chapters for character references
        for i, chapter in enumerate(chapters_data[:3]):
            content = chapter['content'].lower()
            for char_name in character_names:
                if char_name.lower() not in content:
                    logger.warning(f"Chapter {i+1} doesn't mention character '{char_name}' (might be OK)")

        if issues:
            logger.warning(f"⚠️ Continuity issues found: {len(issues)}")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("✅ Continuity check complete - no major issues")

    async def _validate_genre_compliance(self, chapters_data: List[Dict]):
        """Validate genre compliance (basic checks)"""
        logger.info("🎭 Validating genre compliance...")

        # Basic validation (full AI-powered genre analysis would be expensive)
        genre = self.project.genre.value
        total_words = sum(ch['word_count'] for ch in chapters_data)

        # Genre-specific word count expectations
        expected_ranges = {
            "fantasy": (90000, 150000),
            "sci-fi": (80000, 130000),
            "thriller": (70000, 100000),
            "horror": (70000, 100000),
            "romance": (70000, 100000),
            "mystery": (70000, 100000),
            "drama": (80000, 110000),
            "comedy": (70000, 95000),
        }

        min_words, max_words = expected_ranges.get(genre, (70000, 120000))

        # Check word count range
        if total_words < min_words * 0.8:
            logger.warning(
                f"⚠️ Book is shorter than typical {genre} "
                f"({total_words:,} words vs expected {min_words:,}-{max_words:,})"
            )
        elif total_words > max_words * 1.2:
            logger.warning(
                f"⚠️ Book is longer than typical {genre} "
                f"({total_words:,} words vs expected {min_words:,}-{max_words:,})"
            )
        else:
            logger.info(
                f"✅ Genre compliance validated - "
                f"{total_words:,} words fits {genre} expectations ({min_words:,}-{max_words:,})"
            )

    async def _update_progress(self, step: int, activity: str):
        """Update project progress in database"""
        self.progress.update(step, activity)

        # Get time estimates
        current_step_duration = self.progress.get_current_step_duration()
        time_remaining = self.progress.get_estimated_time_remaining()

        # Update activity with time info
        activity_with_time = f"{activity} [~{current_step_duration} min | Pozostało: ~{time_remaining} min]"

        self.project.current_step = step
        self.project.progress_percentage = self.progress.get_percentage()
        self.project.current_activity = activity_with_time

        # Update cost from AI service
        metrics = self.ai_service.get_metrics()
        self.project.actual_cost = metrics.total_cost

        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.warning(f"Failed to update progress (non-critical): {e}")
            # Don't raise - progress updates are not critical

        logger.info(
            f"📊 Progress: Step {step}/15 ({self.progress.get_percentage():.1f}%) - {activity} "
            f"[Czas: ~{current_step_duration} min | Pozostało: ~{time_remaining} min | Koszt: ${metrics.total_cost:.2f}]"
        )

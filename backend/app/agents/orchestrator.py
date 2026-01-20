"""
Main Orchestrator - the brain of NarraForge.
Coordinates all agents and manages the book generation pipeline.
"""
from typing import Optional
from datetime import datetime
import logging

from app.agents.world_agent import WorldAgent
from app.agents.character_agent import CharacterAgent
from app.agents.plot_agent import PlotAgent
from app.agents.prose_agent import ProseAgent
from app.agents.consistency import ConsistencyGuardian
from app.agents.director_agent import DirectorAgent
from app.agents.publisher_agent import PublisherAgent
from app.core.cost_optimizer import CostOptimizer
from app.core.cost_tracker import CostTracker
from app.core.progress_tracker import ProgressTracker
from app.api.websockets import ws_manager
from app.models.book import Book, BookStatus

logger = logging.getLogger(__name__)


class MainOrchestrator:
    """
    Main Orchestrator - Centralny Mózg NarraForge.
    Koordynuje wszystkich agentów i zarządza procesem generowania.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id

        # Initialize agents
        self.world_agent = WorldAgent()
        self.character_agent = CharacterAgent()
        self.plot_agent = PlotAgent()
        self.prose_agent = ProseAgent()
        self.consistency_guardian = ConsistencyGuardian()
        self.director_agent = DirectorAgent()
        self.publisher_agent = PublisherAgent()

        # Initialize support systems
        self.cost_optimizer = CostOptimizer()
        self.cost_tracker = CostTracker()
        self.progress_tracker = ProgressTracker()

    async def generate_book(self, book: Book) -> Book:
        """
        Main book generation pipeline.

        Pipeline:
        1. Create world (5%)
        2. Create characters (10%)
        3. Create plot (15%)
        4. Write chapters (70%)
        5. Polish chapters (80-95%)
        6. Finalize (95-100%)

        Args:
            book: Book model to generate

        Returns:
            Complete book with all content
        """
        try:
            logger.info(f"Starting book generation: {book.id} - genre: {book.genre}")

            # Update status
            book.status = BookStatus.GENERATING

            # ============================
            # PHASE 1: CONCEPT (15%)
            # ============================
            await self._notify_phase("concept", "Tworzenie koncepcji...", 0)

            # 1.1 Create World
            await self._notify_agent("world", "working", "Architekt Świata buduje uniwersum...")
            world_data = await self.world_agent.create_world(
                genre=book.genre.value,
                cost_optimizer=self.cost_optimizer,
                cost_tracker=self.cost_tracker,
            )
            book.world = self._world_dict_to_model(world_data, book.id)
            await self._notify_progress(5)
            await self._notify_agent("world", "completed", f"Świat '{world_data.get('name')}' gotowy")

            # 1.2 Create Characters
            await self._notify_agent("character", "working", "Kreator Dusz ożywia bohaterów...")
            characters_data = await self.character_agent.create_characters(
                genre=book.genre.value,
                world=world_data,
                cost_optimizer=self.cost_optimizer,
                cost_tracker=self.cost_tracker,
            )
            book.characters = [
                self._character_dict_to_model(c, book.id) for c in characters_data
            ]
            await self._notify_progress(10)
            await self._notify_agent(
                "character", "completed", f"Stworzono {len(characters_data)} postaci"
            )

            # 1.3 Create Plot
            await self._notify_agent("plot", "working", "Mistrz Fabuły snuje intrygę...")
            plot_data = await self.plot_agent.create_plot(
                genre=book.genre.value,
                world=world_data,
                characters=characters_data,
                cost_optimizer=self.cost_optimizer,
                cost_tracker=self.cost_tracker,
            )
            book.plot = self._plot_dict_to_model(plot_data, book.id)
            total_chapters = len(plot_data.get('chapters', []))
            await self._notify_progress(15)
            await self._notify_agent(
                "plot", "completed", f"Fabuła z {total_chapters} rozdziałami gotowa"
            )

            # ============================
            # PHASE 2: WRITING (70%)
            # ============================
            await self._notify_phase("writing", "Pisanie rozdziałów...", 15)

            chapters_written = []
            chapter_outlines = plot_data.get('chapters', [])

            for i, chapter_outline in enumerate(chapter_outlines):
                chapter_num = i + 1

                # 2.1 Write Chapter
                await self._notify_agent(
                    "prose", "working", f"Mistrz Słowa pisze rozdział {chapter_num}..."
                )

                chapter_outline['total_chapters'] = total_chapters
                chapter_data = await self.prose_agent.write_chapter(
                    chapter_outline=chapter_outline,
                    genre=book.genre.value,
                    world=world_data,
                    characters=characters_data,
                    previous_chapters=chapters_written,
                    cost_optimizer=self.cost_optimizer,
                    cost_tracker=self.cost_tracker,
                )

                # 2.2 Verify Consistency
                await self._notify_agent(
                    "consistency", "working", "Strażnik Spójności weryfikuje..."
                )

                consistency_result = await self.consistency_guardian.verify(
                    new_chapter=chapter_data,
                    world=world_data,
                    characters=characters_data,
                    previous_chapters=chapters_written,
                    cost_optimizer=self.cost_optimizer,
                    cost_tracker=self.cost_tracker,
                )

                # 2.3 Repair if needed
                if not consistency_result.is_consistent:
                    await self._notify_agent(
                        "consistency", "repairing",
                        f"Znaleziono {len(consistency_result.issues)} problemów, naprawiam..."
                    )

                    chapter_data = await self.prose_agent.repair_chapter(
                        chapter=chapter_data,
                        issues=consistency_result.issues,
                        world=world_data,
                        characters=characters_data,
                        cost_optimizer=self.cost_optimizer,
                        cost_tracker=self.cost_tracker,
                    )

                chapters_written.append(chapter_data)

                # Update progress
                chapter_progress = 15 + (55 * chapter_num / total_chapters)
                await self._notify_progress(chapter_progress)

                # Send chapter preview
                await ws_manager.send_chapter_preview(
                    self.session_id,
                    chapter_num,
                    chapter_data.get('content', '')[:500]
                )

                await self._notify_agent("prose", "completed", f"Rozdział {chapter_num} gotowy")

            book.chapters = [
                self._chapter_dict_to_model(c, book.id) for c in chapters_written
            ]

            # ============================
            # PHASE 3: POLISH (10%)
            # ============================
            await self._notify_phase("polishing", "Szlify reżyserskie...", 70)

            await self._notify_agent("director", "working", "Reżyser literacki poleruje dzieło...")

            polished_chapters = await self.director_agent.polish_book(
                chapters=chapters_written,
                genre=book.genre.value,
                cost_optimizer=self.cost_optimizer,
                cost_tracker=self.cost_tracker,
            )
            book.chapters = [
                self._chapter_dict_to_model(c, book.id) for c in polished_chapters
            ]

            await self._notify_progress(80)
            await self._notify_agent("director", "completed", "Szlify zakończone")

            # ============================
            # PHASE 4: PUBLISHING (5%)
            # ============================
            await self._notify_phase("publishing", "Przygotowanie do publikacji...", 80)

            await self._notify_agent("publisher", "working", "Agent wydawniczy finalizuje...")

            final_book = await self.publisher_agent.finalize(
                book=book,
                cost_optimizer=self.cost_optimizer,
                cost_tracker=self.cost_tracker,
            )

            await self._notify_progress(95)
            await self._notify_agent("publisher", "completed", "Książka gotowa!")

            # ============================
            # PHASE 5: FINALIZE
            # ============================
            await self._notify_phase("saving", "Zapisywanie...", 95)

            final_book.status = BookStatus.COMPLETED
            final_book.completed_at = datetime.utcnow()
            final_book.cost_total = self.cost_tracker.total_cost
            final_book.cost_breakdown = self.cost_tracker.cost_breakdown

            await self._notify_progress(100)
            await ws_manager.send_completion(self.session_id, str(final_book.id))

            logger.info(
                f"Book generation complete: {final_book.id} - "
                f"'{final_book.title}' - ${final_book.cost_total:.4f}"
            )

            return final_book

        except Exception as e:
            logger.error(f"Book generation failed: {e}", exc_info=True)
            book.status = BookStatus.FAILED
            await self._notify_error(str(e))
            raise

    async def _notify_phase(self, phase: str, message: str, progress: float):
        """Notify about phase change."""
        self.progress_tracker.update(phase=phase, message=message, progress=progress)
        await ws_manager.send_progress(self.session_id, {
            "phase": phase,
            "message": message,
            "progress": progress,
        })

    async def _notify_progress(self, progress: float):
        """Notify about progress."""
        self.progress_tracker.update(progress=progress)
        await ws_manager.send_progress(self.session_id, {"progress": progress})

        # Send cost update
        await ws_manager.send_cost_update(self.session_id, {
            "total": self.cost_tracker.total_cost,
            "breakdown": self.cost_tracker.cost_breakdown,
        })

    async def _notify_agent(self, agent: str, status: str, details: str):
        """Notify about agent status."""
        await ws_manager.send_agent_status(
            self.session_id, agent, status, {"message": details}
        )

    async def _notify_error(self, error: str):
        """Notify about error."""
        await ws_manager.send_progress(self.session_id, {
            "error": error,
            "progress": -1,
        })

    def _world_dict_to_model(self, world_data: dict, book_id) -> object:
        """Convert world dict to model (simplified)."""
        from app.models.book import World
        return World(
            book_id=book_id,
            name=world_data.get('name', 'Unknown'),
            description=world_data.get('description', ''),
            geography=world_data.get('geography', {}),
            history=world_data.get('history', {}),
            rules=world_data.get('rules', {}),
            societies=world_data.get('societies', {}),
            details=world_data.get('details', {}),
        )

    def _character_dict_to_model(self, char_data: dict, book_id) -> object:
        """Convert character dict to model (simplified)."""
        from app.models.book import Character
        return Character(
            book_id=book_id,
            name=char_data.get('name', 'Unknown'),
            full_name=char_data.get('full_name', ''),
            role=char_data.get('role', ''),
            appearance=char_data.get('appearance', {}),
            personality=char_data.get('personality', {}),
            backstory=char_data.get('backstory', {}),
            motivations=char_data.get('motivations', {}),
            voice=char_data.get('voice', {}),
            arc=char_data.get('arc', {}),
        )

    def _plot_dict_to_model(self, plot_data: dict, book_id) -> object:
        """Convert plot dict to model (simplified)."""
        from app.models.book import Plot
        return Plot(
            book_id=book_id,
            structure_type=plot_data.get('structure_type', ''),
            theme=plot_data.get('theme', ''),
            hook=plot_data.get('hook', ''),
            inciting_incident=plot_data.get('inciting_incident', ''),
            midpoint=plot_data.get('midpoint', ''),
            climax=plot_data.get('climax', ''),
            resolution=plot_data.get('resolution', ''),
            subplots=plot_data.get('subplots', []),
        )

    def _chapter_dict_to_model(self, chapter_data: dict, book_id) -> object:
        """Convert chapter dict to model (simplified)."""
        from app.models.book import Chapter
        return Chapter(
            book_id=book_id,
            number=chapter_data.get('number', 1),
            title=chapter_data.get('title', ''),
            content=chapter_data.get('content', ''),
            word_count=chapter_data.get('word_count', 0),
            outline_goal=chapter_data.get('outline_goal', ''),
            outline_summary=chapter_data.get('outline_summary', ''),
            location=chapter_data.get('location', ''),
            pov_character_id=None,
        )

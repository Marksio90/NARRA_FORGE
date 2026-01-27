"""
Series management service for multi-book sagas

Handles:
- Series creation and planning
- Continuity tracking across books
- Character arc management
- Plot thread tracking
- Next book generation with full context
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from app.models.series import Series, SeriesCharacterArc, SeriesPlotThread
from app.models.project import Project
from app.models.world_bible import WorldBible
from app.models.character import Character
from app.agents.model_tier_manager import model_tier_manager

logger = logging.getLogger(__name__)


class SeriesService:
    """Service for managing book series"""

    def __init__(self):
        self.model_manager = model_tier_manager

    async def create_series(
        self,
        db: Session,
        user_id: int,
        name: str,
        genre: str,
        planned_books: int = 3,
        description: Optional[str] = None,
        language: str = "polski"
    ) -> Series:
        """
        Create a new series with AI-generated series arc.

        Args:
            db: Database session
            user_id: Owner user ID
            name: Series name
            genre: Genre of the series
            planned_books: Number of planned books
            description: Optional description/premise
            language: Language for generation

        Returns:
            Created Series object
        """
        logger.info(f"Creating series '{name}' with {planned_books} planned books")

        # Create shared world bible for the series
        world_bible = WorldBible(
            name=f"{name} - Shared Universe",
        )
        db.add(world_bible)
        db.flush()

        # Generate series arc using AI
        series_arc = await self._plan_series_arc(
            name=name,
            genre=genre,
            num_books=planned_books,
            description=description,
            language=language
        )

        # Create series
        series = Series(
            user_id=user_id,
            name=name,
            description=description,
            genre=genre,
            language=language,
            planned_books=planned_books,
            shared_world_bible_id=world_bible.id,
            series_arc=series_arc
        )

        db.add(series)
        db.commit()
        db.refresh(series)

        logger.info(f"Created series {series.id}: {series.name}")
        return series

    async def _plan_series_arc(
        self,
        name: str,
        genre: str,
        num_books: int,
        description: Optional[str],
        language: str = "polski"
    ) -> str:
        """Generate overarching series arc using AI"""

        if language == "polski":
            prompt = f"""Zaplanuj arc fabularny dla {num_books}-tomowej serii {genre} zatytulowanej "{name}".

Opis/premisa: {description or "Stworz angażującą serię"}

Stworz MAKRO-ARC obejmujący wszystkie {num_books} ksiazek:

1. **GLOWNY KONFLIKT**: Jaki jest centralny konflikt/pytanie CALEJ serii?
2. **ESKALACJA**: Jak konflikt eskaluje przez kolejne tomy?
3. **ARC KAZDEGO TOMU**: Jaki jest glowny fokus/rozwiazanie kazdej ksiazki?
4. **ELEMENTY POWTARZAJACE SIE**: Jakie motywy/postacie/tajemnice sie powtarzaja?
5. **KULMINACJA SERII**: Jak wszystko laczy sie w finalowym tomie?

Format odpowiedzi:
```
GLOWNY KONFLIKT: [jeden akapit]

TOM 1: [pomysl na tytul] - [glowny arc]
- Fokus: [co ta ksiazka osiaga]
- Konczy sie: [cliffhanger/setup dla Tomu 2]

TOM 2: [pomysl na tytul] - [glowny arc]
- Fokus: [co ta ksiazka osiaga]
- Konczy sie: [cliffhanger/setup dla Tomu 3]

...

KULMINACJA SERII: [jak sie rozwiazuje]
```"""
        else:
            prompt = f"""Plan the story arc for a {num_books}-book {genre} series titled "{name}".

Description/premise: {description or "Create an engaging series"}

Create a MACRO-ARC spanning all {num_books} books:

1. **MAIN CONFLICT**: What is the core conflict/question of the ENTIRE series?
2. **ESCALATION**: How does the conflict escalate across books?
3. **PER-BOOK ARCS**: What is the main focus/resolution of each book?
4. **RECURRING ELEMENTS**: What themes/characters/mysteries recur?
5. **SERIES CLIMAX**: How does it all come together in the final book?

Format:
```
MAIN CONFLICT: [one paragraph]

BOOK 1: [title idea] - [main arc]
- Focus: [what this book accomplishes]
- Ends with: [cliffhanger/setup for Book 2]

BOOK 2: [title idea] - [main arc]
- Focus: [what this book accomplishes]
- Ends with: [cliffhanger/setup for Book 3]

...

SERIES CLIMAX: [how it resolves]
```"""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are an expert series planner specializing in multi-book story arcs.",
            task_type="plot_structure",
            temperature=0.8,
            max_tokens=2000
        )

        return result.get("content", "") if result.get("success") else ""

    async def prepare_next_book(
        self,
        db: Session,
        series_id: int,
        user_id: int
    ) -> Project:
        """
        Prepare the next book in series with full continuity context.

        Args:
            db: Database session
            series_id: Series ID
            user_id: User ID

        Returns:
            Created Project for the next book

        Raises:
            ValueError: If series not ready for next book
        """
        series = db.query(Series).filter(Series.id == series_id).first()
        if not series:
            raise ValueError("Series not found")

        if series.user_id != user_id:
            raise ValueError("Not authorized to access this series")

        if not series.is_ready_for_next_book():
            raise ValueError("Series is not ready for next book")

        next_book_number = series.get_next_book_number()
        logger.info(f"Preparing book {next_book_number} for series {series_id}")

        # Load context from previous books
        previous_books = db.query(Project).filter(
            and_(
                Project.series_id == series_id,
                Project.book_number_in_series < next_book_number
            )
        ).order_by(Project.book_number_in_series).all()

        # Build continuity context
        continuity_context = await self._build_continuity_context(
            db=db,
            series=series,
            previous_books=previous_books
        )

        # Generate book title
        book_title = await self._generate_series_book_title(
            series=series,
            book_number=next_book_number,
            continuity_context=continuity_context
        )

        # Create project
        project = Project(
            user_id=user_id,
            series_id=series_id,
            book_number_in_series=next_book_number,
            name=book_title,
            genre=series.genre,
            # Share world bible
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        logger.info(f"Created project {project.id} for book {next_book_number} in series {series_id}")
        return project

    async def _build_continuity_context(
        self,
        db: Session,
        series: Series,
        previous_books: List[Project]
    ) -> Dict[str, Any]:
        """Build comprehensive context from previous books"""

        context = {
            "series_arc": series.series_arc,
            "completed_books": series.completed_books,
            "previous_book_summaries": [],
            "recurring_characters": [],
            "character_states": [],
            "unresolved_plot_threads": [],
            "resolved_plot_threads": [],
            "world_elements": series.shared_elements or {},
            "timeline": series.timeline or [],
        }

        # Get summaries of previous books
        for book in previous_books:
            if book.plot_structure:
                # Get plot structure data
                plot_data = {}
                if hasattr(book.plot_structure, 'main_conflict'):
                    plot_data['main_conflict'] = book.plot_structure.main_conflict

                context["previous_book_summaries"].append({
                    "book_number": book.book_number_in_series,
                    "title": book.name,
                    "plot_data": plot_data
                })

        # Get character arcs
        character_arcs = db.query(SeriesCharacterArc).filter(
            SeriesCharacterArc.series_id == series.id
        ).all()

        for arc in character_arcs:
            context["character_states"].append({
                "name": arc.character_name,
                "current_state": arc.current_state,
                "is_alive": arc.is_alive,
                "last_seen_book": arc.last_appearance_book,
                "key_moments": arc.key_moments or [],
                "relationships": arc.relationships or {}
            })

        # Get unresolved plot threads
        unresolved = db.query(SeriesPlotThread).filter(
            and_(
                SeriesPlotThread.series_id == series.id,
                SeriesPlotThread.is_resolved == False
            )
        ).all()

        for thread in unresolved:
            context["unresolved_plot_threads"].append({
                "name": thread.name,
                "description": thread.description,
                "introduced_in": thread.introduced_in_book,
                "is_main_plot": thread.is_main_plot,
                "key_events": thread.key_events or [],
                "foreshadowing": thread.foreshadowing or []
            })

        # Get resolved plot threads (for reference)
        resolved = db.query(SeriesPlotThread).filter(
            and_(
                SeriesPlotThread.series_id == series.id,
                SeriesPlotThread.is_resolved == True
            )
        ).all()

        for thread in resolved:
            context["resolved_plot_threads"].append({
                "name": thread.name,
                "introduced_in": thread.introduced_in_book,
                "resolved_in": thread.resolved_in_book
            })

        return context

    async def _generate_series_book_title(
        self,
        series: Series,
        book_number: int,
        continuity_context: Dict[str, Any]
    ) -> str:
        """Generate title for book in series"""

        previous_titles = [
            b["title"] for b in continuity_context.get("previous_book_summaries", [])
        ]

        if series.language == "polski":
            prompt = f"""Wygeneruj tytul dla Tomu {book_number} serii "{series.name}".

Arc serii:
{series.series_arc[:500] if series.series_arc else "Brak"}

Poprzednie tytuly:
{chr(10).join(previous_titles) if previous_titles else "Brak (to pierwszy tom)"}

Wymagania:
- Pasuje do konwencji nazewnictwa serii
- Sugeruje fokus tego tomu
- Brzmi jak czesc serii
- Jest chwytliwy i zapamietywalny

Wygeneruj 5 opcji tytulow, a nastepnie wybierz najlepszy.

FORMAT:
1. [tytul]
2. [tytul]
3. [tytul]
4. [tytul]
5. [tytul]

NAJLEPSZY: [wybrany tytul]"""
        else:
            prompt = f"""Generate title for Book {book_number} in the "{series.name}" series.

Series Arc:
{series.series_arc[:500] if series.series_arc else "None"}

Previous Titles:
{chr(10).join(previous_titles) if previous_titles else "None (this is book 1)"}

Requirements:
- Fits the series naming convention
- Hints at this book's focus
- Sounds like part of a series
- Is compelling and memorable

Generate 5 title options, then select the best one.

FORMAT:
1. [title]
2. [title]
3. [title]
4. [title]
5. [title]

BEST: [selected title]"""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are an expert book title generator.",
            task_type="metadata",
            temperature=0.9,
            max_tokens=500
        )

        if result.get("success"):
            content = result["content"]
            # Extract best title
            if "NAJLEPSZY:" in content:
                title = content.split("NAJLEPSZY:")[1].strip().split('\n')[0]
                return title.strip()
            elif "BEST:" in content:
                title = content.split("BEST:")[1].strip().split('\n')[0]
                return title.strip()

        # Fallback
        return f"{series.name} - Tom {book_number}"

    def add_character_to_series(
        self,
        db: Session,
        series_id: int,
        character_name: str,
        first_book: int,
        starting_state: str = "",
        target_end_state: str = ""
    ) -> SeriesCharacterArc:
        """Add a recurring character to track across the series"""

        arc = SeriesCharacterArc(
            series_id=series_id,
            character_name=character_name,
            first_appearance_book=first_book,
            starting_state=starting_state,
            current_state=starting_state,
            target_end_state=target_end_state
        )

        db.add(arc)
        db.commit()
        db.refresh(arc)

        # Also update series JSONB
        series = db.query(Series).filter(Series.id == series_id).first()
        if series:
            series.add_recurring_character(character_name, first_book, starting_state)
            db.commit()

        return arc

    def add_plot_thread(
        self,
        db: Session,
        series_id: int,
        name: str,
        introduced_book: int,
        description: str = "",
        is_main_plot: bool = False,
        introduced_chapter: Optional[int] = None
    ) -> SeriesPlotThread:
        """Add a plot thread to track across the series"""

        thread = SeriesPlotThread(
            series_id=series_id,
            name=name,
            description=description,
            introduced_in_book=introduced_book,
            introduced_in_chapter=introduced_chapter,
            is_main_plot=is_main_plot
        )

        db.add(thread)
        db.commit()
        db.refresh(thread)

        # Also update series JSONB
        series = db.query(Series).filter(Series.id == series_id).first()
        if series:
            series.add_plot_thread(name, introduced_book, description)
            db.commit()

        return thread

    def update_character_state(
        self,
        db: Session,
        arc_id: int,
        new_state: str,
        book_number: int,
        key_moment: Optional[str] = None,
        chapter: Optional[int] = None
    ) -> SeriesCharacterArc:
        """Update a character's state after events in a book"""

        arc = db.query(SeriesCharacterArc).filter(
            SeriesCharacterArc.id == arc_id
        ).first()

        if not arc:
            raise ValueError("Character arc not found")

        arc.current_state = new_state
        arc.last_appearance_book = book_number

        if key_moment:
            arc.add_key_moment(book_number, chapter or 0, key_moment)

        db.commit()
        db.refresh(arc)
        return arc

    def resolve_plot_thread(
        self,
        db: Session,
        thread_id: int,
        resolved_book: int,
        resolved_chapter: Optional[int] = None
    ) -> SeriesPlotThread:
        """Mark a plot thread as resolved"""

        thread = db.query(SeriesPlotThread).filter(
            SeriesPlotThread.id == thread_id
        ).first()

        if not thread:
            raise ValueError("Plot thread not found")

        thread.resolve(resolved_book, resolved_chapter or 0)
        db.commit()
        db.refresh(thread)

        # Also update series JSONB
        series = db.query(Series).filter(Series.id == thread.series_id).first()
        if series:
            series.resolve_plot_thread(thread.name, resolved_book)
            db.commit()

        return thread

    async def validate_series_consistency(
        self,
        db: Session,
        series_id: int
    ) -> List[Dict[str, Any]]:
        """
        Validate consistency across the series.
        Returns list of potential issues found.
        """
        series = db.query(Series).filter(Series.id == series_id).first()
        if not series:
            raise ValueError("Series not found")

        issues = []

        # Get all books
        books = db.query(Project).filter(
            Project.series_id == series_id
        ).order_by(Project.book_number_in_series).all()

        if len(books) < 2:
            return []  # Need at least 2 books to check

        # Check for dead characters appearing later
        character_arcs = db.query(SeriesCharacterArc).filter(
            SeriesCharacterArc.series_id == series_id
        ).all()

        for arc in character_arcs:
            if not arc.is_alive and arc.death_book:
                if arc.last_appearance_book and arc.last_appearance_book > arc.death_book:
                    issues.append({
                        "type": "dead_character_appears",
                        "severity": "high",
                        "character": arc.character_name,
                        "died_in_book": arc.death_book,
                        "appeared_in_book": arc.last_appearance_book,
                        "message": f"Character '{arc.character_name}' died in book {arc.death_book} but appeared in book {arc.last_appearance_book}"
                    })

        # Check for unresolved main plot threads in completed series
        if series.is_complete:
            unresolved = db.query(SeriesPlotThread).filter(
                and_(
                    SeriesPlotThread.series_id == series_id,
                    SeriesPlotThread.is_resolved == False,
                    SeriesPlotThread.is_main_plot == True
                )
            ).all()

            for thread in unresolved:
                issues.append({
                    "type": "unresolved_main_plot",
                    "severity": "high",
                    "thread": thread.name,
                    "introduced_in": thread.introduced_in_book,
                    "message": f"Main plot thread '{thread.name}' from book {thread.introduced_in_book} was never resolved"
                })

        # Check timeline consistency
        if series.timeline:
            # Basic timeline check
            for i, entry in enumerate(series.timeline[:-1]):
                if i + 1 < len(series.timeline):
                    next_entry = series.timeline[i + 1]
                    # This is a simplified check - real implementation would be more sophisticated
                    pass

        return issues

    def mark_book_completed(
        self,
        db: Session,
        series_id: int,
        project_id: int
    ) -> Series:
        """Mark a book as completed and update series status"""

        series = db.query(Series).filter(Series.id == series_id).first()
        if not series:
            raise ValueError("Series not found")

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or project.series_id != series_id:
            raise ValueError("Project not found or not part of this series")

        series.mark_book_completed()
        db.commit()
        db.refresh(series)

        logger.info(f"Series {series_id} now has {series.completed_books}/{series.planned_books} books")
        return series

    def get_series_summary(
        self,
        db: Session,
        series_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive series summary"""

        series = db.query(Series).filter(Series.id == series_id).first()
        if not series:
            raise ValueError("Series not found")

        books = db.query(Project).filter(
            Project.series_id == series_id
        ).order_by(Project.book_number_in_series).all()

        character_arcs = db.query(SeriesCharacterArc).filter(
            SeriesCharacterArc.series_id == series_id
        ).all()

        plot_threads = db.query(SeriesPlotThread).filter(
            SeriesPlotThread.series_id == series_id
        ).all()

        return {
            "series": {
                "id": series.id,
                "name": series.name,
                "genre": series.genre,
                "planned_books": series.planned_books,
                "completed_books": series.completed_books,
                "is_complete": series.is_complete,
                "series_arc": series.series_arc
            },
            "books": [
                {
                    "number": b.book_number_in_series,
                    "title": b.name,
                    "status": b.status.value if b.status else "unknown",
                    "id": b.id
                }
                for b in books
            ],
            "characters": [
                {
                    "name": c.character_name,
                    "is_alive": c.is_alive,
                    "first_book": c.first_appearance_book,
                    "last_book": c.last_appearance_book,
                    "current_state": c.current_state
                }
                for c in character_arcs
            ],
            "plot_threads": {
                "resolved": [
                    {"name": t.name, "introduced": t.introduced_in_book, "resolved": t.resolved_in_book}
                    for t in plot_threads if t.is_resolved
                ],
                "unresolved": [
                    {"name": t.name, "introduced": t.introduced_in_book, "is_main": t.is_main_plot}
                    for t in plot_threads if not t.is_resolved
                ]
            }
        }


# Singleton instance
series_service = SeriesService()

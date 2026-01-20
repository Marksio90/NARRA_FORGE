"""
Celery tasks for book generation pipeline
"""

from celery import Task
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.project import Project, ProjectStatus
from app.models.world_bible import WorldBible
from app.models.character import Character, CharacterRole
from app.models.plot_structure import PlotStructure
from app.models.chapter import Chapter

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session"""
    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db


def _create_world_bible(db: Session, project: Project) -> WorldBible:
    """Create World Bible with genre-appropriate content"""
    genre = project.genre.value

    world_bible = WorldBible(
        project_id=project.id,
        geography={
            "world_type": "galaxy" if genre == "sci-fi" else "continent",
            "locations": [
                {
                    "name": "The Capital" if genre != "sci-fi" else "New Terra Station",
                    "type": "city" if genre != "sci-fi" else "space station",
                    "description": f"Central hub of activity in this {genre} world",
                    "population": 5000000
                }
            ]
        },
        history={
            "eras": [
                {
                    "name": "The Great Change",
                    "start_year": -100,
                    "end_year": 0,
                    "key_events": ["Foundation", "First conflict", "Resolution"]
                }
            ],
            "current_year": 2247 if genre == "sci-fi" else 1024
        },
        systems={
            "technology_level": "advanced FTL" if genre == "sci-fi" else "medieval",
            "magic_system": {"exists": genre == "fantasy", "type": "elemental"} if genre == "fantasy" else {},
            "economic_system": {"type": "mixed economy"},
            "political_system": {"type": "democracy" if genre == "sci-fi" else "monarchy"}
        },
        cultures={
            "cultures": [
                {
                    "name": "Main Culture",
                    "values": ["honor", "loyalty", "courage"],
                    "customs": ["traditional greeting", "coming of age ceremony"],
                    "language": "Common Tongue"
                }
            ]
        },
        rules={
            "physics": "standard" if genre != "fantasy" else "magic-enhanced",
            "magic_rules": ["Rule 1", "Rule 2"] if genre == "fantasy" else [],
            "limitations": ["Cannot travel faster than light"] if genre == "sci-fi" else []
        },
        glossary={
            "terms": [
                {
                    "term": "Quantum Fold" if genre == "sci-fi" else "The Veil",
                    "definition": "A key concept in this world",
                    "usage": "Used frequently by characters"
                }
            ]
        },
        notes="This world bible was auto-generated based on genre conventions."
    )

    db.add(world_bible)
    db.commit()
    db.refresh(world_bible)

    logger.info(f"Created World Bible for project {project.id}")
    return world_bible


def _create_characters(db: Session, project: Project) -> list[Character]:
    """Create main characters based on project parameters"""
    params = project.parameters
    char_count = params.get("main_character_count", 4)

    characters = []

    # Protagonist
    protag = Character(
        project_id=project.id,
        name=params.get("title_suggestions", {}).get("main_character_name", "Alex Morgan"),
        role=CharacterRole.PROTAGONIST,
        profile={
            "biography": {
                "age": 28,
                "background": "Grew up in difficult circumstances",
                "occupation": "Varies by story",
                "education": "Self-taught"
            },
            "psychology": {
                "mbti": "INTJ",
                "traits": ["determined", "clever", "compassionate"],
                "fears": ["failure", "loss of loved ones"],
                "desires": ["justice", "peace", "understanding"]
            },
            "physical": {
                "appearance": "Average height, determined eyes",
                "distinctive_features": ["scar on left hand", "always wears a pendant"]
            },
            "ghost_wound": {
                "ghost": "Lost someone important in the past",
                "wound": "Struggles to trust others"
            }
        },
        arc={
            "starting_state": "Cynical and closed-off",
            "want_vs_need": {
                "want": "To succeed alone",
                "need": "To learn to trust and work with others"
            },
            "transformation_moments": ["Chapter 7: First breakthrough", "Chapter 18: Major revelation"],
            "ending_state": "Open-hearted and connected"
        },
        voice_guide="Speaks in short, clipped sentences. Uses dry humor. Avoids emotional language.",
        relationships={}
    )
    characters.append(protag)

    # Antagonist
    antag = Character(
        project_id=project.id,
        name="Viktor Shade",
        role=CharacterRole.ANTAGONIST,
        profile={
            "biography": {
                "age": 45,
                "background": "Once was a hero, now corrupted",
                "occupation": "Leader of opposition force"
            },
            "psychology": {
                "mbti": "ENTJ",
                "traits": ["charismatic", "ruthless", "intelligent"],
                "fears": ["irrelevance", "weakness"],
                "desires": ["power", "control", "legacy"]
            }
        },
        arc={
            "starting_state": "Confident and in control",
            "ending_state": "Defeated but respected"
        },
        voice_guide="Eloquent and persuasive. Uses manipulation tactics.",
        relationships={}
    )
    characters.append(antag)

    # Supporting characters
    for i in range(min(char_count - 2, 3)):
        supp = Character(
            project_id=project.id,
            name=f"Supporting Character {i+1}",
            role=CharacterRole.SUPPORTING,
            profile={
                "biography": {"age": 25 + i * 5},
                "psychology": {
                    "traits": ["loyal", "brave", "witty"]
                }
            },
            voice_guide=f"Unique voice pattern {i+1}"
        )
        characters.append(supp)

    db.add_all(characters)
    db.commit()

    for char in characters:
        db.refresh(char)

    logger.info(f"Created {len(characters)} characters for project {project.id}")
    return characters


def _create_plot_structure(db: Session, project: Project) -> PlotStructure:
    """Create plot structure based on project parameters"""
    params = project.parameters
    chapter_count = params.get("chapter_count", 25)

    plot = PlotStructure(
        project_id=project.id,
        structure_type=params.get("structure_type", "Hero's Journey"),
        acts={
            "act_1": {
                "name": "Setup",
                "chapters": list(range(1, chapter_count // 4 + 1)),
                "key_events": ["Introduction", "Inciting Incident", "Call to Adventure"],
                "goals": ["Establish world", "Introduce characters", "Set up conflict"]
            },
            "act_2a": {
                "name": "Rising Action",
                "chapters": list(range(chapter_count // 4 + 1, chapter_count // 2 + 1)),
                "key_events": ["First attempt", "Mentor guidance", "Small victories"],
                "goals": ["Build skills", "Deepen relationships", "Raise stakes"]
            },
            "act_2b": {
                "name": "Midpoint Crisis",
                "chapters": list(range(chapter_count // 2 + 1, 3 * chapter_count // 4 + 1)),
                "key_events": ["Major setback", "Dark night of the soul", "Realization"],
                "goals": ["Challenge protagonist", "Test convictions", "Force growth"]
            },
            "act_3": {
                "name": "Resolution",
                "chapters": list(range(3 * chapter_count // 4 + 1, chapter_count + 1)),
                "key_events": ["Final preparation", "Climax", "Resolution"],
                "goals": ["Confront antagonist", "Resolve all threads", "Show transformation"]
            }
        },
        main_conflict="Protagonist must overcome the antagonist and their own inner demons to save what they love.",
        stakes={
            "personal": "Loss of identity and purpose",
            "global": "The fate of the world/society hangs in balance",
            "escalation": ["Local threat", "Regional danger", "Global catastrophe"]
        },
        plot_points={
            "inciting_incident": {"chapter": 2, "description": "Event that disrupts normal life"},
            "first_plot_point": {"chapter": chapter_count // 4, "description": "Point of no return"},
            "midpoint": {"chapter": chapter_count // 2, "description": "Everything changes"},
            "second_plot_point": {"chapter": 3 * chapter_count // 4, "description": "Final push begins"},
            "climax": {"chapter": chapter_count - 2, "description": "Ultimate confrontation"},
            "resolution": {"chapter": chapter_count, "description": "New normal established"}
        },
        subplots=[
            {
                "name": "B-Story: Romance",
                "characters": ["Protagonist", "Love Interest"],
                "description": "Protagonist learns to open their heart",
                "intersection_points": [3, 7, 12, 18, 23]
            },
            {
                "name": "C-Story: Mentor Relationship",
                "characters": ["Protagonist", "Mentor"],
                "description": "Learning and eventual surpassing of teacher",
                "intersection_points": [5, 10, 15, 20]
            }
        ],
        tension_graph=[
            {"chapter": i, "tension": min(10, 3 + i // 3), "emotion": "curious" if i < 5 else "anxious"}
            for i in range(1, chapter_count + 1)
        ],
        foreshadowing=[
            {
                "planted_in_chapter": 3,
                "payoff_in_chapter": chapter_count - 5,
                "description": "Hint about the antagonist's true nature"
            },
            {
                "planted_in_chapter": 7,
                "payoff_in_chapter": chapter_count - 2,
                "description": "Setup for the final confrontation"
            }
        ]
    )

    db.add(plot)
    db.commit()
    db.refresh(plot)

    logger.info(f"Created plot structure for project {project.id}")
    return plot


def _create_chapters(db: Session, project: Project, characters: list[Character]) -> list[Chapter]:
    """Create chapters with actual content"""
    params = project.parameters
    chapter_count = params.get("chapter_count", 25)
    target_words = params.get("target_word_count", 90000)
    words_per_chapter = target_words // chapter_count

    chapters = []

    for i in range(1, chapter_count + 1):
        # Generate chapter content based on position in story
        if i == 1:
            content = _generate_opening_chapter(project, characters, words_per_chapter)
        elif i == chapter_count:
            content = _generate_closing_chapter(project, characters, words_per_chapter)
        else:
            content = _generate_middle_chapter(project, characters, i, words_per_chapter)

        chapter = Chapter(
            project_id=project.id,
            number=i,
            title=f"Chapter {i}",
            pov_character_id=characters[0].id if characters else None,
            outline={
                "setting": f"Location appropriate for chapter {i}",
                "characters_present": [c.name for c in characters[:3]],
                "goal": f"Advance plot in chapter {i}",
                "emotional_beat": "tension" if i % 3 == 0 else "relief",
                "key_reveals": [f"Reveal {i}"] if i % 5 == 0 else []
            },
            content=content,
            word_count=len(content.split()),
            quality_score=85.0,
            is_complete=2  # Final
        )

        chapters.append(chapter)

    db.add_all(chapters)
    db.commit()

    for chapter in chapters:
        db.refresh(chapter)

    logger.info(f"Created {len(chapters)} chapters for project {project.id}")
    return chapters


def _generate_opening_chapter(project: Project, characters: list[Character], target_words: int) -> str:
    """Generate opening chapter content"""
    protag_name = characters[0].name if characters else "The Protagonist"
    genre = project.genre.value

    content = f"""# Chapter 1: The Beginning

{protag_name} had always known this day would come. The signs were there, subtle at first, but growing more insistent with each passing hour.

The morning started like any other in this {genre} world. But beneath the surface of normalcy, something was stirring—something that would change everything.

As {protag_name} went about their routine, they couldn't shake the feeling that they were being watched. The familiar streets seemed different somehow, charged with an energy that hadn't been there before.

It was in that moment, standing at the crossroads of the old life and whatever came next, that the first sign appeared.

"""

    # Pad to approximate target length
    while len(content.split()) < target_words * 0.8:
        content += f"\n{protag_name} reflected on the path that had led to this moment. Each decision, each choice, had been a step toward this inevitable confrontation with destiny.\n\n"
        content += "The world around them continued its daily rhythm, unaware of the storm that was about to break.\n\n"

    return content


def _generate_middle_chapter(project: Project, characters: list[Character], chapter_num: int, target_words: int) -> str:
    """Generate middle chapter content"""
    protag_name = characters[0].name if characters else "The Protagonist"

    content = f"""# Chapter {chapter_num}

The journey continued, each step taking {protag_name} further from the safety of the familiar and deeper into the unknown.

New challenges emerged, testing not just skills but character itself. The lessons learned along the way were hard-won, paid for in sweat, tears, and determination.

Relationships deepened. Alliances formed. Trust was built, broken, and sometimes rebuilt stronger than before.

Through it all, {protag_name} kept moving forward, driven by a purpose that had become clearer with each passing chapter of this adventure.

"""

    # Pad to target length
    while len(content.split()) < target_words * 0.8:
        content += f"\nThe events of chapter {chapter_num} brought new understanding and new questions. What had seemed simple at the start revealed itself to be far more complex.\n\n"
        content += f"{protag_name} adapted, learned, and grew with each challenge overcome.\n\n"

    return content


def _generate_closing_chapter(project: Project, characters: list[Character], target_words: int) -> str:
    """Generate closing chapter content"""
    protag_name = characters[0].name if characters else "The Protagonist"

    content = f"""# Final Chapter: Resolution

The journey that had begun so long ago was finally reaching its conclusion. {protag_name} stood on the threshold of the final confrontation, armed not just with skills and knowledge, but with wisdom earned through hardship.

Everything had led to this moment. Every ally, every enemy, every lesson learned—all of it converged here, at the climax of the story.

The resolution came not with a sudden burst but with a quiet certainty. {protag_name} had changed, transformed by the journey from who they had been into who they needed to become.

As the dust settled and the new normal emerged, there was time for reflection. The world was different now—better in some ways, more complicated in others. But it was a world worth fighting for.

{protag_name} looked toward the horizon, where new adventures surely waited. But for now, this chapter was complete.

The end... and perhaps, a new beginning.
"""

    while len(content.split()) < target_words * 0.8:
        content += "\nReflections on the journey, the growth, and the future filled the final pages of this story.\n\n"

    return content


@celery_app.task(base=DatabaseTask, bind=True)
def run_full_pipeline(self, project_id: int):
    """
    Run the complete 15-step book generation pipeline

    MOCK IMPLEMENTATION - demonstrates progress tracking
    In production, this would call actual AI models for each step
    """
    import time

    db = self.db

    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"success": False, "error": "Project not found"}

        project.status = ProjectStatus.GENERATING
        project.started_at = datetime.utcnow()
        db.commit()

        logger.info(f"Starting FULL pipeline for project {project_id}: {project.name}")

        # 15-step pipeline with ACTUAL content generation
        total_steps = 15
        characters = []

        # Step 1: Initialize
        project.current_step = 1
        project.progress_percentage = (1 / total_steps) * 100
        project.current_activity = "Inicjalizacja Projektu"
        db.commit()
        logger.info(f"Project {project_id} - Step 1/15: Inicjalizacja")
        time.sleep(1)

        # Step 2: Analyze parameters (already done in simulation)
        project.current_step = 2
        project.progress_percentage = (2 / total_steps) * 100
        project.current_activity = "Analiza Parametrów AI"
        db.commit()
        logger.info(f"Project {project_id} - Step 2/15: Analiza")
        time.sleep(1)

        # Step 3: Create World Bible
        project.current_step = 3
        project.progress_percentage = (3 / total_steps) * 100
        project.current_activity = "Generowanie World Bible"
        db.commit()
        logger.info(f"Project {project_id} - Step 3/15: World Bible")
        _create_world_bible(db, project)
        time.sleep(2)

        # Step 4-5: Create Characters
        project.current_step = 4
        project.progress_percentage = (4 / total_steps) * 100
        project.current_activity = "Kreacja Postaci Głównych"
        db.commit()
        logger.info(f"Project {project_id} - Step 4/15: Main Characters")
        characters = _create_characters(db, project)
        time.sleep(2)

        project.current_step = 5
        project.progress_percentage = (5 / total_steps) * 100
        project.current_activity = "Kreacja Postaci Pobocznych"
        db.commit()
        logger.info(f"Project {project_id} - Step 5/15: Supporting Characters")
        time.sleep(2)

        # Step 6-7: Create Plot Structure
        project.current_step = 6
        project.progress_percentage = (6 / total_steps) * 100
        project.current_activity = "Projektowanie Głównej Osi Fabularnej"
        db.commit()
        logger.info(f"Project {project_id} - Step 6/15: Plot Structure")
        _create_plot_structure(db, project)
        time.sleep(2)

        project.current_step = 7
        project.progress_percentage = (7 / total_steps) * 100
        project.current_activity = "Projektowanie Wątków Pobocznych"
        db.commit()
        logger.info(f"Project {project_id} - Step 7/15: Subplots")
        time.sleep(2)

        # Step 8: Chapter Breakdown
        project.current_step = 8
        project.progress_percentage = (8 / total_steps) * 100
        project.current_activity = "Chapter Breakdown"
        db.commit()
        logger.info(f"Project {project_id} - Step 8/15: Chapter Breakdown")
        time.sleep(2)

        # Step 9: Scene Detailing
        project.current_step = 9
        project.progress_percentage = (9 / total_steps) * 100
        project.current_activity = "Scene Detailing"
        db.commit()
        logger.info(f"Project {project_id} - Step 9/15: Scene Details")
        time.sleep(2)

        # Step 10: Pre-Writing Validation
        project.current_step = 10
        project.progress_percentage = (10 / total_steps) * 100
        project.current_activity = "Pre-Writing Validation"
        db.commit()
        logger.info(f"Project {project_id} - Step 10/15: Validation")
        time.sleep(2)

        # Step 11: Generate ALL Chapters (the big one!)
        project.current_step = 11
        project.progress_percentage = (11 / total_steps) * 100
        project.current_activity = "Generowanie Wszystkich Rozdziałów"
        db.commit()
        logger.info(f"Project {project_id} - Step 11/15: Generating ALL Chapters")
        _create_chapters(db, project, characters)
        time.sleep(3)

        # Step 12: Continuity Check
        project.current_step = 12
        project.progress_percentage = (12 / total_steps) * 100
        project.current_activity = "Continuity Check"
        db.commit()
        logger.info(f"Project {project_id} - Step 12/15: Continuity")
        time.sleep(2)

        # Step 13: Style Polishing
        project.current_step = 13
        project.progress_percentage = (13 / total_steps) * 100
        project.current_activity = "Style Polishing"
        db.commit()
        logger.info(f"Project {project_id} - Step 13/15: Polishing")
        time.sleep(2)

        # Step 14: Genre Compliance
        project.current_step = 14
        project.progress_percentage = (14 / total_steps) * 100
        project.current_activity = "Genre Compliance Audit"
        db.commit()
        logger.info(f"Project {project_id} - Step 14/15: Genre Check")
        time.sleep(2)

        # Step 15: Finalization
        project.current_step = 15
        project.progress_percentage = (15 / total_steps) * 100
        project.current_activity = "Final Assembly & Export"
        db.commit()
        logger.info(f"Project {project_id} - Step 15/15: Finalization")
        time.sleep(2)

        # Mark as completed
        project.status = ProjectStatus.COMPLETED
        project.progress_percentage = 100.0
        project.current_step = 15
        project.current_activity = "Zakończone"
        project.completed_at = datetime.utcnow()
        db.commit()

        # Count generated content
        chapter_count = db.query(Chapter).filter(Chapter.project_id == project_id).count()
        character_count = db.query(Character).filter(Character.project_id == project_id).count()

        logger.info(f"✅ Pipeline completed for project {project_id}!")
        logger.info(f"   Generated: {chapter_count} chapters, {character_count} characters, 1 world bible, 1 plot structure")

        return {
            "success": True,
            "project_id": project_id,
            "message": f"Generation completed! Created {chapter_count} chapters, {character_count} characters, world bible, and plot structure.",
            "stats": {
                "chapters": chapter_count,
                "characters": character_count,
                "world_bible": 1,
                "plot_structure": 1
            }
        }

    except Exception as e:
        logger.error(f"Pipeline failed for project {project_id}: {e}", exc_info=True)

        # Mark project as failed
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = ProjectStatus.FAILED
                project.current_activity = f"Błąd: {str(e)}"
                db.commit()
        except:
            pass

        return {"success": False, "error": str(e)}
    finally:
        db.close()

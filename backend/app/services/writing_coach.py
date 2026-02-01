"""
AI Writing Coach - NarraForge 3.0 Phase 4

Intelligent writing assistant providing real-time feedback, writing exercises,
skill development tracking, and personalized coaching for authors.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class WritingSkill(Enum):
    """Writing skills to develop"""
    DIALOGUE = "dialogue"
    DESCRIPTION = "description"
    PACING = "pacing"
    CHARACTER_DEVELOPMENT = "character_development"
    PLOT_STRUCTURE = "plot_structure"
    WORLDBUILDING = "worldbuilding"
    VOICE = "voice"
    SHOW_DONT_TELL = "show_dont_tell"
    TENSION = "tension"
    EMOTIONAL_DEPTH = "emotional_depth"
    SENTENCE_VARIETY = "sentence_variety"
    WORD_CHOICE = "word_choice"


class FeedbackType(Enum):
    """Types of writing feedback"""
    STRENGTH = "strength"
    IMPROVEMENT = "improvement"
    SUGGESTION = "suggestion"
    WARNING = "warning"
    TIP = "tip"
    EXERCISE = "exercise"


class ExerciseType(Enum):
    """Types of writing exercises"""
    PROMPT = "prompt"
    REWRITE = "rewrite"
    EXPANSION = "expansion"
    REDUCTION = "reduction"
    DIALOGUE_ONLY = "dialogue_only"
    DESCRIPTION_ONLY = "description_only"
    PERSPECTIVE_SHIFT = "perspective_shift"
    TIMED_WRITING = "timed_writing"


class SkillLevel(Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    DEVELOPING = "developing"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    EXPERT = "expert"


class CoachingMode(Enum):
    """Coaching interaction modes"""
    GENTLE = "gentle"          # Encouraging, soft feedback
    BALANCED = "balanced"      # Mix of praise and critique
    STRICT = "strict"          # Focus on improvement
    MENTOR = "mentor"          # Teaching-focused
    PEER = "peer"              # Collaborative feedback


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class WritingFeedback:
    """A piece of writing feedback"""
    feedback_id: str
    feedback_type: FeedbackType
    skill: WritingSkill
    title: str
    description: str
    text_reference: Optional[str]
    position: Optional[Tuple[int, int]]  # start, end
    example_before: Optional[str]
    example_after: Optional[str]
    priority: int  # 1-5
    actionable: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedback_id": self.feedback_id,
            "feedback_type": self.feedback_type.value,
            "skill": self.skill.value,
            "title": self.title,
            "description": self.description,
            "text_reference": self.text_reference,
            "position": list(self.position) if self.position else None,
            "example_before": self.example_before,
            "example_after": self.example_after,
            "priority": self.priority,
            "actionable": self.actionable
        }


@dataclass
class WritingExercise:
    """A writing exercise"""
    exercise_id: str
    exercise_type: ExerciseType
    skill_focus: List[WritingSkill]
    title: str
    instructions: str
    prompt: str
    constraints: Dict[str, Any]
    time_limit_minutes: Optional[int]
    difficulty: int  # 1-5
    example_response: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exercise_id": self.exercise_id,
            "exercise_type": self.exercise_type.value,
            "skill_focus": [s.value for s in self.skill_focus],
            "title": self.title,
            "instructions": self.instructions,
            "prompt": self.prompt,
            "constraints": self.constraints,
            "time_limit_minutes": self.time_limit_minutes,
            "difficulty": self.difficulty,
            "example_response": self.example_response
        }


@dataclass
class ExerciseSubmission:
    """A submitted exercise"""
    submission_id: str
    exercise_id: str
    user_id: str
    content: str
    submitted_at: datetime
    time_spent_minutes: int
    feedback: List[WritingFeedback]
    score: float
    skill_improvements: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "submission_id": self.submission_id,
            "exercise_id": self.exercise_id,
            "user_id": self.user_id,
            "content": self.content,
            "submitted_at": self.submitted_at.isoformat(),
            "time_spent_minutes": self.time_spent_minutes,
            "feedback": [f.to_dict() for f in self.feedback],
            "score": self.score,
            "skill_improvements": self.skill_improvements
        }


@dataclass
class SkillProgress:
    """Progress in a writing skill"""
    skill: WritingSkill
    level: SkillLevel
    score: float  # 0-100
    exercises_completed: int
    feedback_addressed: int
    last_practiced: datetime
    growth_rate: float  # Recent improvement rate
    strengths: List[str]
    areas_to_improve: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill": self.skill.value,
            "level": self.level.value,
            "score": self.score,
            "exercises_completed": self.exercises_completed,
            "feedback_addressed": self.feedback_addressed,
            "last_practiced": self.last_practiced.isoformat(),
            "growth_rate": self.growth_rate,
            "strengths": self.strengths,
            "areas_to_improve": self.areas_to_improve
        }


@dataclass
class WriterProfile:
    """Profile of a writer being coached"""
    profile_id: str
    user_id: str
    name: str
    skill_levels: Dict[WritingSkill, SkillProgress]
    preferred_genres: List[str]
    writing_goals: List[str]
    coaching_mode: CoachingMode
    daily_word_goal: int
    words_written_today: int
    total_words_written: int
    streak_days: int
    achievements: List[str]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "user_id": self.user_id,
            "name": self.name,
            "skill_levels": {
                skill.value: progress.to_dict()
                for skill, progress in self.skill_levels.items()
            },
            "preferred_genres": self.preferred_genres,
            "writing_goals": self.writing_goals,
            "coaching_mode": self.coaching_mode.value,
            "daily_word_goal": self.daily_word_goal,
            "words_written_today": self.words_written_today,
            "total_words_written": self.total_words_written,
            "streak_days": self.streak_days,
            "achievements": self.achievements,
            "overall_level": self._calculate_overall_level(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def _calculate_overall_level(self) -> str:
        """Calculate overall writing level."""
        if not self.skill_levels:
            return SkillLevel.BEGINNER.value

        avg_score = sum(p.score for p in self.skill_levels.values()) / len(self.skill_levels)

        if avg_score >= 90:
            return SkillLevel.EXPERT.value
        elif avg_score >= 75:
            return SkillLevel.PROFICIENT.value
        elif avg_score >= 55:
            return SkillLevel.COMPETENT.value
        elif avg_score >= 35:
            return SkillLevel.DEVELOPING.value
        return SkillLevel.BEGINNER.value


@dataclass
class CoachingSession:
    """A coaching session"""
    session_id: str
    profile_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    focus_skills: List[WritingSkill]
    text_analyzed: str
    feedback_given: List[WritingFeedback]
    exercises_assigned: List[WritingExercise]
    goals_set: List[str]
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "profile_id": self.profile_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "focus_skills": [s.value for s in self.focus_skills],
            "feedback_count": len(self.feedback_given),
            "exercises_assigned": len(self.exercises_assigned),
            "goals_set": self.goals_set,
            "notes": self.notes
        }


@dataclass
class WritingPrompt:
    """A creative writing prompt"""
    prompt_id: str
    category: str  # genre, emotion, setting, etc.
    prompt_text: str
    genre_tags: List[str]
    difficulty: int
    estimated_words: int
    time_suggestion_minutes: int
    skill_focus: List[WritingSkill]
    bonus_challenges: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "category": self.category,
            "prompt_text": self.prompt_text,
            "genre_tags": self.genre_tags,
            "difficulty": self.difficulty,
            "estimated_words": self.estimated_words,
            "time_suggestion_minutes": self.time_suggestion_minutes,
            "skill_focus": [s.value for s in self.skill_focus],
            "bonus_challenges": self.bonus_challenges
        }


# =============================================================================
# EXERCISE TEMPLATES
# =============================================================================

EXERCISE_TEMPLATES = {
    WritingSkill.DIALOGUE: [
        {
            "title": "Subtext w dialogu",
            "instructions": "Napisz rozmowę, w której postacie mówią jedno, ale mają na myśli coś innego",
            "prompt": "Dwoje ludzi rozmawia o pogodzie, ale tak naprawdę kłócą się o coś ważnego",
            "constraints": {"min_exchanges": 8, "max_words": 500}
        },
        {
            "title": "Dialog bez tagów",
            "instructions": "Napisz dialog tak charakterystyczny, że czytelnik rozpozna kto mówi bez tagów dialogowych",
            "prompt": "Nauczyciel i student rozmawiają o ocenie",
            "constraints": {"no_dialogue_tags": True, "min_exchanges": 6}
        }
    ],
    WritingSkill.DESCRIPTION: [
        {
            "title": "Pięć zmysłów",
            "instructions": "Opisz scenę używając wszystkich pięciu zmysłów",
            "prompt": "Opisz targ miejski w upalny letni dzień",
            "constraints": {"must_use": ["wzrok", "słuch", "zapach", "dotyk", "smak"]}
        },
        {
            "title": "Minimalistyczny opis",
            "instructions": "Opisz miejsce używając maksymalnie 50 słów, ale stwórz pełny obraz",
            "prompt": "Opuszczony dom na wsi",
            "constraints": {"max_words": 50}
        }
    ],
    WritingSkill.SHOW_DONT_TELL: [
        {
            "title": "Emocja bez nazywania",
            "instructions": "Pokaż emocję postaci bez używania nazwy tej emocji",
            "prompt": "Pokaż strach postaci",
            "constraints": {"forbidden_words": ["strach", "bał", "przerażenie", "lęk"]}
        },
        {
            "title": "Przepisz telling na showing",
            "instructions": "Przepisz podany fragment, zamieniając 'telling' na 'showing'",
            "prompt": "Anna była bardzo smutna po śmierci babci. Płakała cały dzień i nie chciała z nikim rozmawiać.",
            "constraints": {"rewrite": True}
        }
    ],
    WritingSkill.PACING: [
        {
            "title": "Zmiana tempa",
            "instructions": "Napisz scenę, która zaczyna się powoli i przyspiesza do kulminacji",
            "prompt": "Postać odkrywa, że ktoś włamał się do jej domu",
            "constraints": {"min_words": 300}
        }
    ],
    WritingSkill.CHARACTER_DEVELOPMENT: [
        {
            "title": "Charakterystyka przez działanie",
            "instructions": "Przedstaw postać wyłącznie przez jej działania, bez opisu",
            "prompt": "Pokaż, że postać jest samotna",
            "constraints": {"no_direct_description": True}
        }
    ]
}


# =============================================================================
# FEEDBACK PATTERNS
# =============================================================================

FEEDBACK_PATTERNS = {
    "overuse_adverbs": {
        "type": FeedbackType.IMPROVEMENT,
        "skill": WritingSkill.WORD_CHOICE,
        "title": "Nadmiar przysłówków",
        "description": "Rozważ zastąpienie przysłówków silniejszymi czasownikami",
        "pattern": ["bardzo", "naprawdę", "całkowicie", "absolutnie"]
    },
    "telling_not_showing": {
        "type": FeedbackType.IMPROVEMENT,
        "skill": WritingSkill.SHOW_DONT_TELL,
        "title": "Informowanie zamiast pokazywania",
        "description": "Pokaż emocje postaci przez działania i reakcje fizyczne zamiast je nazywać"
    },
    "passive_voice": {
        "type": FeedbackType.SUGGESTION,
        "skill": WritingSkill.SENTENCE_VARIETY,
        "title": "Strona bierna",
        "description": "Rozważ użycie strony czynnej dla większej dynamiki"
    },
    "strong_opening": {
        "type": FeedbackType.STRENGTH,
        "skill": WritingSkill.PACING,
        "title": "Silne otwarcie",
        "description": "Świetne otwarcie, które wciąga czytelnika"
    },
    "vivid_description": {
        "type": FeedbackType.STRENGTH,
        "skill": WritingSkill.DESCRIPTION,
        "title": "Żywy opis",
        "description": "Doskonałe użycie szczegółów sensorycznych"
    }
}


# =============================================================================
# MAIN CLASS
# =============================================================================

class AIWritingCoach:
    """
    AI Writing Coach

    Provides personalized writing coaching, feedback, exercises,
    and skill development tracking.
    """

    def __init__(self):
        self.profiles: Dict[str, WriterProfile] = {}
        self.sessions: Dict[str, CoachingSession] = {}
        self.exercises: Dict[str, WritingExercise] = {}
        self.submissions: Dict[str, List[ExerciseSubmission]] = {}
        self.prompts: Dict[str, WritingPrompt] = {}

        # Initialize prompts
        self._initialize_prompts()

    def _initialize_prompts(self):
        """Initialize writing prompts database."""
        prompts_data = [
            ("Nieoczekiwany gość", "Ktoś puka do drzwi o północy", "thriller", 500, 30),
            ("Ostatni list", "Postać pisze list, który nigdy nie zostanie wysłany", "drama", 400, 25),
            ("Znalezisko", "Dziecko znajduje tajemniczy przedmiot w ogrodzie", "fantasy", 600, 35),
            ("Rozmowa", "Dwoje nieznajomych rozmawia w poczekalni", "literary", 450, 30),
            ("Powrót", "Postać wraca do rodzinnego miasta po 20 latach", "drama", 550, 35)
        ]

        for title, prompt, genre, words, time in prompts_data:
            p = WritingPrompt(
                prompt_id=str(uuid.uuid4()),
                category=genre,
                prompt_text=prompt,
                genre_tags=[genre],
                difficulty=3,
                estimated_words=words,
                time_suggestion_minutes=time,
                skill_focus=[WritingSkill.DESCRIPTION, WritingSkill.CHARACTER_DEVELOPMENT],
                bonus_challenges=["Użyj wszystkich pięciu zmysłów", "Zakończ niespodziewanie"]
            )
            self.prompts[p.prompt_id] = p

    async def create_writer_profile(
        self,
        user_id: str,
        name: str,
        preferred_genres: List[str],
        writing_goals: List[str],
        coaching_mode: CoachingMode = CoachingMode.BALANCED
    ) -> WriterProfile:
        """
        Create a new writer profile.
        """
        # Initialize skill levels
        skill_levels = {}
        for skill in WritingSkill:
            skill_levels[skill] = SkillProgress(
                skill=skill,
                level=SkillLevel.BEGINNER,
                score=25.0,
                exercises_completed=0,
                feedback_addressed=0,
                last_practiced=datetime.now(),
                growth_rate=0.0,
                strengths=[],
                areas_to_improve=[]
            )

        profile = WriterProfile(
            profile_id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            skill_levels=skill_levels,
            preferred_genres=preferred_genres,
            writing_goals=writing_goals,
            coaching_mode=coaching_mode,
            daily_word_goal=500,
            words_written_today=0,
            total_words_written=0,
            streak_days=0,
            achievements=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.profiles[profile.profile_id] = profile
        return profile

    async def analyze_writing(
        self,
        profile_id: str,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze writing and provide feedback.
        """
        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        feedback = []

        # Analyze various aspects
        feedback.extend(self._analyze_dialogue(text))
        feedback.extend(self._analyze_description(text))
        feedback.extend(self._analyze_pacing(text))
        feedback.extend(self._analyze_word_choice(text))
        feedback.extend(self._analyze_show_dont_tell(text))

        # Sort by priority
        feedback.sort(key=lambda f: f.priority, reverse=True)

        # Calculate scores
        scores = self._calculate_skill_scores(text, feedback)

        # Generate summary
        summary = self._generate_feedback_summary(feedback, profile.coaching_mode)

        return {
            "text_length": len(text),
            "word_count": len(text.split()),
            "feedback": [f.to_dict() for f in feedback],
            "skill_scores": scores,
            "summary": summary,
            "strengths": [f.to_dict() for f in feedback if f.feedback_type == FeedbackType.STRENGTH],
            "improvements": [f.to_dict() for f in feedback if f.feedback_type == FeedbackType.IMPROVEMENT],
            "next_steps": self._suggest_next_steps(feedback, profile)
        }

    async def start_coaching_session(
        self,
        profile_id: str,
        focus_skills: Optional[List[WritingSkill]] = None,
        text: Optional[str] = None
    ) -> CoachingSession:
        """
        Start a coaching session.
        """
        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        # Determine focus skills
        if not focus_skills:
            focus_skills = self._recommend_focus_skills(profile)

        # Analyze text if provided
        feedback = []
        if text:
            analysis = await self.analyze_writing(profile_id, text)
            feedback = [WritingFeedback(**f) for f in analysis["feedback"]]

        # Generate exercises
        exercises = self._generate_exercises(focus_skills, profile)

        session = CoachingSession(
            session_id=str(uuid.uuid4()),
            profile_id=profile_id,
            started_at=datetime.now(),
            ended_at=None,
            focus_skills=focus_skills,
            text_analyzed=text or "",
            feedback_given=feedback,
            exercises_assigned=exercises,
            goals_set=[],
            notes=""
        )

        self.sessions[session.session_id] = session

        return session

    async def get_exercise(
        self,
        profile_id: str,
        skill: Optional[WritingSkill] = None,
        difficulty: Optional[int] = None
    ) -> WritingExercise:
        """
        Get a writing exercise.
        """
        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        # Determine skill to practice
        if not skill:
            skill = self._recommend_skill_to_practice(profile)

        # Determine difficulty
        if not difficulty:
            skill_progress = profile.skill_levels.get(skill)
            if skill_progress:
                difficulty = max(1, min(5, int(skill_progress.score / 20)))
            else:
                difficulty = 2

        # Get exercise template
        templates = EXERCISE_TEMPLATES.get(skill, [])
        if not templates:
            templates = EXERCISE_TEMPLATES[WritingSkill.DESCRIPTION]

        template = templates[0]  # Would randomly select in production

        exercise = WritingExercise(
            exercise_id=str(uuid.uuid4()),
            exercise_type=ExerciseType.PROMPT,
            skill_focus=[skill],
            title=template["title"],
            instructions=template["instructions"],
            prompt=template["prompt"],
            constraints=template.get("constraints", {}),
            time_limit_minutes=20,
            difficulty=difficulty,
            example_response=None
        )

        self.exercises[exercise.exercise_id] = exercise

        return exercise

    async def submit_exercise(
        self,
        profile_id: str,
        exercise_id: str,
        content: str,
        time_spent: int
    ) -> ExerciseSubmission:
        """
        Submit an exercise for evaluation.
        """
        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        exercise = self.exercises.get(exercise_id)
        if not exercise:
            raise ValueError("Exercise not found")

        # Evaluate submission
        feedback = self._evaluate_exercise_submission(content, exercise)
        score = self._calculate_submission_score(feedback, exercise)

        # Calculate skill improvements
        improvements = {}
        for skill in exercise.skill_focus:
            base_improvement = score / 100 * 2  # Max 2 points per exercise
            improvements[skill.value] = base_improvement

        submission = ExerciseSubmission(
            submission_id=str(uuid.uuid4()),
            exercise_id=exercise_id,
            user_id=profile.user_id,
            content=content,
            submitted_at=datetime.now(),
            time_spent_minutes=time_spent,
            feedback=feedback,
            score=score,
            skill_improvements=improvements
        )

        # Update profile
        await self._update_profile_after_submission(profile, submission)

        # Store submission
        if profile_id not in self.submissions:
            self.submissions[profile_id] = []
        self.submissions[profile_id].append(submission)

        return submission

    async def get_writing_prompt(
        self,
        genre: Optional[str] = None,
        skill_focus: Optional[WritingSkill] = None
    ) -> WritingPrompt:
        """
        Get a creative writing prompt.
        """
        prompts = list(self.prompts.values())

        if genre:
            prompts = [p for p in prompts if genre in p.genre_tags]

        if skill_focus:
            prompts = [p for p in prompts if skill_focus in p.skill_focus]

        if not prompts:
            prompts = list(self.prompts.values())

        # Return first matching (would randomize in production)
        return prompts[0]

    async def get_skill_recommendations(
        self,
        profile_id: str
    ) -> Dict[str, Any]:
        """
        Get personalized skill development recommendations.
        """
        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        recommendations = []

        # Find weakest skills
        sorted_skills = sorted(
            profile.skill_levels.items(),
            key=lambda x: x[1].score
        )

        for skill, progress in sorted_skills[:3]:
            recommendations.append({
                "skill": skill.value,
                "current_level": progress.level.value,
                "current_score": progress.score,
                "priority": "high" if progress.score < 40 else "medium",
                "exercises_suggested": self._get_exercises_for_skill(skill),
                "tips": self._get_tips_for_skill(skill)
            })

        # Find skills that haven't been practiced recently
        stale_skills = [
            (skill, progress)
            for skill, progress in profile.skill_levels.items()
            if (datetime.now() - progress.last_practiced).days > 7
        ]

        return {
            "profile_id": profile_id,
            "overall_level": profile._calculate_overall_level(),
            "priority_recommendations": recommendations,
            "stale_skills": [
                {"skill": s.value, "days_since_practice": (datetime.now() - p.last_practiced).days}
                for s, p in stale_skills
            ],
            "next_milestone": self._calculate_next_milestone(profile),
            "suggested_daily_focus": self._suggest_daily_focus(profile)
        }

    async def log_writing_session(
        self,
        profile_id: str,
        word_count: int,
        duration_minutes: int,
        text_sample: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log a writing session.
        """
        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        # Update word counts
        profile.words_written_today += word_count
        profile.total_words_written += word_count

        # Check daily goal
        goal_achieved = profile.words_written_today >= profile.daily_word_goal

        # Update streak
        if goal_achieved:
            profile.streak_days += 1

            # Check for achievements
            new_achievements = []
            if profile.streak_days == 7:
                new_achievements.append("Tydzień w siodle!")
            if profile.streak_days == 30:
                new_achievements.append("Miesiąc pisania!")
            if profile.total_words_written >= 10000:
                new_achievements.append("10 000 słów!")
            if profile.total_words_written >= 50000:
                new_achievements.append("Powieść na horyzoncie!")

            for achievement in new_achievements:
                if achievement not in profile.achievements:
                    profile.achievements.append(achievement)

        profile.updated_at = datetime.now()

        # Quick analysis if text provided
        quick_feedback = None
        if text_sample:
            analysis = await self.analyze_writing(profile_id, text_sample)
            quick_feedback = analysis["summary"]

        return {
            "words_logged": word_count,
            "total_today": profile.words_written_today,
            "daily_goal": profile.daily_word_goal,
            "goal_achieved": goal_achieved,
            "progress_percent": min(100, profile.words_written_today / profile.daily_word_goal * 100),
            "streak_days": profile.streak_days,
            "total_words": profile.total_words_written,
            "new_achievements": new_achievements if goal_achieved else [],
            "quick_feedback": quick_feedback,
            "encouragement": self._get_encouragement(profile, goal_achieved)
        }

    async def get_daily_challenge(
        self,
        profile_id: str
    ) -> Dict[str, Any]:
        """
        Get a daily writing challenge.
        """
        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        # Get skill to focus on
        skill = self._recommend_skill_to_practice(profile)

        # Get exercise
        exercise = await self.get_exercise(profile_id, skill)

        # Get prompt
        prompt = await self.get_writing_prompt(
            genre=profile.preferred_genres[0] if profile.preferred_genres else None,
            skill_focus=skill
        )

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "skill_focus": skill.value,
            "exercise": exercise.to_dict(),
            "prompt": prompt.to_dict(),
            "bonus_goal": f"Napisz {profile.daily_word_goal + 100} słów dziś!",
            "tip_of_the_day": self._get_tip_of_the_day(skill)
        }

    # =========================================================================
    # ANALYSIS HELPERS
    # =========================================================================

    def _analyze_dialogue(self, text: str) -> List[WritingFeedback]:
        """Analyze dialogue quality."""
        feedback = []

        # Check for dialogue
        dialogue_count = text.count('"') // 2

        if dialogue_count > 0:
            # Check for varied dialogue tags
            basic_tags = ["powiedział", "powiedziała", "zapytał", "odpowiedział"]
            tag_count = sum(text.lower().count(tag) for tag in basic_tags)

            if tag_count > dialogue_count * 0.8:
                feedback.append(WritingFeedback(
                    feedback_id=str(uuid.uuid4()),
                    feedback_type=FeedbackType.IMPROVEMENT,
                    skill=WritingSkill.DIALOGUE,
                    title="Monotonne tagi dialogowe",
                    description="Rozważ użycie bardziej zróżnicowanych tagów lub akcji zamiast tagów",
                    text_reference=None,
                    position=None,
                    example_before='"Idę" - powiedział.',
                    example_after='"Idę" - rzucił przez ramię.',
                    priority=3,
                    actionable=True
                ))

        return feedback

    def _analyze_description(self, text: str) -> List[WritingFeedback]:
        """Analyze descriptive writing."""
        feedback = []

        # Check for sensory words
        sensory_words = {
            "wzrok": ["widział", "zobaczył", "patrzył", "błyszczał", "ciemny", "jasny"],
            "słuch": ["usłyszał", "szum", "cisza", "głos", "krzyk", "szept"],
            "zapach": ["pachniał", "zapach", "woń", "smród"],
            "dotyk": ["dotknął", "gładki", "szorstki", "zimny", "ciepły"],
            "smak": ["smakował", "słodki", "gorzki", "kwaśny"]
        }

        senses_used = []
        for sense, words in sensory_words.items():
            if any(word in text.lower() for word in words):
                senses_used.append(sense)

        if len(senses_used) >= 3:
            feedback.append(WritingFeedback(
                feedback_id=str(uuid.uuid4()),
                feedback_type=FeedbackType.STRENGTH,
                skill=WritingSkill.DESCRIPTION,
                title="Bogaty opis sensoryczny",
                description=f"Świetne użycie zmysłów: {', '.join(senses_used)}",
                text_reference=None,
                position=None,
                example_before=None,
                example_after=None,
                priority=2,
                actionable=False
            ))
        elif len(senses_used) <= 1:
            missing = [s for s in sensory_words.keys() if s not in senses_used]
            feedback.append(WritingFeedback(
                feedback_id=str(uuid.uuid4()),
                feedback_type=FeedbackType.SUGGESTION,
                skill=WritingSkill.DESCRIPTION,
                title="Ograniczony opis sensoryczny",
                description=f"Rozważ dodanie: {', '.join(missing[:3])}",
                text_reference=None,
                position=None,
                example_before=None,
                example_after=None,
                priority=3,
                actionable=True
            ))

        return feedback

    def _analyze_pacing(self, text: str) -> List[WritingFeedback]:
        """Analyze pacing."""
        feedback = []

        sentences = text.split(".")
        if sentences:
            lengths = [len(s.split()) for s in sentences if s.strip()]

            if lengths:
                avg_length = sum(lengths) / len(lengths)
                variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)

                if variance < 10:
                    feedback.append(WritingFeedback(
                        feedback_id=str(uuid.uuid4()),
                        feedback_type=FeedbackType.IMPROVEMENT,
                        skill=WritingSkill.SENTENCE_VARIETY,
                        title="Monotonna długość zdań",
                        description="Zdania mają podobną długość - rozważ większą różnorodność",
                        text_reference=None,
                        position=None,
                        example_before="Szedł dalej. Było ciemno. Bał się. Nie wiedział co robić.",
                        example_after="Szedł dalej mimo ciemności, która go otaczała. Bał się. Co mógł zrobić?",
                        priority=3,
                        actionable=True
                    ))

        return feedback

    def _analyze_word_choice(self, text: str) -> List[WritingFeedback]:
        """Analyze word choice."""
        feedback = []

        # Check for overused adverbs
        adverbs = ["bardzo", "naprawdę", "całkowicie", "absolutnie", "właściwie"]
        adverb_count = sum(text.lower().count(adv) for adv in adverbs)

        word_count = len(text.split())
        if word_count > 0 and adverb_count / word_count > 0.02:
            feedback.append(WritingFeedback(
                feedback_id=str(uuid.uuid4()),
                feedback_type=FeedbackType.IMPROVEMENT,
                skill=WritingSkill.WORD_CHOICE,
                title="Nadmiar przysłówków",
                description="Rozważ zastąpienie przysłówków silniejszymi czasownikami",
                text_reference=None,
                position=None,
                example_before="Biegł bardzo szybko.",
                example_after="Pędził.",
                priority=4,
                actionable=True
            ))

        return feedback

    def _analyze_show_dont_tell(self, text: str) -> List[WritingFeedback]:
        """Analyze show don't tell."""
        feedback = []

        # Check for emotion naming
        emotion_words = ["smutny", "szczęśliwy", "zły", "przestraszony", "zaskoczony", "znudzony"]
        for word in emotion_words:
            if word in text.lower():
                feedback.append(WritingFeedback(
                    feedback_id=str(uuid.uuid4()),
                    feedback_type=FeedbackType.TIP,
                    skill=WritingSkill.SHOW_DONT_TELL,
                    title=f"Nazwana emocja: '{word}'",
                    description="Rozważ pokazanie tej emocji przez działania i reakcje fizyczne",
                    text_reference=None,
                    position=None,
                    example_before=f"Była {word}.",
                    example_after="Pokaż przez: wyraz twarzy, gesty, działania, myśli",
                    priority=3,
                    actionable=True
                ))
                break  # One feedback is enough

        return feedback

    def _calculate_skill_scores(
        self,
        text: str,
        feedback: List[WritingFeedback]
    ) -> Dict[str, float]:
        """Calculate skill scores from analysis."""
        scores = {skill.value: 50.0 for skill in WritingSkill}

        for f in feedback:
            if f.feedback_type == FeedbackType.STRENGTH:
                scores[f.skill.value] += 10
            elif f.feedback_type == FeedbackType.IMPROVEMENT:
                scores[f.skill.value] -= 5
            elif f.feedback_type == FeedbackType.WARNING:
                scores[f.skill.value] -= 10

        # Clamp to 0-100
        return {k: max(0, min(100, v)) for k, v in scores.items()}

    def _generate_feedback_summary(
        self,
        feedback: List[WritingFeedback],
        mode: CoachingMode
    ) -> str:
        """Generate a summary of feedback."""
        strengths = [f for f in feedback if f.feedback_type == FeedbackType.STRENGTH]
        improvements = [f for f in feedback if f.feedback_type == FeedbackType.IMPROVEMENT]

        if mode == CoachingMode.GENTLE:
            summary = f"Świetna robota! "
            if strengths:
                summary += f"Szczególnie podoba mi się {strengths[0].title.lower()}. "
            if improvements:
                summary += f"Mała sugestia: {improvements[0].title.lower()}."
        elif mode == CoachingMode.STRICT:
            summary = f"Znalazłem {len(improvements)} obszarów do poprawy. "
            if improvements:
                summary += f"Priorytet: {improvements[0].title}."
        else:  # BALANCED
            summary = ""
            if strengths:
                summary += f"Mocne strony: {strengths[0].title.lower()}. "
            if improvements:
                summary += f"Do pracy: {improvements[0].title.lower()}."

        return summary

    def _suggest_next_steps(
        self,
        feedback: List[WritingFeedback],
        profile: WriterProfile
    ) -> List[str]:
        """Suggest next steps based on feedback."""
        steps = []

        improvements = [f for f in feedback if f.feedback_type == FeedbackType.IMPROVEMENT and f.actionable]

        for imp in improvements[:3]:
            steps.append(f"Popracuj nad: {imp.title}")

        if not steps:
            steps.append("Kontynuuj pisanie i eksperymentuj z nowymi technikami")

        return steps

    def _recommend_focus_skills(self, profile: WriterProfile) -> List[WritingSkill]:
        """Recommend skills to focus on."""
        sorted_skills = sorted(
            profile.skill_levels.items(),
            key=lambda x: x[1].score
        )
        return [skill for skill, _ in sorted_skills[:3]]

    def _recommend_skill_to_practice(self, profile: WriterProfile) -> WritingSkill:
        """Recommend a single skill to practice."""
        # Prioritize lowest score that hasn't been practiced recently
        candidates = []
        for skill, progress in profile.skill_levels.items():
            days_since = (datetime.now() - progress.last_practiced).days
            priority = (100 - progress.score) + days_since * 5
            candidates.append((skill, priority))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    def _generate_exercises(
        self,
        skills: List[WritingSkill],
        profile: WriterProfile
    ) -> List[WritingExercise]:
        """Generate exercises for skills."""
        exercises = []

        for skill in skills:
            templates = EXERCISE_TEMPLATES.get(skill, [])
            if templates:
                template = templates[0]
                exercise = WritingExercise(
                    exercise_id=str(uuid.uuid4()),
                    exercise_type=ExerciseType.PROMPT,
                    skill_focus=[skill],
                    title=template["title"],
                    instructions=template["instructions"],
                    prompt=template["prompt"],
                    constraints=template.get("constraints", {}),
                    time_limit_minutes=20,
                    difficulty=3,
                    example_response=None
                )
                exercises.append(exercise)

        return exercises

    def _evaluate_exercise_submission(
        self,
        content: str,
        exercise: WritingExercise
    ) -> List[WritingFeedback]:
        """Evaluate an exercise submission."""
        feedback = []

        # Check constraints
        constraints = exercise.constraints

        word_count = len(content.split())

        if "max_words" in constraints:
            if word_count > constraints["max_words"]:
                feedback.append(WritingFeedback(
                    feedback_id=str(uuid.uuid4()),
                    feedback_type=FeedbackType.WARNING,
                    skill=exercise.skill_focus[0],
                    title="Przekroczony limit słów",
                    description=f"Maksimum: {constraints['max_words']}, napisano: {word_count}",
                    text_reference=None,
                    position=None,
                    example_before=None,
                    example_after=None,
                    priority=4,
                    actionable=True
                ))

        if "min_words" in constraints:
            if word_count < constraints["min_words"]:
                feedback.append(WritingFeedback(
                    feedback_id=str(uuid.uuid4()),
                    feedback_type=FeedbackType.WARNING,
                    skill=exercise.skill_focus[0],
                    title="Za mało słów",
                    description=f"Minimum: {constraints['min_words']}, napisano: {word_count}",
                    text_reference=None,
                    position=None,
                    example_before=None,
                    example_after=None,
                    priority=4,
                    actionable=True
                ))

        # Add general feedback
        if word_count > 100:
            feedback.append(WritingFeedback(
                feedback_id=str(uuid.uuid4()),
                feedback_type=FeedbackType.STRENGTH,
                skill=exercise.skill_focus[0],
                title="Dobry wysiłek",
                description="Ukończyłeś ćwiczenie z odpowiednią ilością treści",
                text_reference=None,
                position=None,
                example_before=None,
                example_after=None,
                priority=2,
                actionable=False
            ))

        return feedback

    def _calculate_submission_score(
        self,
        feedback: List[WritingFeedback],
        exercise: WritingExercise
    ) -> float:
        """Calculate submission score."""
        base_score = 70.0

        for f in feedback:
            if f.feedback_type == FeedbackType.STRENGTH:
                base_score += 10
            elif f.feedback_type == FeedbackType.WARNING:
                base_score -= 15
            elif f.feedback_type == FeedbackType.IMPROVEMENT:
                base_score -= 5

        return max(0, min(100, base_score))

    async def _update_profile_after_submission(
        self,
        profile: WriterProfile,
        submission: ExerciseSubmission
    ):
        """Update profile after exercise submission."""
        for skill_str, improvement in submission.skill_improvements.items():
            skill = WritingSkill(skill_str)
            if skill in profile.skill_levels:
                progress = profile.skill_levels[skill]
                progress.score = min(100, progress.score + improvement)
                progress.exercises_completed += 1
                progress.last_practiced = datetime.now()

                # Update level
                if progress.score >= 90:
                    progress.level = SkillLevel.EXPERT
                elif progress.score >= 75:
                    progress.level = SkillLevel.PROFICIENT
                elif progress.score >= 55:
                    progress.level = SkillLevel.COMPETENT
                elif progress.score >= 35:
                    progress.level = SkillLevel.DEVELOPING
                else:
                    progress.level = SkillLevel.BEGINNER

        profile.updated_at = datetime.now()

    def _get_exercises_for_skill(self, skill: WritingSkill) -> List[str]:
        """Get exercise names for a skill."""
        templates = EXERCISE_TEMPLATES.get(skill, [])
        return [t["title"] for t in templates]

    def _get_tips_for_skill(self, skill: WritingSkill) -> List[str]:
        """Get tips for improving a skill."""
        tips = {
            WritingSkill.DIALOGUE: [
                "Słuchaj jak ludzie naprawdę rozmawiają",
                "Każda postać powinna mieć unikalny głos",
                "Używaj podtekstu - nie zawsze mów wprost"
            ],
            WritingSkill.DESCRIPTION: [
                "Angażuj wszystkie pięć zmysłów",
                "Mniej znaczy więcej - wybieraj konkretne detale",
                "Opisuj przez działanie, nie listę cech"
            ],
            WritingSkill.SHOW_DONT_TELL: [
                "Zamiast 'był smutny' pokaż: spuszczoną głowę, cichy głos",
                "Używaj fizycznych reakcji na emocje",
                "Pozwól czytelnikowi wyciągnąć wnioski"
            ]
        }
        return tips.get(skill, ["Ćwicz regularnie", "Czytaj dużo w swoim gatunku"])

    def _calculate_next_milestone(self, profile: WriterProfile) -> Dict[str, Any]:
        """Calculate next milestone to achieve."""
        milestones = [
            (10000, "10 000 słów"),
            (25000, "25 000 słów - opowiadanie"),
            (50000, "50 000 słów - powieść"),
            (100000, "100 000 słów - epik")
        ]

        for threshold, name in milestones:
            if profile.total_words_written < threshold:
                return {
                    "name": name,
                    "target": threshold,
                    "current": profile.total_words_written,
                    "remaining": threshold - profile.total_words_written
                }

        return {
            "name": "Mistrz!",
            "target": profile.total_words_written,
            "current": profile.total_words_written,
            "remaining": 0
        }

    def _suggest_daily_focus(self, profile: WriterProfile) -> str:
        """Suggest what to focus on today."""
        skill = self._recommend_skill_to_practice(profile)
        return f"Dziś skup się na: {skill.value.replace('_', ' ')}"

    def _get_encouragement(self, profile: WriterProfile, goal_achieved: bool) -> str:
        """Get encouragement message."""
        if goal_achieved:
            messages = [
                "Świetna robota! Cel osiągnięty!",
                "Niesamowite! Twoja seria trwa!",
                "Brawo! Każde słowo się liczy!"
            ]
        else:
            progress = profile.words_written_today / profile.daily_word_goal * 100
            if progress >= 75:
                messages = ["Prawie! Jeszcze trochę!"]
            elif progress >= 50:
                messages = ["W połowie drogi! Dasz radę!"]
            else:
                messages = ["Każde słowo przybliża Cię do celu!"]

        return messages[0]

    def _get_tip_of_the_day(self, skill: WritingSkill) -> str:
        """Get tip of the day."""
        tips = self._get_tips_for_skill(skill)
        return tips[0] if tips else "Pisz codziennie, nawet jeśli tylko trochę."

    # =========================================================================
    # PUBLIC GETTERS
    # =========================================================================

    def get_profile(self, profile_id: str) -> Optional[WriterProfile]:
        """Get a writer profile by ID."""
        return self.profiles.get(profile_id)

    def get_session(self, session_id: str) -> Optional[CoachingSession]:
        """Get a coaching session by ID."""
        return self.sessions.get(session_id)

    def list_profiles(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List writer profiles."""
        profiles = self.profiles.values()

        if user_id:
            profiles = [p for p in profiles if p.user_id == user_id]

        return [p.to_dict() for p in profiles]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_writing_coach: Optional[AIWritingCoach] = None


def get_writing_coach() -> AIWritingCoach:
    """Get the singleton writing coach instance."""
    global _writing_coach
    if _writing_coach is None:
        _writing_coach = AIWritingCoach()
    return _writing_coach


# Singleton instance for API usage
ai_writing_coach = get_writing_coach()

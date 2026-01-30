"""
Predictive Reader Psychology Engine - NarraForge 3.0 Phase 3

Advanced system for predicting and optimizing reader psychological response.
Analyzes emotional engagement, attention, satisfaction, and reading patterns.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import uuid
import math


# =============================================================================
# ENUMS
# =============================================================================

class EmotionalState(Enum):
    """Reader emotional states"""
    ENGAGED = "engaged"
    EXCITED = "excited"
    TENSE = "tense"
    SAD = "sad"
    HAPPY = "happy"
    ANXIOUS = "anxious"
    CURIOUS = "curious"
    BORED = "bored"
    SATISFIED = "satisfied"
    FRUSTRATED = "frustrated"
    SURPRISED = "surprised"
    NOSTALGIC = "nostalgic"


class EngagementLevel(Enum):
    """Levels of reader engagement"""
    DEEP_FLOW = "deep_flow"        # Completely absorbed
    ENGAGED = "engaged"             # Actively reading
    INTERESTED = "interested"       # Following along
    PASSIVE = "passive"             # Reading but not invested
    DISTRACTED = "distracted"       # Attention wandering
    DISENGAGED = "disengaged"       # Lost interest


class ReaderType(Enum):
    """Reader archetypes"""
    ANALYTICAL = "analytical"       # Loves puzzles, details, logic
    EMOTIONAL = "emotional"         # Seeks emotional connection
    THRILL_SEEKER = "thrill_seeker" # Wants action and excitement
    ESCAPIST = "escapist"           # Seeks immersion in other worlds
    INTELLECTUAL = "intellectual"   # Wants ideas and concepts
    ROMANTIC = "romantic"           # Seeks relationship stories
    CASUAL = "casual"               # Light entertainment seeker


class AttentionTrigger(Enum):
    """Elements that capture attention"""
    CONFLICT = "conflict"
    MYSTERY = "mystery"
    DANGER = "danger"
    ROMANCE = "romance"
    HUMOR = "humor"
    REVELATION = "revelation"
    CHARACTER_MOMENT = "character_moment"
    ACTION = "action"
    TWIST = "twist"
    EMOTION = "emotion"


class PsychologicalHook(Enum):
    """Psychological hooks for engagement"""
    CLIFFHANGER = "cliffhanger"
    OPEN_LOOP = "open_loop"
    CURIOSITY_GAP = "curiosity_gap"
    EMOTIONAL_INVESTMENT = "emotional_investment"
    ANTICIPATION = "anticipation"
    PAYOFF = "payoff"
    PATTERN_BREAK = "pattern_break"
    IDENTIFICATION = "identification"


class SatisfactionFactor(Enum):
    """Factors affecting reader satisfaction"""
    RESOLUTION = "resolution"
    CHARACTER_GROWTH = "character_growth"
    EMOTIONAL_CATHARSIS = "emotional_catharsis"
    INTELLECTUAL_REWARD = "intellectual_reward"
    SURPRISE = "surprise"
    VALIDATION = "validation"
    MEANING = "meaning"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class EmotionalBeat:
    """A single emotional moment in the story"""
    beat_id: str
    chapter: int
    paragraph: int
    emotion: EmotionalState
    intensity: float  # 0.0 to 1.0
    trigger: AttentionTrigger
    duration_paragraphs: int
    characters_involved: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "beat_id": self.beat_id,
            "chapter": self.chapter,
            "paragraph": self.paragraph,
            "emotion": self.emotion.value,
            "intensity": self.intensity,
            "trigger": self.trigger.value,
            "duration_paragraphs": self.duration_paragraphs,
            "characters_involved": self.characters_involved
        }


@dataclass
class EngagementPoint:
    """Predicted engagement at a point in the story"""
    chapter: int
    paragraph: int
    engagement_level: EngagementLevel
    engagement_score: float  # 0.0 to 1.0
    attention_factors: List[AttentionTrigger]
    hooks_active: List[PsychologicalHook]
    predicted_dropout_risk: float  # Probability reader will stop

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter": self.chapter,
            "paragraph": self.paragraph,
            "engagement_level": self.engagement_level.value,
            "engagement_score": self.engagement_score,
            "attention_factors": [f.value for f in self.attention_factors],
            "hooks_active": [h.value for h in self.hooks_active],
            "predicted_dropout_risk": self.predicted_dropout_risk
        }


@dataclass
class ReaderProfile:
    """Profile of target reader psychology"""
    profile_id: str
    reader_type: ReaderType
    preferred_emotions: List[EmotionalState]
    attention_triggers: List[AttentionTrigger]
    optimal_pacing: str  # "fast", "medium", "slow"
    complexity_preference: float  # 0.0 to 1.0
    emotional_depth_preference: float
    action_preference: float
    romance_tolerance: float
    horror_tolerance: float
    reading_speed: str  # "slow", "medium", "fast"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "reader_type": self.reader_type.value,
            "preferred_emotions": [e.value for e in self.preferred_emotions],
            "attention_triggers": [t.value for t in self.attention_triggers],
            "optimal_pacing": self.optimal_pacing,
            "complexity_preference": self.complexity_preference,
            "emotional_depth_preference": self.emotional_depth_preference,
            "action_preference": self.action_preference,
            "romance_tolerance": self.romance_tolerance,
            "horror_tolerance": self.horror_tolerance,
            "reading_speed": self.reading_speed
        }


@dataclass
class PsychologicalMoment:
    """A psychologically significant moment"""
    moment_id: str
    moment_type: str
    chapter: int
    description: str
    psychological_impact: float
    hooks_used: List[PsychologicalHook]
    expected_reader_response: str
    optimization_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "moment_id": self.moment_id,
            "moment_type": self.moment_type,
            "chapter": self.chapter,
            "description": self.description,
            "psychological_impact": self.psychological_impact,
            "hooks_used": [h.value for h in self.hooks_used],
            "expected_reader_response": self.expected_reader_response,
            "optimization_notes": self.optimization_notes
        }


@dataclass
class ChapterPsychology:
    """Psychological analysis of a chapter"""
    chapter_number: int
    emotional_arc: List[EmotionalBeat]
    engagement_curve: List[EngagementPoint]
    hooks_placed: List[PsychologicalHook]
    opening_strength: float
    closing_strength: float
    average_engagement: float
    emotional_range: float  # Variety of emotions
    pacing_score: float
    predicted_satisfaction: float
    improvement_suggestions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "emotional_arc": [b.to_dict() for b in self.emotional_arc],
            "engagement_curve": [p.to_dict() for p in self.engagement_curve],
            "hooks_placed": [h.value for h in self.hooks_placed],
            "opening_strength": self.opening_strength,
            "closing_strength": self.closing_strength,
            "average_engagement": self.average_engagement,
            "emotional_range": self.emotional_range,
            "pacing_score": self.pacing_score,
            "predicted_satisfaction": self.predicted_satisfaction,
            "improvement_suggestions": self.improvement_suggestions
        }


@dataclass
class SatisfactionPrediction:
    """Predicted reader satisfaction"""
    overall_score: float
    by_factor: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    target_audience_fit: float
    reread_probability: float
    recommendation_probability: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "by_factor": self.by_factor,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "target_audience_fit": self.target_audience_fit,
            "reread_probability": self.reread_probability,
            "recommendation_probability": self.recommendation_probability
        }


@dataclass
class PsychologyReport:
    """Full psychological analysis report"""
    report_id: str
    project_id: str
    target_reader: ReaderProfile
    chapter_analyses: List[ChapterPsychology]
    overall_emotional_journey: List[EmotionalBeat]
    key_moments: List[PsychologicalMoment]
    satisfaction_prediction: SatisfactionPrediction
    engagement_statistics: Dict[str, Any]
    optimization_priority: List[str]
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "project_id": self.project_id,
            "target_reader": self.target_reader.to_dict(),
            "chapter_analyses": [c.to_dict() for c in self.chapter_analyses],
            "overall_emotional_journey": [b.to_dict() for b in self.overall_emotional_journey],
            "key_moments": [m.to_dict() for m in self.key_moments],
            "satisfaction_prediction": self.satisfaction_prediction.to_dict(),
            "engagement_statistics": self.engagement_statistics,
            "optimization_priority": self.optimization_priority,
            "created_at": self.created_at.isoformat()
        }


# =============================================================================
# READER TYPE PROFILES
# =============================================================================

READER_TYPE_PROFILES = {
    ReaderType.ANALYTICAL: {
        "preferred_emotions": [EmotionalState.CURIOUS, EmotionalState.SATISFIED, EmotionalState.SURPRISED],
        "attention_triggers": [AttentionTrigger.MYSTERY, AttentionTrigger.REVELATION, AttentionTrigger.TWIST],
        "optimal_pacing": "medium",
        "complexity_preference": 0.8,
        "emotional_depth_preference": 0.5,
        "action_preference": 0.4
    },
    ReaderType.EMOTIONAL: {
        "preferred_emotions": [EmotionalState.SAD, EmotionalState.HAPPY, EmotionalState.NOSTALGIC],
        "attention_triggers": [AttentionTrigger.EMOTION, AttentionTrigger.CHARACTER_MOMENT, AttentionTrigger.ROMANCE],
        "optimal_pacing": "slow",
        "complexity_preference": 0.4,
        "emotional_depth_preference": 0.9,
        "action_preference": 0.3
    },
    ReaderType.THRILL_SEEKER: {
        "preferred_emotions": [EmotionalState.EXCITED, EmotionalState.TENSE, EmotionalState.ANXIOUS],
        "attention_triggers": [AttentionTrigger.ACTION, AttentionTrigger.DANGER, AttentionTrigger.CONFLICT],
        "optimal_pacing": "fast",
        "complexity_preference": 0.3,
        "emotional_depth_preference": 0.4,
        "action_preference": 0.9
    },
    ReaderType.ESCAPIST: {
        "preferred_emotions": [EmotionalState.ENGAGED, EmotionalState.CURIOUS, EmotionalState.HAPPY],
        "attention_triggers": [AttentionTrigger.MYSTERY, AttentionTrigger.REVELATION, AttentionTrigger.CHARACTER_MOMENT],
        "optimal_pacing": "medium",
        "complexity_preference": 0.5,
        "emotional_depth_preference": 0.6,
        "action_preference": 0.5
    },
    ReaderType.INTELLECTUAL: {
        "preferred_emotions": [EmotionalState.CURIOUS, EmotionalState.SATISFIED, EmotionalState.SURPRISED],
        "attention_triggers": [AttentionTrigger.REVELATION, AttentionTrigger.TWIST, AttentionTrigger.MYSTERY],
        "optimal_pacing": "slow",
        "complexity_preference": 0.9,
        "emotional_depth_preference": 0.6,
        "action_preference": 0.2
    },
    ReaderType.ROMANTIC: {
        "preferred_emotions": [EmotionalState.HAPPY, EmotionalState.SAD, EmotionalState.NOSTALGIC],
        "attention_triggers": [AttentionTrigger.ROMANCE, AttentionTrigger.EMOTION, AttentionTrigger.CHARACTER_MOMENT],
        "optimal_pacing": "slow",
        "complexity_preference": 0.3,
        "emotional_depth_preference": 0.8,
        "action_preference": 0.2
    },
    ReaderType.CASUAL: {
        "preferred_emotions": [EmotionalState.ENGAGED, EmotionalState.HAPPY, EmotionalState.EXCITED],
        "attention_triggers": [AttentionTrigger.HUMOR, AttentionTrigger.ACTION, AttentionTrigger.TWIST],
        "optimal_pacing": "fast",
        "complexity_preference": 0.2,
        "emotional_depth_preference": 0.4,
        "action_preference": 0.6
    }
}


# =============================================================================
# GENRE PSYCHOLOGY MAPPINGS
# =============================================================================

GENRE_PSYCHOLOGY = {
    "thriller": {
        "dominant_emotions": [EmotionalState.TENSE, EmotionalState.ANXIOUS, EmotionalState.EXCITED],
        "key_hooks": [PsychologicalHook.CLIFFHANGER, PsychologicalHook.OPEN_LOOP, PsychologicalHook.CURIOSITY_GAP],
        "target_readers": [ReaderType.THRILL_SEEKER, ReaderType.ANALYTICAL],
        "optimal_tension_curve": "rising_with_peaks"
    },
    "romance": {
        "dominant_emotions": [EmotionalState.HAPPY, EmotionalState.SAD, EmotionalState.NOSTALGIC],
        "key_hooks": [PsychologicalHook.EMOTIONAL_INVESTMENT, PsychologicalHook.ANTICIPATION, PsychologicalHook.IDENTIFICATION],
        "target_readers": [ReaderType.ROMANTIC, ReaderType.EMOTIONAL],
        "optimal_tension_curve": "will_they_wont_they"
    },
    "fantasy": {
        "dominant_emotions": [EmotionalState.CURIOUS, EmotionalState.EXCITED, EmotionalState.ENGAGED],
        "key_hooks": [PsychologicalHook.CURIOSITY_GAP, PsychologicalHook.ANTICIPATION, PsychologicalHook.PAYOFF],
        "target_readers": [ReaderType.ESCAPIST, ReaderType.THRILL_SEEKER],
        "optimal_tension_curve": "epic_journey"
    },
    "horror": {
        "dominant_emotions": [EmotionalState.ANXIOUS, EmotionalState.TENSE, EmotionalState.SURPRISED],
        "key_hooks": [PsychologicalHook.OPEN_LOOP, PsychologicalHook.PATTERN_BREAK, PsychologicalHook.ANTICIPATION],
        "target_readers": [ReaderType.THRILL_SEEKER],
        "optimal_tension_curve": "creeping_dread"
    },
    "mystery": {
        "dominant_emotions": [EmotionalState.CURIOUS, EmotionalState.SURPRISED, EmotionalState.SATISFIED],
        "key_hooks": [PsychologicalHook.CURIOSITY_GAP, PsychologicalHook.OPEN_LOOP, PsychologicalHook.PAYOFF],
        "target_readers": [ReaderType.ANALYTICAL, ReaderType.INTELLECTUAL],
        "optimal_tension_curve": "puzzle_revelation"
    },
    "drama": {
        "dominant_emotions": [EmotionalState.SAD, EmotionalState.HAPPY, EmotionalState.NOSTALGIC],
        "key_hooks": [PsychologicalHook.EMOTIONAL_INVESTMENT, PsychologicalHook.IDENTIFICATION, PsychologicalHook.PAYOFF],
        "target_readers": [ReaderType.EMOTIONAL, ReaderType.INTELLECTUAL],
        "optimal_tension_curve": "emotional_waves"
    },
    "scifi": {
        "dominant_emotions": [EmotionalState.CURIOUS, EmotionalState.EXCITED, EmotionalState.SURPRISED],
        "key_hooks": [PsychologicalHook.CURIOSITY_GAP, PsychologicalHook.ANTICIPATION, PsychologicalHook.PATTERN_BREAK],
        "target_readers": [ReaderType.INTELLECTUAL, ReaderType.ESCAPIST],
        "optimal_tension_curve": "discovery_arc"
    }
}


# =============================================================================
# MAIN CLASS
# =============================================================================

class ReaderPsychologyEngine:
    """
    Predictive Reader Psychology Engine

    Analyzes and predicts reader psychological responses to optimize
    engagement, emotional impact, and satisfaction.
    """

    def __init__(self):
        self.reader_profiles: Dict[str, ReaderProfile] = {}
        self.reports: Dict[str, PsychologyReport] = {}
        self.emotional_beats: Dict[str, List[EmotionalBeat]] = {}

    async def analyze_full_story(
        self,
        project_id: str,
        chapters: List[Dict[str, Any]],
        genre: str,
        target_reader_type: Optional[ReaderType] = None
    ) -> PsychologyReport:
        """
        Perform full psychological analysis of a story.
        """
        # Create or get target reader profile
        if target_reader_type:
            target_reader = self._create_reader_profile(target_reader_type)
        else:
            # Infer from genre
            genre_info = GENRE_PSYCHOLOGY.get(genre.lower(), GENRE_PSYCHOLOGY["drama"])
            target_reader = self._create_reader_profile(genre_info["target_readers"][0])

        # Analyze each chapter
        chapter_analyses = []
        all_emotional_beats = []

        for chapter in chapters:
            chapter_num = chapter.get("number", len(chapter_analyses) + 1)
            text = chapter.get("text", "")

            analysis = await self._analyze_chapter_psychology(
                text, chapter_num, genre, target_reader
            )
            chapter_analyses.append(analysis)
            all_emotional_beats.extend(analysis.emotional_arc)

        # Identify key psychological moments
        key_moments = self._identify_key_moments(chapter_analyses, genre)

        # Predict overall satisfaction
        satisfaction = self._predict_satisfaction(
            chapter_analyses, all_emotional_beats, target_reader, genre
        )

        # Calculate engagement statistics
        engagement_stats = self._calculate_engagement_statistics(chapter_analyses)

        # Generate optimization priorities
        optimization_priority = self._generate_optimization_priorities(
            chapter_analyses, satisfaction, target_reader
        )

        report = PsychologyReport(
            report_id=str(uuid.uuid4()),
            project_id=project_id,
            target_reader=target_reader,
            chapter_analyses=chapter_analyses,
            overall_emotional_journey=all_emotional_beats,
            key_moments=key_moments,
            satisfaction_prediction=satisfaction,
            engagement_statistics=engagement_stats,
            optimization_priority=optimization_priority,
            created_at=datetime.now()
        )

        self.reports[report.report_id] = report
        return report

    async def analyze_chapter(
        self,
        chapter_text: str,
        chapter_number: int,
        genre: str,
        target_reader_type: Optional[ReaderType] = None
    ) -> ChapterPsychology:
        """
        Analyze psychology of a single chapter.
        """
        if target_reader_type:
            target_reader = self._create_reader_profile(target_reader_type)
        else:
            genre_info = GENRE_PSYCHOLOGY.get(genre.lower(), GENRE_PSYCHOLOGY["drama"])
            target_reader = self._create_reader_profile(genre_info["target_readers"][0])

        return await self._analyze_chapter_psychology(
            chapter_text, chapter_number, genre, target_reader
        )

    async def predict_engagement(
        self,
        text: str,
        position_in_chapter: float,  # 0.0 to 1.0
        current_hooks: List[PsychologicalHook],
        reader_type: ReaderType
    ) -> EngagementPoint:
        """
        Predict engagement at a specific point.
        """
        reader_profile = self._create_reader_profile(reader_type)

        # Analyze text for attention factors
        attention_factors = self._detect_attention_triggers(text)

        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(
            attention_factors, current_hooks, reader_profile, position_in_chapter
        )

        # Determine engagement level
        engagement_level = self._score_to_engagement_level(engagement_score)

        # Calculate dropout risk
        dropout_risk = self._calculate_dropout_risk(
            engagement_score, position_in_chapter, current_hooks
        )

        return EngagementPoint(
            chapter=0,
            paragraph=0,
            engagement_level=engagement_level,
            engagement_score=engagement_score,
            attention_factors=attention_factors,
            hooks_active=current_hooks,
            predicted_dropout_risk=dropout_risk
        )

    async def optimize_chapter_opening(
        self,
        opening_text: str,
        genre: str,
        target_reader_type: ReaderType
    ) -> Dict[str, Any]:
        """
        Analyze and suggest optimizations for chapter opening.
        """
        reader = self._create_reader_profile(target_reader_type)

        # Analyze current opening
        current_strength = self._evaluate_opening_strength(opening_text, genre, reader)

        # Identify missing hooks
        current_hooks = self._detect_hooks(opening_text)
        recommended_hooks = self._get_recommended_hooks(genre, "opening")
        missing_hooks = [h for h in recommended_hooks if h not in current_hooks]

        # Generate suggestions
        suggestions = self._generate_opening_suggestions(
            opening_text, missing_hooks, genre, reader
        )

        return {
            "current_strength": current_strength,
            "current_hooks": [h.value for h in current_hooks],
            "missing_hooks": [h.value for h in missing_hooks],
            "suggestions": suggestions,
            "ideal_elements": self._get_ideal_opening_elements(genre)
        }

    async def optimize_chapter_ending(
        self,
        ending_text: str,
        genre: str,
        is_final_chapter: bool
    ) -> Dict[str, Any]:
        """
        Analyze and suggest optimizations for chapter ending.
        """
        # Analyze current ending
        current_strength = self._evaluate_ending_strength(ending_text, is_final_chapter)

        # Check for cliffhangers and hooks
        has_cliffhanger = self._detect_cliffhanger(ending_text)
        current_hooks = self._detect_hooks(ending_text)

        # Generate suggestions
        suggestions = []

        if not is_final_chapter and not has_cliffhanger:
            suggestions.append({
                "type": "add_hook",
                "description": "Rozważ dodanie elementu zawieszenia na koniec rozdziału",
                "impact": "high"
            })

        if is_final_chapter:
            satisfaction_elements = self._check_satisfaction_elements(ending_text)
            if not satisfaction_elements["resolution"]:
                suggestions.append({
                    "type": "add_resolution",
                    "description": "Upewnij się, że główne wątki zostały rozwiązane",
                    "impact": "critical"
                })

        return {
            "current_strength": current_strength,
            "has_cliffhanger": has_cliffhanger,
            "current_hooks": [h.value for h in current_hooks],
            "suggestions": suggestions,
            "is_final_chapter": is_final_chapter
        }

    async def analyze_emotional_pacing(
        self,
        chapters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze emotional pacing across the story.
        """
        emotional_curve = []

        for chapter in chapters:
            chapter_num = chapter.get("number", len(emotional_curve) + 1)
            text = chapter.get("text", "")

            # Detect dominant emotion
            emotions = self._detect_emotions(text)
            dominant = max(emotions.items(), key=lambda x: x[1]) if emotions else (EmotionalState.ENGAGED, 0.5)

            # Calculate intensity
            intensity = self._calculate_emotional_intensity(text)

            emotional_curve.append({
                "chapter": chapter_num,
                "dominant_emotion": dominant[0].value,
                "intensity": intensity,
                "emotion_distribution": {e.value: v for e, v in emotions.items()}
            })

        # Analyze pacing
        pacing_analysis = self._analyze_emotional_curve(emotional_curve)

        return {
            "emotional_curve": emotional_curve,
            "pacing_analysis": pacing_analysis,
            "recommendations": self._generate_pacing_recommendations(pacing_analysis)
        }

    def create_reader_profile(
        self,
        reader_type: ReaderType,
        customizations: Optional[Dict[str, Any]] = None
    ) -> ReaderProfile:
        """
        Create a custom reader profile.
        """
        profile = self._create_reader_profile(reader_type)

        if customizations:
            # Apply customizations
            if "complexity_preference" in customizations:
                profile.complexity_preference = customizations["complexity_preference"]
            if "emotional_depth_preference" in customizations:
                profile.emotional_depth_preference = customizations["emotional_depth_preference"]
            if "action_preference" in customizations:
                profile.action_preference = customizations["action_preference"]

        self.reader_profiles[profile.profile_id] = profile
        return profile

    # =========================================================================
    # ANALYSIS METHODS
    # =========================================================================

    async def _analyze_chapter_psychology(
        self,
        text: str,
        chapter_number: int,
        genre: str,
        target_reader: ReaderProfile
    ) -> ChapterPsychology:
        """Analyze psychology of a single chapter."""
        paragraphs = text.split("\n\n")

        # Extract emotional beats
        emotional_arc = []
        for i, para in enumerate(paragraphs):
            if len(para) > 50:
                emotions = self._detect_emotions(para)
                if emotions:
                    dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                    trigger = self._detect_primary_trigger(para)

                    beat = EmotionalBeat(
                        beat_id=str(uuid.uuid4()),
                        chapter=chapter_number,
                        paragraph=i + 1,
                        emotion=dominant_emotion[0],
                        intensity=dominant_emotion[1],
                        trigger=trigger,
                        duration_paragraphs=1,
                        characters_involved=self._extract_characters(para)
                    )
                    emotional_arc.append(beat)

        # Calculate engagement curve
        engagement_curve = []
        for i, para in enumerate(paragraphs):
            position = i / max(len(paragraphs), 1)
            hooks = self._detect_hooks(para)
            triggers = self._detect_attention_triggers(para)

            score = self._calculate_engagement_score(
                triggers, hooks, target_reader, position
            )

            point = EngagementPoint(
                chapter=chapter_number,
                paragraph=i + 1,
                engagement_level=self._score_to_engagement_level(score),
                engagement_score=score,
                attention_factors=triggers,
                hooks_active=hooks,
                predicted_dropout_risk=self._calculate_dropout_risk(score, position, hooks)
            )
            engagement_curve.append(point)

        # Analyze hooks
        all_hooks = []
        for para in paragraphs:
            all_hooks.extend(self._detect_hooks(para))
        hooks_placed = list(set(all_hooks))

        # Calculate metrics
        opening_strength = self._evaluate_opening_strength(
            "\n\n".join(paragraphs[:3]) if len(paragraphs) >= 3 else text,
            genre, target_reader
        )

        closing_strength = self._evaluate_ending_strength(
            "\n\n".join(paragraphs[-3:]) if len(paragraphs) >= 3 else text,
            False  # Assume not final chapter
        )

        avg_engagement = sum(p.engagement_score for p in engagement_curve) / max(len(engagement_curve), 1)

        # Emotional range - how many different emotions
        unique_emotions = len(set(b.emotion for b in emotional_arc))
        emotional_range = unique_emotions / len(EmotionalState)

        # Pacing score
        pacing_score = self._calculate_pacing_score(engagement_curve)

        # Predicted satisfaction
        predicted_satisfaction = self._calculate_chapter_satisfaction(
            emotional_arc, engagement_curve, hooks_placed, target_reader
        )

        # Generate improvement suggestions
        suggestions = self._generate_chapter_suggestions(
            emotional_arc, engagement_curve, hooks_placed,
            opening_strength, closing_strength, target_reader
        )

        return ChapterPsychology(
            chapter_number=chapter_number,
            emotional_arc=emotional_arc,
            engagement_curve=engagement_curve,
            hooks_placed=hooks_placed,
            opening_strength=opening_strength,
            closing_strength=closing_strength,
            average_engagement=avg_engagement,
            emotional_range=emotional_range,
            pacing_score=pacing_score,
            predicted_satisfaction=predicted_satisfaction,
            improvement_suggestions=suggestions
        )

    def _create_reader_profile(self, reader_type: ReaderType) -> ReaderProfile:
        """Create a reader profile from type."""
        type_profile = READER_TYPE_PROFILES.get(reader_type, READER_TYPE_PROFILES[ReaderType.CASUAL])

        return ReaderProfile(
            profile_id=str(uuid.uuid4()),
            reader_type=reader_type,
            preferred_emotions=type_profile["preferred_emotions"],
            attention_triggers=type_profile["attention_triggers"],
            optimal_pacing=type_profile["optimal_pacing"],
            complexity_preference=type_profile["complexity_preference"],
            emotional_depth_preference=type_profile["emotional_depth_preference"],
            action_preference=type_profile["action_preference"],
            romance_tolerance=0.5,
            horror_tolerance=0.5,
            reading_speed="medium"
        )

    def _detect_emotions(self, text: str) -> Dict[EmotionalState, float]:
        """Detect emotions in text."""
        emotions = {}
        lower = text.lower()

        # Simple keyword-based detection (would use ML in production)
        emotion_keywords = {
            EmotionalState.TENSE: ["napięcie", "niepokój", "strach", "drżenie", "serce"],
            EmotionalState.HAPPY: ["radość", "śmiech", "uśmiech", "szczęście", "wesele"],
            EmotionalState.SAD: ["smutek", "łzy", "płacz", "ból", "żal", "strata"],
            EmotionalState.EXCITED: ["ekscytacja", "podekscytowanie", "entuzjazm", "energia"],
            EmotionalState.CURIOUS: ["ciekawy", "tajemnica", "zagadka", "dlaczego", "pytanie"],
            EmotionalState.ANXIOUS: ["lęk", "obawa", "martwić", "bać się", "trwoga"],
            EmotionalState.SURPRISED: ["zaskoczenie", "szok", "nie do wiary", "niemożliwe"],
            EmotionalState.NOSTALGIC: ["wspomnienie", "przeszłość", "dawniej", "pamiętam"]
        }

        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for kw in keywords if kw in lower) / len(keywords)
            if score > 0:
                emotions[emotion] = min(score * 2, 1.0)

        # Default to engaged if no strong emotions detected
        if not emotions:
            emotions[EmotionalState.ENGAGED] = 0.5

        return emotions

    def _detect_attention_triggers(self, text: str) -> List[AttentionTrigger]:
        """Detect attention triggers in text."""
        triggers = []
        lower = text.lower()

        trigger_patterns = {
            AttentionTrigger.CONFLICT: ["walka", "spór", "kłótnia", "przeciw", "wróg"],
            AttentionTrigger.MYSTERY: ["tajemnica", "zagadka", "sekret", "ukryte", "nieznane"],
            AttentionTrigger.DANGER: ["niebezpieczeństwo", "zagrożenie", "śmierć", "ryzyko"],
            AttentionTrigger.ROMANCE: ["miłość", "pocałunek", "serce", "uczucie", "kocham"],
            AttentionTrigger.HUMOR: ["śmiech", "żart", "zabawne", "komiczny"],
            AttentionTrigger.REVELATION: ["odkrycie", "prawda", "okazało się", "zrozumiał"],
            AttentionTrigger.ACTION: ["biegł", "skoczył", "uderzył", "walczył", "gonił"],
            AttentionTrigger.TWIST: ["nie spodziewał", "zaskoczenie", "nagle", "niespodziewanie"]
        }

        for trigger, patterns in trigger_patterns.items():
            if any(p in lower for p in patterns):
                triggers.append(trigger)

        return triggers

    def _detect_hooks(self, text: str) -> List[PsychologicalHook]:
        """Detect psychological hooks in text."""
        hooks = []
        lower = text.lower()

        # Check for cliffhanger
        if any(phrase in lower for phrase in ["co teraz", "co się stanie", "czekał", "miał się dowiedzieć"]):
            hooks.append(PsychologicalHook.CLIFFHANGER)

        # Check for open loop
        if "?" in text or any(phrase in lower for phrase in ["dlaczego", "jak", "co", "kto"]):
            hooks.append(PsychologicalHook.OPEN_LOOP)

        # Check for curiosity gap
        if any(phrase in lower for phrase in ["sekret", "tajemnica", "niedługo", "wkrótce"]):
            hooks.append(PsychologicalHook.CURIOSITY_GAP)

        # Check for anticipation
        if any(phrase in lower for phrase in ["nadchodzi", "zbliża się", "czekał na", "spodziewał się"]):
            hooks.append(PsychologicalHook.ANTICIPATION)

        return hooks

    def _detect_primary_trigger(self, text: str) -> AttentionTrigger:
        """Detect the primary attention trigger."""
        triggers = self._detect_attention_triggers(text)
        if triggers:
            return triggers[0]
        return AttentionTrigger.CHARACTER_MOMENT

    def _extract_characters(self, text: str) -> List[str]:
        """Extract character names from text."""
        # Simplified - would use NER in production
        return []

    def _calculate_engagement_score(
        self,
        triggers: List[AttentionTrigger],
        hooks: List[PsychologicalHook],
        reader: ReaderProfile,
        position: float
    ) -> float:
        """Calculate engagement score."""
        base_score = 0.5

        # Add points for triggers that match reader preferences
        for trigger in triggers:
            if trigger in reader.attention_triggers:
                base_score += 0.15
            else:
                base_score += 0.05

        # Add points for active hooks
        base_score += len(hooks) * 0.1

        # Position modifier - beginning and end more important
        if position < 0.1 or position > 0.9:
            base_score *= 1.1

        return min(base_score, 1.0)

    def _score_to_engagement_level(self, score: float) -> EngagementLevel:
        """Convert score to engagement level."""
        if score >= 0.85:
            return EngagementLevel.DEEP_FLOW
        elif score >= 0.7:
            return EngagementLevel.ENGAGED
        elif score >= 0.55:
            return EngagementLevel.INTERESTED
        elif score >= 0.4:
            return EngagementLevel.PASSIVE
        elif score >= 0.25:
            return EngagementLevel.DISTRACTED
        return EngagementLevel.DISENGAGED

    def _calculate_dropout_risk(
        self,
        engagement_score: float,
        position: float,
        hooks: List[PsychologicalHook]
    ) -> float:
        """Calculate risk of reader dropping out."""
        base_risk = 1.0 - engagement_score

        # Reduce risk if hooks are active
        base_risk *= (1.0 - len(hooks) * 0.1)

        # Position affects risk - early chapters have higher dropout
        if position < 0.2:
            base_risk *= 1.3

        return min(base_risk, 1.0)

    def _evaluate_opening_strength(
        self,
        opening_text: str,
        genre: str,
        reader: ReaderProfile
    ) -> float:
        """Evaluate strength of chapter opening."""
        score = 0.5

        # Check for hooks
        hooks = self._detect_hooks(opening_text)
        score += len(hooks) * 0.1

        # Check for triggers
        triggers = self._detect_attention_triggers(opening_text)
        matching_triggers = [t for t in triggers if t in reader.attention_triggers]
        score += len(matching_triggers) * 0.15

        # Check length (not too long)
        words = len(opening_text.split())
        if 50 <= words <= 200:
            score += 0.1

        return min(score, 1.0)

    def _evaluate_ending_strength(
        self,
        ending_text: str,
        is_final: bool
    ) -> float:
        """Evaluate strength of chapter ending."""
        score = 0.5

        hooks = self._detect_hooks(ending_text)

        if is_final:
            # Final chapter should have resolution
            satisfaction = self._check_satisfaction_elements(ending_text)
            score += 0.2 if satisfaction["resolution"] else 0
            score += 0.1 if satisfaction["emotional_catharsis"] else 0
        else:
            # Non-final should have cliffhanger or hook
            if PsychologicalHook.CLIFFHANGER in hooks:
                score += 0.3
            score += len(hooks) * 0.1

        return min(score, 1.0)

    def _detect_cliffhanger(self, text: str) -> bool:
        """Detect if text ends with a cliffhanger."""
        lower = text.lower()
        cliffhanger_patterns = [
            "co teraz", "nagle", "wtedy", "nie wiedział", "czekał",
            "miał się przekonać", "...", "?!"
        ]
        return any(p in lower for p in cliffhanger_patterns)

    def _check_satisfaction_elements(self, text: str) -> Dict[str, bool]:
        """Check for satisfaction elements."""
        lower = text.lower()
        return {
            "resolution": any(w in lower for w in ["koniec", "rozwiązanie", "w końcu", "nareszcie"]),
            "emotional_catharsis": any(w in lower for w in ["szczęście", "spokój", "ulga", "radość"]),
            "closure": any(w in lower for w in ["pożegnanie", "zakończenie", "epilog"])
        }

    def _calculate_pacing_score(self, engagement_curve: List[EngagementPoint]) -> float:
        """Calculate pacing score based on engagement curve."""
        if len(engagement_curve) < 2:
            return 0.5

        # Good pacing has variation but not too extreme
        scores = [p.engagement_score for p in engagement_curve]
        variance = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)

        # Ideal variance is moderate (not flat, not chaotic)
        if 0.02 <= variance <= 0.1:
            return 0.8
        elif variance < 0.02:
            return 0.5  # Too flat
        else:
            return 0.6  # Too chaotic

    def _calculate_chapter_satisfaction(
        self,
        emotional_arc: List[EmotionalBeat],
        engagement_curve: List[EngagementPoint],
        hooks: List[PsychologicalHook],
        reader: ReaderProfile
    ) -> float:
        """Calculate predicted chapter satisfaction."""
        score = 0.5

        # Emotional alignment with reader preferences
        emotions_present = set(b.emotion for b in emotional_arc)
        preferred_present = emotions_present & set(reader.preferred_emotions)
        score += len(preferred_present) * 0.1

        # Engagement average
        avg_engagement = sum(p.engagement_score for p in engagement_curve) / max(len(engagement_curve), 1)
        score += avg_engagement * 0.2

        # Hooks for continuation
        score += min(len(hooks) * 0.05, 0.2)

        return min(score, 1.0)

    def _generate_chapter_suggestions(
        self,
        emotional_arc: List[EmotionalBeat],
        engagement_curve: List[EngagementPoint],
        hooks: List[PsychologicalHook],
        opening_strength: float,
        closing_strength: float,
        reader: ReaderProfile
    ) -> List[str]:
        """Generate improvement suggestions for a chapter."""
        suggestions = []

        if opening_strength < 0.6:
            suggestions.append("Wzmocnij otwarcie rozdziału - dodaj hak lub element napięcia")

        if closing_strength < 0.6:
            suggestions.append("Dodaj element zawieszenia lub emocjonalny moment na końcu rozdziału")

        avg_engagement = sum(p.engagement_score for p in engagement_curve) / max(len(engagement_curve), 1)
        if avg_engagement < 0.5:
            suggestions.append("Ogólne zaangażowanie jest niskie - dodaj więcej elementów akcji lub napięcia")

        low_points = [p for p in engagement_curve if p.engagement_score < 0.4]
        if len(low_points) > len(engagement_curve) * 0.3:
            suggestions.append("Zbyt wiele momentów niskiego zaangażowania - rozważ skrócenie lub dodanie konfliktów")

        emotions = set(b.emotion for b in emotional_arc)
        if len(emotions) < 2:
            suggestions.append("Rozdział ma ograniczony zakres emocjonalny - dodaj kontrast")

        return suggestions

    def _identify_key_moments(
        self,
        chapter_analyses: List[ChapterPsychology],
        genre: str
    ) -> List[PsychologicalMoment]:
        """Identify key psychological moments in the story."""
        moments = []

        for analysis in chapter_analyses:
            # Find high-intensity emotional beats
            for beat in analysis.emotional_arc:
                if beat.intensity >= 0.7:
                    moment = PsychologicalMoment(
                        moment_id=str(uuid.uuid4()),
                        moment_type="emotional_peak",
                        chapter=analysis.chapter_number,
                        description=f"Silny moment {beat.emotion.value}",
                        psychological_impact=beat.intensity,
                        hooks_used=[],
                        expected_reader_response=self._predict_response(beat.emotion),
                        optimization_notes=""
                    )
                    moments.append(moment)

            # Find engagement peaks
            for point in analysis.engagement_curve:
                if point.engagement_score >= 0.85:
                    moment = PsychologicalMoment(
                        moment_id=str(uuid.uuid4()),
                        moment_type="engagement_peak",
                        chapter=analysis.chapter_number,
                        description="Moment głębokiego zaangażowania",
                        psychological_impact=point.engagement_score,
                        hooks_used=point.hooks_active,
                        expected_reader_response="Pełne zanurzenie w historii",
                        optimization_notes=""
                    )
                    moments.append(moment)

        return moments

    def _predict_response(self, emotion: EmotionalState) -> str:
        """Predict reader response to an emotion."""
        responses = {
            EmotionalState.TENSE: "Czytelnik będzie wstrzymywał oddech",
            EmotionalState.HAPPY: "Czytelnik poczuje radość i satysfakcję",
            EmotionalState.SAD: "Czytelnik może poczuć wzruszenie",
            EmotionalState.EXCITED: "Czytelnik będzie chciał czytać dalej",
            EmotionalState.CURIOUS: "Czytelnik będzie szukał odpowiedzi",
            EmotionalState.ANXIOUS: "Czytelnik poczuje niepokój o postaci",
            EmotionalState.SURPRISED: "Czytelnik przeżyje moment 'wow'",
            EmotionalState.NOSTALGIC: "Czytelnik poczuje ciepło i refleksję"
        }
        return responses.get(emotion, "Czytelnik będzie zaangażowany")

    def _predict_satisfaction(
        self,
        chapter_analyses: List[ChapterPsychology],
        emotional_beats: List[EmotionalBeat],
        reader: ReaderProfile,
        genre: str
    ) -> SatisfactionPrediction:
        """Predict overall reader satisfaction."""
        # Calculate by factors
        by_factor = {}

        # Resolution
        last_chapter = chapter_analyses[-1] if chapter_analyses else None
        by_factor["resolution"] = last_chapter.closing_strength if last_chapter else 0.5

        # Character growth (simplified)
        by_factor["character_growth"] = 0.6

        # Emotional catharsis
        high_intensity = [b for b in emotional_beats if b.intensity >= 0.7]
        by_factor["emotional_catharsis"] = min(len(high_intensity) * 0.1, 1.0)

        # Intellectual reward
        by_factor["intellectual_reward"] = reader.complexity_preference * 0.7

        # Surprise
        twists = sum(
            1 for c in chapter_analyses
            for h in c.hooks_placed
            if h == PsychologicalHook.PATTERN_BREAK
        )
        by_factor["surprise"] = min(twists * 0.2, 1.0)

        # Overall score
        overall = sum(by_factor.values()) / len(by_factor)

        # Strengths and weaknesses
        strengths = [f for f, v in by_factor.items() if v >= 0.7]
        weaknesses = [f for f, v in by_factor.items() if v < 0.5]

        # Target audience fit
        avg_engagement = sum(c.average_engagement for c in chapter_analyses) / max(len(chapter_analyses), 1)

        return SatisfactionPrediction(
            overall_score=overall,
            by_factor=by_factor,
            strengths=strengths,
            weaknesses=weaknesses,
            target_audience_fit=avg_engagement,
            reread_probability=overall * 0.6,
            recommendation_probability=overall * 0.8
        )

    def _calculate_engagement_statistics(
        self,
        chapter_analyses: List[ChapterPsychology]
    ) -> Dict[str, Any]:
        """Calculate engagement statistics."""
        all_scores = []
        for analysis in chapter_analyses:
            all_scores.extend([p.engagement_score for p in analysis.engagement_curve])

        if not all_scores:
            return {"average": 0, "min": 0, "max": 0, "std_dev": 0}

        avg = sum(all_scores) / len(all_scores)
        min_score = min(all_scores)
        max_score = max(all_scores)
        variance = sum((s - avg)**2 for s in all_scores) / len(all_scores)
        std_dev = math.sqrt(variance)

        return {
            "average": avg,
            "min": min_score,
            "max": max_score,
            "std_dev": std_dev,
            "total_data_points": len(all_scores),
            "chapters_analyzed": len(chapter_analyses)
        }

    def _generate_optimization_priorities(
        self,
        chapter_analyses: List[ChapterPsychology],
        satisfaction: SatisfactionPrediction,
        reader: ReaderProfile
    ) -> List[str]:
        """Generate prioritized optimization recommendations."""
        priorities = []

        # Check opening chapters
        if chapter_analyses and chapter_analyses[0].opening_strength < 0.6:
            priorities.append("WYSOKI: Wzmocnij początek książki - kluczowe dla utrzymania czytelnika")

        # Check for low engagement chapters
        low_chapters = [c for c in chapter_analyses if c.average_engagement < 0.5]
        if low_chapters:
            chapters_str = ", ".join(str(c.chapter_number) for c in low_chapters)
            priorities.append(f"WYSOKI: Popraw zaangażowanie w rozdziałach: {chapters_str}")

        # Check satisfaction weaknesses
        for weakness in satisfaction.weaknesses:
            priorities.append(f"ŚREDNI: Wzmocnij element: {weakness}")

        # Check ending
        if chapter_analyses and chapter_analyses[-1].closing_strength < 0.7:
            priorities.append("ŚREDNI: Wzmocnij zakończenie książki")

        return priorities

    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calculate overall emotional intensity of text."""
        emotions = self._detect_emotions(text)
        if not emotions:
            return 0.3
        return max(emotions.values())

    def _analyze_emotional_curve(self, emotional_curve: List[Dict]) -> Dict[str, Any]:
        """Analyze the emotional curve for pacing insights."""
        if len(emotional_curve) < 2:
            return {"pattern": "unknown", "variance": 0}

        intensities = [e["intensity"] for e in emotional_curve]
        avg = sum(intensities) / len(intensities)
        variance = sum((i - avg)**2 for i in intensities) / len(intensities)

        # Detect pattern
        if variance < 0.05:
            pattern = "flat"
        elif intensities[-1] > intensities[0] + 0.2:
            pattern = "rising"
        elif intensities[-1] < intensities[0] - 0.2:
            pattern = "falling"
        else:
            pattern = "varied"

        return {
            "pattern": pattern,
            "variance": variance,
            "average_intensity": avg,
            "peak_chapter": intensities.index(max(intensities)) + 1,
            "low_chapter": intensities.index(min(intensities)) + 1
        }

    def _generate_pacing_recommendations(self, pacing_analysis: Dict) -> List[str]:
        """Generate pacing recommendations."""
        recommendations = []

        if pacing_analysis["pattern"] == "flat":
            recommendations.append("Krzywa emocjonalna jest zbyt płaska - dodaj więcej wzlotów i upadków")
        elif pacing_analysis["pattern"] == "falling":
            recommendations.append("Intensywność emocjonalna spada - rozważ budowanie do klimaksu")

        if pacing_analysis.get("variance", 0) > 0.2:
            recommendations.append("Duże wahania emocjonalne - sprawdź czy przejścia są płynne")

        return recommendations

    def _generate_opening_suggestions(
        self,
        opening: str,
        missing_hooks: List[PsychologicalHook],
        genre: str,
        reader: ReaderProfile
    ) -> List[Dict[str, Any]]:
        """Generate suggestions for improving opening."""
        suggestions = []

        if PsychologicalHook.CURIOSITY_GAP in missing_hooks:
            suggestions.append({
                "hook": "curiosity_gap",
                "suggestion": "Wprowadź pytanie lub tajemnicę, która zainteresuje czytelnika",
                "example": "Zacznij od intrigującego stwierdzenia lub niezwykłej sytuacji"
            })

        if PsychologicalHook.OPEN_LOOP in missing_hooks:
            suggestions.append({
                "hook": "open_loop",
                "suggestion": "Otwórz wątek, który czytelnik będzie chciał zobaczyć zamknięty",
                "example": "Wspomnij o czymś, co zostanie wyjaśnione później"
            })

        return suggestions

    def _get_ideal_opening_elements(self, genre: str) -> List[str]:
        """Get ideal opening elements for a genre."""
        genre_openings = {
            "thriller": ["Natychmiastowe napięcie", "Tajemnicza sytuacja", "Zagrożenie"],
            "romance": ["Intrygująca postać", "Moment emocjonalny", "Obietnica chemii"],
            "fantasy": ["Niezwykły świat", "Magiczny element", "Zaproszenie do przygody"],
            "mystery": ["Zagadka", "Niewyjaśnione zdarzenie", "Intrygująca postać"],
            "horror": ["Niepokojąca atmosfera", "Normalnść przed burzą", "Subtelne zagrożenie"]
        }
        return genre_openings.get(genre.lower(), ["Silne otwarcie", "Intrygująca sytuacja"])

    def _get_recommended_hooks(self, genre: str, position: str) -> List[PsychologicalHook]:
        """Get recommended hooks for genre and position."""
        genre_hooks = GENRE_PSYCHOLOGY.get(genre.lower(), GENRE_PSYCHOLOGY["drama"])
        return genre_hooks.get("key_hooks", [PsychologicalHook.CURIOSITY_GAP])

    # =========================================================================
    # PUBLIC GETTERS
    # =========================================================================

    def get_report(self, report_id: str) -> Optional[PsychologyReport]:
        """Get a psychology report by ID."""
        return self.reports.get(report_id)

    def get_reader_profile(self, profile_id: str) -> Optional[ReaderProfile]:
        """Get a reader profile by ID."""
        return self.reader_profiles.get(profile_id)

    def list_reports(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all reports."""
        reports = self.reports.values()
        if project_id:
            reports = [r for r in reports if r.project_id == project_id]

        return [
            {
                "report_id": r.report_id,
                "project_id": r.project_id,
                "satisfaction_score": r.satisfaction_prediction.overall_score,
                "created_at": r.created_at.isoformat()
            }
            for r in reports
        ]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_psychology_engine: Optional[ReaderPsychologyEngine] = None


def get_psychology_engine() -> ReaderPsychologyEngine:
    """Get the singleton psychology engine instance."""
    global _psychology_engine
    if _psychology_engine is None:
        _psychology_engine = ReaderPsychologyEngine()
    return _psychology_engine

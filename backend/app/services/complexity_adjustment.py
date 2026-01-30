"""
Dynamic Complexity Adjustment System - NarraForge 3.0 Phase 3

Intelligent system for dynamically adjusting narrative complexity
based on target audience, genre requirements, and reading level.
Ensures optimal readability while maintaining engagement.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import uuid
import math
import re


# =============================================================================
# ENUMS
# =============================================================================

class ReadingLevel(Enum):
    """Target reading levels"""
    CHILDREN = "children"          # Ages 6-10
    MIDDLE_GRADE = "middle_grade"  # Ages 10-14
    YOUNG_ADULT = "young_adult"    # Ages 14-18
    ADULT = "adult"                # Ages 18+
    ACADEMIC = "academic"          # Academic/scholarly
    SIMPLIFIED = "simplified"      # Easy reading


class ComplexityDimension(Enum):
    """Dimensions of text complexity"""
    VOCABULARY = "vocabulary"
    SENTENCE_STRUCTURE = "sentence_structure"
    PARAGRAPH_LENGTH = "paragraph_length"
    PLOT_COMPLEXITY = "plot_complexity"
    CHARACTER_DEPTH = "character_depth"
    THEME_DEPTH = "theme_depth"
    DIALOGUE_SOPHISTICATION = "dialogue_sophistication"
    NARRATIVE_TECHNIQUES = "narrative_techniques"


class AdjustmentDirection(Enum):
    """Direction of complexity adjustment"""
    SIMPLIFY = "simplify"
    MAINTAIN = "maintain"
    ENHANCE = "enhance"


class VocabularyLevel(Enum):
    """Vocabulary complexity levels"""
    BASIC = "basic"           # Common, everyday words
    INTERMEDIATE = "intermediate"  # Some advanced vocabulary
    ADVANCED = "advanced"     # Rich, varied vocabulary
    LITERARY = "literary"     # Literary and artistic vocabulary
    SPECIALIZED = "specialized"  # Domain-specific terms


class SentenceComplexity(Enum):
    """Sentence structure complexity"""
    SIMPLE = "simple"         # Subject-verb-object
    COMPOUND = "compound"     # Multiple clauses
    COMPLEX = "complex"       # Subordinate clauses
    SOPHISTICATED = "sophisticated"  # Literary structures


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ComplexityMetrics:
    """Metrics measuring text complexity"""
    avg_sentence_length: float
    avg_word_length: float
    avg_paragraph_length: float
    vocabulary_richness: float  # Type-token ratio
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    gunning_fog_index: float
    complex_word_ratio: float
    dialogue_ratio: float
    passive_voice_ratio: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "avg_sentence_length": self.avg_sentence_length,
            "avg_word_length": self.avg_word_length,
            "avg_paragraph_length": self.avg_paragraph_length,
            "vocabulary_richness": self.vocabulary_richness,
            "flesch_reading_ease": self.flesch_reading_ease,
            "flesch_kincaid_grade": self.flesch_kincaid_grade,
            "gunning_fog_index": self.gunning_fog_index,
            "complex_word_ratio": self.complex_word_ratio,
            "dialogue_ratio": self.dialogue_ratio,
            "passive_voice_ratio": self.passive_voice_ratio
        }


@dataclass
class ComplexityProfile:
    """Target complexity profile for a reading level"""
    profile_id: str
    reading_level: ReadingLevel
    target_sentence_length: Tuple[int, int]  # min, max
    target_word_length: Tuple[float, float]
    target_paragraph_length: Tuple[int, int]
    vocabulary_level: VocabularyLevel
    sentence_complexity: SentenceComplexity
    max_flesch_kincaid_grade: float
    min_flesch_reading_ease: float
    allowed_narrative_techniques: List[str]
    theme_depth_level: int  # 1-5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "reading_level": self.reading_level.value,
            "target_sentence_length": list(self.target_sentence_length),
            "target_word_length": list(self.target_word_length),
            "target_paragraph_length": list(self.target_paragraph_length),
            "vocabulary_level": self.vocabulary_level.value,
            "sentence_complexity": self.sentence_complexity.value,
            "max_flesch_kincaid_grade": self.max_flesch_kincaid_grade,
            "min_flesch_reading_ease": self.min_flesch_reading_ease,
            "allowed_narrative_techniques": self.allowed_narrative_techniques,
            "theme_depth_level": self.theme_depth_level
        }


@dataclass
class ComplexityAdjustment:
    """A single adjustment recommendation"""
    adjustment_id: str
    dimension: ComplexityDimension
    direction: AdjustmentDirection
    current_value: float
    target_value: float
    priority: int  # 1-5, 5 being highest
    description: str
    example_before: str
    example_after: str
    auto_applicable: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adjustment_id": self.adjustment_id,
            "dimension": self.dimension.value,
            "direction": self.direction.value,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "priority": self.priority,
            "description": self.description,
            "example_before": self.example_before,
            "example_after": self.example_after,
            "auto_applicable": self.auto_applicable
        }


@dataclass
class ChapterComplexityAnalysis:
    """Complexity analysis of a chapter"""
    chapter_number: int
    metrics: ComplexityMetrics
    reading_level_detected: ReadingLevel
    adjustments_needed: List[ComplexityAdjustment]
    complexity_score: float  # 0-100
    readability_score: float  # 0-100
    consistency_with_previous: float  # 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "metrics": self.metrics.to_dict(),
            "reading_level_detected": self.reading_level_detected.value,
            "adjustments_needed": [a.to_dict() for a in self.adjustments_needed],
            "complexity_score": self.complexity_score,
            "readability_score": self.readability_score,
            "consistency_with_previous": self.consistency_with_previous
        }


@dataclass
class ComplexityReport:
    """Full complexity analysis report"""
    report_id: str
    project_id: str
    target_profile: ComplexityProfile
    chapter_analyses: List[ChapterComplexityAnalysis]
    overall_metrics: ComplexityMetrics
    overall_complexity_score: float
    overall_readability_score: float
    consistency_score: float
    total_adjustments_needed: int
    priority_adjustments: List[ComplexityAdjustment]
    recommendations: List[str]
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "project_id": self.project_id,
            "target_profile": self.target_profile.to_dict(),
            "chapter_analyses": [c.to_dict() for c in self.chapter_analyses],
            "overall_metrics": self.overall_metrics.to_dict(),
            "overall_complexity_score": self.overall_complexity_score,
            "overall_readability_score": self.overall_readability_score,
            "consistency_score": self.consistency_score,
            "total_adjustments_needed": self.total_adjustments_needed,
            "priority_adjustments": [a.to_dict() for a in self.priority_adjustments],
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat()
        }


# =============================================================================
# READING LEVEL PROFILES
# =============================================================================

READING_LEVEL_PROFILES = {
    ReadingLevel.CHILDREN: ComplexityProfile(
        profile_id="children_001",
        reading_level=ReadingLevel.CHILDREN,
        target_sentence_length=(5, 12),
        target_word_length=(3.0, 5.0),
        target_paragraph_length=(2, 5),
        vocabulary_level=VocabularyLevel.BASIC,
        sentence_complexity=SentenceComplexity.SIMPLE,
        max_flesch_kincaid_grade=4.0,
        min_flesch_reading_ease=80.0,
        allowed_narrative_techniques=["first_person", "third_person_limited", "linear"],
        theme_depth_level=1
    ),
    ReadingLevel.MIDDLE_GRADE: ComplexityProfile(
        profile_id="middle_grade_001",
        reading_level=ReadingLevel.MIDDLE_GRADE,
        target_sentence_length=(8, 18),
        target_word_length=(4.0, 6.0),
        target_paragraph_length=(3, 8),
        vocabulary_level=VocabularyLevel.INTERMEDIATE,
        sentence_complexity=SentenceComplexity.COMPOUND,
        max_flesch_kincaid_grade=7.0,
        min_flesch_reading_ease=65.0,
        allowed_narrative_techniques=["first_person", "third_person", "linear", "simple_flashback"],
        theme_depth_level=2
    ),
    ReadingLevel.YOUNG_ADULT: ComplexityProfile(
        profile_id="young_adult_001",
        reading_level=ReadingLevel.YOUNG_ADULT,
        target_sentence_length=(10, 22),
        target_word_length=(4.5, 7.0),
        target_paragraph_length=(4, 12),
        vocabulary_level=VocabularyLevel.INTERMEDIATE,
        sentence_complexity=SentenceComplexity.COMPLEX,
        max_flesch_kincaid_grade=10.0,
        min_flesch_reading_ease=55.0,
        allowed_narrative_techniques=["all_perspectives", "flashback", "multiple_timelines", "unreliable_narrator"],
        theme_depth_level=3
    ),
    ReadingLevel.ADULT: ComplexityProfile(
        profile_id="adult_001",
        reading_level=ReadingLevel.ADULT,
        target_sentence_length=(12, 28),
        target_word_length=(5.0, 8.0),
        target_paragraph_length=(5, 15),
        vocabulary_level=VocabularyLevel.ADVANCED,
        sentence_complexity=SentenceComplexity.SOPHISTICATED,
        max_flesch_kincaid_grade=14.0,
        min_flesch_reading_ease=40.0,
        allowed_narrative_techniques=["all"],
        theme_depth_level=4
    ),
    ReadingLevel.ACADEMIC: ComplexityProfile(
        profile_id="academic_001",
        reading_level=ReadingLevel.ACADEMIC,
        target_sentence_length=(15, 35),
        target_word_length=(6.0, 10.0),
        target_paragraph_length=(6, 20),
        vocabulary_level=VocabularyLevel.SPECIALIZED,
        sentence_complexity=SentenceComplexity.SOPHISTICATED,
        max_flesch_kincaid_grade=18.0,
        min_flesch_reading_ease=25.0,
        allowed_narrative_techniques=["all", "metafiction", "experimental"],
        theme_depth_level=5
    ),
    ReadingLevel.SIMPLIFIED: ComplexityProfile(
        profile_id="simplified_001",
        reading_level=ReadingLevel.SIMPLIFIED,
        target_sentence_length=(4, 10),
        target_word_length=(3.0, 4.5),
        target_paragraph_length=(2, 4),
        vocabulary_level=VocabularyLevel.BASIC,
        sentence_complexity=SentenceComplexity.SIMPLE,
        max_flesch_kincaid_grade=3.0,
        min_flesch_reading_ease=90.0,
        allowed_narrative_techniques=["first_person", "third_person_limited", "linear"],
        theme_depth_level=1
    )
}


# =============================================================================
# GENRE COMPLEXITY MODIFIERS
# =============================================================================

GENRE_COMPLEXITY_MODIFIERS = {
    "thriller": {
        "sentence_length_modifier": -2,  # Shorter for pace
        "paragraph_length_modifier": -2,
        "vocabulary_adjustment": 0,
        "preferred_techniques": ["cliffhanger_chapters", "short_scenes"]
    },
    "romance": {
        "sentence_length_modifier": 0,
        "paragraph_length_modifier": 1,
        "vocabulary_adjustment": 0,
        "preferred_techniques": ["emotional_beats", "internal_monologue"]
    },
    "fantasy": {
        "sentence_length_modifier": 2,
        "paragraph_length_modifier": 2,
        "vocabulary_adjustment": 1,  # More elaborate vocabulary
        "preferred_techniques": ["worldbuilding_exposition", "epic_scope"]
    },
    "literary": {
        "sentence_length_modifier": 3,
        "paragraph_length_modifier": 3,
        "vocabulary_adjustment": 2,
        "preferred_techniques": ["all", "experimental"]
    },
    "mystery": {
        "sentence_length_modifier": 0,
        "paragraph_length_modifier": 0,
        "vocabulary_adjustment": 0,
        "preferred_techniques": ["red_herrings", "clue_placement"]
    },
    "horror": {
        "sentence_length_modifier": -1,
        "paragraph_length_modifier": -1,
        "vocabulary_adjustment": 0,
        "preferred_techniques": ["atmosphere_building", "tension_pacing"]
    },
    "scifi": {
        "sentence_length_modifier": 1,
        "paragraph_length_modifier": 1,
        "vocabulary_adjustment": 1,
        "preferred_techniques": ["technical_exposition", "worldbuilding"]
    }
}


# =============================================================================
# MAIN CLASS
# =============================================================================

class DynamicComplexityAdjuster:
    """
    Dynamic Complexity Adjustment System

    Analyzes and adjusts text complexity to match target reading levels
    and genre requirements.
    """

    def __init__(self):
        self.profiles: Dict[str, ComplexityProfile] = {}
        self.reports: Dict[str, ComplexityReport] = {}

        # Initialize default profiles
        for level, profile in READING_LEVEL_PROFILES.items():
            self.profiles[profile.profile_id] = profile

    async def analyze_complexity(
        self,
        project_id: str,
        chapters: List[Dict[str, Any]],
        target_level: ReadingLevel,
        genre: Optional[str] = None
    ) -> ComplexityReport:
        """
        Analyze text complexity against target level.
        """
        target_profile = READING_LEVEL_PROFILES.get(target_level)
        if not target_profile:
            target_profile = READING_LEVEL_PROFILES[ReadingLevel.ADULT]

        # Apply genre modifiers
        if genre:
            target_profile = self._apply_genre_modifiers(target_profile, genre)

        # Analyze each chapter
        chapter_analyses = []
        previous_metrics = None

        for chapter in chapters:
            chapter_num = chapter.get("number", len(chapter_analyses) + 1)
            text = chapter.get("text", "")

            analysis = await self._analyze_chapter_complexity(
                text, chapter_num, target_profile, previous_metrics
            )
            chapter_analyses.append(analysis)
            previous_metrics = analysis.metrics

        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(chapter_analyses)

        # Calculate scores
        complexity_score = self._calculate_complexity_score(overall_metrics, target_profile)
        readability_score = self._calculate_readability_score(overall_metrics)
        consistency_score = self._calculate_consistency_score(chapter_analyses)

        # Gather priority adjustments
        all_adjustments = []
        for analysis in chapter_analyses:
            all_adjustments.extend(analysis.adjustments_needed)

        priority_adjustments = sorted(
            all_adjustments, key=lambda x: x.priority, reverse=True
        )[:10]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            chapter_analyses, target_profile, overall_metrics
        )

        report = ComplexityReport(
            report_id=str(uuid.uuid4()),
            project_id=project_id,
            target_profile=target_profile,
            chapter_analyses=chapter_analyses,
            overall_metrics=overall_metrics,
            overall_complexity_score=complexity_score,
            overall_readability_score=readability_score,
            consistency_score=consistency_score,
            total_adjustments_needed=len(all_adjustments),
            priority_adjustments=priority_adjustments,
            recommendations=recommendations,
            created_at=datetime.now()
        )

        self.reports[report.report_id] = report
        return report

    async def analyze_text(
        self,
        text: str,
        target_level: Optional[ReadingLevel] = None
    ) -> Dict[str, Any]:
        """
        Quick complexity analysis of a text.
        """
        metrics = self._calculate_metrics(text)
        detected_level = self._detect_reading_level(metrics)

        result = {
            "metrics": metrics.to_dict(),
            "detected_level": detected_level.value,
            "complexity_score": self._metric_to_complexity_score(metrics),
            "readability_score": self._calculate_readability_score(metrics)
        }

        if target_level:
            target_profile = READING_LEVEL_PROFILES.get(target_level)
            adjustments = self._generate_adjustments(metrics, target_profile)
            result["target_level"] = target_level.value
            result["adjustments_needed"] = [a.to_dict() for a in adjustments]
            result["match_score"] = self._calculate_match_score(metrics, target_profile)

        return result

    async def simplify_text(
        self,
        text: str,
        target_level: ReadingLevel
    ) -> Dict[str, Any]:
        """
        Simplify text to match target reading level.
        """
        target_profile = READING_LEVEL_PROFILES.get(target_level)
        if not target_profile:
            return {"error": "Unknown reading level"}

        original_metrics = self._calculate_metrics(text)
        simplified_text = text

        # Apply simplifications
        simplifications = []

        # Simplify sentences
        if original_metrics.avg_sentence_length > target_profile.target_sentence_length[1]:
            simplified_text, sent_changes = self._simplify_sentences(
                simplified_text, target_profile.target_sentence_length[1]
            )
            simplifications.extend(sent_changes)

        # Simplify vocabulary
        if target_profile.vocabulary_level in [VocabularyLevel.BASIC, VocabularyLevel.INTERMEDIATE]:
            simplified_text, vocab_changes = self._simplify_vocabulary(
                simplified_text, target_profile.vocabulary_level
            )
            simplifications.extend(vocab_changes)

        # Recalculate metrics
        new_metrics = self._calculate_metrics(simplified_text)

        return {
            "original_text": text,
            "simplified_text": simplified_text,
            "original_metrics": original_metrics.to_dict(),
            "new_metrics": new_metrics.to_dict(),
            "target_level": target_level.value,
            "simplifications_made": len(simplifications),
            "simplification_details": simplifications[:20]  # First 20
        }

    async def enhance_complexity(
        self,
        text: str,
        target_level: ReadingLevel
    ) -> Dict[str, Any]:
        """
        Enhance text complexity for more sophisticated audience.
        """
        target_profile = READING_LEVEL_PROFILES.get(target_level)
        if not target_profile:
            return {"error": "Unknown reading level"}

        original_metrics = self._calculate_metrics(text)
        enhanced_text = text

        # Apply enhancements
        enhancements = []

        # Enhance vocabulary
        if target_profile.vocabulary_level in [VocabularyLevel.ADVANCED, VocabularyLevel.LITERARY]:
            enhanced_text, vocab_changes = self._enhance_vocabulary(
                enhanced_text, target_profile.vocabulary_level
            )
            enhancements.extend(vocab_changes)

        # Enhance sentence structure
        if target_profile.sentence_complexity in [SentenceComplexity.COMPLEX, SentenceComplexity.SOPHISTICATED]:
            enhanced_text, struct_changes = self._enhance_sentence_structure(
                enhanced_text, target_profile.sentence_complexity
            )
            enhancements.extend(struct_changes)

        # Recalculate metrics
        new_metrics = self._calculate_metrics(enhanced_text)

        return {
            "original_text": text,
            "enhanced_text": enhanced_text,
            "original_metrics": original_metrics.to_dict(),
            "new_metrics": new_metrics.to_dict(),
            "target_level": target_level.value,
            "enhancements_made": len(enhancements),
            "enhancement_details": enhancements[:20]
        }

    async def get_readability_scores(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive readability scores.
        """
        metrics = self._calculate_metrics(text)

        return {
            "flesch_reading_ease": {
                "score": metrics.flesch_reading_ease,
                "interpretation": self._interpret_flesch_ease(metrics.flesch_reading_ease)
            },
            "flesch_kincaid_grade": {
                "score": metrics.flesch_kincaid_grade,
                "interpretation": f"Poziom klasy szkolnej: {metrics.flesch_kincaid_grade:.1f}"
            },
            "gunning_fog_index": {
                "score": metrics.gunning_fog_index,
                "interpretation": f"Lata edukacji potrzebne: {metrics.gunning_fog_index:.1f}"
            },
            "recommended_audience": self._detect_reading_level(metrics).value,
            "statistics": {
                "avg_sentence_length": metrics.avg_sentence_length,
                "avg_word_length": metrics.avg_word_length,
                "complex_word_ratio": metrics.complex_word_ratio,
                "vocabulary_richness": metrics.vocabulary_richness
            }
        }

    def create_custom_profile(
        self,
        profile_data: Dict[str, Any]
    ) -> ComplexityProfile:
        """
        Create a custom complexity profile.
        """
        profile = ComplexityProfile(
            profile_id=str(uuid.uuid4()),
            reading_level=ReadingLevel(profile_data.get("reading_level", "adult")),
            target_sentence_length=tuple(profile_data.get("target_sentence_length", (12, 28))),
            target_word_length=tuple(profile_data.get("target_word_length", (5.0, 8.0))),
            target_paragraph_length=tuple(profile_data.get("target_paragraph_length", (5, 15))),
            vocabulary_level=VocabularyLevel(profile_data.get("vocabulary_level", "advanced")),
            sentence_complexity=SentenceComplexity(profile_data.get("sentence_complexity", "complex")),
            max_flesch_kincaid_grade=profile_data.get("max_flesch_kincaid_grade", 14.0),
            min_flesch_reading_ease=profile_data.get("min_flesch_reading_ease", 40.0),
            allowed_narrative_techniques=profile_data.get("allowed_narrative_techniques", ["all"]),
            theme_depth_level=profile_data.get("theme_depth_level", 4)
        )

        self.profiles[profile.profile_id] = profile
        return profile

    # =========================================================================
    # METRICS CALCULATION
    # =========================================================================

    def _calculate_metrics(self, text: str) -> ComplexityMetrics:
        """Calculate text complexity metrics."""
        if not text:
            return ComplexityMetrics(
                avg_sentence_length=0, avg_word_length=0, avg_paragraph_length=0,
                vocabulary_richness=0, flesch_reading_ease=100, flesch_kincaid_grade=0,
                gunning_fog_index=0, complex_word_ratio=0, dialogue_ratio=0, passive_voice_ratio=0
            )

        # Split into components
        sentences = self._split_sentences(text)
        words = self._extract_words(text)
        paragraphs = [p for p in text.split("\n\n") if p.strip()]

        # Basic metrics
        total_words = len(words)
        total_sentences = len(sentences)
        total_syllables = sum(self._count_syllables(w) for w in words)

        avg_sentence_length = total_words / max(total_sentences, 1)
        avg_word_length = sum(len(w) for w in words) / max(total_words, 1)
        avg_paragraph_length = total_sentences / max(len(paragraphs), 1)

        # Vocabulary richness (type-token ratio)
        unique_words = set(w.lower() for w in words)
        vocabulary_richness = len(unique_words) / max(total_words, 1)

        # Flesch Reading Ease
        flesch_reading_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (total_syllables / max(total_words, 1)))
        flesch_reading_ease = max(0, min(100, flesch_reading_ease))

        # Flesch-Kincaid Grade Level
        flesch_kincaid_grade = (0.39 * avg_sentence_length) + (11.8 * (total_syllables / max(total_words, 1))) - 15.59
        flesch_kincaid_grade = max(0, flesch_kincaid_grade)

        # Gunning Fog Index
        complex_words = [w for w in words if self._count_syllables(w) >= 3]
        complex_word_ratio = len(complex_words) / max(total_words, 1)
        gunning_fog_index = 0.4 * (avg_sentence_length + 100 * complex_word_ratio)

        # Dialogue ratio
        dialogue_markers = text.count('"') + text.count('—') + text.count('–')
        dialogue_ratio = min(dialogue_markers / max(total_sentences, 1), 1.0)

        # Passive voice ratio (simplified detection)
        passive_patterns = ["został", "była", "było", "byli", "zostały", "jest", "są"]
        passive_count = sum(1 for p in passive_patterns if p in text.lower())
        passive_voice_ratio = min(passive_count / max(total_sentences, 1), 1.0)

        return ComplexityMetrics(
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length,
            avg_paragraph_length=avg_paragraph_length,
            vocabulary_richness=vocabulary_richness,
            flesch_reading_ease=flesch_reading_ease,
            flesch_kincaid_grade=flesch_kincaid_grade,
            gunning_fog_index=gunning_fog_index,
            complex_word_ratio=complex_word_ratio,
            dialogue_ratio=dialogue_ratio,
            passive_voice_ratio=passive_voice_ratio
        )

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (would use proper NLP in production)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text."""
        # Remove punctuation and split
        words = re.findall(r'\b[a-ząćęłńóśźżA-ZĄĆĘŁŃÓŚŹŻ]+\b', text)
        return words

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (Polish approximation)."""
        word = word.lower()
        vowels = "aeiouyąęó"
        count = 0
        prev_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel

        return max(count, 1)

    # =========================================================================
    # ANALYSIS METHODS
    # =========================================================================

    async def _analyze_chapter_complexity(
        self,
        text: str,
        chapter_number: int,
        target_profile: ComplexityProfile,
        previous_metrics: Optional[ComplexityMetrics]
    ) -> ChapterComplexityAnalysis:
        """Analyze a single chapter's complexity."""
        metrics = self._calculate_metrics(text)
        detected_level = self._detect_reading_level(metrics)
        adjustments = self._generate_adjustments(metrics, target_profile)

        complexity_score = self._metric_to_complexity_score(metrics)
        readability_score = self._calculate_readability_score(metrics)

        # Calculate consistency with previous chapter
        consistency = 1.0
        if previous_metrics:
            consistency = self._calculate_metrics_consistency(metrics, previous_metrics)

        return ChapterComplexityAnalysis(
            chapter_number=chapter_number,
            metrics=metrics,
            reading_level_detected=detected_level,
            adjustments_needed=adjustments,
            complexity_score=complexity_score,
            readability_score=readability_score,
            consistency_with_previous=consistency
        )

    def _detect_reading_level(self, metrics: ComplexityMetrics) -> ReadingLevel:
        """Detect reading level from metrics."""
        grade = metrics.flesch_kincaid_grade

        if grade <= 4:
            return ReadingLevel.CHILDREN
        elif grade <= 7:
            return ReadingLevel.MIDDLE_GRADE
        elif grade <= 10:
            return ReadingLevel.YOUNG_ADULT
        elif grade <= 14:
            return ReadingLevel.ADULT
        else:
            return ReadingLevel.ACADEMIC

    def _generate_adjustments(
        self,
        metrics: ComplexityMetrics,
        target_profile: ComplexityProfile
    ) -> List[ComplexityAdjustment]:
        """Generate adjustment recommendations."""
        adjustments = []

        # Sentence length adjustment
        target_sent_len = (target_profile.target_sentence_length[0] + target_profile.target_sentence_length[1]) / 2
        if metrics.avg_sentence_length > target_profile.target_sentence_length[1]:
            adjustments.append(ComplexityAdjustment(
                adjustment_id=str(uuid.uuid4()),
                dimension=ComplexityDimension.SENTENCE_STRUCTURE,
                direction=AdjustmentDirection.SIMPLIFY,
                current_value=metrics.avg_sentence_length,
                target_value=target_sent_len,
                priority=4,
                description="Skróć zdania do docelowej długości",
                example_before="To zdanie jest bardzo długie i zawiera wiele różnych informacji, które mogłyby być rozdzielone.",
                example_after="To zdanie jest długie. Zawiera wiele informacji. Mogłyby być rozdzielone.",
                auto_applicable=True
            ))
        elif metrics.avg_sentence_length < target_profile.target_sentence_length[0]:
            adjustments.append(ComplexityAdjustment(
                adjustment_id=str(uuid.uuid4()),
                dimension=ComplexityDimension.SENTENCE_STRUCTURE,
                direction=AdjustmentDirection.ENHANCE,
                current_value=metrics.avg_sentence_length,
                target_value=target_sent_len,
                priority=3,
                description="Połącz krótkie zdania dla lepszego flow",
                example_before="Szedł. Było ciemno. Bał się.",
                example_after="Szedł przez ciemną ulicę, czując narastający strach.",
                auto_applicable=True
            ))

        # Vocabulary adjustment
        if metrics.complex_word_ratio > 0.3 and target_profile.vocabulary_level in [VocabularyLevel.BASIC, VocabularyLevel.INTERMEDIATE]:
            adjustments.append(ComplexityAdjustment(
                adjustment_id=str(uuid.uuid4()),
                dimension=ComplexityDimension.VOCABULARY,
                direction=AdjustmentDirection.SIMPLIFY,
                current_value=metrics.complex_word_ratio,
                target_value=0.15,
                priority=5,
                description="Uprość słownictwo - zamień złożone słowa na prostsze",
                example_before="Manifestował dezaprobatę",
                example_after="Okazywał niezadowolenie",
                auto_applicable=True
            ))

        # Readability adjustment
        if metrics.flesch_reading_ease < target_profile.min_flesch_reading_ease:
            adjustments.append(ComplexityAdjustment(
                adjustment_id=str(uuid.uuid4()),
                dimension=ComplexityDimension.SENTENCE_STRUCTURE,
                direction=AdjustmentDirection.SIMPLIFY,
                current_value=metrics.flesch_reading_ease,
                target_value=target_profile.min_flesch_reading_ease,
                priority=5,
                description="Popraw ogólną czytelność tekstu",
                example_before="",
                example_after="",
                auto_applicable=False
            ))

        return adjustments

    def _calculate_overall_metrics(
        self,
        chapter_analyses: List[ChapterComplexityAnalysis]
    ) -> ComplexityMetrics:
        """Calculate overall metrics from chapter analyses."""
        if not chapter_analyses:
            return ComplexityMetrics(
                avg_sentence_length=0, avg_word_length=0, avg_paragraph_length=0,
                vocabulary_richness=0, flesch_reading_ease=100, flesch_kincaid_grade=0,
                gunning_fog_index=0, complex_word_ratio=0, dialogue_ratio=0, passive_voice_ratio=0
            )

        return ComplexityMetrics(
            avg_sentence_length=sum(c.metrics.avg_sentence_length for c in chapter_analyses) / len(chapter_analyses),
            avg_word_length=sum(c.metrics.avg_word_length for c in chapter_analyses) / len(chapter_analyses),
            avg_paragraph_length=sum(c.metrics.avg_paragraph_length for c in chapter_analyses) / len(chapter_analyses),
            vocabulary_richness=sum(c.metrics.vocabulary_richness for c in chapter_analyses) / len(chapter_analyses),
            flesch_reading_ease=sum(c.metrics.flesch_reading_ease for c in chapter_analyses) / len(chapter_analyses),
            flesch_kincaid_grade=sum(c.metrics.flesch_kincaid_grade for c in chapter_analyses) / len(chapter_analyses),
            gunning_fog_index=sum(c.metrics.gunning_fog_index for c in chapter_analyses) / len(chapter_analyses),
            complex_word_ratio=sum(c.metrics.complex_word_ratio for c in chapter_analyses) / len(chapter_analyses),
            dialogue_ratio=sum(c.metrics.dialogue_ratio for c in chapter_analyses) / len(chapter_analyses),
            passive_voice_ratio=sum(c.metrics.passive_voice_ratio for c in chapter_analyses) / len(chapter_analyses)
        )

    def _calculate_complexity_score(
        self,
        metrics: ComplexityMetrics,
        target_profile: ComplexityProfile
    ) -> float:
        """Calculate how well metrics match target complexity."""
        scores = []

        # Sentence length match
        target_sent = (target_profile.target_sentence_length[0] + target_profile.target_sentence_length[1]) / 2
        sent_diff = abs(metrics.avg_sentence_length - target_sent) / target_sent
        scores.append(max(0, 100 - sent_diff * 50))

        # Grade level match
        grade_diff = abs(metrics.flesch_kincaid_grade - target_profile.max_flesch_kincaid_grade)
        scores.append(max(0, 100 - grade_diff * 10))

        # Reading ease match
        ease_diff = abs(metrics.flesch_reading_ease - target_profile.min_flesch_reading_ease)
        scores.append(max(0, 100 - ease_diff))

        return sum(scores) / len(scores)

    def _calculate_readability_score(self, metrics: ComplexityMetrics) -> float:
        """Calculate readability score from metrics."""
        # Normalize Flesch Reading Ease to 0-100
        return max(0, min(100, metrics.flesch_reading_ease))

    def _metric_to_complexity_score(self, metrics: ComplexityMetrics) -> float:
        """Convert metrics to a single complexity score."""
        # Higher values = more complex
        score = (
            metrics.avg_sentence_length * 2 +
            metrics.flesch_kincaid_grade * 5 +
            metrics.complex_word_ratio * 100 +
            (100 - metrics.flesch_reading_ease)
        ) / 4

        return max(0, min(100, score))

    def _calculate_consistency_score(
        self,
        chapter_analyses: List[ChapterComplexityAnalysis]
    ) -> float:
        """Calculate consistency across chapters."""
        if len(chapter_analyses) < 2:
            return 1.0

        consistencies = [c.consistency_with_previous for c in chapter_analyses[1:]]
        return sum(consistencies) / len(consistencies)

    def _calculate_metrics_consistency(
        self,
        current: ComplexityMetrics,
        previous: ComplexityMetrics
    ) -> float:
        """Calculate consistency between two sets of metrics."""
        diffs = [
            abs(current.avg_sentence_length - previous.avg_sentence_length) / max(previous.avg_sentence_length, 1),
            abs(current.flesch_reading_ease - previous.flesch_reading_ease) / 100,
            abs(current.vocabulary_richness - previous.vocabulary_richness)
        ]

        avg_diff = sum(diffs) / len(diffs)
        return max(0, 1 - avg_diff)

    def _calculate_match_score(
        self,
        metrics: ComplexityMetrics,
        target_profile: ComplexityProfile
    ) -> float:
        """Calculate how well text matches target profile."""
        return self._calculate_complexity_score(metrics, target_profile) / 100

    # =========================================================================
    # TEXT MODIFICATION METHODS
    # =========================================================================

    def _simplify_sentences(
        self,
        text: str,
        max_length: int
    ) -> Tuple[str, List[Dict]]:
        """Simplify long sentences."""
        changes = []
        sentences = self._split_sentences(text)
        simplified_sentences = []

        for sentence in sentences:
            words = sentence.split()
            if len(words) > max_length:
                # Split at conjunction or comma
                parts = re.split(r',\s*|\s+i\s+|\s+oraz\s+|\s+ale\s+', sentence)
                if len(parts) > 1:
                    simplified_sentences.extend([p.strip() for p in parts if p.strip()])
                    changes.append({
                        "type": "sentence_split",
                        "original": sentence[:50] + "...",
                        "result": f"Podzielono na {len(parts)} zdań"
                    })
                else:
                    simplified_sentences.append(sentence)
            else:
                simplified_sentences.append(sentence)

        return ". ".join(simplified_sentences) + ".", changes

    def _simplify_vocabulary(
        self,
        text: str,
        target_level: VocabularyLevel
    ) -> Tuple[str, List[Dict]]:
        """Simplify vocabulary."""
        changes = []

        # Simple word replacements (would use comprehensive dictionary in production)
        replacements = {
            "manifestował": "pokazywał",
            "dezaprobata": "niezadowolenie",
            "konstatować": "stwierdzić",
            "implementować": "wprowadzać",
            "egzystencja": "życie",
            "permanentny": "stały",
            "fundamentalny": "podstawowy",
            "transformacja": "zmiana"
        }

        modified_text = text
        for complex_word, simple_word in replacements.items():
            if complex_word in modified_text.lower():
                modified_text = re.sub(
                    complex_word, simple_word, modified_text, flags=re.IGNORECASE
                )
                changes.append({
                    "type": "vocabulary_simplification",
                    "original": complex_word,
                    "replacement": simple_word
                })

        return modified_text, changes

    def _enhance_vocabulary(
        self,
        text: str,
        target_level: VocabularyLevel
    ) -> Tuple[str, List[Dict]]:
        """Enhance vocabulary complexity."""
        changes = []

        # Simple word enhancements (would use comprehensive dictionary in production)
        enhancements = {
            "pokazywał": "manifestował",
            "niezadowolenie": "dezaprobatę",
            "stwierdzić": "konstatować",
            "wprowadzać": "implementować",
            "życie": "egzystencję",
            "stały": "permanentny",
            "podstawowy": "fundamentalny",
            "zmiana": "transformacja"
        }

        modified_text = text
        for simple_word, complex_word in enhancements.items():
            if simple_word in modified_text.lower():
                modified_text = re.sub(
                    simple_word, complex_word, modified_text, flags=re.IGNORECASE
                )
                changes.append({
                    "type": "vocabulary_enhancement",
                    "original": simple_word,
                    "replacement": complex_word
                })

        return modified_text, changes

    def _enhance_sentence_structure(
        self,
        text: str,
        target_complexity: SentenceComplexity
    ) -> Tuple[str, List[Dict]]:
        """Enhance sentence structure complexity."""
        changes = []
        # Would implement sentence combining and subordination in production
        return text, changes

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _apply_genre_modifiers(
        self,
        profile: ComplexityProfile,
        genre: str
    ) -> ComplexityProfile:
        """Apply genre-specific modifiers to profile."""
        modifiers = GENRE_COMPLEXITY_MODIFIERS.get(genre.lower(), {})

        if not modifiers:
            return profile

        # Create modified profile
        sent_mod = modifiers.get("sentence_length_modifier", 0)
        para_mod = modifiers.get("paragraph_length_modifier", 0)

        return ComplexityProfile(
            profile_id=profile.profile_id,
            reading_level=profile.reading_level,
            target_sentence_length=(
                profile.target_sentence_length[0] + sent_mod,
                profile.target_sentence_length[1] + sent_mod
            ),
            target_word_length=profile.target_word_length,
            target_paragraph_length=(
                profile.target_paragraph_length[0] + para_mod,
                profile.target_paragraph_length[1] + para_mod
            ),
            vocabulary_level=profile.vocabulary_level,
            sentence_complexity=profile.sentence_complexity,
            max_flesch_kincaid_grade=profile.max_flesch_kincaid_grade,
            min_flesch_reading_ease=profile.min_flesch_reading_ease,
            allowed_narrative_techniques=profile.allowed_narrative_techniques,
            theme_depth_level=profile.theme_depth_level
        )

    def _interpret_flesch_ease(self, score: float) -> str:
        """Interpret Flesch Reading Ease score."""
        if score >= 90:
            return "Bardzo łatwy - poziom podstawówki"
        elif score >= 80:
            return "Łatwy - zrozumiały dla 11-latka"
        elif score >= 70:
            return "Dość łatwy - zrozumiały dla 13-latka"
        elif score >= 60:
            return "Standardowy - zrozumiały dla 15-latka"
        elif score >= 50:
            return "Dość trudny - poziom licealny"
        elif score >= 30:
            return "Trudny - poziom akademicki"
        else:
            return "Bardzo trudny - poziom specjalistyczny"

    def _generate_recommendations(
        self,
        chapter_analyses: List[ChapterComplexityAnalysis],
        target_profile: ComplexityProfile,
        overall_metrics: ComplexityMetrics
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Check overall readability
        if overall_metrics.flesch_reading_ease < target_profile.min_flesch_reading_ease:
            recommendations.append(
                f"Ogólna czytelność ({overall_metrics.flesch_reading_ease:.1f}) jest poniżej celu ({target_profile.min_flesch_reading_ease}). "
                "Uprość zdania i słownictwo."
            )

        # Check grade level
        if overall_metrics.flesch_kincaid_grade > target_profile.max_flesch_kincaid_grade:
            recommendations.append(
                f"Poziom trudności ({overall_metrics.flesch_kincaid_grade:.1f}) przekracza cel ({target_profile.max_flesch_kincaid_grade}). "
                "Rozważ uproszczenie tekstu."
            )

        # Check consistency
        inconsistent_chapters = [
            c for c in chapter_analyses
            if c.consistency_with_previous < 0.7
        ]
        if inconsistent_chapters:
            chapters_str = ", ".join(str(c.chapter_number) for c in inconsistent_chapters)
            recommendations.append(
                f"Niespójność stylistyczna w rozdziałach: {chapters_str}. "
                "Wyrównaj poziom złożoności."
            )

        # Check vocabulary richness
        if overall_metrics.vocabulary_richness < 0.3:
            recommendations.append(
                "Niskie bogactwo słownictwa. Rozważ użycie bardziej zróżnicowanych słów."
            )
        elif overall_metrics.vocabulary_richness > 0.7:
            recommendations.append(
                "Bardzo wysokie bogactwo słownictwa. Może utrudniać czytanie."
            )

        return recommendations

    # =========================================================================
    # PUBLIC GETTERS
    # =========================================================================

    def get_report(self, report_id: str) -> Optional[ComplexityReport]:
        """Get a complexity report by ID."""
        return self.reports.get(report_id)

    def get_profile(self, profile_id: str) -> Optional[ComplexityProfile]:
        """Get a complexity profile by ID."""
        return self.profiles.get(profile_id)

    def list_reading_levels(self) -> List[Dict[str, Any]]:
        """List all reading levels with descriptions."""
        return [
            {
                "level": level.value,
                "description": self._get_level_description(level),
                "profile": READING_LEVEL_PROFILES[level].to_dict()
            }
            for level in ReadingLevel
        ]

    def _get_level_description(self, level: ReadingLevel) -> str:
        """Get description for reading level."""
        descriptions = {
            ReadingLevel.CHILDREN: "Dla dzieci 6-10 lat",
            ReadingLevel.MIDDLE_GRADE: "Dla młodzieży 10-14 lat",
            ReadingLevel.YOUNG_ADULT: "Dla młodzieży 14-18 lat",
            ReadingLevel.ADULT: "Dla dorosłych czytelników",
            ReadingLevel.ACADEMIC: "Poziom akademicki/specjalistyczny",
            ReadingLevel.SIMPLIFIED: "Uproszczony dla łatwego czytania"
        }
        return descriptions.get(level, "")


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_complexity_adjuster: Optional[DynamicComplexityAdjuster] = None


def get_complexity_adjuster() -> DynamicComplexityAdjuster:
    """Get the singleton complexity adjuster instance."""
    global _complexity_adjuster
    if _complexity_adjuster is None:
        _complexity_adjuster = DynamicComplexityAdjuster()
    return _complexity_adjuster

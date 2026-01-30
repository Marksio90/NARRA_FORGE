"""
Emotional Resonance Engine (ERE) - NarraForge 3.0

Advanced emotional mapping and optimization system for narrative content.
Creates and analyzes 12-dimensional emotional vectors for each paragraph,
predicts reader emotional trajectory, and optimizes for maximum cathartic impact.

Based on:
- Plutchik's Wheel of Emotions
- Narrative Arc Theory
- Psychological Response Models
- Reader Experience Optimization

Features:
1. 12-dimensional emotion vectors per paragraph
2. Emotional trajectory prediction
3. Intensity calibration per genre
4. Cathartic moment detection and optimization
5. Flat sequence detection and correction
6. Emotional arc analysis and recommendations
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import math
from collections import defaultdict

from app.services.ai_service import AIService
from app.models.project import GenreType

logger = logging.getLogger(__name__)


# =============================================================================
# EMOTION DEFINITIONS
# =============================================================================

class EmotionDimension(str, Enum):
    """12 dimensions of emotional experience in narrative"""
    FEAR = "fear"                   # Strach - danger, threat, anxiety
    HOPE = "hope"                   # Nadzieja - anticipation of positive outcome
    SADNESS = "sadness"             # Smutek - loss, grief, melancholy
    JOY = "joy"                     # Radość - happiness, triumph, satisfaction
    ANGER = "anger"                 # Gniew - frustration, injustice, rage
    SURPRISE = "surprise"           # Zaskoczenie - unexpected turns, revelations
    SHAME = "shame"                 # Wstyd - embarrassment, guilt, regret
    PRIDE = "pride"                 # Duma - achievement, dignity, honor
    LONGING = "longing"             # Tęsknota - desire, nostalgia, yearning
    RELIEF = "relief"               # Ulga - release of tension, safety
    TENSION = "tension"             # Napięcie - suspense, anticipation of conflict
    CATHARSIS = "catharsis"         # Katharsis - emotional release, transformation


class EmotionalArcType(str, Enum):
    """Types of emotional arcs in narrative"""
    RISE = "rise"                   # Building positive emotions
    FALL = "fall"                   # Declining into negative
    RISE_FALL = "rise_fall"         # Classic tragedy arc
    FALL_RISE = "fall_rise"         # Redemption/triumph arc
    OSCILLATION = "oscillation"     # Alternating highs and lows
    PLATEAU = "plateau"             # Sustained emotional state
    CRESCENDO = "crescendo"         # Building to climax
    RESOLUTION = "resolution"       # Post-climax settling


class EmotionalIssueType(str, Enum):
    """Types of emotional issues detected"""
    FLAT_SEQUENCE = "flat_sequence"             # Too little variation
    JARRING_TRANSITION = "jarring_transition"   # Too sudden shift
    MISSING_BUILDUP = "missing_buildup"         # Climax without preparation
    UNEARNED_EMOTION = "unearned_emotion"       # Emotion without cause
    EMOTIONAL_WHIPLASH = "emotional_whiplash"   # Too many rapid changes
    MONOTONOUS_TONE = "monotonous_tone"         # Same emotion too long
    WEAK_CATHARSIS = "weak_catharsis"           # Unsatisfying climax
    PACING_MISMATCH = "pacing_mismatch"         # Speed doesn't match emotion


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class EmotionVector:
    """12-dimensional emotion vector for a text segment"""
    fear: float = 0.0
    hope: float = 0.0
    sadness: float = 0.0
    joy: float = 0.0
    anger: float = 0.0
    surprise: float = 0.0
    shame: float = 0.0
    pride: float = 0.0
    longing: float = 0.0
    relief: float = 0.0
    tension: float = 0.0
    catharsis: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "fear": round(self.fear, 3),
            "hope": round(self.hope, 3),
            "sadness": round(self.sadness, 3),
            "joy": round(self.joy, 3),
            "anger": round(self.anger, 3),
            "surprise": round(self.surprise, 3),
            "shame": round(self.shame, 3),
            "pride": round(self.pride, 3),
            "longing": round(self.longing, 3),
            "relief": round(self.relief, 3),
            "tension": round(self.tension, 3),
            "catharsis": round(self.catharsis, 3)
        }

    @property
    def magnitude(self) -> float:
        """Total emotional intensity"""
        values = [self.fear, self.hope, self.sadness, self.joy, self.anger,
                  self.surprise, self.shame, self.pride, self.longing,
                  self.relief, self.tension, self.catharsis]
        return math.sqrt(sum(v**2 for v in values))

    @property
    def dominant_emotion(self) -> str:
        """The strongest emotion in this vector"""
        emotions = self.to_dict()
        return max(emotions, key=emotions.get)

    @property
    def valence(self) -> float:
        """Overall positive/negative balance (-1 to 1)"""
        positive = self.hope + self.joy + self.pride + self.relief + self.catharsis
        negative = self.fear + self.sadness + self.anger + self.shame
        total = positive + negative
        if total == 0:
            return 0
        return (positive - negative) / total

    def distance_to(self, other: 'EmotionVector') -> float:
        """Euclidean distance to another emotion vector"""
        self_dict = self.to_dict()
        other_dict = other.to_dict()
        return math.sqrt(sum(
            (self_dict[k] - other_dict[k])**2
            for k in self_dict.keys()
        ))


@dataclass
class ParagraphAnalysis:
    """Emotional analysis of a single paragraph"""
    paragraph_index: int
    text_preview: str  # First 100 chars
    emotion_vector: EmotionVector
    dominant_emotion: str
    intensity: float  # 0-1 overall intensity
    valence: float  # -1 to 1 (negative to positive)
    pacing_suggestion: str  # slow/medium/fast
    narrative_beat: str  # What this paragraph does narratively

    def to_dict(self) -> Dict:
        return {
            "paragraph_index": self.paragraph_index,
            "text_preview": self.text_preview,
            "emotion_vector": self.emotion_vector.to_dict(),
            "dominant_emotion": self.dominant_emotion,
            "intensity": round(self.intensity, 3),
            "valence": round(self.valence, 3),
            "pacing_suggestion": self.pacing_suggestion,
            "narrative_beat": self.narrative_beat
        }


@dataclass
class EmotionalIssue:
    """A detected emotional issue in the narrative"""
    issue_type: EmotionalIssueType
    severity: str  # "critical", "major", "minor"
    location: str  # e.g., "paragraphs 5-8", "chapter transition"
    description: str
    suggestion: str
    affected_paragraphs: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "issue_type": self.issue_type.value,
            "severity": self.severity,
            "location": self.location,
            "description": self.description,
            "suggestion": self.suggestion,
            "affected_paragraphs": self.affected_paragraphs
        }


@dataclass
class CatharticMoment:
    """A detected or planned cathartic moment"""
    paragraph_index: int
    catharsis_type: str  # "revelation", "reunion", "victory", "sacrifice", "transformation"
    intensity: float  # 0-1
    buildup_adequate: bool
    release_adequate: bool
    improvement_suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "paragraph_index": self.paragraph_index,
            "catharsis_type": self.catharsis_type,
            "intensity": round(self.intensity, 3),
            "buildup_adequate": self.buildup_adequate,
            "release_adequate": self.release_adequate,
            "improvement_suggestions": self.improvement_suggestions
        }


@dataclass
class EmotionalTrajectory:
    """Complete emotional trajectory of a narrative segment"""
    paragraphs: List[ParagraphAnalysis]
    arc_type: EmotionalArcType
    overall_valence: float
    average_intensity: float
    peak_moments: List[int]  # Paragraph indices of emotional peaks
    valley_moments: List[int]  # Paragraph indices of emotional lows
    cathartic_moments: List[CatharticMoment]
    issues: List[EmotionalIssue]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            "paragraphs": [p.to_dict() for p in self.paragraphs],
            "arc_type": self.arc_type.value,
            "overall_valence": round(self.overall_valence, 3),
            "average_intensity": round(self.average_intensity, 3),
            "peak_moments": self.peak_moments,
            "valley_moments": self.valley_moments,
            "cathartic_moments": [c.to_dict() for c in self.cathartic_moments],
            "issues": [i.to_dict() for i in self.issues],
            "recommendations": self.recommendations
        }


@dataclass
class EmotionalResonanceReport:
    """Complete emotional analysis report"""
    total_paragraphs: int
    trajectory: EmotionalTrajectory
    emotion_heatmap: Dict[str, List[float]]  # emotion -> values per paragraph
    genre_calibration: Dict[str, float]  # How well calibrated for genre
    bestseller_emotional_score: float  # 0-100
    summary: str

    def to_dict(self) -> Dict:
        return {
            "total_paragraphs": self.total_paragraphs,
            "trajectory": self.trajectory.to_dict(),
            "emotion_heatmap": self.emotion_heatmap,
            "genre_calibration": self.genre_calibration,
            "bestseller_emotional_score": round(self.bestseller_emotional_score, 1),
            "summary": self.summary
        }


# =============================================================================
# GENRE EMOTIONAL PROFILES
# =============================================================================

GENRE_EMOTIONAL_PROFILES: Dict[str, Dict[str, Any]] = {
    "thriller": {
        "primary_emotions": ["tension", "fear", "surprise"],
        "secondary_emotions": ["relief", "hope"],
        "ideal_intensity_range": (0.6, 0.9),
        "tension_baseline": 0.5,
        "catharsis_frequency": "high",
        "emotional_volatility": "high",
        "pacing": "fast"
    },
    "horror": {
        "primary_emotions": ["fear", "tension", "surprise"],
        "secondary_emotions": ["sadness", "longing"],
        "ideal_intensity_range": (0.5, 0.95),
        "tension_baseline": 0.6,
        "catharsis_frequency": "medium",
        "emotional_volatility": "medium",
        "pacing": "building"
    },
    "romance": {
        "primary_emotions": ["longing", "joy", "hope"],
        "secondary_emotions": ["sadness", "pride"],
        "ideal_intensity_range": (0.4, 0.85),
        "tension_baseline": 0.3,
        "catharsis_frequency": "medium",
        "emotional_volatility": "medium",
        "pacing": "varied"
    },
    "fantasy": {
        "primary_emotions": ["hope", "fear", "pride"],
        "secondary_emotions": ["joy", "longing", "catharsis"],
        "ideal_intensity_range": (0.4, 0.9),
        "tension_baseline": 0.4,
        "catharsis_frequency": "medium",
        "emotional_volatility": "high",
        "pacing": "epic"
    },
    "sci_fi": {
        "primary_emotions": ["hope", "fear", "surprise"],
        "secondary_emotions": ["longing", "tension"],
        "ideal_intensity_range": (0.3, 0.85),
        "tension_baseline": 0.4,
        "catharsis_frequency": "medium",
        "emotional_volatility": "medium",
        "pacing": "varied"
    },
    "mystery": {
        "primary_emotions": ["tension", "surprise", "fear"],
        "secondary_emotions": ["relief", "pride"],
        "ideal_intensity_range": (0.4, 0.85),
        "tension_baseline": 0.5,
        "catharsis_frequency": "low",
        "emotional_volatility": "medium",
        "pacing": "building"
    },
    "drama": {
        "primary_emotions": ["sadness", "hope", "anger"],
        "secondary_emotions": ["shame", "pride", "catharsis"],
        "ideal_intensity_range": (0.5, 0.9),
        "tension_baseline": 0.4,
        "catharsis_frequency": "high",
        "emotional_volatility": "high",
        "pacing": "emotional"
    },
    "comedy": {
        "primary_emotions": ["joy", "surprise", "relief"],
        "secondary_emotions": ["shame", "pride"],
        "ideal_intensity_range": (0.3, 0.7),
        "tension_baseline": 0.2,
        "catharsis_frequency": "low",
        "emotional_volatility": "high",
        "pacing": "fast"
    },
    "religious": {
        "primary_emotions": ["hope", "catharsis", "longing"],
        "secondary_emotions": ["fear", "joy", "pride"],
        "ideal_intensity_range": (0.4, 0.85),
        "tension_baseline": 0.3,
        "catharsis_frequency": "high",
        "emotional_volatility": "medium",
        "pacing": "contemplative"
    }
}


# =============================================================================
# EMOTIONAL RESONANCE ENGINE
# =============================================================================

class EmotionalResonanceEngine:
    """
    Advanced emotional analysis and optimization engine.

    Analyzes text for emotional content, tracks emotional trajectories,
    detects issues, and provides optimization recommendations.
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()
        self._genre_profiles = GENRE_EMOTIONAL_PROFILES

    # =========================================================================
    # MAIN ANALYSIS METHODS
    # =========================================================================

    async def analyze_emotional_resonance(
        self,
        content: str,
        genre: GenreType,
        chapter_number: Optional[int] = None,
        is_climax: bool = False
    ) -> EmotionalResonanceReport:
        """
        Comprehensive emotional analysis of text content.

        Args:
            content: Text content to analyze
            genre: Genre for calibration
            chapter_number: Optional chapter number for context
            is_climax: Whether this is a climactic chapter

        Returns:
            EmotionalResonanceReport with full analysis
        """
        genre_str = genre.value.lower()
        genre_profile = self._genre_profiles.get(genre_str, self._genre_profiles["drama"])

        # Split into paragraphs
        paragraphs = self._split_into_paragraphs(content)

        if not paragraphs:
            return self._empty_report()

        # Analyze each paragraph
        paragraph_analyses = []
        for i, para in enumerate(paragraphs):
            if len(para.strip()) < 20:  # Skip very short paragraphs
                continue
            analysis = await self._analyze_paragraph(para, i, genre_str)
            paragraph_analyses.append(analysis)

        if not paragraph_analyses:
            return self._empty_report()

        # Build trajectory
        trajectory = self._build_trajectory(paragraph_analyses, genre_profile, is_climax)

        # Create emotion heatmap
        heatmap = self._create_heatmap(paragraph_analyses)

        # Calculate genre calibration
        calibration = self._calculate_genre_calibration(paragraph_analyses, genre_profile)

        # Calculate overall emotional score
        score = self._calculate_emotional_score(trajectory, calibration, genre_profile)

        # Generate summary
        summary = self._generate_summary(trajectory, score, genre_str)

        return EmotionalResonanceReport(
            total_paragraphs=len(paragraph_analyses),
            trajectory=trajectory,
            emotion_heatmap=heatmap,
            genre_calibration=calibration,
            bestseller_emotional_score=score,
            summary=summary
        )

    async def analyze_paragraph_vector(
        self,
        paragraph: str,
        genre: str = "drama"
    ) -> EmotionVector:
        """
        Analyze a single paragraph and return its emotion vector.
        """
        analysis = await self._analyze_paragraph(paragraph, 0, genre)
        return analysis.emotion_vector

    async def predict_reader_state(
        self,
        paragraphs_so_far: List[str],
        genre: str
    ) -> Dict[str, Any]:
        """
        Predict the reader's emotional state at this point in the narrative.
        """
        if not paragraphs_so_far:
            return {
                "current_emotion": "neutral",
                "tension_level": 0.0,
                "engagement_level": 0.5,
                "expectations": [],
                "vulnerability_to": []
            }

        # Analyze recent paragraphs
        recent = paragraphs_so_far[-5:]  # Last 5 paragraphs
        analyses = []
        for i, para in enumerate(recent):
            if para.strip():
                analysis = await self._analyze_paragraph(para, i, genre)
                analyses.append(analysis)

        if not analyses:
            return self._default_reader_state()

        # Calculate current state
        latest = analyses[-1]
        avg_tension = sum(a.emotion_vector.tension for a in analyses) / len(analyses)
        avg_intensity = sum(a.intensity for a in analyses) / len(analyses)

        # Determine expectations based on trajectory
        expectations = self._predict_expectations(analyses, genre)

        # Determine vulnerabilities (what would hit hard emotionally)
        vulnerabilities = self._determine_vulnerabilities(analyses)

        return {
            "current_emotion": latest.dominant_emotion,
            "tension_level": round(avg_tension, 2),
            "engagement_level": round(min(1.0, avg_intensity * 1.2), 2),
            "expectations": expectations,
            "vulnerability_to": vulnerabilities,
            "emotional_momentum": self._calculate_momentum(analyses)
        }

    async def optimize_emotional_impact(
        self,
        content: str,
        genre: GenreType,
        target_emotion: Optional[str] = None,
        target_intensity: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Provide specific recommendations to optimize emotional impact.
        """
        report = await self.analyze_emotional_resonance(content, genre)

        optimizations = {
            "current_score": report.bestseller_emotional_score,
            "target_score": 85.0,
            "specific_changes": [],
            "general_recommendations": report.trajectory.recommendations
        }

        # Analyze issues and provide fixes
        for issue in report.trajectory.issues:
            fix = self._generate_fix_for_issue(issue, genre.value.lower())
            optimizations["specific_changes"].append({
                "issue": issue.description,
                "location": issue.location,
                "fix": fix
            })

        # If target emotion specified
        if target_emotion:
            boost_rec = self._recommend_emotion_boost(
                target_emotion,
                report.trajectory.paragraphs,
                target_intensity or 0.7
            )
            optimizations["emotion_boost"] = boost_rec

        return optimizations

    # =========================================================================
    # PARAGRAPH ANALYSIS
    # =========================================================================

    async def _analyze_paragraph(
        self,
        paragraph: str,
        index: int,
        genre: str
    ) -> ParagraphAnalysis:
        """Analyze a single paragraph for emotional content."""
        prompt = f"""Przeanalizuj emocjonalną zawartość tego akapitu narracji ({genre}):

"{paragraph[:800]}"

Oceń intensywność każdej emocji na skali 0.0-1.0:
- fear (strach, lęk, niepokój)
- hope (nadzieja, optymizm)
- sadness (smutek, żal, melancholia)
- joy (radość, szczęście, triumf)
- anger (gniew, frustracja, złość)
- surprise (zaskoczenie, szok)
- shame (wstyd, poczucie winy)
- pride (duma, godność)
- longing (tęsknota, pragnienie)
- relief (ulga, ukojenie)
- tension (napięcie, suspens)
- catharsis (katharsis, emocjonalne oczyszczenie)

Odpowiedz TYLKO w JSON:
{{
    "emotions": {{
        "fear": 0.0,
        "hope": 0.0,
        "sadness": 0.0,
        "joy": 0.0,
        "anger": 0.0,
        "surprise": 0.0,
        "shame": 0.0,
        "pride": 0.0,
        "longing": 0.0,
        "relief": 0.0,
        "tension": 0.0,
        "catharsis": 0.0
    }},
    "dominant": "najsilniejsza emocja",
    "intensity": 0.0-1.0,
    "pacing": "slow/medium/fast",
    "narrative_beat": "co ten akapit robi narracyjnie"
}}"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=1,
                max_tokens=500,
                temperature=0.2
            )

            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                emotions = data.get("emotions", {})

                vector = EmotionVector(
                    fear=float(emotions.get("fear", 0)),
                    hope=float(emotions.get("hope", 0)),
                    sadness=float(emotions.get("sadness", 0)),
                    joy=float(emotions.get("joy", 0)),
                    anger=float(emotions.get("anger", 0)),
                    surprise=float(emotions.get("surprise", 0)),
                    shame=float(emotions.get("shame", 0)),
                    pride=float(emotions.get("pride", 0)),
                    longing=float(emotions.get("longing", 0)),
                    relief=float(emotions.get("relief", 0)),
                    tension=float(emotions.get("tension", 0)),
                    catharsis=float(emotions.get("catharsis", 0))
                )

                return ParagraphAnalysis(
                    paragraph_index=index,
                    text_preview=paragraph[:100],
                    emotion_vector=vector,
                    dominant_emotion=data.get("dominant", vector.dominant_emotion),
                    intensity=float(data.get("intensity", vector.magnitude / 3.46)),  # Normalize
                    valence=vector.valence,
                    pacing_suggestion=data.get("pacing", "medium"),
                    narrative_beat=data.get("narrative_beat", "continuation")
                )

        except Exception as e:
            logger.warning(f"Error analyzing paragraph: {e}")

        # Return default analysis
        return self._default_paragraph_analysis(paragraph, index)

    def _default_paragraph_analysis(self, paragraph: str, index: int) -> ParagraphAnalysis:
        """Return default analysis when AI fails."""
        return ParagraphAnalysis(
            paragraph_index=index,
            text_preview=paragraph[:100],
            emotion_vector=EmotionVector(tension=0.3),
            dominant_emotion="neutral",
            intensity=0.3,
            valence=0.0,
            pacing_suggestion="medium",
            narrative_beat="continuation"
        )

    # =========================================================================
    # TRAJECTORY BUILDING
    # =========================================================================

    def _build_trajectory(
        self,
        paragraphs: List[ParagraphAnalysis],
        genre_profile: Dict,
        is_climax: bool
    ) -> EmotionalTrajectory:
        """Build emotional trajectory from paragraph analyses."""
        # Calculate overall metrics
        overall_valence = sum(p.valence for p in paragraphs) / len(paragraphs)
        average_intensity = sum(p.intensity for p in paragraphs) / len(paragraphs)

        # Find peaks and valleys
        intensities = [p.intensity for p in paragraphs]
        peaks = self._find_peaks(intensities)
        valleys = self._find_valleys(intensities)

        # Determine arc type
        arc_type = self._determine_arc_type(paragraphs, is_climax)

        # Detect cathartic moments
        cathartic_moments = self._detect_cathartic_moments(paragraphs)

        # Detect issues
        issues = self._detect_issues(paragraphs, genre_profile)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            paragraphs, issues, genre_profile, is_climax
        )

        return EmotionalTrajectory(
            paragraphs=paragraphs,
            arc_type=arc_type,
            overall_valence=overall_valence,
            average_intensity=average_intensity,
            peak_moments=peaks,
            valley_moments=valleys,
            cathartic_moments=cathartic_moments,
            issues=issues,
            recommendations=recommendations
        )

    def _find_peaks(self, intensities: List[float]) -> List[int]:
        """Find local maxima in intensity."""
        peaks = []
        for i in range(1, len(intensities) - 1):
            if intensities[i] > intensities[i-1] and intensities[i] > intensities[i+1]:
                if intensities[i] > 0.6:  # Only significant peaks
                    peaks.append(i)
        return peaks

    def _find_valleys(self, intensities: List[float]) -> List[int]:
        """Find local minima in intensity."""
        valleys = []
        for i in range(1, len(intensities) - 1):
            if intensities[i] < intensities[i-1] and intensities[i] < intensities[i+1]:
                if intensities[i] < 0.4:  # Only significant valleys
                    valleys.append(i)
        return valleys

    def _determine_arc_type(
        self,
        paragraphs: List[ParagraphAnalysis],
        is_climax: bool
    ) -> EmotionalArcType:
        """Determine the emotional arc type."""
        if len(paragraphs) < 3:
            return EmotionalArcType.PLATEAU

        valences = [p.valence for p in paragraphs]
        start = sum(valences[:len(valences)//4]) / (len(valences)//4 or 1)
        end = sum(valences[-(len(valences)//4):]) / (len(valences)//4 or 1)

        if is_climax:
            return EmotionalArcType.CRESCENDO

        diff = end - start

        # Check for oscillation
        changes = sum(1 for i in range(1, len(valences))
                      if abs(valences[i] - valences[i-1]) > 0.3)
        if changes > len(valences) * 0.4:
            return EmotionalArcType.OSCILLATION

        # Check for monotony
        if all(abs(v - valences[0]) < 0.2 for v in valences):
            return EmotionalArcType.PLATEAU

        # Check direction
        if diff > 0.3:
            if start < -0.2:
                return EmotionalArcType.FALL_RISE
            return EmotionalArcType.RISE
        elif diff < -0.3:
            if start > 0.2:
                return EmotionalArcType.RISE_FALL
            return EmotionalArcType.FALL
        else:
            return EmotionalArcType.RESOLUTION

    def _detect_cathartic_moments(
        self,
        paragraphs: List[ParagraphAnalysis]
    ) -> List[CatharticMoment]:
        """Detect and analyze cathartic moments."""
        moments = []

        for i, para in enumerate(paragraphs):
            if para.emotion_vector.catharsis > 0.5 or para.intensity > 0.8:
                # Check buildup
                buildup_ok = True
                if i > 2:
                    prev_tensions = [p.emotion_vector.tension for p in paragraphs[max(0, i-3):i]]
                    buildup_ok = any(t > 0.4 for t in prev_tensions)

                # Check release
                release_ok = True
                if i < len(paragraphs) - 2:
                    next_intensities = [p.intensity for p in paragraphs[i+1:min(len(paragraphs), i+3)]]
                    release_ok = any(ni < para.intensity - 0.2 for ni in next_intensities)

                # Determine type
                cath_type = "revelation" if para.emotion_vector.surprise > 0.5 else \
                           "victory" if para.emotion_vector.pride > 0.5 else \
                           "reunion" if para.emotion_vector.joy > 0.5 else \
                           "sacrifice" if para.emotion_vector.sadness > 0.5 else \
                           "transformation"

                suggestions = []
                if not buildup_ok:
                    suggestions.append("Dodaj więcej napięcia w poprzedzających akapitach")
                if not release_ok:
                    suggestions.append("Pozwól na emocjonalne wyciszenie po kulminacji")

                moments.append(CatharticMoment(
                    paragraph_index=i,
                    catharsis_type=cath_type,
                    intensity=para.intensity,
                    buildup_adequate=buildup_ok,
                    release_adequate=release_ok,
                    improvement_suggestions=suggestions
                ))

        return moments

    # =========================================================================
    # ISSUE DETECTION
    # =========================================================================

    def _detect_issues(
        self,
        paragraphs: List[ParagraphAnalysis],
        genre_profile: Dict
    ) -> List[EmotionalIssue]:
        """Detect emotional issues in the narrative."""
        issues = []

        # Check for flat sequences
        flat_issues = self._check_flat_sequences(paragraphs)
        issues.extend(flat_issues)

        # Check for jarring transitions
        jarring_issues = self._check_jarring_transitions(paragraphs)
        issues.extend(jarring_issues)

        # Check intensity against genre
        intensity_issues = self._check_intensity_calibration(paragraphs, genre_profile)
        issues.extend(intensity_issues)

        # Check for emotional whiplash
        whiplash_issues = self._check_emotional_whiplash(paragraphs)
        issues.extend(whiplash_issues)

        return issues

    def _check_flat_sequences(self, paragraphs: List[ParagraphAnalysis]) -> List[EmotionalIssue]:
        """Detect sequences with too little emotional variation."""
        issues = []
        window_size = 4

        for i in range(len(paragraphs) - window_size):
            window = paragraphs[i:i+window_size]
            intensities = [p.intensity for p in window]
            variation = max(intensities) - min(intensities)

            if variation < 0.15:  # Too flat
                issues.append(EmotionalIssue(
                    issue_type=EmotionalIssueType.FLAT_SEQUENCE,
                    severity="major" if variation < 0.1 else "minor",
                    location=f"akapity {i+1}-{i+window_size}",
                    description="Sekwencja ma zbyt mało emocjonalnej wariacji",
                    suggestion="Wprowadź moment napięcia, zaskoczenia lub emocjonalnego kontrastu",
                    affected_paragraphs=list(range(i, i+window_size))
                ))

        return issues

    def _check_jarring_transitions(self, paragraphs: List[ParagraphAnalysis]) -> List[EmotionalIssue]:
        """Detect sudden emotional shifts without transition."""
        issues = []

        for i in range(1, len(paragraphs)):
            prev = paragraphs[i-1]
            curr = paragraphs[i]

            distance = prev.emotion_vector.distance_to(curr.emotion_vector)

            if distance > 1.5:  # Very different emotional states
                issues.append(EmotionalIssue(
                    issue_type=EmotionalIssueType.JARRING_TRANSITION,
                    severity="critical" if distance > 2.0 else "major",
                    location=f"między akapitami {i} i {i+1}",
                    description=f"Nagłe przejście z '{prev.dominant_emotion}' do '{curr.dominant_emotion}'",
                    suggestion="Dodaj akapit przejściowy lub zmiękczenie emocjonalnej zmiany",
                    affected_paragraphs=[i-1, i]
                ))

        return issues

    def _check_intensity_calibration(
        self,
        paragraphs: List[ParagraphAnalysis],
        genre_profile: Dict
    ) -> List[EmotionalIssue]:
        """Check if intensity is calibrated for genre."""
        issues = []
        ideal_range = genre_profile.get("ideal_intensity_range", (0.3, 0.8))

        avg_intensity = sum(p.intensity for p in paragraphs) / len(paragraphs)

        if avg_intensity < ideal_range[0]:
            issues.append(EmotionalIssue(
                issue_type=EmotionalIssueType.PACING_MISMATCH,
                severity="major",
                location="cały fragment",
                description=f"Intensywność emocjonalna ({avg_intensity:.2f}) zbyt niska dla gatunku",
                suggestion=f"Zwiększ intensywność emocji do zakresu {ideal_range[0]:.1f}-{ideal_range[1]:.1f}",
                affected_paragraphs=list(range(len(paragraphs)))
            ))
        elif avg_intensity > ideal_range[1]:
            issues.append(EmotionalIssue(
                issue_type=EmotionalIssueType.PACING_MISMATCH,
                severity="minor",
                location="cały fragment",
                description=f"Intensywność emocjonalna ({avg_intensity:.2f}) bardzo wysoka",
                suggestion="Rozważ dodanie momentów wyciszenia dla kontrastu",
                affected_paragraphs=list(range(len(paragraphs)))
            ))

        return issues

    def _check_emotional_whiplash(self, paragraphs: List[ParagraphAnalysis]) -> List[EmotionalIssue]:
        """Detect too many rapid emotional changes."""
        issues = []
        rapid_changes = 0

        for i in range(1, len(paragraphs)):
            distance = paragraphs[i-1].emotion_vector.distance_to(paragraphs[i].emotion_vector)
            if distance > 0.8:
                rapid_changes += 1

        change_ratio = rapid_changes / len(paragraphs)
        if change_ratio > 0.5:
            issues.append(EmotionalIssue(
                issue_type=EmotionalIssueType.EMOTIONAL_WHIPLASH,
                severity="major",
                location="cały fragment",
                description="Zbyt wiele nagłych zmian emocjonalnych",
                suggestion="Ustabilizuj emocje - pozwól czytelnikowi poczuć każdą emocję dłużej",
                affected_paragraphs=list(range(len(paragraphs)))
            ))

        return issues

    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================

    def _generate_recommendations(
        self,
        paragraphs: List[ParagraphAnalysis],
        issues: List[EmotionalIssue],
        genre_profile: Dict,
        is_climax: bool
    ) -> List[str]:
        """Generate specific recommendations for improvement."""
        recommendations = []

        # Issue-based recommendations
        if any(i.issue_type == EmotionalIssueType.FLAT_SEQUENCE for i in issues):
            recommendations.append(
                "Wprowadź więcej emocjonalnej wariacji - niech napięcie faluje"
            )

        if any(i.issue_type == EmotionalIssueType.JARRING_TRANSITION for i in issues):
            recommendations.append(
                "Wygładź przejścia emocjonalne - dodaj akapity przejściowe"
            )

        # Genre-specific recommendations
        primary_emotions = genre_profile.get("primary_emotions", [])
        actual_dominant = self._get_dominant_emotions(paragraphs)

        missing = [e for e in primary_emotions if e not in actual_dominant[:3]]
        if missing:
            recommendations.append(
                f"Wzmocnij emocje kluczowe dla gatunku: {', '.join(missing)}"
            )

        # Climax-specific
        if is_climax:
            max_intensity = max(p.intensity for p in paragraphs)
            if max_intensity < 0.8:
                recommendations.append(
                    "To rozdziały kulminacyjny - zwiększ szczytową intensywność emocji"
                )

            catharsis_present = any(p.emotion_vector.catharsis > 0.3 for p in paragraphs)
            if not catharsis_present:
                recommendations.append(
                    "Dodaj moment katharsis - emocjonalnego oczyszczenia"
                )

        # Pacing recommendations
        tension_baseline = genre_profile.get("tension_baseline", 0.4)
        avg_tension = sum(p.emotion_vector.tension for p in paragraphs) / len(paragraphs)
        if avg_tension < tension_baseline - 0.2:
            recommendations.append(
                f"Zwiększ poziom napięcia narracyjnego (obecny: {avg_tension:.2f}, optymalny: {tension_baseline:.2f}+)"
            )

        return recommendations[:5]  # Limit to top 5

    def _get_dominant_emotions(self, paragraphs: List[ParagraphAnalysis]) -> List[str]:
        """Get the most common dominant emotions."""
        emotion_counts = defaultdict(int)
        for p in paragraphs:
            emotion_counts[p.dominant_emotion] += 1

        sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
        return [e[0] for e in sorted_emotions]

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _split_into_paragraphs(self, content: str) -> List[str]:
        """Split content into paragraphs."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        return paragraphs

    def _create_heatmap(self, paragraphs: List[ParagraphAnalysis]) -> Dict[str, List[float]]:
        """Create emotion heatmap from paragraph analyses."""
        heatmap = {
            "fear": [], "hope": [], "sadness": [], "joy": [],
            "anger": [], "surprise": [], "shame": [], "pride": [],
            "longing": [], "relief": [], "tension": [], "catharsis": []
        }

        for p in paragraphs:
            vector = p.emotion_vector.to_dict()
            for emotion in heatmap:
                heatmap[emotion].append(vector.get(emotion, 0))

        return heatmap

    def _calculate_genre_calibration(
        self,
        paragraphs: List[ParagraphAnalysis],
        genre_profile: Dict
    ) -> Dict[str, float]:
        """Calculate how well calibrated the emotions are for the genre."""
        calibration = {}

        primary = genre_profile.get("primary_emotions", [])
        secondary = genre_profile.get("secondary_emotions", [])

        for emotion in primary:
            avg = sum(getattr(p.emotion_vector, emotion, 0) for p in paragraphs) / len(paragraphs)
            # Primary emotions should be strong
            calibration[emotion] = min(1.0, avg * 2)  # Boost scoring

        for emotion in secondary:
            avg = sum(getattr(p.emotion_vector, emotion, 0) for p in paragraphs) / len(paragraphs)
            calibration[emotion] = min(1.0, avg * 1.5)

        # Calculate overall calibration
        if calibration:
            calibration["overall"] = sum(calibration.values()) / len(calibration)

        return calibration

    def _calculate_emotional_score(
        self,
        trajectory: EmotionalTrajectory,
        calibration: Dict[str, float],
        genre_profile: Dict
    ) -> float:
        """Calculate overall emotional resonance score (0-100)."""
        score = 50.0  # Base score

        # Calibration bonus (up to +20)
        calibration_bonus = calibration.get("overall", 0.5) * 20
        score += calibration_bonus

        # Issue penalties
        for issue in trajectory.issues:
            if issue.severity == "critical":
                score -= 10
            elif issue.severity == "major":
                score -= 5
            else:
                score -= 2

        # Arc type bonus
        arc_bonuses = {
            EmotionalArcType.CRESCENDO: 10,
            EmotionalArcType.RISE_FALL: 8,
            EmotionalArcType.FALL_RISE: 8,
            EmotionalArcType.OSCILLATION: 5,
            EmotionalArcType.RISE: 3,
            EmotionalArcType.FALL: 3,
            EmotionalArcType.RESOLUTION: 2,
            EmotionalArcType.PLATEAU: -5
        }
        score += arc_bonuses.get(trajectory.arc_type, 0)

        # Cathartic moments bonus
        good_catharsis = sum(1 for c in trajectory.cathartic_moments
                             if c.buildup_adequate and c.release_adequate)
        score += good_catharsis * 5

        # Variation bonus
        if trajectory.peak_moments and trajectory.valley_moments:
            score += 5

        return max(0, min(100, score))

    def _generate_summary(
        self,
        trajectory: EmotionalTrajectory,
        score: float,
        genre: str
    ) -> str:
        """Generate human-readable summary."""
        level = "znakomity" if score >= 85 else \
                "dobry" if score >= 70 else \
                "przeciętny" if score >= 55 else "wymaga pracy"

        issues_text = f"{len(trajectory.issues)} problemów" if trajectory.issues else "brak problemów"

        return (
            f"Rezonans emocjonalny: {level} ({score:.0f}/100). "
            f"Łuk: {trajectory.arc_type.value}. "
            f"Wykryto {issues_text}. "
            f"Momentów katartycznych: {len(trajectory.cathartic_moments)}."
        )

    def _empty_report(self) -> EmotionalResonanceReport:
        """Return empty report when no content to analyze."""
        return EmotionalResonanceReport(
            total_paragraphs=0,
            trajectory=EmotionalTrajectory(
                paragraphs=[],
                arc_type=EmotionalArcType.PLATEAU,
                overall_valence=0,
                average_intensity=0,
                peak_moments=[],
                valley_moments=[],
                cathartic_moments=[],
                issues=[],
                recommendations=[]
            ),
            emotion_heatmap={},
            genre_calibration={},
            bestseller_emotional_score=0,
            summary="Brak treści do analizy."
        )

    def _default_reader_state(self) -> Dict[str, Any]:
        """Return default reader state."""
        return {
            "current_emotion": "neutral",
            "tension_level": 0.3,
            "engagement_level": 0.5,
            "expectations": [],
            "vulnerability_to": []
        }

    def _predict_expectations(
        self,
        analyses: List[ParagraphAnalysis],
        genre: str
    ) -> List[str]:
        """Predict what reader expects next based on trajectory."""
        expectations = []

        if analyses:
            latest = analyses[-1]

            # If tension is high, reader expects release
            if latest.emotion_vector.tension > 0.6:
                expectations.append("rozwiązanie napięcia")

            # If positive, reader might expect complication
            if latest.valence > 0.3:
                expectations.append("komplikacja lub przeszkoda")

            # If negative, reader hopes for improvement
            if latest.valence < -0.3:
                expectations.append("promyk nadziei lub zwrot")

            # Genre-specific
            if genre == "thriller":
                expectations.append("niespodziewany twist")
            elif genre == "romance":
                expectations.append("moment zbliżenia lub rozłąki")

        return expectations[:3]

    def _determine_vulnerabilities(
        self,
        analyses: List[ParagraphAnalysis]
    ) -> List[str]:
        """Determine what would emotionally affect reader most now."""
        vulnerabilities = []

        if analyses:
            # Calculate emotional investment
            avg_joy = sum(a.emotion_vector.joy for a in analyses) / len(analyses)
            avg_fear = sum(a.emotion_vector.fear for a in analyses) / len(analyses)
            avg_hope = sum(a.emotion_vector.hope for a in analyses) / len(analyses)

            # After hope, betrayal hits hard
            if avg_hope > 0.4:
                vulnerabilities.append("zdrada oczekiwań")

            # After joy, loss hits hard
            if avg_joy > 0.4:
                vulnerabilities.append("strata")

            # After fear, relief is powerful
            if avg_fear > 0.4:
                vulnerabilities.append("niespodziewana pomoc")

            # General vulnerabilities
            vulnerabilities.append("śmierć bliskiej postaci")
            vulnerabilities.append("zaskakujące odkrycie")

        return vulnerabilities[:4]

    def _calculate_momentum(self, analyses: List[ParagraphAnalysis]) -> str:
        """Calculate emotional momentum direction."""
        if len(analyses) < 2:
            return "stable"

        recent_valence = [a.valence for a in analyses[-3:]]
        if len(recent_valence) >= 2:
            trend = recent_valence[-1] - recent_valence[0]
            if trend > 0.2:
                return "rising"
            elif trend < -0.2:
                return "falling"

        return "stable"

    def _generate_fix_for_issue(self, issue: EmotionalIssue, genre: str) -> str:
        """Generate specific fix recommendation for an issue."""
        fixes = {
            EmotionalIssueType.FLAT_SEQUENCE:
                "Dodaj nieoczekiwane odkrycie, napięcie interpersonalne, lub moment wewnętrznego konfliktu",
            EmotionalIssueType.JARRING_TRANSITION:
                "Wstaw akapit przejściowy pokazujący wewnętrzną reakcję postaci na zmianę sytuacji",
            EmotionalIssueType.MISSING_BUILDUP:
                "Dodaj 2-3 akapity budujące napięcie przed kulminacją: przeszkody, narastający strach, deadline",
            EmotionalIssueType.UNEARNED_EMOTION:
                "Pokaż przyczynę emocji - wydarzenia lub wspomnienia uzasadniające reakcję",
            EmotionalIssueType.EMOTIONAL_WHIPLASH:
                "Pozwól czytelnikowi poczuć każdą emocję przez minimum 2-3 akapity przed zmianą",
            EmotionalIssueType.MONOTONOUS_TONE:
                "Wprowadź kontrastujący moment - humor w tragedii, napięcie w sielance",
            EmotionalIssueType.WEAK_CATHARSIS:
                "Zwiększ stawkę przed kulminacją i daj czas na emocjonalną reakcję po",
            EmotionalIssueType.PACING_MISMATCH:
                f"Dostosuj tempo do gatunku {genre}: krótsze zdania przy napięciu, dłuższe przy refleksji"
        }

        return fixes.get(issue.issue_type, "Przeanalizuj kontekst i dostosuj emocje do sytuacji")

    def _recommend_emotion_boost(
        self,
        target_emotion: str,
        paragraphs: List[ParagraphAnalysis],
        target_intensity: float
    ) -> Dict[str, Any]:
        """Recommend how to boost specific emotion."""
        current_level = 0
        for p in paragraphs:
            current_level += getattr(p.emotion_vector, target_emotion, 0)
        current_level /= len(paragraphs) if paragraphs else 1

        techniques = {
            "fear": ["Dodaj nieznane zagrożenie", "Pokaż konsekwencje porażki", "Skróć zdania, zwiększ tempo"],
            "hope": ["Pokaż małą wygraną", "Wprowadź sojusznika", "Przypomnij cel walki"],
            "sadness": ["Pokaż stratę", "Użyj retrospekcji szczęśliwych chwil", "Skup się na detalu bólu"],
            "joy": ["Pokaż triumf", "Wzmocnij więzi międzyludzkie", "Użyj jasnych obrazów"],
            "tension": ["Dodaj tykający zegar", "Ukryj informację", "Zakończ akapit cliffhangerem"],
            "surprise": ["Wprowadź twist", "Odwróć oczekiwania", "Ujawnij sekret"],
            "catharsis": ["Pozwól postaci wyrazić emocje", "Daj moment akceptacji", "Zakończ wątek"]
        }

        return {
            "target_emotion": target_emotion,
            "current_level": round(current_level, 2),
            "target_intensity": target_intensity,
            "gap": round(target_intensity - current_level, 2),
            "techniques": techniques.get(target_emotion, ["Wzmocnij obecność tej emocji w dialogu i akcji"])
        }


# =============================================================================
# SINGLETON AND FACTORY
# =============================================================================

_emotional_engine: Optional[EmotionalResonanceEngine] = None


def get_emotional_resonance_engine() -> EmotionalResonanceEngine:
    """Get or create emotional resonance engine instance."""
    global _emotional_engine
    if _emotional_engine is None:
        _emotional_engine = EmotionalResonanceEngine()
    return _emotional_engine

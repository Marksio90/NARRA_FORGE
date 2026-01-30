"""
Predictive Pacing Algorithm - NarraForge 3.0

System predykcyjnego sterowania tempem narracji:
- Analiza tempa w czasie rzeczywistym
- Przewidywanie optymalnego tempa na podstawie arc'u
- Wykrywanie problemów z tempem
- Automatyczne sugestie korekt
- Gatunkowe profile tempa
- Integracja z emocjonalnym arc'iem

"Każda strona płynie z perfekcyjnym rytmem"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
import math

from app.services.llm_service import get_llm_service
from app.models.project import GenreType


# =============================================================================
# ENUMS
# =============================================================================

class PacingLevel(Enum):
    """Poziomy tempa narracji"""
    VERY_SLOW = "very_slow"  # Głęboka refleksja, medytacyjne
    SLOW = "slow"  # Spokojne budowanie
    MODERATE = "moderate"  # Zbalansowane
    FAST = "fast"  # Dynamiczne, napięcie
    VERY_FAST = "very_fast"  # Akcja, kulminacja


class NarrativePhase(Enum):
    """Fazy narracyjne (struktura trzech aktów)"""
    SETUP = "setup"  # Wprowadzenie, świat zwykły
    INCITING_INCIDENT = "inciting_incident"  # Wydarzenie inicjujące
    RISING_ACTION = "rising_action"  # Eskalacja
    MIDPOINT = "midpoint"  # Punkt środkowy
    COMPLICATIONS = "complications"  # Komplikacje
    CRISIS = "crisis"  # Kryzys
    CLIMAX = "climax"  # Kulminacja
    FALLING_ACTION = "falling_action"  # Opadanie akcji
    RESOLUTION = "resolution"  # Rozwiązanie


class PacingIssueType(Enum):
    """Typy problemów z tempem"""
    TOO_SLOW_FOR_GENRE = "too_slow_for_genre"
    TOO_FAST_FOR_PHASE = "too_fast_for_phase"
    MONOTONOUS = "monotonous"  # Brak wariacji
    JARRING_TRANSITION = "jarring_transition"  # Zbyt nagła zmiana
    WEAK_BUILDUP = "weak_buildup"  # Słabe budowanie do kulminacji
    ANTICLIMACTIC = "anticlimactic"  # Rozczarowująca kulminacja
    RUSHED_RESOLUTION = "rushed_resolution"  # Zbyt szybkie rozwiązanie
    DRAGGING_MIDDLE = "dragging_middle"  # Wlokący się środek
    NO_BREATHING_ROOM = "no_breathing_room"  # Brak wytchnienia
    LOST_MOMENTUM = "lost_momentum"  # Utrata rozpędu


class SceneWeight(Enum):
    """Waga sceny w arc'u fabularnym"""
    FILLER = "filler"  # Wypełniacz
    MINOR = "minor"  # Mniejsza scena
    STANDARD = "standard"  # Standardowa
    IMPORTANT = "important"  # Ważna
    PIVOTAL = "pivotal"  # Kluczowa
    CLIMACTIC = "climactic"  # Kulminacyjna


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PacingMeasurement:
    """Pomiar tempa pojedynczego fragmentu"""
    segment_id: str
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    dialogue_ratio: float
    action_verb_density: float
    description_density: float
    tension_level: float  # 0-1
    pacing_score: float  # 0-1 (0=bardzo wolne, 1=bardzo szybkie)
    pacing_level: PacingLevel

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "avg_sentence_length": self.avg_sentence_length,
            "dialogue_ratio": self.dialogue_ratio,
            "action_verb_density": self.action_verb_density,
            "description_density": self.description_density,
            "tension_level": self.tension_level,
            "pacing_score": self.pacing_score,
            "pacing_level": self.pacing_level.value
        }


@dataclass
class ChapterPacingProfile:
    """Profil tempa rozdziału"""
    chapter_number: int
    narrative_phase: NarrativePhase
    scene_weight: SceneWeight
    target_pacing: PacingLevel
    actual_measurements: List[PacingMeasurement]
    overall_pacing_score: float
    pacing_variance: float  # Wariacja tempa w rozdziale
    tension_arc: List[float]  # Arc napięcia przez rozdział
    issues: List[Dict[str, Any]]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "narrative_phase": self.narrative_phase.value,
            "scene_weight": self.scene_weight.value,
            "target_pacing": self.target_pacing.value,
            "actual_measurements": [m.to_dict() for m in self.actual_measurements],
            "overall_pacing_score": self.overall_pacing_score,
            "pacing_variance": self.pacing_variance,
            "tension_arc": self.tension_arc,
            "issues": self.issues,
            "recommendations": self.recommendations
        }


@dataclass
class PacingPrediction:
    """Predykcja optymalnego tempa"""
    chapter_number: int
    narrative_phase: NarrativePhase
    recommended_pacing: PacingLevel
    pacing_range: Tuple[float, float]  # Min-max score
    tension_targets: List[float]  # Docelowy arc napięcia
    scene_type_distribution: Dict[str, float]  # Rozkład typów scen
    breathing_points: List[int]  # Gdzie umieścić wytchnienie
    acceleration_points: List[int]  # Gdzie przyspieszyć
    key_moments: List[Dict[str, Any]]  # Kluczowe momenty do uwzględnienia

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "narrative_phase": self.narrative_phase.value,
            "recommended_pacing": self.recommended_pacing.value,
            "pacing_range": self.pacing_range,
            "tension_targets": self.tension_targets,
            "scene_type_distribution": self.scene_type_distribution,
            "breathing_points": self.breathing_points,
            "acceleration_points": self.acceleration_points,
            "key_moments": self.key_moments
        }


@dataclass
class PacingIssue:
    """Problem z tempem"""
    issue_type: PacingIssueType
    severity: str  # minor, moderate, major, critical
    location: str  # Gdzie występuje
    description: str
    suggested_fix: str
    expected_improvement: float  # Oczekiwana poprawa (0-1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_type": self.issue_type.value,
            "severity": self.severity,
            "location": self.location,
            "description": self.description,
            "suggested_fix": self.suggested_fix,
            "expected_improvement": self.expected_improvement
        }


@dataclass
class BookPacingReport:
    """Raport tempa całej książki"""
    total_chapters: int
    chapter_profiles: List[ChapterPacingProfile]
    overall_pacing_score: float
    pacing_consistency: float
    genre_fit: float  # Dopasowanie do gatunku
    global_issues: List[PacingIssue]
    pacing_curve: List[float]  # Krzywa tempa przez całą książkę
    tension_curve: List[float]  # Krzywa napięcia
    recommendations: List[str]
    bestseller_pacing_score: float  # Jak dobrze pasuje do bestsellerów

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_chapters": self.total_chapters,
            "chapter_profiles": [c.to_dict() for c in self.chapter_profiles],
            "overall_pacing_score": self.overall_pacing_score,
            "pacing_consistency": self.pacing_consistency,
            "genre_fit": self.genre_fit,
            "global_issues": [i.to_dict() for i in self.global_issues],
            "pacing_curve": self.pacing_curve,
            "tension_curve": self.tension_curve,
            "recommendations": self.recommendations,
            "bestseller_pacing_score": self.bestseller_pacing_score
        }


# =============================================================================
# GENRE PACING PROFILES
# =============================================================================

GENRE_PACING_PROFILES = {
    GenreType.THRILLER: {
        "baseline_pacing": 0.7,
        "pacing_variance": 0.25,
        "tension_floor": 0.4,
        "climax_pacing": 0.95,
        "resolution_pacing": 0.4,
        "breathing_frequency": 3,  # Co ile scen oddech
        "phase_pacing": {
            NarrativePhase.SETUP: 0.5,
            NarrativePhase.INCITING_INCIDENT: 0.7,
            NarrativePhase.RISING_ACTION: 0.75,
            NarrativePhase.MIDPOINT: 0.85,
            NarrativePhase.COMPLICATIONS: 0.7,
            NarrativePhase.CRISIS: 0.9,
            NarrativePhase.CLIMAX: 0.95,
            NarrativePhase.FALLING_ACTION: 0.5,
            NarrativePhase.RESOLUTION: 0.4
        }
    },
    GenreType.ROMANCE: {
        "baseline_pacing": 0.5,
        "pacing_variance": 0.2,
        "tension_floor": 0.2,
        "climax_pacing": 0.8,
        "resolution_pacing": 0.3,
        "breathing_frequency": 2,
        "phase_pacing": {
            NarrativePhase.SETUP: 0.4,
            NarrativePhase.INCITING_INCIDENT: 0.5,
            NarrativePhase.RISING_ACTION: 0.55,
            NarrativePhase.MIDPOINT: 0.7,
            NarrativePhase.COMPLICATIONS: 0.6,
            NarrativePhase.CRISIS: 0.75,
            NarrativePhase.CLIMAX: 0.8,
            NarrativePhase.FALLING_ACTION: 0.4,
            NarrativePhase.RESOLUTION: 0.3
        }
    },
    GenreType.FANTASY: {
        "baseline_pacing": 0.55,
        "pacing_variance": 0.3,
        "tension_floor": 0.25,
        "climax_pacing": 0.9,
        "resolution_pacing": 0.35,
        "breathing_frequency": 3,
        "phase_pacing": {
            NarrativePhase.SETUP: 0.4,
            NarrativePhase.INCITING_INCIDENT: 0.6,
            NarrativePhase.RISING_ACTION: 0.65,
            NarrativePhase.MIDPOINT: 0.75,
            NarrativePhase.COMPLICATIONS: 0.6,
            NarrativePhase.CRISIS: 0.85,
            NarrativePhase.CLIMAX: 0.9,
            NarrativePhase.FALLING_ACTION: 0.45,
            NarrativePhase.RESOLUTION: 0.35
        }
    },
    GenreType.HORROR: {
        "baseline_pacing": 0.55,
        "pacing_variance": 0.35,
        "tension_floor": 0.35,
        "climax_pacing": 0.9,
        "resolution_pacing": 0.5,
        "breathing_frequency": 4,
        "phase_pacing": {
            NarrativePhase.SETUP: 0.4,
            NarrativePhase.INCITING_INCIDENT: 0.65,
            NarrativePhase.RISING_ACTION: 0.6,
            NarrativePhase.MIDPOINT: 0.75,
            NarrativePhase.COMPLICATIONS: 0.65,
            NarrativePhase.CRISIS: 0.85,
            NarrativePhase.CLIMAX: 0.9,
            NarrativePhase.FALLING_ACTION: 0.55,
            NarrativePhase.RESOLUTION: 0.5
        }
    },
    GenreType.MYSTERY: {
        "baseline_pacing": 0.55,
        "pacing_variance": 0.2,
        "tension_floor": 0.3,
        "climax_pacing": 0.85,
        "resolution_pacing": 0.4,
        "breathing_frequency": 3,
        "phase_pacing": {
            NarrativePhase.SETUP: 0.45,
            NarrativePhase.INCITING_INCIDENT: 0.6,
            NarrativePhase.RISING_ACTION: 0.55,
            NarrativePhase.MIDPOINT: 0.7,
            NarrativePhase.COMPLICATIONS: 0.6,
            NarrativePhase.CRISIS: 0.8,
            NarrativePhase.CLIMAX: 0.85,
            NarrativePhase.FALLING_ACTION: 0.45,
            NarrativePhase.RESOLUTION: 0.4
        }
    },
    GenreType.SCIFI: {
        "baseline_pacing": 0.6,
        "pacing_variance": 0.25,
        "tension_floor": 0.3,
        "climax_pacing": 0.9,
        "resolution_pacing": 0.4,
        "breathing_frequency": 3,
        "phase_pacing": {
            NarrativePhase.SETUP: 0.45,
            NarrativePhase.INCITING_INCIDENT: 0.65,
            NarrativePhase.RISING_ACTION: 0.65,
            NarrativePhase.MIDPOINT: 0.75,
            NarrativePhase.COMPLICATIONS: 0.65,
            NarrativePhase.CRISIS: 0.85,
            NarrativePhase.CLIMAX: 0.9,
            NarrativePhase.FALLING_ACTION: 0.5,
            NarrativePhase.RESOLUTION: 0.4
        }
    }
}

# Default profile for unknown genres
DEFAULT_PACING_PROFILE = {
    "baseline_pacing": 0.55,
    "pacing_variance": 0.25,
    "tension_floor": 0.25,
    "climax_pacing": 0.85,
    "resolution_pacing": 0.4,
    "breathing_frequency": 3,
    "phase_pacing": {
        NarrativePhase.SETUP: 0.45,
        NarrativePhase.INCITING_INCIDENT: 0.6,
        NarrativePhase.RISING_ACTION: 0.6,
        NarrativePhase.MIDPOINT: 0.7,
        NarrativePhase.COMPLICATIONS: 0.6,
        NarrativePhase.CRISIS: 0.8,
        NarrativePhase.CLIMAX: 0.85,
        NarrativePhase.FALLING_ACTION: 0.45,
        NarrativePhase.RESOLUTION: 0.4
    }
}


# =============================================================================
# PREDICTIVE PACING ENGINE
# =============================================================================

class PredictivePacingEngine:
    """
    Silnik predykcyjnego sterowania tempem narracji.

    Funkcje:
    - Analiza tempa tekstu
    - Przewidywanie optymalnego tempa
    - Wykrywanie problemów z tempem
    - Generowanie rekomendacji
    - Monitorowanie arc'u napięcia
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.genre_profiles = GENRE_PACING_PROFILES

    def _get_llm(self, tier: str = "mid"):
        """Get appropriate LLM based on tier"""
        return self.llm_service.get_client(tier)

    def _get_genre_profile(self, genre: GenreType) -> Dict[str, Any]:
        """Pobiera profil tempa dla gatunku"""
        return self.genre_profiles.get(genre, DEFAULT_PACING_PROFILE)

    def _score_to_level(self, score: float) -> PacingLevel:
        """Konwertuje score na poziom tempa"""
        if score < 0.2:
            return PacingLevel.VERY_SLOW
        elif score < 0.4:
            return PacingLevel.SLOW
        elif score < 0.6:
            return PacingLevel.MODERATE
        elif score < 0.8:
            return PacingLevel.FAST
        else:
            return PacingLevel.VERY_FAST

    # =========================================================================
    # PACING MEASUREMENT
    # =========================================================================

    async def measure_pacing(
        self,
        text: str,
        segment_id: str = "segment_1"
    ) -> PacingMeasurement:
        """
        Mierzy tempo pojedynczego fragmentu tekstu.
        """
        # Basic statistics
        words = text.split()
        word_count = len(words)

        import re
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)

        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # Dialogue ratio (simple approximation)
        dialogue_markers = text.count('"') + text.count('—') + text.count('–')
        dialogue_ratio = min(1.0, dialogue_markers / (word_count / 20 + 1))

        # Use LLM for deeper analysis
        prompt = f"""Przeanalizuj tempo narracji poniższego fragmentu.

TEKST:
{text[:2000]}

Oceń na skali 0.0-1.0:
1. action_verb_density: gęstość czasowników akcji (0=mało, 1=dużo)
2. description_density: gęstość opisów (0=mało, 1=dużo)
3. tension_level: poziom napięcia (0=spokój, 1=kulminacja)
4. pacing_score: ogólne tempo (0=bardzo wolne, 1=bardzo szybkie)

Odpowiedz w JSON."""

        response = await self._get_llm("low").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        analysis = json.loads(response.choices[0].message.content)

        pacing_score = float(analysis.get("pacing_score", 0.5))

        return PacingMeasurement(
            segment_id=segment_id,
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=avg_sentence_length,
            dialogue_ratio=dialogue_ratio,
            action_verb_density=float(analysis.get("action_verb_density", 0.5)),
            description_density=float(analysis.get("description_density", 0.5)),
            tension_level=float(analysis.get("tension_level", 0.5)),
            pacing_score=pacing_score,
            pacing_level=self._score_to_level(pacing_score)
        )

    async def analyze_chapter_pacing(
        self,
        chapter_text: str,
        chapter_number: int,
        total_chapters: int,
        genre: GenreType,
        chapter_summary: Optional[str] = None
    ) -> ChapterPacingProfile:
        """
        Analizuje tempo całego rozdziału.
        """
        genre_profile = self._get_genre_profile(genre)

        # Determine narrative phase based on position
        narrative_phase = self._determine_narrative_phase(chapter_number, total_chapters)

        # Split chapter into segments
        paragraphs = chapter_text.split('\n\n')
        segments = []
        current_segment = []
        current_word_count = 0

        for para in paragraphs:
            current_segment.append(para)
            current_word_count += len(para.split())
            if current_word_count >= 500:  # ~500 words per segment
                segments.append('\n\n'.join(current_segment))
                current_segment = []
                current_word_count = 0

        if current_segment:
            segments.append('\n\n'.join(current_segment))

        # Measure each segment
        measurements = []
        for i, segment in enumerate(segments[:10]):  # Max 10 segments
            measurement = await self.measure_pacing(segment, f"segment_{i+1}")
            measurements.append(measurement)

        # Calculate overall stats
        if measurements:
            overall_score = sum(m.pacing_score for m in measurements) / len(measurements)
            scores = [m.pacing_score for m in measurements]
            variance = sum((s - overall_score) ** 2 for s in scores) / len(scores)
            tension_arc = [m.tension_level for m in measurements]
        else:
            overall_score = 0.5
            variance = 0.0
            tension_arc = []

        # Get target pacing for this phase
        target_score = genre_profile["phase_pacing"].get(narrative_phase, 0.5)
        target_pacing = self._score_to_level(target_score)

        # Determine scene weight
        scene_weight = await self._determine_scene_weight(
            chapter_summary or chapter_text[:1000],
            narrative_phase
        )

        # Detect issues
        issues = self._detect_chapter_issues(
            measurements,
            target_score,
            genre_profile,
            narrative_phase
        )

        # Generate recommendations
        recommendations = self._generate_chapter_recommendations(
            overall_score,
            target_score,
            variance,
            issues,
            genre,
            narrative_phase
        )

        return ChapterPacingProfile(
            chapter_number=chapter_number,
            narrative_phase=narrative_phase,
            scene_weight=scene_weight,
            target_pacing=target_pacing,
            actual_measurements=measurements,
            overall_pacing_score=overall_score,
            pacing_variance=variance ** 0.5,
            tension_arc=tension_arc,
            issues=issues,
            recommendations=recommendations
        )

    def _determine_narrative_phase(
        self,
        chapter_number: int,
        total_chapters: int
    ) -> NarrativePhase:
        """Określa fazę narracyjną na podstawie pozycji rozdziału"""
        progress = chapter_number / total_chapters

        if progress <= 0.1:
            return NarrativePhase.SETUP
        elif progress <= 0.15:
            return NarrativePhase.INCITING_INCIDENT
        elif progress <= 0.4:
            return NarrativePhase.RISING_ACTION
        elif progress <= 0.5:
            return NarrativePhase.MIDPOINT
        elif progress <= 0.7:
            return NarrativePhase.COMPLICATIONS
        elif progress <= 0.8:
            return NarrativePhase.CRISIS
        elif progress <= 0.9:
            return NarrativePhase.CLIMAX
        elif progress <= 0.95:
            return NarrativePhase.FALLING_ACTION
        else:
            return NarrativePhase.RESOLUTION

    async def _determine_scene_weight(
        self,
        content_summary: str,
        phase: NarrativePhase
    ) -> SceneWeight:
        """Określa wagę sceny"""
        prompt = f"""Na podstawie opisu sceny i fazy narracyjnej, określ wagę sceny.

OPIS/FRAGMENT:
{content_summary[:500]}

FAZA NARRACYJNA: {phase.value}

Wybierz wagę sceny:
- filler: wypełniacz, nieistotna
- minor: mniejsza scena
- standard: standardowa scena
- important: ważna dla fabuły
- pivotal: kluczowa, punkt zwrotny
- climactic: kulminacyjna

Odpowiedz jednym słowem (wagą)."""

        response = await self._get_llm("low").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        weight_str = response.choices[0].message.content.strip().lower()

        try:
            return SceneWeight(weight_str)
        except ValueError:
            return SceneWeight.STANDARD

    def _detect_chapter_issues(
        self,
        measurements: List[PacingMeasurement],
        target_score: float,
        genre_profile: Dict[str, Any],
        phase: NarrativePhase
    ) -> List[Dict[str, Any]]:
        """Wykrywa problemy z tempem w rozdziale"""
        issues = []

        if not measurements:
            return issues

        scores = [m.pacing_score for m in measurements]
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)

        # Check if too slow for genre
        if avg_score < genre_profile["baseline_pacing"] - 0.2:
            issues.append({
                "type": PacingIssueType.TOO_SLOW_FOR_GENRE.value,
                "severity": "moderate",
                "description": f"Tempo ({avg_score:.2f}) poniżej typowego dla gatunku ({genre_profile['baseline_pacing']:.2f})"
            })

        # Check if too fast for phase
        phase_target = genre_profile["phase_pacing"].get(phase, 0.5)
        if avg_score > phase_target + 0.25 and phase in [NarrativePhase.SETUP, NarrativePhase.RESOLUTION]:
            issues.append({
                "type": PacingIssueType.TOO_FAST_FOR_PHASE.value,
                "severity": "moderate",
                "description": f"Zbyt szybkie tempo ({avg_score:.2f}) dla fazy {phase.value}"
            })

        # Check for monotony
        if variance < 0.02 and len(measurements) > 3:
            issues.append({
                "type": PacingIssueType.MONOTONOUS.value,
                "severity": "minor",
                "description": "Brak wariacji tempa - monotonia"
            })

        # Check for jarring transitions
        for i in range(1, len(scores)):
            if abs(scores[i] - scores[i-1]) > 0.4:
                issues.append({
                    "type": PacingIssueType.JARRING_TRANSITION.value,
                    "severity": "moderate",
                    "description": f"Nagła zmiana tempa między segmentami {i} i {i+1}"
                })

        # Check for weak buildup (if approaching climax)
        if phase == NarrativePhase.CRISIS:
            if len(scores) >= 3 and scores[-1] < scores[-3]:
                issues.append({
                    "type": PacingIssueType.WEAK_BUILDUP.value,
                    "severity": "major",
                    "description": "Słabe budowanie napięcia przed kulminacją"
                })

        # Check for no breathing room
        high_tension_count = sum(1 for m in measurements if m.tension_level > 0.7)
        if high_tension_count > len(measurements) * 0.8 and phase != NarrativePhase.CLIMAX:
            issues.append({
                "type": PacingIssueType.NO_BREATHING_ROOM.value,
                "severity": "moderate",
                "description": "Brak momentów wytchnienia przy ciągłym napięciu"
            })

        return issues

    def _generate_chapter_recommendations(
        self,
        actual_score: float,
        target_score: float,
        variance: float,
        issues: List[Dict[str, Any]],
        genre: GenreType,
        phase: NarrativePhase
    ) -> List[str]:
        """Generuje rekomendacje dla rozdziału"""
        recommendations = []

        diff = target_score - actual_score

        if abs(diff) > 0.15:
            if diff > 0:
                recommendations.append("Przyspiesz tempo: skróć zdania, dodaj więcej dialogu, usuń nadmiarowe opisy")
            else:
                recommendations.append("Zwolnij tempo: rozwiń opisy, dodaj refleksje postaci, wydłuż sceny")

        if variance < 0.02:
            recommendations.append("Dodaj wariację tempa: przeplataj szybsze i wolniejsze fragmenty")

        for issue in issues:
            if issue["type"] == PacingIssueType.JARRING_TRANSITION.value:
                recommendations.append("Wygładź przejścia między scenami, dodaj sceny przejściowe")
            elif issue["type"] == PacingIssueType.NO_BREATHING_ROOM.value:
                recommendations.append("Dodaj momenty wytchnienia: ciche refleksje, opisy krajobrazów")
            elif issue["type"] == PacingIssueType.WEAK_BUILDUP.value:
                recommendations.append("Wzmocnij budowanie: stopniowo zwiększaj stawki i napięcie")

        if phase == NarrativePhase.CLIMAX and actual_score < 0.75:
            recommendations.append("Kulminacja wymaga intensywniejszego tempa: skróć zdania, zwiększ akcję")

        if phase == NarrativePhase.SETUP and actual_score > 0.65:
            recommendations.append("Wprowadzenie powinno być spokojniejsze: pozwól czytelnikowi poznać świat")

        return recommendations

    # =========================================================================
    # PACING PREDICTION
    # =========================================================================

    async def predict_optimal_pacing(
        self,
        chapter_number: int,
        total_chapters: int,
        genre: GenreType,
        plot_points: List[str] = None,
        previous_pacing: Optional[float] = None
    ) -> PacingPrediction:
        """
        Przewiduje optymalne tempo dla rozdziału.
        """
        genre_profile = self._get_genre_profile(genre)
        phase = self._determine_narrative_phase(chapter_number, total_chapters)

        # Get base pacing for phase
        base_pacing = genre_profile["phase_pacing"].get(phase, 0.5)
        variance = genre_profile["pacing_variance"]

        # Calculate pacing range
        pacing_min = max(0.0, base_pacing - variance)
        pacing_max = min(1.0, base_pacing + variance)

        # Determine recommended level
        recommended_pacing = self._score_to_level(base_pacing)

        # Generate tension targets (simplified arc within chapter)
        if phase == NarrativePhase.CLIMAX:
            tension_targets = [0.7, 0.8, 0.85, 0.9, 0.95, 0.9, 0.8]
        elif phase in [NarrativePhase.RISING_ACTION, NarrativePhase.CRISIS]:
            tension_targets = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75]
        elif phase == NarrativePhase.SETUP:
            tension_targets = [0.2, 0.25, 0.3, 0.35, 0.4]
        elif phase == NarrativePhase.RESOLUTION:
            tension_targets = [0.5, 0.45, 0.4, 0.35, 0.3, 0.25]
        else:
            tension_targets = [0.4, 0.45, 0.5, 0.55, 0.5, 0.45]

        # Scene type distribution based on phase
        scene_distribution = self._get_scene_distribution(phase, genre)

        # Breathing points
        breathing_freq = genre_profile["breathing_frequency"]
        breathing_points = list(range(breathing_freq, 10, breathing_freq))

        # Acceleration points
        acceleration_points = []
        if phase in [NarrativePhase.RISING_ACTION, NarrativePhase.CRISIS, NarrativePhase.CLIMAX]:
            acceleration_points = [int(len(tension_targets) * 0.7)]

        # Key moments to consider
        key_moments = []
        if plot_points:
            for i, point in enumerate(plot_points[:3]):
                key_moments.append({
                    "description": point,
                    "suggested_position": (i + 1) * 2,
                    "pacing_boost": 0.1 if "zwrot" in point.lower() or "odkrycie" in point.lower() else 0
                })

        return PacingPrediction(
            chapter_number=chapter_number,
            narrative_phase=phase,
            recommended_pacing=recommended_pacing,
            pacing_range=(pacing_min, pacing_max),
            tension_targets=tension_targets,
            scene_type_distribution=scene_distribution,
            breathing_points=breathing_points,
            acceleration_points=acceleration_points,
            key_moments=key_moments
        )

    def _get_scene_distribution(
        self,
        phase: NarrativePhase,
        genre: GenreType
    ) -> Dict[str, float]:
        """Oblicza rozkład typów scen dla fazy"""
        base_distributions = {
            NarrativePhase.SETUP: {"dialogue": 0.35, "description": 0.35, "action": 0.1, "introspection": 0.2},
            NarrativePhase.INCITING_INCIDENT: {"dialogue": 0.3, "description": 0.2, "action": 0.3, "introspection": 0.2},
            NarrativePhase.RISING_ACTION: {"dialogue": 0.35, "description": 0.2, "action": 0.25, "introspection": 0.2},
            NarrativePhase.MIDPOINT: {"dialogue": 0.3, "description": 0.15, "action": 0.35, "introspection": 0.2},
            NarrativePhase.COMPLICATIONS: {"dialogue": 0.35, "description": 0.2, "action": 0.25, "introspection": 0.2},
            NarrativePhase.CRISIS: {"dialogue": 0.25, "description": 0.15, "action": 0.4, "introspection": 0.2},
            NarrativePhase.CLIMAX: {"dialogue": 0.2, "description": 0.1, "action": 0.5, "introspection": 0.2},
            NarrativePhase.FALLING_ACTION: {"dialogue": 0.35, "description": 0.25, "action": 0.15, "introspection": 0.25},
            NarrativePhase.RESOLUTION: {"dialogue": 0.4, "description": 0.25, "action": 0.1, "introspection": 0.25}
        }

        distribution = base_distributions.get(phase, {"dialogue": 0.3, "description": 0.25, "action": 0.25, "introspection": 0.2})

        # Adjust for genre
        if genre == GenreType.THRILLER:
            distribution["action"] += 0.1
            distribution["description"] -= 0.1
        elif genre == GenreType.ROMANCE:
            distribution["dialogue"] += 0.1
            distribution["action"] -= 0.1
        elif genre == GenreType.FANTASY:
            distribution["description"] += 0.1
            distribution["introspection"] -= 0.05
            distribution["dialogue"] -= 0.05

        return distribution

    # =========================================================================
    # BOOK-LEVEL ANALYSIS
    # =========================================================================

    async def analyze_book_pacing(
        self,
        chapters: List[str],
        genre: GenreType,
        chapter_summaries: List[str] = None
    ) -> BookPacingReport:
        """
        Analizuje tempo całej książki.
        """
        total_chapters = len(chapters)
        chapter_profiles = []

        for i, chapter_text in enumerate(chapters):
            summary = chapter_summaries[i] if chapter_summaries and i < len(chapter_summaries) else None
            profile = await self.analyze_chapter_pacing(
                chapter_text,
                i + 1,
                total_chapters,
                genre,
                summary
            )
            chapter_profiles.append(profile)

        # Calculate global metrics
        pacing_scores = [p.overall_pacing_score for p in chapter_profiles]
        overall_pacing = sum(pacing_scores) / len(pacing_scores) if pacing_scores else 0.5

        # Consistency (how close to expected arc)
        genre_profile = self._get_genre_profile(genre)
        expected_scores = []
        for i, p in enumerate(chapter_profiles):
            expected_scores.append(genre_profile["phase_pacing"].get(p.narrative_phase, 0.5))

        deviations = [abs(a - e) for a, e in zip(pacing_scores, expected_scores)]
        consistency = 1.0 - (sum(deviations) / len(deviations)) if deviations else 1.0

        # Genre fit
        baseline = genre_profile["baseline_pacing"]
        genre_fit = 1.0 - abs(overall_pacing - baseline)

        # Collect all issues
        all_issues = []
        for profile in chapter_profiles:
            for issue in profile.issues:
                all_issues.append(PacingIssue(
                    issue_type=PacingIssueType(issue["type"]),
                    severity=issue["severity"],
                    location=f"Rozdział {profile.chapter_number}",
                    description=issue["description"],
                    suggested_fix="",
                    expected_improvement=0.0
                ))

        # Detect global issues
        global_issues = self._detect_global_issues(chapter_profiles, genre_profile)
        all_issues.extend(global_issues)

        # Build curves
        pacing_curve = pacing_scores
        tension_curve = [
            max(p.tension_arc) if p.tension_arc else 0.5
            for p in chapter_profiles
        ]

        # Generate global recommendations
        recommendations = self._generate_book_recommendations(
            chapter_profiles,
            all_issues,
            overall_pacing,
            consistency,
            genre
        )

        # Calculate bestseller score
        bestseller_score = self._calculate_bestseller_pacing_score(
            pacing_curve,
            tension_curve,
            consistency,
            genre_fit,
            len([i for i in all_issues if i.severity in ["major", "critical"]])
        )

        return BookPacingReport(
            total_chapters=total_chapters,
            chapter_profiles=chapter_profiles,
            overall_pacing_score=overall_pacing,
            pacing_consistency=consistency,
            genre_fit=genre_fit,
            global_issues=all_issues,
            pacing_curve=pacing_curve,
            tension_curve=tension_curve,
            recommendations=recommendations,
            bestseller_pacing_score=bestseller_score
        )

    def _detect_global_issues(
        self,
        profiles: List[ChapterPacingProfile],
        genre_profile: Dict[str, Any]
    ) -> List[PacingIssue]:
        """Wykrywa globalne problemy z tempem"""
        issues = []

        if len(profiles) < 3:
            return issues

        pacing_scores = [p.overall_pacing_score for p in profiles]

        # Check for dragging middle (act 2)
        middle_start = len(profiles) // 4
        middle_end = 3 * len(profiles) // 4
        middle_scores = pacing_scores[middle_start:middle_end]
        if middle_scores:
            middle_avg = sum(middle_scores) / len(middle_scores)
            if middle_avg < genre_profile["baseline_pacing"] - 0.15:
                issues.append(PacingIssue(
                    issue_type=PacingIssueType.DRAGGING_MIDDLE,
                    severity="major",
                    location="Drugi akt",
                    description="Środek książki ma zbyt wolne tempo",
                    suggested_fix="Dodaj więcej konfliktów i przyspieszonych scen w środkowej części",
                    expected_improvement=0.15
                ))

        # Check for anticlimactic ending
        climax_idx = int(len(profiles) * 0.85)
        if climax_idx < len(profiles):
            climax_score = pacing_scores[climax_idx]
            pre_climax_avg = sum(pacing_scores[climax_idx-2:climax_idx]) / 2 if climax_idx >= 2 else 0.5
            if climax_score < pre_climax_avg:
                issues.append(PacingIssue(
                    issue_type=PacingIssueType.ANTICLIMACTIC,
                    severity="critical",
                    location="Kulminacja",
                    description="Kulminacja ma wolniejsze tempo niż sceny ją poprzedzające",
                    suggested_fix="Zintensyfikuj scenę kulminacyjną, skróć zdania, zwiększ stawki",
                    expected_improvement=0.2
                ))

        # Check for rushed resolution
        if len(profiles) > 2:
            resolution_profile = profiles[-1]
            if resolution_profile.overall_pacing_score > 0.7:
                issues.append(PacingIssue(
                    issue_type=PacingIssueType.RUSHED_RESOLUTION,
                    severity="moderate",
                    location="Zakończenie",
                    description="Rozwiązanie jest zbyt pośpieszne",
                    suggested_fix="Zwolnij zakończenie, pozwól postaciom i czytelnikowi przeżyć emocje",
                    expected_improvement=0.1
                ))

        # Check for lost momentum
        for i in range(2, len(pacing_scores)):
            if pacing_scores[i] < pacing_scores[i-1] - 0.2 and pacing_scores[i] < pacing_scores[i-2] - 0.2:
                phase = profiles[i].narrative_phase
                if phase not in [NarrativePhase.FALLING_ACTION, NarrativePhase.RESOLUTION]:
                    issues.append(PacingIssue(
                        issue_type=PacingIssueType.LOST_MOMENTUM,
                        severity="moderate",
                        location=f"Rozdział {i+1}",
                        description="Nagła utrata rozpędu narracji",
                        suggested_fix="Dodaj element napięcia lub konfliktu aby utrzymać zaangażowanie",
                        expected_improvement=0.1
                    ))

        return issues

    def _generate_book_recommendations(
        self,
        profiles: List[ChapterPacingProfile],
        issues: List[PacingIssue],
        overall_pacing: float,
        consistency: float,
        genre: GenreType
    ) -> List[str]:
        """Generuje rekomendacje dla całej książki"""
        recommendations = []

        if consistency < 0.6:
            recommendations.append("Popraw spójność tempa: wyrównaj różnice między rozdziałami, wygładź przejścia")

        major_issues = [i for i in issues if i.severity in ["major", "critical"]]
        if len(major_issues) > 3:
            recommendations.append("Skup się na naprawie poważnych problemów z tempem przed dalszą edycją")

        # Genre-specific recommendations
        genre_profile = self._get_genre_profile(genre)
        if overall_pacing < genre_profile["baseline_pacing"] - 0.1:
            recommendations.append(f"Dla gatunku {genre.value} zalecane jest szybsze tempo - rozważ przyspieszenie narracji")
        elif overall_pacing > genre_profile["baseline_pacing"] + 0.1:
            recommendations.append(f"Tempo może być zbyt szybkie dla {genre.value} - dodaj momenty refleksji")

        # Check tension arc
        tension_scores = [max(p.tension_arc) if p.tension_arc else 0.5 for p in profiles]
        if tension_scores:
            max_tension_idx = tension_scores.index(max(tension_scores))
            expected_climax_idx = int(len(profiles) * 0.85)
            if abs(max_tension_idx - expected_climax_idx) > 2:
                recommendations.append("Przesuń punkt maksymalnego napięcia bliżej kulminacji (~85% książki)")

        return recommendations

    def _calculate_bestseller_pacing_score(
        self,
        pacing_curve: List[float],
        tension_curve: List[float],
        consistency: float,
        genre_fit: float,
        major_issues: int
    ) -> float:
        """Oblicza wynik dopasowania tempa do wzorców bestsellerów"""
        # Base score from genre fit and consistency
        base_score = (genre_fit * 0.4 + consistency * 0.4)

        # Penalty for major issues
        issue_penalty = min(0.2, major_issues * 0.05)

        # Bonus for good pacing arc
        if len(pacing_curve) >= 5:
            # Check for proper climax positioning
            climax_position = pacing_curve.index(max(pacing_curve)) / len(pacing_curve)
            if 0.75 <= climax_position <= 0.9:
                base_score += 0.1

            # Check for proper resolution (slower ending)
            if pacing_curve[-1] < pacing_curve[-2]:
                base_score += 0.05

        # Bonus for good tension arc
        if len(tension_curve) >= 5:
            # Check for rising tension
            rising_sections = sum(1 for i in range(1, len(tension_curve)-1) if tension_curve[i] > tension_curve[i-1])
            if rising_sections >= len(tension_curve) * 0.5:
                base_score += 0.05

        final_score = max(0.0, min(1.0, base_score - issue_penalty))
        return round(final_score, 3)


# =============================================================================
# SINGLETON
# =============================================================================

_pacing_engine: Optional[PredictivePacingEngine] = None

def get_predictive_pacing_engine() -> PredictivePacingEngine:
    """Get singleton instance of predictive pacing engine"""
    global _pacing_engine
    if _pacing_engine is None:
        _pacing_engine = PredictivePacingEngine()
    return _pacing_engine

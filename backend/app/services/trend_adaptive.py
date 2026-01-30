"""
Trend-Adaptive Content Generation - NarraForge 3.0 Phase 3

Intelligent system for adapting narrative content to current market trends,
reader preferences, and emerging themes in literature.

Monitors literary trends, bestseller patterns, and reader feedback
to optimize content generation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from datetime import datetime, timedelta
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class TrendCategory(Enum):
    """Categories of literary trends"""
    THEME = "theme"                    # Thematic trends
    GENRE = "genre"                    # Genre popularity
    CHARACTER = "character"            # Character archetypes
    SETTING = "setting"                # Setting preferences
    NARRATIVE = "narrative"            # Narrative techniques
    STYLE = "style"                    # Writing style trends
    FORMAT = "format"                  # Book format trends
    MARKETING = "marketing"            # Marketing/packaging trends


class TrendStrength(Enum):
    """Strength of a trend"""
    EMERGING = "emerging"              # Just starting
    GROWING = "growing"                # Gaining popularity
    PEAK = "peak"                      # At maximum popularity
    STABLE = "stable"                  # Consistent popularity
    DECLINING = "declining"            # Losing popularity
    FADING = "fading"                  # Nearly gone


class TrendSource(Enum):
    """Sources for trend data"""
    BESTSELLER_LISTS = "bestseller_lists"
    SOCIAL_MEDIA = "social_media"
    READER_REVIEWS = "reader_reviews"
    PUBLISHER_DATA = "publisher_data"
    LITERARY_AWARDS = "literary_awards"
    BOOKSTAGRAM = "bookstagram"
    BOOKTOK = "booktok"
    GOODREADS = "goodreads"
    AMAZON = "amazon"


class AdaptationType(Enum):
    """Types of content adaptation"""
    THEME_INJECTION = "theme_injection"
    CHARACTER_ARCHETYPE = "character_archetype"
    TROPE_INCLUSION = "trope_inclusion"
    STYLE_ADJUSTMENT = "style_adjustment"
    SETTING_MODERNIZATION = "setting_modernization"
    PACING_CHANGE = "pacing_change"
    FORMAT_OPTIMIZATION = "format_optimization"


class MarketSegment(Enum):
    """Target market segments"""
    MAINSTREAM = "mainstream"
    LITERARY = "literary"
    COMMERCIAL = "commercial"
    INDIE = "indie"
    ACADEMIC = "academic"
    YOUNG_ADULT = "young_adult"
    NEW_ADULT = "new_adult"
    CHILDREN = "children"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Trend:
    """A single literary trend"""
    trend_id: str
    name: str
    category: TrendCategory
    strength: TrendStrength
    description: str
    keywords: List[str]
    related_genres: List[str]
    examples: List[str]  # Example books/authors
    emerged_date: datetime
    peak_date: Optional[datetime]
    confidence: float  # 0.0 to 1.0
    sources: List[TrendSource]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trend_id": self.trend_id,
            "name": self.name,
            "category": self.category.value,
            "strength": self.strength.value,
            "description": self.description,
            "keywords": self.keywords,
            "related_genres": self.related_genres,
            "examples": self.examples,
            "emerged_date": self.emerged_date.isoformat(),
            "peak_date": self.peak_date.isoformat() if self.peak_date else None,
            "confidence": self.confidence,
            "sources": [s.value for s in self.sources]
        }


@dataclass
class TrendApplication:
    """How a trend can be applied to content"""
    application_id: str
    trend: Trend
    adaptation_type: AdaptationType
    implementation_guide: str
    examples: List[Dict[str, str]]  # before/after examples
    impact_score: float  # Expected market impact
    difficulty: str  # "easy", "medium", "hard"
    risk_level: str  # "low", "medium", "high"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "application_id": self.application_id,
            "trend_name": self.trend.name,
            "adaptation_type": self.adaptation_type.value,
            "implementation_guide": self.implementation_guide,
            "examples": self.examples,
            "impact_score": self.impact_score,
            "difficulty": self.difficulty,
            "risk_level": self.risk_level
        }


@dataclass
class MarketAnalysis:
    """Analysis of market conditions"""
    analysis_id: str
    segment: MarketSegment
    genre: str
    trending_up: List[str]
    trending_down: List[str]
    stable_elements: List[str]
    saturated_elements: List[str]  # Overused
    opportunities: List[str]
    risks: List[str]
    competitor_analysis: Dict[str, Any]
    analyzed_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "segment": self.segment.value,
            "genre": self.genre,
            "trending_up": self.trending_up,
            "trending_down": self.trending_down,
            "stable_elements": self.stable_elements,
            "saturated_elements": self.saturated_elements,
            "opportunities": self.opportunities,
            "risks": self.risks,
            "competitor_analysis": self.competitor_analysis,
            "analyzed_at": self.analyzed_at.isoformat()
        }


@dataclass
class ContentAdaptation:
    """A specific content adaptation recommendation"""
    adaptation_id: str
    target_element: str  # What to adapt
    current_state: str
    recommended_change: str
    trend_alignment: List[str]  # Which trends this aligns with
    expected_impact: float
    implementation_priority: int  # 1-5
    chapter_scope: Optional[List[int]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adaptation_id": self.adaptation_id,
            "target_element": self.target_element,
            "current_state": self.current_state,
            "recommended_change": self.recommended_change,
            "trend_alignment": self.trend_alignment,
            "expected_impact": self.expected_impact,
            "implementation_priority": self.implementation_priority,
            "chapter_scope": self.chapter_scope
        }


@dataclass
class TrendReport:
    """Comprehensive trend analysis report"""
    report_id: str
    project_id: str
    genre: str
    target_segment: MarketSegment
    current_trends: List[Trend]
    market_analysis: MarketAnalysis
    content_adaptations: List[ContentAdaptation]
    trend_alignment_score: float
    market_readiness_score: float
    recommendations: List[str]
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "project_id": self.project_id,
            "genre": self.genre,
            "target_segment": self.target_segment.value,
            "current_trends": [t.to_dict() for t in self.current_trends],
            "market_analysis": self.market_analysis.to_dict(),
            "content_adaptations": [a.to_dict() for a in self.content_adaptations],
            "trend_alignment_score": self.trend_alignment_score,
            "market_readiness_score": self.market_readiness_score,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat()
        }


# =============================================================================
# TREND DATABASE
# =============================================================================

CURRENT_TRENDS = {
    # Theme trends
    "found_family": Trend(
        trend_id="trend_001",
        name="Found Family",
        category=TrendCategory.THEME,
        strength=TrendStrength.PEAK,
        description="Protagonists creating family bonds with non-blood relatives",
        keywords=["found family", "chosen family", "found siblings", "bond"],
        related_genres=["fantasy", "romance", "young_adult"],
        examples=["A Court of Thorns and Roses", "Six of Crows"],
        emerged_date=datetime(2018, 1, 1),
        peak_date=datetime(2023, 6, 1),
        confidence=0.95,
        sources=[TrendSource.BOOKTOK, TrendSource.GOODREADS]
    ),
    "morally_grey": Trend(
        trend_id="trend_002",
        name="Morally Grey Characters",
        category=TrendCategory.CHARACTER,
        strength=TrendStrength.PEAK,
        description="Complex protagonists with questionable morals",
        keywords=["morally grey", "antihero", "villain protagonist", "dark romance"],
        related_genres=["fantasy", "romance", "thriller"],
        examples=["The Poppy War", "Vicious"],
        emerged_date=datetime(2019, 1, 1),
        peak_date=datetime(2024, 1, 1),
        confidence=0.92,
        sources=[TrendSource.BOOKTOK, TrendSource.SOCIAL_MEDIA]
    ),
    "dual_timeline": Trend(
        trend_id="trend_003",
        name="Dual Timeline",
        category=TrendCategory.NARRATIVE,
        strength=TrendStrength.STABLE,
        description="Stories told across two time periods",
        keywords=["dual timeline", "past and present", "historical mystery"],
        related_genres=["historical", "mystery", "literary"],
        examples=["The Seven Husbands of Evelyn Hugo", "Daisy Jones & The Six"],
        emerged_date=datetime(2015, 1, 1),
        peak_date=datetime(2022, 1, 1),
        confidence=0.88,
        sources=[TrendSource.BESTSELLER_LISTS]
    ),
    "cozy_fantasy": Trend(
        trend_id="trend_004",
        name="Cozy Fantasy",
        category=TrendCategory.GENRE,
        strength=TrendStrength.GROWING,
        description="Low-stakes, comfort-focused fantasy stories",
        keywords=["cozy fantasy", "cottagecore", "low stakes", "comfort read"],
        related_genres=["fantasy", "romance"],
        examples=["Legends & Lattes", "The House in the Cerulean Sea"],
        emerged_date=datetime(2021, 1, 1),
        peak_date=None,
        confidence=0.85,
        sources=[TrendSource.BOOKTOK, TrendSource.GOODREADS]
    ),
    "romantasy": Trend(
        trend_id="trend_005",
        name="Romantasy",
        category=TrendCategory.GENRE,
        strength=TrendStrength.PEAK,
        description="Fantasy with heavy romance elements",
        keywords=["romantasy", "fantasy romance", "fae romance", "enemies to lovers"],
        related_genres=["fantasy", "romance"],
        examples=["A Court of Thorns and Roses", "From Blood and Ash"],
        emerged_date=datetime(2020, 1, 1),
        peak_date=datetime(2024, 1, 1),
        confidence=0.98,
        sources=[TrendSource.BOOKTOK, TrendSource.AMAZON]
    ),
    "mental_health": Trend(
        trend_id="trend_006",
        name="Mental Health Representation",
        category=TrendCategory.THEME,
        strength=TrendStrength.GROWING,
        description="Authentic portrayal of mental health challenges",
        keywords=["mental health", "anxiety", "depression", "therapy", "healing"],
        related_genres=["contemporary", "young_adult", "literary"],
        examples=["It's Kind of a Funny Story", "All the Bright Places"],
        emerged_date=datetime(2017, 1, 1),
        peak_date=None,
        confidence=0.90,
        sources=[TrendSource.READER_REVIEWS, TrendSource.LITERARY_AWARDS]
    ),
    "dark_academia": Trend(
        trend_id="trend_007",
        name="Dark Academia",
        category=TrendCategory.SETTING,
        strength=TrendStrength.DECLINING,
        description="Aesthetic of elite education with dark undertones",
        keywords=["dark academia", "university", "secret society", "intellectual"],
        related_genres=["thriller", "literary", "mystery"],
        examples=["The Secret History", "If We Were Villains"],
        emerged_date=datetime(2019, 1, 1),
        peak_date=datetime(2021, 1, 1),
        confidence=0.80,
        sources=[TrendSource.SOCIAL_MEDIA, TrendSource.BOOKSTAGRAM]
    ),
    "diverse_voices": Trend(
        trend_id="trend_008",
        name="Own Voices / Diverse Authors",
        category=TrendCategory.CHARACTER,
        strength=TrendStrength.STABLE,
        description="Stories by and about underrepresented groups",
        keywords=["own voices", "diverse", "representation", "BIPOC", "LGBTQ+"],
        related_genres=["all"],
        examples=["The Hate U Give", "On Earth We're Briefly Gorgeous"],
        emerged_date=datetime(2016, 1, 1),
        peak_date=datetime(2021, 1, 1),
        confidence=0.93,
        sources=[TrendSource.LITERARY_AWARDS, TrendSource.PUBLISHER_DATA]
    ),
    "spicy_content": Trend(
        trend_id="trend_009",
        name="Spicy Content",
        category=TrendCategory.STYLE,
        strength=TrendStrength.PEAK,
        description="Explicit romantic/sexual content in mainstream books",
        keywords=["spicy", "steamy", "explicit", "adult content", "heat level"],
        related_genres=["romance", "fantasy"],
        examples=["Ice Planet Barbarians", "Haunting Adeline"],
        emerged_date=datetime(2021, 1, 1),
        peak_date=datetime(2024, 1, 1),
        confidence=0.95,
        sources=[TrendSource.BOOKTOK, TrendSource.AMAZON]
    ),
    "cli_fi": Trend(
        trend_id="trend_010",
        name="Climate Fiction (Cli-Fi)",
        category=TrendCategory.THEME,
        strength=TrendStrength.GROWING,
        description="Fiction addressing climate change and environmental issues",
        keywords=["climate fiction", "cli-fi", "environmental", "solarpunk", "apocalypse"],
        related_genres=["scifi", "literary", "dystopia"],
        examples=["The Ministry for the Future", "Bewilderment"],
        emerged_date=datetime(2019, 1, 1),
        peak_date=None,
        confidence=0.82,
        sources=[TrendSource.LITERARY_AWARDS, TrendSource.PUBLISHER_DATA]
    ),
    "short_chapters": Trend(
        trend_id="trend_011",
        name="Short Chapters",
        category=TrendCategory.FORMAT,
        strength=TrendStrength.GROWING,
        description="Books with very short, punchy chapters for mobile reading",
        keywords=["short chapters", "fast paced", "quick reads", "binge reading"],
        related_genres=["thriller", "romance", "young_adult"],
        examples=["The Maid", "Verity"],
        emerged_date=datetime(2020, 1, 1),
        peak_date=None,
        confidence=0.78,
        sources=[TrendSource.AMAZON, TrendSource.PUBLISHER_DATA]
    ),
    "multiple_pov": Trend(
        trend_id="trend_012",
        name="Multiple POV",
        category=TrendCategory.NARRATIVE,
        strength=TrendStrength.STABLE,
        description="Stories told from multiple character perspectives",
        keywords=["multiple POV", "dual POV", "alternating perspectives"],
        related_genres=["romance", "thriller", "fantasy"],
        examples=["It Ends with Us", "The Seven Husbands of Evelyn Hugo"],
        emerged_date=datetime(2015, 1, 1),
        peak_date=datetime(2020, 1, 1),
        confidence=0.88,
        sources=[TrendSource.BESTSELLER_LISTS]
    )
}

# Genre-specific trend relevance
GENRE_TREND_RELEVANCE = {
    "fantasy": ["found_family", "morally_grey", "romantasy", "cozy_fantasy", "multiple_pov"],
    "romance": ["found_family", "morally_grey", "romantasy", "spicy_content", "multiple_pov"],
    "thriller": ["dual_timeline", "short_chapters", "multiple_pov", "dark_academia"],
    "mystery": ["dual_timeline", "dark_academia", "multiple_pov"],
    "scifi": ["cli_fi", "diverse_voices", "dual_timeline"],
    "literary": ["dual_timeline", "mental_health", "diverse_voices", "cli_fi"],
    "young_adult": ["found_family", "mental_health", "diverse_voices", "short_chapters"],
    "horror": ["dark_academia", "dual_timeline", "morally_grey"]
}


# =============================================================================
# TROPE DATABASE
# =============================================================================

POPULAR_TROPES = {
    "enemies_to_lovers": {
        "name": "Enemies to Lovers",
        "popularity": 0.95,
        "genres": ["romance", "fantasy"],
        "description": "Characters start as adversaries and develop romantic feelings",
        "keywords": ["hate to love", "rivalry", "tension"]
    },
    "fake_dating": {
        "name": "Fake Dating",
        "popularity": 0.85,
        "genres": ["romance", "contemporary"],
        "description": "Characters pretend to date for convenience",
        "keywords": ["fake relationship", "pretend couple"]
    },
    "only_one_bed": {
        "name": "Only One Bed",
        "popularity": 0.88,
        "genres": ["romance"],
        "description": "Forced proximity due to limited sleeping arrangements",
        "keywords": ["forced proximity", "sharing bed"]
    },
    "grumpy_sunshine": {
        "name": "Grumpy/Sunshine",
        "popularity": 0.90,
        "genres": ["romance"],
        "description": "Pairing of a grumpy character with an optimistic one",
        "keywords": ["opposites attract", "grumpy x sunshine"]
    },
    "slow_burn": {
        "name": "Slow Burn",
        "popularity": 0.92,
        "genres": ["romance", "fantasy"],
        "description": "Gradual development of romantic relationship",
        "keywords": ["slow build", "tension building"]
    },
    "chosen_one": {
        "name": "The Chosen One",
        "popularity": 0.70,  # Declining
        "genres": ["fantasy", "scifi"],
        "description": "Protagonist destined for greatness",
        "keywords": ["prophecy", "destiny", "special powers"]
    },
    "hidden_identity": {
        "name": "Hidden Identity",
        "popularity": 0.82,
        "genres": ["fantasy", "romance", "thriller"],
        "description": "Character concealing their true identity",
        "keywords": ["secret identity", "disguise", "revelation"]
    },
    "heist_crew": {
        "name": "Heist Crew",
        "popularity": 0.80,
        "genres": ["fantasy", "thriller"],
        "description": "Group assembles for elaborate theft/mission",
        "keywords": ["heist", "crew", "found family", "specialists"]
    },
    "redemption_arc": {
        "name": "Redemption Arc",
        "popularity": 0.85,
        "genres": ["fantasy", "literary"],
        "description": "Villain or flawed character seeking redemption",
        "keywords": ["redemption", "second chance", "atonement"]
    },
    "unreliable_narrator": {
        "name": "Unreliable Narrator",
        "popularity": 0.78,
        "genres": ["thriller", "literary", "mystery"],
        "description": "Narrator whose credibility is compromised",
        "keywords": ["twist", "perspective", "deception"]
    }
}


# =============================================================================
# MAIN CLASS
# =============================================================================

class TrendAdaptiveEngine:
    """
    Trend-Adaptive Content Generation Engine

    Analyzes market trends and adapts content to maximize appeal
    while maintaining artistic integrity.
    """

    def __init__(self):
        self.trends: Dict[str, Trend] = CURRENT_TRENDS.copy()
        self.reports: Dict[str, TrendReport] = {}
        self.market_analyses: Dict[str, MarketAnalysis] = {}

    async def analyze_trends_for_project(
        self,
        project_id: str,
        genre: str,
        target_segment: MarketSegment,
        current_content: Optional[Dict[str, Any]] = None
    ) -> TrendReport:
        """
        Analyze current trends and generate recommendations for a project.
        """
        # Get relevant trends for genre
        relevant_trends = self._get_relevant_trends(genre)

        # Perform market analysis
        market_analysis = await self._analyze_market(genre, target_segment)

        # Generate content adaptations
        content_adaptations = []
        if current_content:
            content_adaptations = self._generate_adaptations(
                current_content, relevant_trends, market_analysis
            )

        # Calculate scores
        trend_alignment = self._calculate_trend_alignment(
            current_content, relevant_trends
        ) if current_content else 0.5

        market_readiness = self._calculate_market_readiness(
            market_analysis, relevant_trends
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            genre, target_segment, relevant_trends, market_analysis
        )

        report = TrendReport(
            report_id=str(uuid.uuid4()),
            project_id=project_id,
            genre=genre,
            target_segment=target_segment,
            current_trends=relevant_trends,
            market_analysis=market_analysis,
            content_adaptations=content_adaptations,
            trend_alignment_score=trend_alignment,
            market_readiness_score=market_readiness,
            recommendations=recommendations,
            created_at=datetime.now()
        )

        self.reports[report.report_id] = report
        return report

    async def get_trending_elements(
        self,
        genre: str,
        category: Optional[TrendCategory] = None
    ) -> Dict[str, Any]:
        """
        Get currently trending elements for a genre.
        """
        relevant_trends = self._get_relevant_trends(genre)

        if category:
            relevant_trends = [t for t in relevant_trends if t.category == category]

        # Get popular tropes
        genre_tropes = {
            name: data for name, data in POPULAR_TROPES.items()
            if genre in data["genres"]
        }

        # Sort by strength
        sorted_trends = sorted(
            relevant_trends,
            key=lambda t: (
                t.strength == TrendStrength.PEAK,
                t.strength == TrendStrength.GROWING,
                t.confidence
            ),
            reverse=True
        )

        return {
            "genre": genre,
            "trends": [t.to_dict() for t in sorted_trends],
            "popular_tropes": genre_tropes,
            "recommendations": self._get_quick_recommendations(genre, sorted_trends)
        }

    async def analyze_content_trends(
        self,
        text: str,
        genre: str
    ) -> Dict[str, Any]:
        """
        Analyze how well content aligns with current trends.
        """
        relevant_trends = self._get_relevant_trends(genre)

        # Check for trend keywords
        trend_matches = []
        for trend in relevant_trends:
            match_count = sum(1 for kw in trend.keywords if kw.lower() in text.lower())
            if match_count > 0:
                trend_matches.append({
                    "trend": trend.name,
                    "strength": trend.strength.value,
                    "keyword_matches": match_count,
                    "confidence": match_count / len(trend.keywords)
                })

        # Check for tropes
        trope_matches = []
        for trope_id, trope_data in POPULAR_TROPES.items():
            if genre in trope_data["genres"]:
                match_count = sum(1 for kw in trope_data["keywords"] if kw.lower() in text.lower())
                if match_count > 0:
                    trope_matches.append({
                        "trope": trope_data["name"],
                        "popularity": trope_data["popularity"],
                        "keyword_matches": match_count
                    })

        # Calculate overall trend alignment
        alignment_score = len(trend_matches) / max(len(relevant_trends), 1)

        return {
            "genre": genre,
            "trend_alignment_score": alignment_score,
            "trend_matches": trend_matches,
            "trope_matches": trope_matches,
            "missing_opportunities": self._identify_missing_trends(
                genre, trend_matches, relevant_trends
            ),
            "recommendations": self._generate_content_recommendations(
                trend_matches, trope_matches, genre
            )
        }

    async def suggest_trending_elements(
        self,
        genre: str,
        existing_elements: List[str]
    ) -> Dict[str, Any]:
        """
        Suggest trending elements to add to content.
        """
        relevant_trends = self._get_relevant_trends(genre)

        # Find trends not yet represented
        unrepresented_trends = []
        for trend in relevant_trends:
            if not any(elem.lower() in " ".join(trend.keywords).lower() for elem in existing_elements):
                unrepresented_trends.append(trend)

        # Find tropes not yet used
        unused_tropes = []
        for trope_id, trope_data in POPULAR_TROPES.items():
            if genre in trope_data["genres"]:
                if not any(elem.lower() in " ".join(trope_data["keywords"]).lower() for elem in existing_elements):
                    unused_tropes.append(trope_data)

        # Prioritize suggestions
        suggestions = []

        # Peak/growing trends first
        for trend in unrepresented_trends:
            if trend.strength in [TrendStrength.PEAK, TrendStrength.GROWING]:
                suggestions.append({
                    "type": "trend",
                    "name": trend.name,
                    "priority": "high" if trend.strength == TrendStrength.PEAK else "medium",
                    "description": trend.description,
                    "implementation_tips": self._get_implementation_tips(trend)
                })

        # Popular tropes
        for trope in sorted(unused_tropes, key=lambda t: t["popularity"], reverse=True)[:5]:
            suggestions.append({
                "type": "trope",
                "name": trope["name"],
                "priority": "high" if trope["popularity"] > 0.85 else "medium",
                "description": trope["description"],
                "implementation_tips": self._get_trope_tips(trope)
            })

        return {
            "genre": genre,
            "current_elements": existing_elements,
            "suggestions": suggestions[:10],
            "market_insight": self._get_market_insight(genre)
        }

    async def forecast_trends(
        self,
        months_ahead: int = 6
    ) -> Dict[str, Any]:
        """
        Forecast trend trajectories.
        """
        forecasts = []

        for trend in self.trends.values():
            forecast = self._forecast_single_trend(trend, months_ahead)
            forecasts.append(forecast)

        # Identify emerging opportunities
        emerging = [
            f for f in forecasts
            if f["predicted_strength"] in ["growing", "peak"]
            and f["current_strength"] in ["emerging", "growing"]
        ]

        # Identify declining trends to avoid
        declining = [
            f for f in forecasts
            if f["predicted_strength"] in ["declining", "fading"]
        ]

        return {
            "forecast_period_months": months_ahead,
            "forecasts": forecasts,
            "emerging_opportunities": emerging,
            "declining_trends": declining,
            "recommendations": self._generate_forecast_recommendations(emerging, declining)
        }

    def get_genre_profile(self, genre: str) -> Dict[str, Any]:
        """
        Get a complete trend profile for a genre.
        """
        relevant_trends = self._get_relevant_trends(genre)
        genre_tropes = {
            name: data for name, data in POPULAR_TROPES.items()
            if genre in data["genres"]
        }

        return {
            "genre": genre,
            "active_trends": [
                {
                    "name": t.name,
                    "strength": t.strength.value,
                    "category": t.category.value
                }
                for t in relevant_trends
            ],
            "popular_tropes": [
                {
                    "name": data["name"],
                    "popularity": data["popularity"]
                }
                for name, data in sorted(
                    genre_tropes.items(),
                    key=lambda x: x[1]["popularity"],
                    reverse=True
                )
            ],
            "recommended_elements": self._get_recommended_elements(genre),
            "elements_to_avoid": self._get_saturated_elements(genre),
            "market_position": self._analyze_genre_market(genre)
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_relevant_trends(self, genre: str) -> List[Trend]:
        """Get trends relevant to a genre."""
        relevant_ids = GENRE_TREND_RELEVANCE.get(genre.lower(), [])

        relevant_trends = [
            self.trends[tid] for tid in relevant_ids
            if tid in self.trends
        ]

        # Also include universal trends
        for trend in self.trends.values():
            if "all" in trend.related_genres and trend not in relevant_trends:
                relevant_trends.append(trend)

        return relevant_trends

    async def _analyze_market(
        self,
        genre: str,
        segment: MarketSegment
    ) -> MarketAnalysis:
        """Perform market analysis for a genre."""
        relevant_trends = self._get_relevant_trends(genre)

        # Categorize trends
        trending_up = [
            t.name for t in relevant_trends
            if t.strength in [TrendStrength.EMERGING, TrendStrength.GROWING]
        ]

        trending_down = [
            t.name for t in relevant_trends
            if t.strength in [TrendStrength.DECLINING, TrendStrength.FADING]
        ]

        stable = [
            t.name for t in relevant_trends
            if t.strength == TrendStrength.STABLE
        ]

        # Identify saturated elements (peak trends that have been around too long)
        saturated = [
            t.name for t in relevant_trends
            if t.strength == TrendStrength.PEAK and t.emerged_date < datetime.now() - timedelta(days=730)
        ]

        # Identify opportunities
        opportunities = self._identify_opportunities(genre, relevant_trends)

        # Identify risks
        risks = self._identify_risks(genre, relevant_trends)

        analysis = MarketAnalysis(
            analysis_id=str(uuid.uuid4()),
            segment=segment,
            genre=genre,
            trending_up=trending_up,
            trending_down=trending_down,
            stable_elements=stable,
            saturated_elements=saturated,
            opportunities=opportunities,
            risks=risks,
            competitor_analysis=self._analyze_competitors(genre),
            analyzed_at=datetime.now()
        )

        self.market_analyses[analysis.analysis_id] = analysis
        return analysis

    def _generate_adaptations(
        self,
        content: Dict[str, Any],
        trends: List[Trend],
        market: MarketAnalysis
    ) -> List[ContentAdaptation]:
        """Generate content adaptations based on trends."""
        adaptations = []

        # Check for trending themes not present
        for trend in trends:
            if trend.strength in [TrendStrength.PEAK, TrendStrength.GROWING]:
                # Check if trend elements are in content
                content_str = str(content).lower()
                if not any(kw in content_str for kw in trend.keywords):
                    adaptations.append(ContentAdaptation(
                        adaptation_id=str(uuid.uuid4()),
                        target_element=trend.category.value,
                        current_state="Brak elementu",
                        recommended_change=f"Dodaj elementy trendu '{trend.name}'",
                        trend_alignment=[trend.name],
                        expected_impact=trend.confidence * 0.8,
                        implementation_priority=5 if trend.strength == TrendStrength.PEAK else 4,
                        chapter_scope=None
                    ))

        # Check for declining elements to remove
        for element in market.trending_down:
            if element.lower() in str(content).lower():
                adaptations.append(ContentAdaptation(
                    adaptation_id=str(uuid.uuid4()),
                    target_element="declining_element",
                    current_state=f"Zawiera '{element}'",
                    recommended_change=f"Rozważ zredukowanie lub zmianę '{element}'",
                    trend_alignment=[],
                    expected_impact=0.3,
                    implementation_priority=2,
                    chapter_scope=None
                ))

        return adaptations

    def _calculate_trend_alignment(
        self,
        content: Optional[Dict[str, Any]],
        trends: List[Trend]
    ) -> float:
        """Calculate how well content aligns with trends."""
        if not content or not trends:
            return 0.5

        content_str = str(content).lower()
        matched_trends = 0

        for trend in trends:
            if any(kw in content_str for kw in trend.keywords):
                matched_trends += 1

        return matched_trends / len(trends)

    def _calculate_market_readiness(
        self,
        market: MarketAnalysis,
        trends: List[Trend]
    ) -> float:
        """Calculate market readiness score."""
        score = 0.5

        # Bonus for aligning with trending up elements
        score += len(market.trending_up) * 0.05

        # Bonus for avoiding saturated elements
        score += 0.1 if len(market.saturated_elements) == 0 else 0

        # Bonus for opportunities
        score += len(market.opportunities) * 0.03

        return min(1.0, score)

    def _generate_recommendations(
        self,
        genre: str,
        segment: MarketSegment,
        trends: List[Trend],
        market: MarketAnalysis
    ) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []

        # Peak trends
        peak_trends = [t for t in trends if t.strength == TrendStrength.PEAK]
        if peak_trends:
            recommendations.append(
                f"Wykorzystaj szczytowe trendy: {', '.join(t.name for t in peak_trends[:3])}"
            )

        # Growing trends
        growing_trends = [t for t in trends if t.strength == TrendStrength.GROWING]
        if growing_trends:
            recommendations.append(
                f"Rozważ włączenie rosnących trendów: {', '.join(t.name for t in growing_trends[:3])}"
            )

        # Saturated elements
        if market.saturated_elements:
            recommendations.append(
                f"Unikaj przesyconych elementów: {', '.join(market.saturated_elements[:3])}"
            )

        # Opportunities
        if market.opportunities:
            recommendations.append(
                f"Wykorzystaj szanse rynkowe: {', '.join(market.opportunities[:3])}"
            )

        # Segment-specific
        if segment == MarketSegment.YOUNG_ADULT:
            recommendations.append(
                "Dla YA: Skup się na autentycznych głosach bohaterów i kwestiach zdrowia psychicznego"
            )
        elif segment == MarketSegment.COMMERCIAL:
            recommendations.append(
                "Dla rynku komercyjnego: Priorytet - dynamiczna akcja i silne haki fabularne"
            )

        return recommendations

    def _identify_opportunities(self, genre: str, trends: List[Trend]) -> List[str]:
        """Identify market opportunities."""
        opportunities = []

        # Emerging trends
        emerging = [t for t in trends if t.strength == TrendStrength.EMERGING]
        for trend in emerging:
            opportunities.append(f"Wcześnie adoptuj trend: {trend.name}")

        # Growing trends with high confidence
        for trend in trends:
            if trend.strength == TrendStrength.GROWING and trend.confidence > 0.8:
                opportunities.append(f"Silny wzrost: {trend.name}")

        # Genre combinations
        if genre == "fantasy":
            opportunities.append("Połączenie fantasy z elementami romance (romantasy)")
        if genre == "thriller":
            opportunities.append("Thriller z elementami społecznymi")

        return opportunities[:5]

    def _identify_risks(self, genre: str, trends: List[Trend]) -> List[str]:
        """Identify market risks."""
        risks = []

        # Declining trends
        declining = [t for t in trends if t.strength == TrendStrength.DECLINING]
        for trend in declining:
            risks.append(f"Spadający trend: {trend.name}")

        # Oversaturation
        peak_old = [
            t for t in trends
            if t.strength == TrendStrength.PEAK
            and t.emerged_date < datetime.now() - timedelta(days=1000)
        ]
        for trend in peak_old:
            risks.append(f"Ryzyko przesycenia: {trend.name}")

        return risks[:5]

    def _analyze_competitors(self, genre: str) -> Dict[str, Any]:
        """Analyze competitor landscape."""
        # Simplified - would use real data in production
        return {
            "market_saturation": "medium",
            "dominant_themes": GENRE_TREND_RELEVANCE.get(genre, [])[:3],
            "gap_opportunities": ["emerging subgenres", "underrepresented perspectives"]
        }

    def _identify_missing_trends(
        self,
        genre: str,
        matches: List[Dict],
        trends: List[Trend]
    ) -> List[Dict]:
        """Identify trends not present in content."""
        matched_names = [m["trend"] for m in matches]

        missing = []
        for trend in trends:
            if trend.name not in matched_names:
                if trend.strength in [TrendStrength.PEAK, TrendStrength.GROWING]:
                    missing.append({
                        "trend": trend.name,
                        "strength": trend.strength.value,
                        "opportunity_score": trend.confidence
                    })

        return sorted(missing, key=lambda x: x["opportunity_score"], reverse=True)[:5]

    def _generate_content_recommendations(
        self,
        trend_matches: List[Dict],
        trope_matches: List[Dict],
        genre: str
    ) -> List[str]:
        """Generate content-specific recommendations."""
        recommendations = []

        if not trend_matches:
            recommendations.append("Treść nie wykorzystuje aktualnych trendów - rozważ włączenie popularnych motywów")
        else:
            strong_matches = [m for m in trend_matches if m["confidence"] > 0.5]
            if strong_matches:
                recommendations.append(
                    f"Silne dopasowanie do trendów: {', '.join(m['trend'] for m in strong_matches)}"
                )

        if not trope_matches:
            recommendations.append("Brak rozpoznawalnych tropów - rozważ dodanie popularnych motywów gatunkowych")

        return recommendations

    def _get_implementation_tips(self, trend: Trend) -> List[str]:
        """Get tips for implementing a trend."""
        tips_map = {
            "found_family": [
                "Stwórz grupę bohaterów z różnymi talentami",
                "Pokaż rozwój więzi między postaciami",
                "Dodaj momenty wzajemnego wsparcia"
            ],
            "morally_grey": [
                "Daj bohaterowi przekonujące motywacje",
                "Pokaż wewnętrzny konflikt moralny",
                "Unikaj jednoznacznych osądów"
            ],
            "cozy_fantasy": [
                "Skup się na codziennych przyjemnościach",
                "Ogranicz przemoc i napięcie",
                "Dodaj ciepłe relacje i humor"
            ],
            "dual_timeline": [
                "Połącz obie linie tematycznie",
                "Używaj kontrastów między epokami",
                "Buduj napięcie poprzez odkrywanie przeszłości"
            ]
        }

        return tips_map.get(trend.trend_id, [
            f"Włącz elementy: {', '.join(trend.keywords[:3])}",
            trend.description
        ])

    def _get_trope_tips(self, trope: Dict) -> List[str]:
        """Get tips for implementing a trope."""
        return [
            f"Wykorzystaj słowa kluczowe: {', '.join(trope['keywords'])}",
            trope["description"],
            "Dodaj własny twist, aby wyróżnić się"
        ]

    def _get_market_insight(self, genre: str) -> str:
        """Get market insight for a genre."""
        insights = {
            "fantasy": "Rynek fantasy zdominowany przez romantasy i cozy fantasy. Morally grey characters są kluczowe.",
            "romance": "BookTok napędza sprzedaż. Spicy content i enemies to lovers cieszą się największą popularnością.",
            "thriller": "Krótkie rozdziały i dual timeline dominują. Psychological thriller w trendzie wzrostowym.",
            "mystery": "Dual timeline i unreliable narrator są popularne. Dark academia spada.",
            "scifi": "Cli-fi rośnie. Diverse voices i społeczne komentarze są cenione.",
            "literary": "Mental health i diverse voices dominują nagrody. Dual timeline ciągle popularne."
        }

        return insights.get(genre.lower(), "Śledź trendy BookTok i Goodreads dla najlepszych wskazówek.")

    def _forecast_single_trend(self, trend: Trend, months: int) -> Dict[str, Any]:
        """Forecast a single trend's trajectory."""
        # Simplified forecasting logic
        strength_progression = {
            TrendStrength.EMERGING: TrendStrength.GROWING,
            TrendStrength.GROWING: TrendStrength.PEAK,
            TrendStrength.PEAK: TrendStrength.STABLE,
            TrendStrength.STABLE: TrendStrength.DECLINING,
            TrendStrength.DECLINING: TrendStrength.FADING,
            TrendStrength.FADING: TrendStrength.FADING
        }

        # Calculate predicted strength based on age and current strength
        predicted = trend.strength
        if months > 6:
            predicted = strength_progression.get(trend.strength, trend.strength)

        return {
            "trend_name": trend.name,
            "current_strength": trend.strength.value,
            "predicted_strength": predicted.value,
            "confidence": trend.confidence * 0.8,  # Reduce confidence for forecast
            "recommendation": self._get_forecast_recommendation(trend, predicted)
        }

    def _get_forecast_recommendation(self, trend: Trend, predicted: TrendStrength) -> str:
        """Get recommendation based on forecast."""
        if predicted in [TrendStrength.GROWING, TrendStrength.PEAK]:
            return f"Wykorzystaj {trend.name} - trend w fazie wzrostu"
        elif predicted == TrendStrength.STABLE:
            return f"{trend.name} - bezpieczny wybór, stabilna popularność"
        else:
            return f"Unikaj nadmiernego polegania na {trend.name}"

    def _generate_forecast_recommendations(
        self,
        emerging: List[Dict],
        declining: List[Dict]
    ) -> List[str]:
        """Generate recommendations from forecasts."""
        recommendations = []

        if emerging:
            names = [e["trend_name"] for e in emerging[:3]]
            recommendations.append(f"Skup się na rosnących trendach: {', '.join(names)}")

        if declining:
            names = [d["trend_name"] for d in declining[:3]]
            recommendations.append(f"Ogranicz spadające trendy: {', '.join(names)}")

        recommendations.append("Monitoruj BookTok i Goodreads dla wczesnych sygnałów nowych trendów")

        return recommendations

    def _get_recommended_elements(self, genre: str) -> List[str]:
        """Get recommended elements for a genre."""
        elements = {
            "fantasy": ["found family", "morally grey hero", "romantic subplot", "magic system"],
            "romance": ["strong chemistry", "emotional depth", "satisfying ending", "relatable conflicts"],
            "thriller": ["short chapters", "multiple POV", "twist ending", "time pressure"],
            "mystery": ["fair clues", "complex detective", "atmospheric setting", "satisfying reveal"],
            "scifi": ["thought-provoking premise", "diverse cast", "relevant themes", "detailed worldbuilding"],
            "literary": ["beautiful prose", "complex characters", "meaningful themes", "emotional resonance"]
        }

        return elements.get(genre.lower(), ["strong characters", "engaging plot", "clear voice"])

    def _get_saturated_elements(self, genre: str) -> List[str]:
        """Get saturated/overused elements for a genre."""
        saturated = {
            "fantasy": ["pure evil villain", "chosen one without subversion", "info-dump worldbuilding"],
            "romance": ["miscommunication as only conflict", "love triangle", "perfect hero"],
            "thriller": ["amnesia twist", "it was all a dream", "excessive flashbacks"],
            "mystery": ["butler did it", "random killer", "convenient evidence"],
            "scifi": ["AI uprising without nuance", "pure dystopia", "technobabble"],
            "literary": ["suffering without purpose", "pretentious prose", "ambiguous ending without meaning"]
        }

        return saturated.get(genre.lower(), ["clichés", "predictable plots"])

    def _analyze_genre_market(self, genre: str) -> Dict[str, Any]:
        """Analyze market position for a genre."""
        # Simplified analysis
        positions = {
            "fantasy": {"health": "strong", "growth": "stable", "competition": "high"},
            "romance": {"health": "very strong", "growth": "growing", "competition": "very high"},
            "thriller": {"health": "strong", "growth": "stable", "competition": "high"},
            "mystery": {"health": "stable", "growth": "stable", "competition": "medium"},
            "scifi": {"health": "moderate", "growth": "growing", "competition": "medium"},
            "literary": {"health": "niche", "growth": "stable", "competition": "low"}
        }

        return positions.get(genre.lower(), {"health": "unknown", "growth": "unknown", "competition": "unknown"})

    def _get_quick_recommendations(self, genre: str, trends: List[Trend]) -> List[str]:
        """Get quick recommendations for a genre."""
        recommendations = []

        peak_trends = [t for t in trends if t.strength == TrendStrength.PEAK][:2]
        if peak_trends:
            recommendations.append(f"Must-have: {', '.join(t.name for t in peak_trends)}")

        growing_trends = [t for t in trends if t.strength == TrendStrength.GROWING][:2]
        if growing_trends:
            recommendations.append(f"Rising: {', '.join(t.name for t in growing_trends)}")

        return recommendations

    # =========================================================================
    # PUBLIC GETTERS
    # =========================================================================

    def get_report(self, report_id: str) -> Optional[TrendReport]:
        """Get a trend report by ID."""
        return self.reports.get(report_id)

    def get_trend(self, trend_id: str) -> Optional[Trend]:
        """Get a trend by ID."""
        return self.trends.get(trend_id)

    def list_all_trends(self) -> List[Dict[str, Any]]:
        """List all tracked trends."""
        return [
            {
                "trend_id": t.trend_id,
                "name": t.name,
                "category": t.category.value,
                "strength": t.strength.value,
                "confidence": t.confidence
            }
            for t in self.trends.values()
        ]

    def list_reports(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all reports."""
        reports = self.reports.values()
        if project_id:
            reports = [r for r in reports if r.project_id == project_id]

        return [
            {
                "report_id": r.report_id,
                "project_id": r.project_id,
                "genre": r.genre,
                "trend_alignment": r.trend_alignment_score,
                "created_at": r.created_at.isoformat()
            }
            for r in reports
        ]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_trend_engine: Optional[TrendAdaptiveEngine] = None


def get_trend_engine() -> TrendAdaptiveEngine:
    """Get the singleton trend engine instance."""
    global _trend_engine
    if _trend_engine is None:
        _trend_engine = TrendAdaptiveEngine()
    return _trend_engine

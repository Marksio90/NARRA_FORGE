"""
TITAN Cultural Intelligence System - NarraForge 3.0 Phase 3

Advanced system for cultural awareness, localization, and sensitivity
in narrative generation. Ensures content is culturally appropriate
and resonates with target audiences across different cultures.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from datetime import datetime
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class CultureRegion(Enum):
    """Major cultural regions"""
    WESTERN_EUROPE = "western_europe"
    EASTERN_EUROPE = "eastern_europe"
    NORTH_AMERICA = "north_america"
    LATIN_AMERICA = "latin_america"
    EAST_ASIA = "east_asia"
    SOUTH_ASIA = "south_asia"
    MIDDLE_EAST = "middle_east"
    AFRICA = "africa"
    OCEANIA = "oceania"
    GLOBAL = "global"


class CulturalDimension(Enum):
    """Hofstede cultural dimensions"""
    INDIVIDUALISM = "individualism"          # vs Collectivism
    POWER_DISTANCE = "power_distance"        # High vs Low
    MASCULINITY = "masculinity"              # vs Femininity
    UNCERTAINTY_AVOIDANCE = "uncertainty_avoidance"
    LONG_TERM_ORIENTATION = "long_term_orientation"
    INDULGENCE = "indulgence"                # vs Restraint


class SensitivityCategory(Enum):
    """Categories requiring cultural sensitivity"""
    RELIGION = "religion"
    POLITICS = "politics"
    GENDER = "gender"
    SEXUALITY = "sexuality"
    RACE_ETHNICITY = "race_ethnicity"
    CLASS = "class"
    AGE = "age"
    DISABILITY = "disability"
    VIOLENCE = "violence"
    DEATH = "death"
    FAMILY = "family"
    FOOD = "food"
    CUSTOMS = "customs"


class LocalizationLevel(Enum):
    """Levels of cultural localization"""
    NONE = "none"              # Original content
    LIGHT = "light"            # Minor adjustments
    MODERATE = "moderate"      # Significant adaptations
    DEEP = "deep"              # Major cultural rewrite
    TRANSCREATION = "transcreation"  # Complete reimagining


class CulturalTone(Enum):
    """Cultural communication tones"""
    FORMAL = "formal"
    INFORMAL = "informal"
    DIRECT = "direct"
    INDIRECT = "indirect"
    HIERARCHICAL = "hierarchical"
    EGALITARIAN = "egalitarian"


class SensitivityLevel(Enum):
    """Sensitivity levels for content"""
    SAFE = "safe"              # Universally acceptable
    MILD = "mild"              # Minor sensitivity
    MODERATE = "moderate"      # Requires awareness
    HIGH = "high"              # Requires careful handling
    CRITICAL = "critical"      # May be offensive


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CulturalProfile:
    """Cultural profile for a region/country"""
    profile_id: str
    region: CultureRegion
    country_code: str
    country_name: str
    language: str
    dimensions: Dict[CulturalDimension, float]  # 0.0 to 1.0
    communication_style: CulturalTone
    taboo_topics: List[str]
    sensitive_topics: List[str]
    preferred_themes: List[str]
    storytelling_traditions: List[str]
    name_conventions: Dict[str, Any]
    family_structure: str
    religious_context: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "region": self.region.value,
            "country_code": self.country_code,
            "country_name": self.country_name,
            "language": self.language,
            "dimensions": {d.value: v for d, v in self.dimensions.items()},
            "communication_style": self.communication_style.value,
            "taboo_topics": self.taboo_topics,
            "sensitive_topics": self.sensitive_topics,
            "preferred_themes": self.preferred_themes,
            "storytelling_traditions": self.storytelling_traditions,
            "name_conventions": self.name_conventions,
            "family_structure": self.family_structure,
            "religious_context": self.religious_context
        }


@dataclass
class SensitivityIssue:
    """A detected cultural sensitivity issue"""
    issue_id: str
    category: SensitivityCategory
    level: SensitivityLevel
    description: str
    affected_text: str
    chapter: int
    paragraph: int
    affected_cultures: List[str]
    suggested_alternative: str
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "category": self.category.value,
            "level": self.level.value,
            "description": self.description,
            "affected_text": self.affected_text,
            "chapter": self.chapter,
            "paragraph": self.paragraph,
            "affected_cultures": self.affected_cultures,
            "suggested_alternative": self.suggested_alternative,
            "explanation": self.explanation
        }


@dataclass
class LocalizationSuggestion:
    """Suggestion for cultural localization"""
    suggestion_id: str
    original_text: str
    localized_text: str
    target_culture: str
    localization_type: str
    confidence: float
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "suggestion_id": self.suggestion_id,
            "original_text": self.original_text,
            "localized_text": self.localized_text,
            "target_culture": self.target_culture,
            "localization_type": self.localization_type,
            "confidence": self.confidence,
            "notes": self.notes
        }


@dataclass
class CulturalElement:
    """A cultural element in the story"""
    element_id: str
    element_type: str  # name, custom, food, religion, etc.
    original_value: str
    cultural_context: str
    universality_score: float  # How universal vs culture-specific
    requires_localization: bool
    chapter: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "element_type": self.element_type,
            "original_value": self.original_value,
            "cultural_context": self.cultural_context,
            "universality_score": self.universality_score,
            "requires_localization": self.requires_localization,
            "chapter": self.chapter
        }


@dataclass
class CulturalAdaptation:
    """A cultural adaptation of content"""
    adaptation_id: str
    original_element: CulturalElement
    target_culture: CulturalProfile
    adapted_value: str
    adaptation_notes: str
    approved: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adaptation_id": self.adaptation_id,
            "original_element": self.original_element.to_dict(),
            "target_culture": self.target_culture.country_code,
            "adapted_value": self.adapted_value,
            "adaptation_notes": self.adaptation_notes,
            "approved": self.approved
        }


@dataclass
class CulturalAnalysisReport:
    """Full cultural analysis report"""
    report_id: str
    project_id: str
    source_culture: CulturalProfile
    target_cultures: List[CulturalProfile]
    sensitivity_issues: List[SensitivityIssue]
    cultural_elements: List[CulturalElement]
    localization_suggestions: List[LocalizationSuggestion]
    overall_sensitivity_score: float  # 0.0 = many issues, 1.0 = safe
    cultural_authenticity_score: float
    localization_readiness: float
    recommendations: List[str]
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "project_id": self.project_id,
            "source_culture": self.source_culture.to_dict(),
            "target_cultures": [c.country_code for c in self.target_cultures],
            "sensitivity_issues": [i.to_dict() for i in self.sensitivity_issues],
            "issues_by_level": {
                level.value: len([i for i in self.sensitivity_issues if i.level == level])
                for level in SensitivityLevel
            },
            "cultural_elements": [e.to_dict() for e in self.cultural_elements],
            "localization_suggestions": [s.to_dict() for s in self.localization_suggestions],
            "overall_sensitivity_score": self.overall_sensitivity_score,
            "cultural_authenticity_score": self.cultural_authenticity_score,
            "localization_readiness": self.localization_readiness,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat()
        }


# =============================================================================
# CULTURAL PROFILES DATABASE
# =============================================================================

CULTURAL_PROFILES = {
    "PL": CulturalProfile(
        profile_id="pl_001",
        region=CultureRegion.EASTERN_EUROPE,
        country_code="PL",
        country_name="Polska",
        language="pl",
        dimensions={
            CulturalDimension.INDIVIDUALISM: 0.6,
            CulturalDimension.POWER_DISTANCE: 0.68,
            CulturalDimension.MASCULINITY: 0.64,
            CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.93,
            CulturalDimension.LONG_TERM_ORIENTATION: 0.38,
            CulturalDimension.INDULGENCE: 0.29
        },
        communication_style=CulturalTone.INDIRECT,
        taboo_topics=["holocaust_jokes", "nazi_comparisons", "soviet_praise"],
        sensitive_topics=["religion", "abortion", "lgbt", "russian_relations"],
        preferred_themes=["patriotyzm", "rodzina", "honor", "walka o wolność", "tradycja"],
        storytelling_traditions=["romantyzm", "martyrologia", "realizm magiczny"],
        name_conventions={"patronymic": False, "surname_gender": True, "diminutives": True},
        family_structure="traditional_extended",
        religious_context="catholic_majority"
    ),
    "US": CulturalProfile(
        profile_id="us_001",
        region=CultureRegion.NORTH_AMERICA,
        country_code="US",
        country_name="United States",
        language="en",
        dimensions={
            CulturalDimension.INDIVIDUALISM: 0.91,
            CulturalDimension.POWER_DISTANCE: 0.40,
            CulturalDimension.MASCULINITY: 0.62,
            CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.46,
            CulturalDimension.LONG_TERM_ORIENTATION: 0.26,
            CulturalDimension.INDULGENCE: 0.68
        },
        communication_style=CulturalTone.DIRECT,
        taboo_topics=["racial_slurs", "school_shootings_jokes"],
        sensitive_topics=["race", "gun_control", "politics", "religion"],
        preferred_themes=["self-reliance", "success", "freedom", "diversity", "redemption"],
        storytelling_traditions=["hero_journey", "rags_to_riches", "underdog"],
        name_conventions={"patronymic": False, "surname_gender": False, "middle_name": True},
        family_structure="nuclear_diverse",
        religious_context="pluralistic"
    ),
    "JP": CulturalProfile(
        profile_id="jp_001",
        region=CultureRegion.EAST_ASIA,
        country_code="JP",
        country_name="Japan",
        language="ja",
        dimensions={
            CulturalDimension.INDIVIDUALISM: 0.46,
            CulturalDimension.POWER_DISTANCE: 0.54,
            CulturalDimension.MASCULINITY: 0.95,
            CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.92,
            CulturalDimension.LONG_TERM_ORIENTATION: 0.88,
            CulturalDimension.INDULGENCE: 0.42
        },
        communication_style=CulturalTone.INDIRECT,
        taboo_topics=["wwii_atrocities", "emperor_criticism"],
        sensitive_topics=["suicide", "mental_health", "burakumin", "korean_relations"],
        preferred_themes=["honor", "duty", "perseverance", "harmony", "nature", "seasons"],
        storytelling_traditions=["mono_no_aware", "kishotenketsu", "slice_of_life"],
        name_conventions={"family_first": True, "honorifics": True, "given_name_use": "intimate"},
        family_structure="traditional_multigenerational",
        religious_context="syncretic_shinto_buddhist"
    ),
    "DE": CulturalProfile(
        profile_id="de_001",
        region=CultureRegion.WESTERN_EUROPE,
        country_code="DE",
        country_name="Germany",
        language="de",
        dimensions={
            CulturalDimension.INDIVIDUALISM: 0.67,
            CulturalDimension.POWER_DISTANCE: 0.35,
            CulturalDimension.MASCULINITY: 0.66,
            CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.65,
            CulturalDimension.LONG_TERM_ORIENTATION: 0.83,
            CulturalDimension.INDULGENCE: 0.40
        },
        communication_style=CulturalTone.DIRECT,
        taboo_topics=["nazi_symbols", "holocaust_denial", "nazi_glorification"],
        sensitive_topics=["wwii", "immigration", "east_west_divide"],
        preferred_themes=["precision", "order", "duty", "environmental", "philosophical"],
        storytelling_traditions=["bildungsroman", "fairy_tale", "philosophical_fiction"],
        name_conventions={"formal_you": True, "academic_titles": True},
        family_structure="nuclear_egalitarian",
        religious_context="secular_christian"
    ),
    "BR": CulturalProfile(
        profile_id="br_001",
        region=CultureRegion.LATIN_AMERICA,
        country_code="BR",
        country_name="Brazil",
        language="pt",
        dimensions={
            CulturalDimension.INDIVIDUALISM: 0.38,
            CulturalDimension.POWER_DISTANCE: 0.69,
            CulturalDimension.MASCULINITY: 0.49,
            CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.76,
            CulturalDimension.LONG_TERM_ORIENTATION: 0.44,
            CulturalDimension.INDULGENCE: 0.59
        },
        communication_style=CulturalTone.INFORMAL,
        taboo_topics=["slavery_jokes", "favela_stereotypes"],
        sensitive_topics=["race", "class", "corruption", "amazon_deforestation"],
        preferred_themes=["family", "passion", "joy", "resilience", "carnival", "futebol"],
        storytelling_traditions=["magical_realism", "telenovela", "carnival_spirit"],
        name_conventions={"multiple_names": True, "nicknames": True, "maternal_name": True},
        family_structure="extended_close",
        religious_context="catholic_syncretic"
    ),
    "IN": CulturalProfile(
        profile_id="in_001",
        region=CultureRegion.SOUTH_ASIA,
        country_code="IN",
        country_name="India",
        language="hi",
        dimensions={
            CulturalDimension.INDIVIDUALISM: 0.48,
            CulturalDimension.POWER_DISTANCE: 0.77,
            CulturalDimension.MASCULINITY: 0.56,
            CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.40,
            CulturalDimension.LONG_TERM_ORIENTATION: 0.51,
            CulturalDimension.INDULGENCE: 0.26
        },
        communication_style=CulturalTone.INDIRECT,
        taboo_topics=["caste_jokes", "partition_mockery", "cow_slaughter"],
        sensitive_topics=["caste", "religion", "pakistan", "kashmir", "arranged_marriage"],
        preferred_themes=["family", "duty", "karma", "festivals", "spirituality", "diversity"],
        storytelling_traditions=["epics", "mythology", "bollywood", "oral_tradition"],
        name_conventions={"caste_names": "sensitive", "regional_naming": True},
        family_structure="joint_family",
        religious_context="hindu_pluralistic"
    ),
    "SA": CulturalProfile(
        profile_id="sa_001",
        region=CultureRegion.MIDDLE_EAST,
        country_code="SA",
        country_name="Saudi Arabia",
        language="ar",
        dimensions={
            CulturalDimension.INDIVIDUALISM: 0.25,
            CulturalDimension.POWER_DISTANCE: 0.95,
            CulturalDimension.MASCULINITY: 0.60,
            CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.80,
            CulturalDimension.LONG_TERM_ORIENTATION: 0.36,
            CulturalDimension.INDULGENCE: 0.52
        },
        communication_style=CulturalTone.HIERARCHICAL,
        taboo_topics=["prophet_mockery", "alcohol_promotion", "homosexuality"],
        sensitive_topics=["religion", "royal_family", "gender_segregation", "israel"],
        preferred_themes=["honor", "hospitality", "family", "faith", "desert", "tradition"],
        storytelling_traditions=["arabian_nights", "oral_poetry", "quranic_reference"],
        name_conventions={"ibn_format": True, "tribal_names": True},
        family_structure="patriarchal_extended",
        religious_context="islamic_sunni"
    ),
    "CN": CulturalProfile(
        profile_id="cn_001",
        region=CultureRegion.EAST_ASIA,
        country_code="CN",
        country_name="China",
        language="zh",
        dimensions={
            CulturalDimension.INDIVIDUALISM: 0.20,
            CulturalDimension.POWER_DISTANCE: 0.80,
            CulturalDimension.MASCULINITY: 0.66,
            CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.30,
            CulturalDimension.LONG_TERM_ORIENTATION: 0.87,
            CulturalDimension.INDULGENCE: 0.24
        },
        communication_style=CulturalTone.INDIRECT,
        taboo_topics=["taiwan_independence", "tiananmen", "tibet_freedom", "xinjiang"],
        sensitive_topics=["government", "history", "japan", "hong_kong"],
        preferred_themes=["harmony", "family", "success", "education", "history", "prosperity"],
        storytelling_traditions=["wuxia", "classical_novels", "modern_realism"],
        name_conventions={"family_first": True, "generation_names": True},
        family_structure="filial_piety",
        religious_context="secular_mixed"
    )
}


# =============================================================================
# SENSITIVITY PATTERNS
# =============================================================================

SENSITIVITY_PATTERNS = {
    SensitivityCategory.RELIGION: {
        "keywords": ["bóg", "god", "allah", "religia", "religion", "kościół", "church", "modlitwa", "prayer"],
        "level": SensitivityLevel.MODERATE,
        "advice": "Unikaj wyśmiewania lub deprecjonowania religii"
    },
    SensitivityCategory.POLITICS: {
        "keywords": ["polityka", "politics", "rząd", "government", "prezydent", "president", "partia", "party"],
        "level": SensitivityLevel.MODERATE,
        "advice": "Unikaj jednostronnej propagandy politycznej"
    },
    SensitivityCategory.GENDER: {
        "keywords": ["kobieta", "woman", "mężczyzna", "man", "płeć", "gender"],
        "level": SensitivityLevel.MILD,
        "advice": "Unikaj stereotypów płciowych"
    },
    SensitivityCategory.SEXUALITY: {
        "keywords": ["lgbt", "gay", "lesbian", "trans", "homoseksualny", "homosexual"],
        "level": SensitivityLevel.HIGH,
        "advice": "Różne kultury mają różne podejścia - dostosuj do rynku"
    },
    SensitivityCategory.RACE_ETHNICITY: {
        "keywords": ["rasa", "race", "etniczność", "ethnicity", "kolor skóry", "skin color"],
        "level": SensitivityLevel.HIGH,
        "advice": "Unikaj stereotypów rasowych i etnicznych"
    },
    SensitivityCategory.VIOLENCE: {
        "keywords": ["przemoc", "violence", "morderstwo", "murder", "krew", "blood", "tortury", "torture"],
        "level": SensitivityLevel.MODERATE,
        "advice": "Dostosuj poziom przemocy do rynku docelowego"
    },
    SensitivityCategory.DEATH: {
        "keywords": ["śmierć", "death", "samobójstwo", "suicide", "pogrzeb", "funeral"],
        "level": SensitivityLevel.MODERATE,
        "advice": "Różne kultury różnie podchodzą do tematu śmierci"
    }
}


# =============================================================================
# MAIN CLASS
# =============================================================================

class TitanCulturalIntelligence:
    """
    TITAN Cultural Intelligence System

    Provides cultural awareness, sensitivity checking, and localization
    support for narrative content across different cultures.
    """

    def __init__(self):
        self.cultural_profiles: Dict[str, CulturalProfile] = CULTURAL_PROFILES.copy()
        self.reports: Dict[str, CulturalAnalysisReport] = {}
        self.adaptations: Dict[str, CulturalAdaptation] = {}

    async def analyze_cultural_content(
        self,
        project_id: str,
        chapters: List[Dict[str, Any]],
        source_culture: str = "PL",
        target_cultures: Optional[List[str]] = None
    ) -> CulturalAnalysisReport:
        """
        Perform full cultural analysis of content.
        """
        source_profile = self.cultural_profiles.get(source_culture)
        if not source_profile:
            source_profile = self.cultural_profiles["PL"]

        if target_cultures:
            target_profiles = [
                self.cultural_profiles[c]
                for c in target_cultures
                if c in self.cultural_profiles
            ]
        else:
            target_profiles = list(self.cultural_profiles.values())

        # Detect sensitivity issues
        sensitivity_issues = []
        for chapter in chapters:
            chapter_num = chapter.get("number", 1)
            text = chapter.get("text", "")
            issues = await self._detect_sensitivity_issues(text, chapter_num, target_profiles)
            sensitivity_issues.extend(issues)

        # Extract cultural elements
        cultural_elements = []
        for chapter in chapters:
            chapter_num = chapter.get("number", 1)
            text = chapter.get("text", "")
            elements = self._extract_cultural_elements(text, chapter_num, source_profile)
            cultural_elements.extend(elements)

        # Generate localization suggestions
        localization_suggestions = []
        for element in cultural_elements:
            if element.requires_localization:
                for target in target_profiles:
                    suggestion = self._generate_localization_suggestion(element, target)
                    if suggestion:
                        localization_suggestions.append(suggestion)

        # Calculate scores
        sensitivity_score = self._calculate_sensitivity_score(sensitivity_issues)
        authenticity_score = self._calculate_authenticity_score(cultural_elements, source_profile)
        localization_readiness = self._calculate_localization_readiness(
            cultural_elements, localization_suggestions
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            sensitivity_issues, cultural_elements, target_profiles
        )

        report = CulturalAnalysisReport(
            report_id=str(uuid.uuid4()),
            project_id=project_id,
            source_culture=source_profile,
            target_cultures=target_profiles,
            sensitivity_issues=sensitivity_issues,
            cultural_elements=cultural_elements,
            localization_suggestions=localization_suggestions,
            overall_sensitivity_score=sensitivity_score,
            cultural_authenticity_score=authenticity_score,
            localization_readiness=localization_readiness,
            recommendations=recommendations,
            created_at=datetime.now()
        )

        self.reports[report.report_id] = report
        return report

    async def check_text_sensitivity(
        self,
        text: str,
        target_cultures: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Quick sensitivity check on a piece of text.
        """
        if target_cultures:
            profiles = [self.cultural_profiles[c] for c in target_cultures if c in self.cultural_profiles]
        else:
            profiles = list(self.cultural_profiles.values())

        issues = await self._detect_sensitivity_issues(text, 0, profiles)

        return {
            "text_length": len(text),
            "issues_found": len(issues),
            "issues": [i.to_dict() for i in issues],
            "overall_level": self._get_highest_sensitivity_level(issues),
            "safe_for_cultures": [
                p.country_code for p in profiles
                if not any(p.country_code in i.affected_cultures for i in issues)
            ]
        }

    async def localize_content(
        self,
        text: str,
        source_culture: str,
        target_culture: str,
        localization_level: LocalizationLevel = LocalizationLevel.MODERATE
    ) -> Dict[str, Any]:
        """
        Localize content for a target culture.
        """
        source_profile = self.cultural_profiles.get(source_culture)
        target_profile = self.cultural_profiles.get(target_culture)

        if not source_profile or not target_profile:
            return {"error": "Unknown culture code"}

        # Extract elements to localize
        elements = self._extract_cultural_elements(text, 0, source_profile)

        # Generate adaptations
        adaptations = []
        localized_text = text

        for element in elements:
            if element.requires_localization or localization_level in [LocalizationLevel.DEEP, LocalizationLevel.TRANSCREATION]:
                adaptation = self._create_adaptation(element, target_profile, localization_level)
                if adaptation:
                    adaptations.append(adaptation)
                    # Apply adaptation
                    localized_text = localized_text.replace(
                        element.original_value,
                        adaptation.adapted_value
                    )

        return {
            "original_text": text,
            "localized_text": localized_text,
            "source_culture": source_culture,
            "target_culture": target_culture,
            "localization_level": localization_level.value,
            "adaptations_made": len(adaptations),
            "adaptations": [a.to_dict() for a in adaptations]
        }

    async def get_cultural_recommendations(
        self,
        genre: str,
        target_culture: str
    ) -> Dict[str, Any]:
        """
        Get cultural recommendations for writing in a genre for a target culture.
        """
        profile = self.cultural_profiles.get(target_culture)
        if not profile:
            return {"error": "Unknown culture"}

        recommendations = {
            "culture": profile.country_name,
            "communication_style": profile.communication_style.value,
            "preferred_themes": profile.preferred_themes,
            "storytelling_traditions": profile.storytelling_traditions,
            "avoid_topics": profile.taboo_topics,
            "handle_carefully": profile.sensitive_topics,
            "name_conventions": profile.name_conventions,
            "family_depiction": profile.family_structure,
            "religious_context": profile.religious_context
        }

        # Add genre-specific recommendations
        genre_recommendations = self._get_genre_cultural_tips(genre, profile)
        recommendations["genre_tips"] = genre_recommendations

        # Add dimension-based recommendations
        dimension_tips = self._get_dimension_tips(profile)
        recommendations["dimension_tips"] = dimension_tips

        return recommendations

    async def validate_character_names(
        self,
        names: List[str],
        culture: str
    ) -> Dict[str, Any]:
        """
        Validate character names for cultural appropriateness.
        """
        profile = self.cultural_profiles.get(culture)
        if not profile:
            return {"error": "Unknown culture"}

        validations = []
        for name in names:
            validation = self._validate_name(name, profile)
            validations.append(validation)

        return {
            "culture": profile.country_name,
            "names_checked": len(names),
            "validations": validations,
            "name_conventions": profile.name_conventions
        }

    async def generate_culturally_appropriate_names(
        self,
        culture: str,
        count: int = 10,
        gender: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate culturally appropriate character names.
        """
        profile = self.cultural_profiles.get(culture)
        if not profile:
            return {"error": "Unknown culture"}

        names = self._generate_names(profile, count, gender)

        return {
            "culture": profile.country_name,
            "names": names,
            "naming_conventions": profile.name_conventions
        }

    def add_cultural_profile(
        self,
        country_code: str,
        profile_data: Dict[str, Any]
    ) -> CulturalProfile:
        """
        Add a new cultural profile.
        """
        profile = CulturalProfile(
            profile_id=str(uuid.uuid4()),
            region=CultureRegion(profile_data.get("region", "global")),
            country_code=country_code,
            country_name=profile_data.get("country_name", country_code),
            language=profile_data.get("language", "en"),
            dimensions={
                CulturalDimension(k): v
                for k, v in profile_data.get("dimensions", {}).items()
            },
            communication_style=CulturalTone(profile_data.get("communication_style", "direct")),
            taboo_topics=profile_data.get("taboo_topics", []),
            sensitive_topics=profile_data.get("sensitive_topics", []),
            preferred_themes=profile_data.get("preferred_themes", []),
            storytelling_traditions=profile_data.get("storytelling_traditions", []),
            name_conventions=profile_data.get("name_conventions", {}),
            family_structure=profile_data.get("family_structure", "nuclear"),
            religious_context=profile_data.get("religious_context", "secular")
        )

        self.cultural_profiles[country_code] = profile
        return profile

    # =========================================================================
    # DETECTION METHODS
    # =========================================================================

    async def _detect_sensitivity_issues(
        self,
        text: str,
        chapter_num: int,
        target_profiles: List[CulturalProfile]
    ) -> List[SensitivityIssue]:
        """Detect cultural sensitivity issues in text."""
        issues = []
        paragraphs = text.split("\n\n")

        for para_idx, paragraph in enumerate(paragraphs):
            lower = paragraph.lower()

            # Check against sensitivity patterns
            for category, pattern in SENSITIVITY_PATTERNS.items():
                for keyword in pattern["keywords"]:
                    if keyword in lower:
                        # Check which cultures this affects
                        affected = []
                        for profile in target_profiles:
                            if keyword in profile.taboo_topics or keyword in profile.sensitive_topics:
                                affected.append(profile.country_code)
                            # Also check if any taboo topic keyword is in the text
                            for taboo in profile.taboo_topics:
                                if taboo in lower:
                                    if profile.country_code not in affected:
                                        affected.append(profile.country_code)

                        if affected or pattern["level"] in [SensitivityLevel.HIGH, SensitivityLevel.CRITICAL]:
                            issue = SensitivityIssue(
                                issue_id=str(uuid.uuid4()),
                                category=category,
                                level=pattern["level"],
                                description=f"Wykryto wrażliwy temat: {category.value}",
                                affected_text=paragraph[:200],
                                chapter=chapter_num,
                                paragraph=para_idx + 1,
                                affected_cultures=affected if affected else ["multiple"],
                                suggested_alternative=pattern["advice"],
                                explanation=f"Słowo kluczowe '{keyword}' może być wrażliwe"
                            )
                            issues.append(issue)
                            break  # One issue per category per paragraph

            # Check for culture-specific taboos
            for profile in target_profiles:
                for taboo in profile.taboo_topics:
                    if taboo.replace("_", " ") in lower:
                        issue = SensitivityIssue(
                            issue_id=str(uuid.uuid4()),
                            category=SensitivityCategory.CUSTOMS,
                            level=SensitivityLevel.CRITICAL,
                            description=f"Wykryto temat tabu dla kultury {profile.country_name}",
                            affected_text=paragraph[:200],
                            chapter=chapter_num,
                            paragraph=para_idx + 1,
                            affected_cultures=[profile.country_code],
                            suggested_alternative=f"Usuń lub zmodyfikuj treść dla rynku {profile.country_name}",
                            explanation=f"Temat '{taboo}' jest tabu w kulturze {profile.country_name}"
                        )
                        issues.append(issue)

        return issues

    def _extract_cultural_elements(
        self,
        text: str,
        chapter_num: int,
        source_profile: CulturalProfile
    ) -> List[CulturalElement]:
        """Extract cultural elements from text."""
        elements = []

        # Extract names (simplified - would use NER in production)
        # Look for capitalized words that might be names
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2 and word.isalpha():
                # Might be a name
                element = CulturalElement(
                    element_id=str(uuid.uuid4()),
                    element_type="name",
                    original_value=word,
                    cultural_context=source_profile.country_code,
                    universality_score=0.3,
                    requires_localization=True,
                    chapter=chapter_num
                )
                elements.append(element)

        # Extract food references
        food_keywords = ["jedzenie", "posiłek", "obiad", "śniadanie", "kolacja", "danie", "zupa", "mięso"]
        for keyword in food_keywords:
            if keyword in text.lower():
                # Find the context around the keyword
                idx = text.lower().find(keyword)
                context = text[max(0, idx-20):min(len(text), idx+50)]

                element = CulturalElement(
                    element_id=str(uuid.uuid4()),
                    element_type="food",
                    original_value=context,
                    cultural_context=source_profile.country_code,
                    universality_score=0.4,
                    requires_localization=False,  # Food is often left as-is for authenticity
                    chapter=chapter_num
                )
                elements.append(element)
                break  # One food element per chapter is enough

        # Extract holiday/tradition references
        tradition_keywords = ["święto", "tradycja", "obyczaj", "uroczystość", "wigilia", "wielkanoc"]
        for keyword in tradition_keywords:
            if keyword in text.lower():
                element = CulturalElement(
                    element_id=str(uuid.uuid4()),
                    element_type="tradition",
                    original_value=keyword,
                    cultural_context=source_profile.country_code,
                    universality_score=0.2,
                    requires_localization=True,
                    chapter=chapter_num
                )
                elements.append(element)

        return elements

    def _generate_localization_suggestion(
        self,
        element: CulturalElement,
        target_profile: CulturalProfile
    ) -> Optional[LocalizationSuggestion]:
        """Generate a localization suggestion for an element."""
        if element.cultural_context == target_profile.country_code:
            return None  # No localization needed for same culture

        if element.element_type == "name":
            # Suggest a culturally appropriate name
            localized = self._localize_name(element.original_value, target_profile)

            return LocalizationSuggestion(
                suggestion_id=str(uuid.uuid4()),
                original_text=element.original_value,
                localized_text=localized,
                target_culture=target_profile.country_code,
                localization_type="name_adaptation",
                confidence=0.7,
                notes=f"Imię dostosowane do konwencji {target_profile.country_name}"
            )

        if element.element_type == "tradition":
            # Suggest cultural equivalent or explanation
            return LocalizationSuggestion(
                suggestion_id=str(uuid.uuid4()),
                original_text=element.original_value,
                localized_text=f"{element.original_value} (tradycja {element.cultural_context})",
                target_culture=target_profile.country_code,
                localization_type="cultural_note",
                confidence=0.8,
                notes="Dodano notę wyjaśniającą dla czytelników z innej kultury"
            )

        return None

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _calculate_sensitivity_score(self, issues: List[SensitivityIssue]) -> float:
        """Calculate overall sensitivity score."""
        if not issues:
            return 1.0

        # Weight by severity
        weighted_issues = sum(
            1.0 if i.level == SensitivityLevel.CRITICAL else
            0.7 if i.level == SensitivityLevel.HIGH else
            0.4 if i.level == SensitivityLevel.MODERATE else
            0.2 if i.level == SensitivityLevel.MILD else 0.1
            for i in issues
        )

        # Score decreases with issues
        return max(0.0, 1.0 - (weighted_issues * 0.1))

    def _calculate_authenticity_score(
        self,
        elements: List[CulturalElement],
        source_profile: CulturalProfile
    ) -> float:
        """Calculate cultural authenticity score."""
        if not elements:
            return 0.5

        # Average universality score (lower = more culture-specific = more authentic)
        avg_universality = sum(e.universality_score for e in elements) / len(elements)

        # More culture-specific elements = higher authenticity
        return 1.0 - (avg_universality * 0.5)

    def _calculate_localization_readiness(
        self,
        elements: List[CulturalElement],
        suggestions: List[LocalizationSuggestion]
    ) -> float:
        """Calculate how ready the content is for localization."""
        if not elements:
            return 1.0

        elements_needing_localization = [e for e in elements if e.requires_localization]

        if not elements_needing_localization:
            return 1.0

        # Check how many have suggestions
        coverage = len(suggestions) / max(len(elements_needing_localization), 1)

        return min(coverage, 1.0)

    def _generate_recommendations(
        self,
        issues: List[SensitivityIssue],
        elements: List[CulturalElement],
        target_profiles: List[CulturalProfile]
    ) -> List[str]:
        """Generate cultural recommendations."""
        recommendations = []

        # Critical issues
        critical_issues = [i for i in issues if i.level == SensitivityLevel.CRITICAL]
        if critical_issues:
            recommendations.append(
                f"KRYTYCZNE: Znaleziono {len(critical_issues)} treści, które mogą być obraźliwe - wymagana natychmiastowa rewizja"
            )

        # High sensitivity issues
        high_issues = [i for i in issues if i.level == SensitivityLevel.HIGH]
        if high_issues:
            recommendations.append(
                f"WYSOKIE: {len(high_issues)} elementów wymaga ostrożnego podejścia dla niektórych kultur"
            )

        # Localization needs
        loc_elements = [e for e in elements if e.requires_localization]
        if loc_elements:
            recommendations.append(
                f"LOKALIZACJA: {len(loc_elements)} elementów kulturowych wymaga adaptacji dla rynków zagranicznych"
            )

        # Culture-specific recommendations
        for profile in target_profiles[:3]:  # Top 3 cultures
            if profile.taboo_topics:
                recommendations.append(
                    f"{profile.country_name}: Unikaj tematów - {', '.join(profile.taboo_topics[:3])}"
                )

        return recommendations

    def _get_highest_sensitivity_level(self, issues: List[SensitivityIssue]) -> str:
        """Get the highest sensitivity level from issues."""
        if not issues:
            return SensitivityLevel.SAFE.value

        levels = [i.level for i in issues]

        if SensitivityLevel.CRITICAL in levels:
            return SensitivityLevel.CRITICAL.value
        if SensitivityLevel.HIGH in levels:
            return SensitivityLevel.HIGH.value
        if SensitivityLevel.MODERATE in levels:
            return SensitivityLevel.MODERATE.value
        if SensitivityLevel.MILD in levels:
            return SensitivityLevel.MILD.value

        return SensitivityLevel.SAFE.value

    def _get_genre_cultural_tips(
        self,
        genre: str,
        profile: CulturalProfile
    ) -> List[str]:
        """Get genre-specific cultural tips."""
        tips = []

        genre_lower = genre.lower()

        if genre_lower == "romance":
            if profile.dimensions.get(CulturalDimension.INDULGENCE, 0.5) < 0.4:
                tips.append("Kultura bardziej powściągliwa - unikaj zbyt eksplicytnych scen")
            if "arranged_marriage" in profile.sensitive_topics:
                tips.append("Temat małżeństw aranżowanych wymaga ostrożności")

        if genre_lower == "thriller":
            if profile.dimensions.get(CulturalDimension.UNCERTAINTY_AVOIDANCE, 0.5) > 0.7:
                tips.append("Wysoka unikanie niepewności - zapewnij wyraźne rozwiązanie")

        if genre_lower == "fantasy":
            tips.append(f"Rozważ włączenie elementów {profile.storytelling_traditions[0] if profile.storytelling_traditions else 'lokalnej tradycji'}")

        if genre_lower == "horror":
            if "religion" in profile.sensitive_topics:
                tips.append("Ostrożnie z elementami religijnymi w horrorze")

        return tips

    def _get_dimension_tips(self, profile: CulturalProfile) -> Dict[str, str]:
        """Get tips based on cultural dimensions."""
        tips = {}

        if profile.dimensions.get(CulturalDimension.INDIVIDUALISM, 0.5) > 0.7:
            tips["individualism"] = "Kultura indywidualistyczna - podkreślaj osobiste osiągnięcia bohatera"
        else:
            tips["collectivism"] = "Kultura kolektywistyczna - ważna rola rodziny i społeczności"

        if profile.dimensions.get(CulturalDimension.POWER_DISTANCE, 0.5) > 0.7:
            tips["hierarchy"] = "Wysoki dystans władzy - szanuj hierarchie w relacjach"
        else:
            tips["equality"] = "Niski dystans władzy - relacje mogą być bardziej egalitarne"

        if profile.dimensions.get(CulturalDimension.UNCERTAINTY_AVOIDANCE, 0.5) > 0.7:
            tips["certainty"] = "Wysokie unikanie niepewności - czytelnicy preferują jasne rozwiązania"

        return tips

    def _validate_name(self, name: str, profile: CulturalProfile) -> Dict[str, Any]:
        """Validate a name for cultural appropriateness."""
        validation = {
            "name": name,
            "valid": True,
            "notes": []
        }

        # Check length
        if len(name) < 2:
            validation["valid"] = False
            validation["notes"].append("Imię zbyt krótkie")

        # Check for taboo names (simplified)
        if name.lower() in ["hitler", "stalin", "satan"]:
            validation["valid"] = False
            validation["notes"].append("Imię może być kontrowersyjne")

        # Check naming conventions
        if profile.name_conventions.get("surname_gender"):
            validation["notes"].append("W tej kulturze nazwiska mogą mieć formy rodzajowe")

        return validation

    def _generate_names(
        self,
        profile: CulturalProfile,
        count: int,
        gender: Optional[str]
    ) -> List[Dict[str, str]]:
        """Generate culturally appropriate names."""
        # Simplified name generation (would use cultural name databases in production)
        name_banks = {
            "PL": {
                "male": ["Jan", "Piotr", "Andrzej", "Krzysztof", "Tomasz", "Michał", "Marek", "Adam"],
                "female": ["Anna", "Maria", "Katarzyna", "Małgorzata", "Agnieszka", "Barbara", "Ewa", "Zofia"],
                "surnames": ["Kowalski", "Nowak", "Wiśniewski", "Wójcik", "Kamiński", "Lewandowski"]
            },
            "US": {
                "male": ["John", "Michael", "David", "James", "Robert", "William", "Daniel", "Matthew"],
                "female": ["Mary", "Jennifer", "Linda", "Elizabeth", "Sarah", "Jessica", "Emily", "Ashley"],
                "surnames": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
            },
            "JP": {
                "male": ["Hiroshi", "Takeshi", "Kenji", "Yuki", "Haruto", "Sota", "Yuto", "Riku"],
                "female": ["Yuki", "Sakura", "Hana", "Mei", "Aoi", "Rin", "Mio", "Saki"],
                "surnames": ["Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto"]
            }
        }

        names = []
        bank = name_banks.get(profile.country_code, name_banks["US"])

        import random
        for _ in range(count):
            if gender == "male":
                first = random.choice(bank["male"])
            elif gender == "female":
                first = random.choice(bank["female"])
            else:
                first = random.choice(bank["male"] + bank["female"])

            surname = random.choice(bank["surnames"])

            # Apply naming conventions
            if profile.name_conventions.get("family_first"):
                full_name = f"{surname} {first}"
            else:
                full_name = f"{first} {surname}"

            names.append({
                "first_name": first,
                "surname": surname,
                "full_name": full_name,
                "culture": profile.country_code
            })

        return names

    def _localize_name(self, name: str, target_profile: CulturalProfile) -> str:
        """Localize a name for target culture."""
        # Simple phonetic approximation (would use proper transliteration in production)
        # For now, just return the name with a note
        return name

    def _create_adaptation(
        self,
        element: CulturalElement,
        target_profile: CulturalProfile,
        level: LocalizationLevel
    ) -> Optional[CulturalAdaptation]:
        """Create a cultural adaptation."""
        if level == LocalizationLevel.NONE:
            return None

        adapted_value = element.original_value

        if element.element_type == "name" and level in [LocalizationLevel.DEEP, LocalizationLevel.TRANSCREATION]:
            adapted_value = self._localize_name(element.original_value, target_profile)

        return CulturalAdaptation(
            adaptation_id=str(uuid.uuid4()),
            original_element=element,
            target_culture=target_profile,
            adapted_value=adapted_value,
            adaptation_notes=f"Adaptacja dla {target_profile.country_name}",
            approved=False
        )

    # =========================================================================
    # PUBLIC GETTERS
    # =========================================================================

    def get_report(self, report_id: str) -> Optional[CulturalAnalysisReport]:
        """Get a cultural analysis report by ID."""
        return self.reports.get(report_id)

    def get_cultural_profile(self, country_code: str) -> Optional[CulturalProfile]:
        """Get a cultural profile by country code."""
        return self.cultural_profiles.get(country_code)

    def list_available_cultures(self) -> List[Dict[str, str]]:
        """List all available cultural profiles."""
        return [
            {
                "code": profile.country_code,
                "name": profile.country_name,
                "region": profile.region.value,
                "language": profile.language
            }
            for profile in self.cultural_profiles.values()
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
                "sensitivity_score": r.overall_sensitivity_score,
                "created_at": r.created_at.isoformat()
            }
            for r in reports
        ]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_cultural_intelligence: Optional[TitanCulturalIntelligence] = None


def get_cultural_intelligence() -> TitanCulturalIntelligence:
    """Get the singleton cultural intelligence instance."""
    global _cultural_intelligence
    if _cultural_intelligence is None:
        _cultural_intelligence = TitanCulturalIntelligence()
    return _cultural_intelligence

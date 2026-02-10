"""
Bestseller Quality Engine for NarraForge 2.0

System ensuring bestseller-level quality.
Analyzes text against criteria common to world's best books.
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.services.ai_service import AIService
from app.models.project import GenreType


class QualityLevel(str, Enum):
    """Quality level classifications"""
    MASTERPIECE = "masterpiece"  # 90+
    BESTSELLER = "bestseller"  # 80-89
    PROFESSIONAL = "professional"  # 70-79
    COMPETENT = "competent"  # 60-69
    NEEDS_WORK = "needs_work"  # <60


@dataclass
class CriterionScore:
    """Score for a single quality criterion"""
    name: str
    score: float  # 0-100
    weight: float
    weighted_score: float
    feedback: str
    improvements: List[str]


@dataclass
class BestsellerQualityReport:
    """Complete quality analysis report"""
    total_score: float
    quality_level: QualityLevel
    criteria_scores: Dict[str, CriterionScore]
    strengths: List[str]
    weaknesses: List[str]
    improvement_priority: List[str]
    bestseller_potential: float

    def to_dict(self) -> Dict:
        return {
            "total_score": round(self.total_score, 1),
            "quality_level": self.quality_level.value,
            "criteria_scores": {
                k: {
                    "score": round(v.score, 1),
                    "weight": v.weight,
                    "weighted_score": round(v.weighted_score, 2),
                    "feedback": v.feedback,
                    "improvements": v.improvements
                }
                for k, v in self.criteria_scores.items()
            },
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "improvement_priority": self.improvement_priority,
            "bestseller_potential": round(self.bestseller_potential, 1)
        }


@dataclass
class ImprovementIteration:
    """Record of an improvement iteration"""
    iteration: int
    focus: str
    score_before: float
    score_after: float
    improvement: float


@dataclass
class ImprovedContent:
    """Result of content improvement"""
    original: str
    improved: str
    original_score: float
    final_score: float
    iterations: List[ImprovementIteration]
    quality_level: QualityLevel


class BestsellerQualityEngine:
    """
    System ensuring bestseller-level quality.
    Analyzes text against criteria common to world's best books.
    """

    BESTSELLER_CRITERIA = {
        # 1. HOOK - First sentence/paragraph
        "opening_hook": {
            "weight": 0.15,
            "description": "Czy otwarcie przyciąga uwagę?",
            "criteria": [
                "Intrygujące pierwsze zdanie",
                "Natychmiastowe wprowadzenie napięcia",
                "Unikalne, zapadające w pamięć otwarcie",
                "Brak kliszowych otwarć (ciemna burzowa noc...)"
            ],
            "prompt": """Oceń OTWARCIE tekstu (pierwsze akapity):
- Czy pierwsze zdanie jest intrygujące?
- Czy od razu wprowadza napięcie/pytanie?
- Czy jest unikalne, nie kliszowe?
- Czy czytelnik chce czytać dalej?

Ocena 0-100, gdzie 90+ = poziom bestsellera."""
        },

        # 2. PAGE-TURNER FACTOR
        "page_turner": {
            "weight": 0.20,
            "description": "Czy nie da się odłożyć książki?",
            "criteria": [
                "Każdy rozdział kończy się hakiem",
                "Stałe podnoszenie stawek",
                "Nierozwiązane pytania utrzymują napięcie",
                "Tempo nie pozwala odłożyć książki"
            ],
            "prompt": """Oceń współczynnik PAGE-TURNER:
- Czy są cliffhangery?
- Czy stawki rosną?
- Czy są nierozwiązane pytania trzymające w napięciu?
- Czy tempo jest odpowiednie?

Ocena 0-100, gdzie 90+ = nie da się odłożyć."""
        },

        # 3. CHARACTER DEPTH
        "character_depth": {
            "weight": 0.20,
            "description": "Jak głębokie są postacie?",
            "criteria": [
                "Postacie mają głębokie wewnętrzne konflikty",
                "Każda główna postać ma unikalne WANT/NEED",
                "Postacie zmieniają się przez historię",
                "Czytelnik czuje empatię z postaciami",
                "Antagonista ma zrozumiałe motywacje"
            ],
            "prompt": """Oceń GŁĘBIĘ POSTACI:
- Czy mają wewnętrzne konflikty?
- Czy mają unikalne cele/potrzeby?
- Czy się rozwijają?
- Czy czujesz empatię?
- Czy antagonista jest wielowymiarowy?

Ocena 0-100, gdzie 90+ = postacie na poziomie bestsellerów."""
        },

        # 4. EMOTIONAL RESONANCE
        "emotional_resonance": {
            "weight": 0.15,
            "description": "Jak silne emocje wywołuje?",
            "criteria": [
                "Historia wywołuje silne emocje",
                "Momenty katarsis są dobrze przygotowane",
                "Emocjonalne szczyty i doliny są zbalansowane",
                "Czytelnik czuje się poruszony"
            ],
            "prompt": """Oceń REZONANS EMOCJONALNY:
- Czy tekst wywołuje emocje?
- Czy są momenty wzruszające/ekscytujące?
- Czy emocjonalny łuk jest zbalansowany?
- Czy czytelnik będzie poruszony?

Ocena 0-100, gdzie 90+ = głęboko poruszający."""
        },

        # 5. PROSE QUALITY
        "prose_quality": {
            "weight": 0.15,
            "description": "Jaka jest jakość prozy?",
            "criteria": [
                "Show don't tell",
                "Unikalne metafory i porównania",
                "Brak filter words (czuł że, widział że)",
                "Naturalny dialog z subtelnym subtekstem",
                "Sensory details (5 zmysłów)"
            ],
            "prompt": """Oceń JAKOŚĆ PROZY:
- Czy jest "show don't tell"?
- Czy metafory są świeże?
- Czy brak filter words (czuł że, widział że)?
- Czy dialog jest naturalny?
- Czy są opisy zmysłowe?

Ocena 0-100, gdzie 90+ = proza mistrzowska."""
        },

        # 6. THEMATIC DEPTH
        "thematic_depth": {
            "weight": 0.10,
            "description": "Jaka jest głębia tematyczna?",
            "criteria": [
                "Historia ma głębsze znaczenie",
                "Tematy są subtelalnie wplecione",
                "Uniwersalne prawdy o ludzkiej naturze",
                "Wielowarstwowa interpretacja"
            ],
            "prompt": """Oceń GŁĘBIĘ TEMATYCZNĄ:
- Czy jest głębsze znaczenie?
- Czy tematy są subtelnie wplecione?
- Czy są uniwersalne prawdy?
- Czy możliwa wielowarstwowa interpretacja?

Ocena 0-100, gdzie 90+ = znacząca literatura."""
        },

        # 7. ORIGINALITY
        "originality": {
            "weight": 0.05,
            "description": "Jak oryginalna jest historia?",
            "criteria": [
                "Unikalna premisa lub twist",
                "Świeże podejście do gatunku",
                "Zaskakujące, ale logiczne rozwiązania",
                "Własny głos autora"
            ],
            "prompt": """Oceń ORYGINALNOŚĆ:
- Czy premisa jest unikalna?
- Czy podejście do gatunku świeże?
- Czy rozwiązania zaskakują ale są logiczne?
- Czy jest własny głos?

Ocena 0-100, gdzie 90+ = wysoce oryginalne."""
        }
    }

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()

    # Hard-coded cliché patterns that trigger automatic score penalties
    CLICHE_OPENING_PATTERNS = [
        r"^\s*otworzył[a]?\s+oczy",
        r"^\s*obudził[a]?\s+się",
        r"^\s*zerwał[a]?\s+się\s+(z\s+)?(podłogi|łóżka|ziemi|posadzki)",
        r"^\s*leżał[a]?\s+na\s+(zimn|tward|mokr)",
        r"^\s*ocknął[a]?\s+się",
        r"^\s*otworzyła?\s+oczy",
        r"^\s*świat\s+wokół\s+(niego|niej)\s+wir",
        r"^\s*ciemność\s+otoczyła",
        r"^\s*gęsta[,]?\s+nieprzenikniona\s+ciemność",
    ]

    REPETITIVE_PHRASE_PATTERNS = [
        r"mapa bólu",
        r"duszący sen",
        r"muszę iść dalej",
        r"nie było odwrotu",
        r"gęsta[,]?\s+nieprzenikniona\s+ciemność",
        r"mrok\s+gęstniał",
        r"ciemność\s+pochłonęła",
    ]

    async def analyze_quality(
        self,
        content: str,
        genre: GenreType,
        context: Optional[Dict] = None
    ) -> BestsellerQualityReport:
        """
        Comprehensive quality analysis against bestseller criteria.

        Args:
            content: Text content to analyze
            genre: Genre for context
            context: Optional additional context

        Returns:
            BestsellerQualityReport with detailed analysis
        """
        scores = {}

        # Pre-check: detect hard cliché violations
        cliche_penalty = self._detect_cliche_penalties(content)

        for criterion_name, criterion in self.BESTSELLER_CRITERIA.items():
            score = await self._evaluate_criterion(
                content=content,
                criterion=criterion,
                genre=genre
            )

            score_value = score["value"]
            feedback = score["feedback"]
            improvements = score["improvements"]

            # Apply hard penalty for cliché openings on opening_hook criterion
            if criterion_name == "opening_hook" and cliche_penalty["has_cliche_opening"]:
                score_value = min(score_value, 15)  # Cap at 15/100
                feedback = (
                    f"KARA AUTOMATYCZNA: Wykryto kliszowe otwarcie "
                    f"({cliche_penalty['matched_opening']}). {feedback}"
                )
                improvements = [
                    "KRYTYCZNE: Zmień otwarcie — użyj In Medias Res, dialogu, mikro-detalu lub zaskakującej myśli"
                ] + improvements

            # Apply penalty for repetitive phrases on originality criterion
            if criterion_name == "originality" and cliche_penalty["repetitive_count"] > 2:
                penalty = min(40, cliche_penalty["repetitive_count"] * 10)
                score_value = max(0, score_value - penalty)
                feedback = (
                    f"KARA: Wykryto {cliche_penalty['repetitive_count']} powtarzających się "
                    f"kliszowych fraz. {feedback}"
                )

            scores[criterion_name] = CriterionScore(
                name=criterion_name,
                score=score_value,
                weight=criterion["weight"],
                weighted_score=score_value * criterion["weight"],
                feedback=feedback,
                improvements=improvements
            )

        total_score = sum(s.weighted_score for s in scores.values())

        # Determine quality level
        quality_level = self._determine_quality_level(total_score)

        return BestsellerQualityReport(
            total_score=total_score,
            quality_level=quality_level,
            criteria_scores=scores,
            strengths=self._identify_strengths(scores),
            weaknesses=self._identify_weaknesses(scores),
            improvement_priority=self._prioritize_improvements(scores),
            bestseller_potential=self._calculate_bestseller_potential(total_score, genre)
        )

    async def _evaluate_criterion(
        self,
        content: str,
        criterion: Dict,
        genre: GenreType
    ) -> Dict[str, Any]:
        """Evaluate a single quality criterion."""
        # Truncate content for context limits
        content_sample = content[:4000] if len(content) > 4000 else content

        prompt = f"""
{criterion['prompt']}

GATUNEK: {genre.value}

TEKST DO OCENY:
---
{content_sample}
---

Odpowiedz w formacie JSON:
{{
    "score": <liczba 0-100>,
    "feedback": "<krótki feedback>",
    "improvements": ["<sugestia 1>", "<sugestia 2>"]
}}
"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=1,
                max_tokens=500,
                temperature=0.3
            )

            # Parse response
            import json
            import re

            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return {
                    "value": min(100, max(0, data.get("score", 70))),
                    "feedback": data.get("feedback", ""),
                    "improvements": data.get("improvements", [])
                }

        except Exception as e:
            pass

        # Default score
        return {
            "value": 70,
            "feedback": "Ocena automatyczna",
            "improvements": []
        }

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level based on score."""
        if score >= 90:
            return QualityLevel.MASTERPIECE
        elif score >= 80:
            return QualityLevel.BESTSELLER
        elif score >= 70:
            return QualityLevel.PROFESSIONAL
        elif score >= 60:
            return QualityLevel.COMPETENT
        else:
            return QualityLevel.NEEDS_WORK

    def _identify_strengths(self, scores: Dict[str, CriterionScore]) -> List[str]:
        """Identify top strengths."""
        sorted_scores = sorted(
            scores.items(),
            key=lambda x: x[1].score,
            reverse=True
        )
        return [
            f"{self.BESTSELLER_CRITERIA[name]['description']}: {score.score:.0f}/100"
            for name, score in sorted_scores[:3]
            if score.score >= 75
        ]

    def _identify_weaknesses(self, scores: Dict[str, CriterionScore]) -> List[str]:
        """Identify main weaknesses."""
        sorted_scores = sorted(
            scores.items(),
            key=lambda x: x[1].score
        )
        return [
            f"{self.BESTSELLER_CRITERIA[name]['description']}: {score.score:.0f}/100"
            for name, score in sorted_scores[:3]
            if score.score < 75
        ]

    def _prioritize_improvements(self, scores: Dict[str, CriterionScore]) -> List[str]:
        """Prioritize improvements by impact (weight * potential gain)."""
        improvements = []

        for name, score in scores.items():
            # Calculate potential impact
            potential_gain = 100 - score.score
            weight = score.weight
            impact = potential_gain * weight

            improvements.append((name, impact, score.improvements))

        # Sort by impact
        improvements.sort(key=lambda x: x[1], reverse=True)

        # Return top improvement areas
        return [name for name, _, _ in improvements[:3]]

    def _detect_cliche_penalties(self, content: str) -> Dict[str, Any]:
        """
        Hard detection of cliché patterns that automatically penalize scores.
        This catches problems that AI-based evaluation might miss.
        """
        result = {
            "has_cliche_opening": False,
            "matched_opening": "",
            "repetitive_count": 0,
            "repetitive_matches": [],
        }

        # Check first 500 chars for cliché openings
        opening = content[:500].lower().strip()
        # Remove chapter title lines (e.g. "Rozdział 1", "Rozdział 1: Tytuł")
        opening_lines = opening.split("\n")
        content_start = ""
        for line in opening_lines:
            stripped = line.strip()
            if stripped and not re.match(r"^rozdział\s+\d+", stripped, re.IGNORECASE):
                content_start = stripped
                break

        for pattern in self.CLICHE_OPENING_PATTERNS:
            if re.search(pattern, content_start, re.IGNORECASE):
                result["has_cliche_opening"] = True
                result["matched_opening"] = pattern
                break

        # Check full text for repetitive phrases
        for pattern in self.REPETITIVE_PHRASE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result["repetitive_count"] += len(matches)
                result["repetitive_matches"].append(
                    {"pattern": pattern, "count": len(matches)}
                )

        return result

    def _calculate_bestseller_potential(self, score: float, genre: GenreType) -> float:
        """Calculate bestseller potential score."""
        # Base potential is the score
        potential = score

        # Genre adjustments (some genres have lower bars commercially)
        genre_adjustments = {
            GenreType.THRILLER: 5,  # Thrillers sell well
            GenreType.ROMANCE: 5,  # Romance is popular
            GenreType.MYSTERY: 3,
            GenreType.FANTASY: 0,
            GenreType.SCI_FI: 0,
            GenreType.HORROR: -2,
            GenreType.DRAMA: -3,
            GenreType.COMEDY: 0,
            GenreType.RELIGIOUS: -5,  # Smaller market
        }

        adjustment = genre_adjustments.get(genre, 0)
        potential = min(100, potential + adjustment)

        return potential

    async def improve_to_bestseller(
        self,
        content: str,
        quality_report: BestsellerQualityReport,
        genre: GenreType,
        max_iterations: int = 3
    ) -> ImprovedContent:
        """
        Iteratively improve text to bestseller level.

        Args:
            content: Original content
            quality_report: Initial quality report
            genre: Genre for context
            max_iterations: Maximum improvement iterations

        Returns:
            ImprovedContent with enhanced text
        """
        current_content = content
        current_score = quality_report.total_score
        iterations = []

        for i in range(max_iterations):
            if current_score >= 85:  # Target: bestseller level
                break

            # Find weakest area
            weakest = quality_report.improvement_priority[0] if quality_report.improvement_priority else None
            if not weakest:
                break

            # Get improvements for this area
            criterion_score = quality_report.criteria_scores.get(weakest)
            if not criterion_score:
                break

            # Improve in this area
            improved = await self._improve_criterion(
                content=current_content,
                criterion_name=weakest,
                criterion_config=self.BESTSELLER_CRITERIA[weakest],
                feedback=criterion_score.feedback,
                suggestions=criterion_score.improvements,
                genre=genre
            )

            # Re-evaluate
            new_report = await self.analyze_quality(improved, genre)

            iterations.append(ImprovementIteration(
                iteration=i + 1,
                focus=weakest,
                score_before=current_score,
                score_after=new_report.total_score,
                improvement=new_report.total_score - current_score
            ))

            current_content = improved
            current_score = new_report.total_score
            quality_report = new_report

        return ImprovedContent(
            original=content,
            improved=current_content,
            original_score=quality_report.total_score,
            final_score=current_score,
            iterations=iterations,
            quality_level=self._determine_quality_level(current_score)
        )

    async def _improve_criterion(
        self,
        content: str,
        criterion_name: str,
        criterion_config: Dict,
        feedback: str,
        suggestions: List[str],
        genre: GenreType
    ) -> str:
        """Improve content in a specific criterion area."""
        prompt = f"""
Popraw poniższy tekst, skupiając się na: {criterion_config['description']}

AKTUALNY FEEDBACK: {feedback}

SUGESTIE POPRAWY:
{chr(10).join(f'- {s}' for s in suggestions)}

KRYTERIA DO SPEŁNIENIA:
{chr(10).join(f'- {c}' for c in criterion_config['criteria'])}

GATUNEK: {genre.value}

TEKST DO POPRAWY:
---
{content}
---

Przepisz tekst z poprawkami w tym obszarze.
Zachowaj fabułę i postacie, ale popraw jakość według kryteriów.
Zwróć TYLKO poprawiony tekst.
"""

        try:
            improved = await self.ai_service.generate(
                prompt=prompt,
                model_tier=2,  # Use better model for improvement
                max_tokens=len(content.split()) * 2,
                temperature=0.7
            )
            return improved
        except:
            return content


# Singleton instance
_quality_engine: Optional[BestsellerQualityEngine] = None


def get_quality_engine() -> BestsellerQualityEngine:
    """Get or create quality engine instance."""
    global _quality_engine
    if _quality_engine is None:
        _quality_engine = BestsellerQualityEngine()
    return _quality_engine

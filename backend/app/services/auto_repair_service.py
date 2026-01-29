"""
Auto Repair Service for NarraForge 2.0

Automatically repairs failed chapter/scene generations.
NEVER let a project fail because of a single scene!
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio

from app.services.ai_service import AIService
from app.config import settings


class RepairApproach(str, Enum):
    STANDARD = "standard"
    FOCUSED = "focused"
    MINIMAL = "minimal"
    FALLBACK = "fallback"


@dataclass
class RepairStrategy:
    """Strategy for repairing failed content"""
    tier: int  # 1, 2, or 3
    context_size: str  # full, simplified, minimal
    temperature: float
    approach: RepairApproach
    additional_instructions: str = ""
    max_tokens: int = 4000


@dataclass
class AttemptInfo:
    """Information about a repair attempt"""
    number: int
    strategy: RepairStrategy
    result_length: int = 0
    validation_score: float = 0.0
    error: Optional[str] = None
    success: bool = False


@dataclass
class SceneResult:
    """Result of scene generation with repair info"""
    content: str
    attempts: int
    final_strategy: str
    quality_score: float
    is_fallback: bool = False
    fallback_reason: str = ""
    requires_human_review: bool = False
    attempt_history: List[AttemptInfo] = field(default_factory=list)


class AutoRepairService:
    """
    Automatic repair for failed generations.
    NEVER let a project fail because of one scene!
    """

    MAX_REPAIR_ATTEMPTS = 3

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()

    async def generate_with_repair(
        self,
        scene_data: Dict[str, Any],
        context: Dict[str, Any],
        original_tier: int = 2
    ) -> SceneResult:
        """
        Generate scene with automatic repair on failure.

        Args:
            scene_data: Scene outline and requirements
            context: Full context pack
            original_tier: Starting model tier

        Returns:
            SceneResult with content and repair info
        """
        attempts: List[AttemptInfo] = []

        for attempt in range(1, self.MAX_REPAIR_ATTEMPTS + 1):
            # Select strategy based on previous attempts
            strategy = self._select_strategy(attempt, attempts)

            try:
                # Build prompt based on strategy
                prompt = self._build_prompt(scene_data, context, strategy)

                # Generate content
                result = await self.ai_service.generate(
                    prompt=prompt,
                    model_tier=strategy.tier,
                    max_tokens=strategy.max_tokens,
                    temperature=strategy.temperature
                )

                # Validate result
                validation = await self._validate_result(result, scene_data)

                if validation["is_acceptable"]:
                    return SceneResult(
                        content=result,
                        attempts=attempt,
                        final_strategy=strategy.approach.value,
                        quality_score=validation["score"],
                        attempt_history=attempts
                    )

                # Record attempt
                attempts.append(AttemptInfo(
                    number=attempt,
                    strategy=strategy,
                    result_length=len(result),
                    validation_score=validation["score"],
                    success=False
                ))

            except Exception as e:
                # Record failed attempt
                attempts.append(AttemptInfo(
                    number=attempt,
                    strategy=strategy,
                    error=str(e),
                    success=False
                ))

                # Wait before retry
                await asyncio.sleep(2 ** attempt)

        # All attempts failed - use fallback
        return await self._generate_fallback(scene_data, context, attempts)

    def _select_strategy(
        self,
        attempt: int,
        previous_attempts: List[AttemptInfo]
    ) -> RepairStrategy:
        """
        Select repair strategy based on attempt number and previous failures.
        """
        if attempt == 1:
            # First attempt: standard approach
            return RepairStrategy(
                tier=2,
                context_size="full",
                temperature=0.7,
                approach=RepairApproach.STANDARD,
                max_tokens=4000
            )

        elif attempt == 2:
            # Second attempt: upgrade tier, simplify context
            return RepairStrategy(
                tier=3,  # Upgrade to Claude Opus/GPT-4!
                context_size="simplified",
                temperature=0.6,
                approach=RepairApproach.FOCUSED,
                additional_instructions="""
Skup się TYLKO na tej scenie.
Ignoruj mniej istotne szczegóły kontekstu.
Priorytet: spójność i kompletność.
""",
                max_tokens=3000
            )

        elif attempt == 3:
            # Third attempt: minimal, highest tier
            return RepairStrategy(
                tier=3,
                context_size="minimal",
                temperature=0.5,
                approach=RepairApproach.MINIMAL,
                additional_instructions="""
Napisz PROSTĄ wersję tej sceny.
Maksymalnie 500 słów.
Skup się na: kto, co, gdzie, dlaczego.
Unikaj komplikacji.
""",
                max_tokens=1500
            )

        # Shouldn't reach here, but default to minimal
        return RepairStrategy(
            tier=3,
            context_size="minimal",
            temperature=0.5,
            approach=RepairApproach.MINIMAL,
            max_tokens=1000
        )

    def _build_prompt(
        self,
        scene_data: Dict[str, Any],
        context: Dict[str, Any],
        strategy: RepairStrategy
    ) -> str:
        """Build prompt based on strategy."""
        scene_number = scene_data.get("number", 1)
        scene_title = scene_data.get("title", "Scena")
        scene_goal = scene_data.get("goal", "")
        characters = scene_data.get("characters", [])
        beat_sheet = scene_data.get("beat_sheet", "")

        # Build context based on size
        if strategy.context_size == "full":
            context_text = self._build_full_context(context)
        elif strategy.context_size == "simplified":
            context_text = self._build_simplified_context(context)
        else:  # minimal
            context_text = self._build_minimal_context(context)

        prompt = f"""
SCENA {scene_number}: {scene_title}

CEL SCENY: {scene_goal}

POSTACIE W SCENIE: {', '.join(characters) if characters else 'Do określenia'}

BEAT SHEET:
{beat_sheet if beat_sheet else 'Zrealizuj cel sceny'}

{context_text}

{strategy.additional_instructions}

Napisz scenę w stylu bestsellera.
Użyj technik: Show Don't Tell, Deep POV, sensory details.
Zakończ w sposób budujący napięcie.
"""
        return prompt

    def _build_full_context(self, context: Dict[str, Any]) -> str:
        """Build full context string."""
        parts = []

        if context.get("world_bible"):
            parts.append(f"ŚWIAT: {context['world_bible'][:2000]}...")

        if context.get("characters"):
            parts.append(f"POSTACIE: {context['characters'][:2000]}...")

        if context.get("previous_scene"):
            parts.append(f"POPRZEDNIA SCENA: {context['previous_scene'][:1000]}...")

        if context.get("plot_context"):
            parts.append(f"KONTEKST FABULARNY: {context['plot_context'][:1000]}...")

        return "\n\n".join(parts)

    def _build_simplified_context(self, context: Dict[str, Any]) -> str:
        """Build simplified context - only essential info."""
        parts = []

        if context.get("characters"):
            parts.append(f"POSTACIE (skrót): {context['characters'][:500]}...")

        if context.get("previous_scene"):
            parts.append(f"POPRZEDNIO: {context['previous_scene'][:300]}...")

        return "\n\n".join(parts) if parts else "Kontekst minimalny."

    def _build_minimal_context(self, context: Dict[str, Any]) -> str:
        """Build minimal context - bare essentials only."""
        if context.get("previous_scene"):
            return f"POPRZEDNIO (w skrócie): {context['previous_scene'][:200]}..."
        return "Brak dodatkowego kontekstu."

    async def _validate_result(
        self,
        result: str,
        scene_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate generated content."""
        # Basic validations
        issues = []
        score = 100

        # Check length
        word_count = len(result.split())
        if word_count < 200:
            issues.append("Za krótka scena")
            score -= 30
        elif word_count < 400:
            issues.append("Scena poniżej optymalnej długości")
            score -= 10

        # Check for incomplete content markers
        incomplete_markers = ["...", "[kontynuacja]", "[do uzupełnienia]", "TO BE CONTINUED", "###"]
        for marker in incomplete_markers:
            if marker.lower() in result.lower():
                issues.append(f"Możliwy niekompletny tekst: {marker}")
                score -= 15

        # Check if characters mentioned
        characters = scene_data.get("characters", [])
        if characters:
            mentioned = sum(1 for char in characters if char.lower() in result.lower())
            if mentioned == 0:
                issues.append("Żadna postać nie wspomniana")
                score -= 20

        # Check for dialogue (most scenes should have some)
        if '"' not in result and '„' not in result:
            issues.append("Brak dialogu w scenie")
            score -= 5

        # Acceptable threshold
        is_acceptable = score >= 60 and word_count >= 200

        return {
            "is_acceptable": is_acceptable,
            "score": max(0, score),
            "issues": issues,
            "word_count": word_count
        }

    async def _generate_fallback(
        self,
        scene_data: Dict[str, Any],
        context: Dict[str, Any],
        attempts: List[AttemptInfo]
    ) -> SceneResult:
        """
        Last resort fallback - generate minimal but functional scene.
        """
        scene_number = scene_data.get("number", 1)
        scene_title = scene_data.get("title", "Scena")
        scene_goal = scene_data.get("goal", "Kontynuacja historii")
        characters = scene_data.get("characters", ["Protagonista"])

        fallback_prompt = f"""
TRYB AWARYJNY - generacja minimalna.

Scena {scene_number}: {scene_title}
Cel: {scene_goal}
Postacie: {', '.join(characters[:3])}

Napisz KRÓTKĄ scenę (300-500 słów) która:
1. Realizuje cel sceny
2. Przesuwa fabułę do przodu
3. Jest spójna z poprzednimi scenami (zakładaj że są)

NIE martw się o:
- Bogate opisy
- Głęboką psychologię
- Perfekcyjny styl

PRIORYTET: Funkcjonalność > Jakość

Napisz scenę teraz:
"""

        try:
            result = await self.ai_service.generate(
                prompt=fallback_prompt,
                model_tier=2,  # Tier 2 for fallback
                max_tokens=1000,
                temperature=0.6
            )

            return SceneResult(
                content=result,
                attempts=self.MAX_REPAIR_ATTEMPTS + 1,
                final_strategy=RepairApproach.FALLBACK.value,
                quality_score=60,  # Lower score but functional
                is_fallback=True,
                fallback_reason="All repair attempts failed",
                requires_human_review=True,
                attempt_history=attempts
            )

        except Exception as e:
            # Even fallback failed - return placeholder
            placeholder = f"""
[Scena {scene_number}: {scene_title}]

{characters[0] if characters else 'Bohater'} kontynuował swoją drogę, świadomy że przed nim czeka jeszcze wiele wyzwań.

[UWAGA: Ta scena wymaga ręcznego napisania - automatyczna generacja nie powiodła się. Błąd: {str(e)[:100]}]
"""
            return SceneResult(
                content=placeholder,
                attempts=self.MAX_REPAIR_ATTEMPTS + 2,
                final_strategy="placeholder",
                quality_score=30,
                is_fallback=True,
                fallback_reason=f"Complete failure: {str(e)}",
                requires_human_review=True,
                attempt_history=attempts
            )


# Singleton instance
_repair_service: Optional[AutoRepairService] = None


def get_repair_service() -> AutoRepairService:
    """Get or create repair service instance."""
    global _repair_service
    if _repair_service is None:
        _repair_service = AutoRepairService()
    return _repair_service

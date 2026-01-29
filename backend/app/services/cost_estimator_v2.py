"""
Accurate Cost Estimator V2 for NarraForge 2.0

Fixed cost estimation that accounts for ALL costs, not just prose generation.
Includes proper Polish token coefficients and input context costs.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.services.dynamic_parameters import BookParameters
from app.config import settings


class ModelTier(str, Enum):
    TIER_1 = "TIER_1"  # GPT-4o-mini / Claude Haiku
    TIER_2 = "TIER_2"  # GPT-4o / Claude Sonnet
    TIER_3 = "TIER_3"  # GPT-4 / Claude Opus


@dataclass
class CostBreakdown:
    """Detailed cost breakdown by step"""
    step_name: str
    calls: int
    input_tokens: int
    output_tokens: int
    tier: ModelTier
    cost: float


@dataclass
class DetailedCostEstimate:
    """Complete cost estimation with confidence intervals"""
    breakdown: Dict[str, CostBreakdown]
    subtotal: float
    margin: float
    total: float
    confidence_range: Dict[str, float]
    warnings: List[str]

    def to_dict(self) -> Dict:
        return {
            "breakdown": {
                k: {
                    "step_name": v.step_name,
                    "calls": v.calls,
                    "input_tokens": v.input_tokens,
                    "output_tokens": v.output_tokens,
                    "tier": v.tier.value,
                    "cost": round(v.cost, 4)
                }
                for k, v in self.breakdown.items()
            },
            "subtotal": round(self.subtotal, 2),
            "margin": round(self.margin, 2),
            "total": round(self.total, 2),
            "confidence_range": {
                "min": round(self.confidence_range["min"], 2),
                "max": round(self.confidence_range["max"], 2)
            },
            "warnings": self.warnings
        }


class AccurateCostEstimator:
    """
    NEW, accurate cost estimator.
    Accounts for ALL costs, not just prose generation.
    """

    # CORRECTED token coefficients
    TOKENS_PER_WORD_POLISH = 1.6  # Polish = more tokens (was 1.33)
    TOKENS_PER_WORD_ENGLISH = 1.3

    # Realistic input tokens per scene
    SCENE_INPUT_TOKENS = {
        "system_prompt": 2000,
        "context_pack": 4000,
        "beat_sheet": 1500,
        "previous_scene": 2000,
        "character_context": 2000,
        "world_context": 1500,
        "total": 13000  # NOT 5000!
    }

    # Cost per step
    STEP_COSTS = {
        "titan_analysis": {
            "calls": 12,  # 12 dimensions
            "input_per_call": 500,
            "output_per_call": 1000,
            "tier": ModelTier.TIER_1
        },
        "world_building": {
            "calls": 1,
            "input": 3000,
            "output": 8000,
            "tier": ModelTier.TIER_2
        },
        "character_creation": {
            "calls_per_character": 1,
            "input": 2000,
            "output": 4000,
            "tier": ModelTier.TIER_2
        },
        "plot_architecture": {
            "calls": 1,
            "input": 5000,
            "output": 10000,
            "tier": ModelTier.TIER_2
        },
        "beat_sheet_per_scene": {
            "input": 2000,
            "output": 1500,
            "tier": ModelTier.TIER_1
        },
        "prose_per_scene": {
            "input": 13000,  # Realistic!
            "output": 1800,  # ~1200 words * 1.5
            "tier": ModelTier.TIER_2
        },
        "qa_per_scene": {
            "input": 2500,
            "output": 500,
            "tier": ModelTier.TIER_1
        },
        "continuity_check": {
            "calls": 1,
            "input": 10000,
            "output": 2000,
            "tier": ModelTier.TIER_1
        },
        "style_polish": {
            "calls_per_chapter": 1,
            "input": 5000,
            "output": 3000,
            "tier": ModelTier.TIER_2
        },
        "final_assembly": {
            "calls": 1,
            "input": 2000,
            "output": 1000,
            "tier": ModelTier.TIER_1
        }
    }

    # Model pricing per 1M tokens
    MODEL_PRICES = {
        ModelTier.TIER_1: {
            "input": settings.TIER1_INPUT_COST,  # 0.15
            "output": settings.TIER1_OUTPUT_COST  # 0.60
        },
        ModelTier.TIER_2: {
            "input": settings.TIER2_INPUT_COST,  # 2.50
            "output": settings.TIER2_OUTPUT_COST  # 10.0
        },
        ModelTier.TIER_3: {
            "input": settings.TIER3_INPUT_COST,  # 30.0
            "output": settings.TIER3_OUTPUT_COST  # 60.0
        }
    }

    def estimate_project_cost(
        self,
        parameters: BookParameters,
        include_margin: bool = True
    ) -> DetailedCostEstimate:
        """
        Accurate project cost estimation.

        Args:
            parameters: Book parameters from DynamicParameterGenerator
            include_margin: Whether to add 20% safety margin

        Returns:
            DetailedCostEstimate with full breakdown
        """
        breakdown = {}

        # 1. TITAN Analysis
        titan = self.STEP_COSTS["titan_analysis"]
        breakdown["titan_analysis"] = CostBreakdown(
            step_name="Analiza TITAN (12 wymiarów)",
            calls=titan["calls"],
            input_tokens=titan["calls"] * titan["input_per_call"],
            output_tokens=titan["calls"] * titan["output_per_call"],
            tier=titan["tier"],
            cost=self._calc_cost(
                titan["calls"] * titan["input_per_call"],
                titan["calls"] * titan["output_per_call"],
                titan["tier"]
            )
        )

        # 2. World Building
        wb = self.STEP_COSTS["world_building"]
        breakdown["world_building"] = CostBreakdown(
            step_name="Budowanie świata",
            calls=wb["calls"],
            input_tokens=wb["input"],
            output_tokens=wb["output"],
            tier=wb["tier"],
            cost=self._calc_cost(wb["input"], wb["output"], wb["tier"])
        )

        # 3. Character Creation
        char = self.STEP_COSTS["character_creation"]
        total_chars = parameters.main_characters + parameters.supporting_characters
        breakdown["character_creation"] = CostBreakdown(
            step_name=f"Kreacja postaci ({total_chars} postaci)",
            calls=total_chars,
            input_tokens=char["input"] * total_chars,
            output_tokens=char["output"] * total_chars,
            tier=char["tier"],
            cost=self._calc_cost(
                char["input"] * total_chars,
                char["output"] * total_chars,
                char["tier"]
            )
        )

        # 4. Plot Architecture
        plot = self.STEP_COSTS["plot_architecture"]
        breakdown["plot_architecture"] = CostBreakdown(
            step_name="Architektura fabuły",
            calls=plot["calls"],
            input_tokens=plot["input"],
            output_tokens=plot["output"],
            tier=plot["tier"],
            cost=self._calc_cost(plot["input"], plot["output"], plot["tier"])
        )

        # 5. Scene Generation (BIGGEST COST!)
        total_scenes = parameters.chapter_count * parameters.scenes_per_chapter

        # Beat Sheets
        beat = self.STEP_COSTS["beat_sheet_per_scene"]
        breakdown["beat_sheets"] = CostBreakdown(
            step_name=f"Beat sheets ({total_scenes} scen)",
            calls=total_scenes,
            input_tokens=beat["input"] * total_scenes,
            output_tokens=beat["output"] * total_scenes,
            tier=beat["tier"],
            cost=self._calc_cost(
                beat["input"] * total_scenes,
                beat["output"] * total_scenes,
                beat["tier"]
            )
        )

        # Prose Generation (MAIN COST)
        prose = self.STEP_COSTS["prose_per_scene"]
        breakdown["prose_generation"] = CostBreakdown(
            step_name=f"Generowanie prozy ({total_scenes} scen)",
            calls=total_scenes,
            input_tokens=prose["input"] * total_scenes,
            output_tokens=prose["output"] * total_scenes,
            tier=prose["tier"],
            cost=self._calc_cost(
                prose["input"] * total_scenes,
                prose["output"] * total_scenes,
                prose["tier"]
            )
        )

        # QA Validation
        qa = self.STEP_COSTS["qa_per_scene"]
        breakdown["quality_assurance"] = CostBreakdown(
            step_name=f"Kontrola jakości ({total_scenes} scen)",
            calls=total_scenes,
            input_tokens=qa["input"] * total_scenes,
            output_tokens=qa["output"] * total_scenes,
            tier=qa["tier"],
            cost=self._calc_cost(
                qa["input"] * total_scenes,
                qa["output"] * total_scenes,
                qa["tier"]
            )
        )

        # 6. Style Polish
        style = self.STEP_COSTS["style_polish"]
        breakdown["style_polish"] = CostBreakdown(
            step_name=f"Polerowanie stylu ({parameters.chapter_count} rozdziałów)",
            calls=parameters.chapter_count,
            input_tokens=style["input"] * parameters.chapter_count,
            output_tokens=style["output"] * parameters.chapter_count,
            tier=style["tier"],
            cost=self._calc_cost(
                style["input"] * parameters.chapter_count,
                style["output"] * parameters.chapter_count,
                style["tier"]
            )
        )

        # 7. Continuity Check
        cont = self.STEP_COSTS["continuity_check"]
        breakdown["continuity_check"] = CostBreakdown(
            step_name="Sprawdzanie ciągłości",
            calls=cont["calls"],
            input_tokens=cont["input"],
            output_tokens=cont["output"],
            tier=cont["tier"],
            cost=self._calc_cost(cont["input"], cont["output"], cont["tier"])
        )

        # 8. Final Assembly
        final = self.STEP_COSTS["final_assembly"]
        breakdown["final_assembly"] = CostBreakdown(
            step_name="Finalizacja",
            calls=final["calls"],
            input_tokens=final["input"],
            output_tokens=final["output"],
            tier=final["tier"],
            cost=self._calc_cost(final["input"], final["output"], final["tier"])
        )

        # Calculate totals
        subtotal = sum(b.cost for b in breakdown.values())

        # Safety margin (+20%)
        margin = subtotal * 0.20 if include_margin else 0

        total = subtotal + margin

        # Generate warnings
        warnings = self._generate_warnings(parameters, total)

        return DetailedCostEstimate(
            breakdown=breakdown,
            subtotal=subtotal,
            margin=margin,
            total=total,
            confidence_range={
                "min": total * 0.85,
                "max": total * 1.15
            },
            warnings=warnings
        )

    def _calc_cost(self, input_tokens: int, output_tokens: int, tier: ModelTier) -> float:
        """Calculate cost for given token counts."""
        prices = self.MODEL_PRICES[tier]
        input_cost = (input_tokens / 1_000_000) * prices["input"]
        output_cost = (output_tokens / 1_000_000) * prices["output"]
        return input_cost + output_cost

    def _generate_warnings(self, params: BookParameters, total: float) -> List[str]:
        """Generate warnings for user."""
        warnings = []

        if total > 50:
            warnings.append(f"Szacowany koszt (${total:.2f}) jest wysoki. Rozważ mniejszy zakres.")

        if total > 100:
            warnings.append(f"UWAGA: Koszt (${total:.2f}) przekracza $100. Upewnij się, że to zamierzone.")

        if params.word_count > 150000:
            warnings.append("Bardzo długa książka (>150k słów) - generowanie może potrwać 2+ godziny.")

        if params.main_characters > 10:
            warnings.append("Duża ilość głównych postaci (>10) zwiększa ryzyko niespójności.")

        if params.chapter_count > 40:
            warnings.append("Wiele rozdziałów (>40) - dłuższy czas generowania i wyższy koszt.")

        return warnings

    def estimate_duration_minutes(self, parameters: BookParameters) -> int:
        """Estimate generation duration in minutes."""
        total_scenes = parameters.chapter_count * parameters.scenes_per_chapter

        # Base times per step (in minutes)
        times = {
            "titan_analysis": 2,
            "world_building": 1,
            "character_creation": 0.5 * (parameters.main_characters + parameters.supporting_characters // 2),
            "plot_architecture": 2,
            "beat_sheets": 0.1 * total_scenes,
            "prose_generation": 0.5 * total_scenes,  # ~30 seconds per scene
            "qa": 0.05 * total_scenes,
            "style_polish": 0.2 * parameters.chapter_count,
            "continuity": 2,
            "assembly": 1
        }

        total_minutes = sum(times.values())

        # Add 20% buffer
        return int(total_minutes * 1.2)


# Singleton instance
_cost_estimator: Optional[AccurateCostEstimator] = None


def get_cost_estimator() -> AccurateCostEstimator:
    """Get or create cost estimator instance."""
    global _cost_estimator
    if _cost_estimator is None:
        _cost_estimator = AccurateCostEstimator()
    return _cost_estimator

"""
Accurate Cost Estimator V2 for NarraForge 2.0 (Audited & Fixed)

Fixed:
- ModelTier imported from ai_service.py (canonical source), not duplicated
- Prose output tokens calculated dynamically from target word count
- Polish tokenization coefficient increased to 1.8 (safer for inflected language)
- Steps aligned with ServiceOrchestrator WORKFLOW_TEMPLATES
- Added total_tokens_in/out and estimated_duration_min to DetailedCostEstimate
- Input context per scene increased to 15k (accounts for RAG + GraphRAG context)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging

from app.services.dynamic_parameters import BookParameters
from app.config import settings

# Canonical ModelTier from ai_service.py (int enum: 1, 2, 3)
# NOT duplicated here - this was a critical type mismatch bug
from app.services.ai_service import ModelTier

logger = logging.getLogger(__name__)


@dataclass
class CostBreakdown:
    """Detailed cost breakdown by step"""
    step_name: str
    calls: int
    input_tokens: int
    output_tokens: int
    tier: int  # Plain int (1, 2, 3) for serialization safety
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
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    estimated_duration_min: int = 0

    def to_dict(self) -> Dict:
        return {
            "breakdown": {
                k: {
                    "step_name": v.step_name,
                    "calls": v.calls,
                    "input_tokens": v.input_tokens,
                    "output_tokens": v.output_tokens,
                    "tier": v.tier,
                    "cost": round(v.cost, 4)
                }
                for k, v in self.breakdown.items()
            },
            "subtotal": round(self.subtotal, 2),
            "margin": round(self.margin, 2),
            "total": round(self.total, 2),
            "total_tokens_in": self.total_tokens_in,
            "total_tokens_out": self.total_tokens_out,
            "estimated_duration_min": self.estimated_duration_min,
            "confidence_range": {
                "min": round(self.confidence_range["min"], 2),
                "max": round(self.confidence_range["max"], 2)
            },
            "warnings": self.warnings
        }


class AccurateCostEstimator:
    """
    Accurate cost estimator aligned with ServiceOrchestrator workflow.

    Key fixes over V1:
    - Output tokens for prose calculated from word_count / total_scenes * token_ratio
    - Input context per scene is 15k (system + world bible + chars + previous + RAG + GraphRAG)
    - Polish text tokenization uses 1.8x coefficient (not 1.6 - safer for inflected language)
    - Steps match WORKFLOW_TEMPLATES from orchestrator.py
    """

    # Polish text produces ~1.8 tokens per word due to inflection (cases, genders, etc.)
    # English is ~1.3. Using 1.8 instead of 1.6 provides safety margin.
    TOKENS_PER_WORD_POLISH = 1.8
    TOKENS_PER_WORD_ENGLISH = 1.3

    # Realistic input tokens per scene (all context that goes into the prompt)
    SCENE_INPUT_TOKENS = {
        "system_prompt": 2000,       # System instructions
        "world_bible": 3000,         # World context (cached via prompt caching)
        "beat_sheet": 1500,          # Scene plan
        "previous_scene": 2000,      # Continuity from previous scene
        "character_context": 2000,   # Character profiles for scene chars
        "rag_context": 2000,         # Vector search results from MIRIX
        "relationship_graph": 1000,  # GraphRAG relationship context
        "style_few_shot": 1500,      # Few-shot style examples
        "total": 15000               # Total context per scene call
    }

    # Model pricing per 1M tokens (from config, with int tier keys)
    MODEL_PRICES = {
        1: {"input": settings.TIER1_INPUT_COST, "output": settings.TIER1_OUTPUT_COST},
        2: {"input": settings.TIER2_INPUT_COST, "output": settings.TIER2_OUTPUT_COST},
        3: {"input": settings.TIER3_INPUT_COST, "output": settings.TIER3_OUTPUT_COST},
    }

    def estimate_project_cost(
        self,
        parameters: BookParameters,
        include_margin: bool = True
    ) -> DetailedCostEstimate:
        """
        Accurate project cost estimation aligned with orchestrator workflow.

        Args:
            parameters: Book parameters from DynamicParameterGenerator
            include_margin: Whether to add 20% safety margin

        Returns:
            DetailedCostEstimate with full breakdown
        """
        breakdown = {}
        total_tokens_in = 0
        total_tokens_out = 0
        total_duration = 0  # minutes

        # Core dimensions
        n_chapters = parameters.chapter_count
        n_scenes_per_chapter = parameters.scenes_per_chapter
        total_scenes = n_chapters * n_scenes_per_chapter
        total_chars = parameters.main_characters + parameters.supporting_characters
        target_words = parameters.word_count

        # CRITICAL FIX: Calculate output tokens per scene from target word count
        # 90,000 words / 125 scenes = 720 words/scene * 1.8 = 1,296 tokens/scene
        avg_words_per_scene = target_words / total_scenes if total_scenes > 0 else 0
        output_tokens_per_scene = int(avg_words_per_scene * self.TOKENS_PER_WORD_POLISH)

        # =====================================================================
        # STEP 1: Initialize Project (mirix.initialize)
        # =====================================================================
        step_in, step_out = 500, 200
        breakdown["initialize"] = CostBreakdown(
            step_name="Inicjalizacja projektu",
            calls=1,
            input_tokens=step_in,
            output_tokens=step_out,
            tier=1,
            cost=self._calc_cost(step_in, step_out, 1)
        )
        total_tokens_in += step_in
        total_tokens_out += step_out
        total_duration += 0.5

        # =====================================================================
        # STEP 2: Analyze Trends (trends.analyze)
        # =====================================================================
        # 12 trend dimensions analyzed
        calls = 12
        step_in = 1000 * calls
        step_out = 500 * calls
        breakdown["trends_analysis"] = CostBreakdown(
            step_name="Analiza trendów (12 wymiarów)",
            calls=calls,
            input_tokens=step_in,
            output_tokens=step_out,
            tier=1,
            cost=self._calc_cost(step_in, step_out, 1)
        )
        total_tokens_in += step_in
        total_tokens_out += step_out
        total_duration += 2

        # =====================================================================
        # STEP 3: Create Outline (pacing.create_outline)
        # Plot architecture + chapter breakdown + beat sheets
        # =====================================================================
        step_in = 8000
        step_out = 4000 + (1500 * total_scenes)  # Base outline + beat sheet per scene
        breakdown["outline_and_beats"] = CostBreakdown(
            step_name=f"Architektura fabuły + Beat sheets ({total_scenes} scen)",
            calls=1 + total_scenes,
            input_tokens=step_in + (2000 * total_scenes),
            output_tokens=step_out,
            tier=2,
            cost=self._calc_cost(
                step_in + (2000 * total_scenes),
                step_out,
                2
            )
        )
        total_tokens_in += step_in + (2000 * total_scenes)
        total_tokens_out += step_out
        total_duration += 3 + (0.1 * total_scenes)

        # =====================================================================
        # STEP 4: Develop Characters (consciousness.create_characters)
        # =====================================================================
        step_in = 3000 * total_chars
        step_out = 2000 * total_chars
        breakdown["character_creation"] = CostBreakdown(
            step_name=f"Kreacja postaci ({total_chars} postaci)",
            calls=total_chars,
            input_tokens=step_in,
            output_tokens=step_out,
            tier=2,
            cost=self._calc_cost(step_in, step_out, 2)
        )
        total_tokens_in += step_in
        total_tokens_out += step_out
        total_duration += 0.5 * total_chars

        # =====================================================================
        # STEP 5: Generate Chapters (dialogue.generate) - BIGGEST COST
        # This is the prose generation loop - one call per scene
        # =====================================================================
        scene_input = self.SCENE_INPUT_TOKENS["total"]  # 15,000 tokens context per scene
        scene_output = output_tokens_per_scene  # Dynamically calculated!

        prose_total_in = scene_input * total_scenes
        prose_total_out = scene_output * total_scenes

        # Sanity check: total output tokens must cover target word count
        expected_output_words = prose_total_out / self.TOKENS_PER_WORD_POLISH
        if expected_output_words < target_words * 0.9:
            logger.warning(
                f"Output token estimate ({prose_total_out}) may be too low for "
                f"{target_words} words. Expected minimum: {int(target_words * self.TOKENS_PER_WORD_POLISH)}"
            )

        breakdown["prose_generation"] = CostBreakdown(
            step_name=f"Generowanie prozy ({total_scenes} scen, ~{avg_words_per_scene:.0f} słów/scenę)",
            calls=total_scenes,
            input_tokens=prose_total_in,
            output_tokens=prose_total_out,
            tier=2,
            cost=self._calc_cost(prose_total_in, prose_total_out, 2)
        )
        total_tokens_in += prose_total_in
        total_tokens_out += prose_total_out
        total_duration += 0.5 * total_scenes  # ~30s per scene

        # =====================================================================
        # STEP 6: Apply Style (style.apply)
        # =====================================================================
        # Style polish reads the full chapter and rewrites
        chapter_tokens = int((target_words / n_chapters) * self.TOKENS_PER_WORD_POLISH)
        step_in = chapter_tokens * n_chapters
        step_out = int(step_in * 1.1)  # Rewrite can be slightly longer
        breakdown["style_polish"] = CostBreakdown(
            step_name=f"Polerowanie stylu ({n_chapters} rozdziałów)",
            calls=n_chapters,
            input_tokens=step_in,
            output_tokens=step_out,
            tier=2,
            cost=self._calc_cost(step_in, step_out, 2)
        )
        total_tokens_in += step_in
        total_tokens_out += step_out
        total_duration += 0.3 * n_chapters

        # =====================================================================
        # STEP 7: Emotional Resonance (emotional.enhance)
        # =====================================================================
        step_in = 4000 * total_scenes
        step_out = 500 * total_scenes
        breakdown["emotional_resonance"] = CostBreakdown(
            step_name=f"Rezonans emocjonalny ({total_scenes} scen)",
            calls=total_scenes,
            input_tokens=step_in,
            output_tokens=step_out,
            tier=1,
            cost=self._calc_cost(step_in, step_out, 1)
        )
        total_tokens_in += step_in
        total_tokens_out += step_out
        total_duration += 0.05 * total_scenes

        # =====================================================================
        # STEP 8: Coherence Check (coherence.analyze)
        # =====================================================================
        step_in = 10000 * n_chapters
        step_out = 1000 * n_chapters
        breakdown["coherence_check"] = CostBreakdown(
            step_name=f"Sprawdzanie spójności ({n_chapters} rozdziałów)",
            calls=n_chapters,
            input_tokens=step_in,
            output_tokens=step_out,
            tier=1,
            cost=self._calc_cost(step_in, step_out, 1)
        )
        total_tokens_in += step_in
        total_tokens_out += step_out
        total_duration += 0.2 * n_chapters

        # =====================================================================
        # STEP 9: Cultural Adaptation (cultural.adapt)
        # =====================================================================
        step_in, step_out = 10000, 2000
        breakdown["cultural_adaptation"] = CostBreakdown(
            step_name="Adaptacja kulturowa",
            calls=1,
            input_tokens=step_in,
            output_tokens=step_out,
            tier=2,
            cost=self._calc_cost(step_in, step_out, 2)
        )
        total_tokens_in += step_in
        total_tokens_out += step_out
        total_duration += 2

        # =====================================================================
        # STEP 10: Cover + Illustrations (covers/illustrations - DALL-E)
        # Fixed cost per image, not token-based
        # =====================================================================
        cover_count = 1
        illustration_count = max(1, n_chapters // 5)  # 1 illustration per 5 chapters
        total_images = cover_count + illustration_count
        image_cost = total_images * 0.080  # ~$0.08 per DALL-E 3 HD image

        breakdown["visual_generation"] = CostBreakdown(
            step_name=f"Okładka + ilustracje ({total_images} obrazów)",
            calls=total_images,
            input_tokens=0,
            output_tokens=0,
            tier=3,  # Treat as premium cost
            cost=image_cost
        )
        total_duration += 1

        # =====================================================================
        # CALCULATE TOTALS
        # =====================================================================
        subtotal = sum(b.cost for b in breakdown.values())
        margin = subtotal * 0.20 if include_margin else 0
        total = subtotal + margin

        # Duration buffer
        total_duration = int(total_duration * 1.2)  # +20% buffer

        warnings = self._generate_warnings(parameters, total, total_tokens_out)

        return DetailedCostEstimate(
            breakdown=breakdown,
            subtotal=subtotal,
            margin=margin,
            total=total,
            confidence_range={
                "min": total * 0.85,
                "max": total * 1.25
            },
            warnings=warnings,
            total_tokens_in=total_tokens_in,
            total_tokens_out=total_tokens_out,
            estimated_duration_min=total_duration,
        )

    def _calc_cost(self, input_tokens: int, output_tokens: int, tier: int) -> float:
        """Calculate cost for given token counts. Accepts int tier (1, 2, 3)."""
        # Handle both int and ModelTier enum
        tier_key = int(tier)
        prices = self.MODEL_PRICES.get(tier_key, self.MODEL_PRICES[1])
        input_cost = (input_tokens / 1_000_000) * prices["input"]
        output_cost = (output_tokens / 1_000_000) * prices["output"]
        return input_cost + output_cost

    def _generate_warnings(
        self, params: BookParameters, total: float, total_output_tokens: int
    ) -> List[str]:
        """Generate warnings for user."""
        warnings = []

        if total > settings.MAX_COST_PER_PROJECT:
            warnings.append(
                f"UWAGA: Koszt (${total:.2f}) przekracza budżet bezpieczeństwa "
                f"(${settings.MAX_COST_PER_PROJECT:.0f})."
            )
        elif total > 50:
            warnings.append(
                f"Szacowany koszt (${total:.2f}) jest wysoki. Rozważ mniejszy zakres."
            )

        if params.word_count > 150000:
            warnings.append(
                "Bardzo długa książka (>150k słów) - generowanie może potrwać 2+ godziny."
            )

        if params.main_characters > 10:
            warnings.append(
                "Duża ilość głównych postaci (>10) zwiększa ryzyko niespójności."
            )

        if params.chapter_count > 40:
            warnings.append(
                "Wiele rozdziałów (>40) - dłuższy czas generowania i wyższy koszt."
            )

        # Math sanity check
        expected_words = total_output_tokens / self.TOKENS_PER_WORD_POLISH
        if expected_words < params.word_count * 0.8:
            warnings.append(
                f"Szacowana liczba tokenów wyjściowych ({total_output_tokens:,}) "
                f"może być niewystarczająca dla {params.word_count:,} słów. "
                f"Rzeczywisty koszt może być wyższy."
            )

        return warnings

    def estimate_duration_minutes(self, parameters: BookParameters) -> int:
        """Estimate generation duration in minutes."""
        total_scenes = parameters.chapter_count * parameters.scenes_per_chapter
        total_chars = parameters.main_characters + parameters.supporting_characters // 2

        times = {
            "initialize": 0.5,
            "trends": 2,
            "outline_beats": 3 + (0.1 * total_scenes),
            "characters": 0.5 * total_chars,
            "prose": 0.5 * total_scenes,
            "style": 0.3 * parameters.chapter_count,
            "emotional": 0.05 * total_scenes,
            "coherence": 0.2 * parameters.chapter_count,
            "cultural": 2,
            "visuals": 1,
        }

        total_minutes = sum(times.values())
        return int(total_minutes * 1.2)  # +20% buffer


# Singleton instance
_cost_estimator: Optional[AccurateCostEstimator] = None


def get_cost_estimator() -> AccurateCostEstimator:
    """Get or create cost estimator instance."""
    global _cost_estimator
    if _cost_estimator is None:
        _cost_estimator = AccurateCostEstimator()
    return _cost_estimator

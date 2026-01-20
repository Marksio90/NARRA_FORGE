"""
Cost tracker - tracks costs in real-time.
"""
from typing import Dict
from app.core.cost_optimizer import ModelTier, CostOptimizer
import logging

logger = logging.getLogger(__name__)


class CostTracker:
    """
    Tracks costs in real-time during book generation.
    """

    def __init__(self):
        self.total_cost = 0.0
        self.cost_breakdown = {
            'world_building': 0.0,
            'character_creation': 0.0,
            'plot_generation': 0.0,
            'prose_writing': 0.0,
            'consistency_checks': 0.0,
            'polish_and_edit': 0.0,
            'publishing': 0.0,
        }
        self.model_usage = {tier.name: 0 for tier in ModelTier}
        self.cost_optimizer = CostOptimizer()

    def log_usage(
        self,
        model: ModelTier,
        input_tokens: int,
        output_tokens: int,
        phase: str
    ) -> float:
        """
        Log usage and update costs.

        Args:
            model: Model tier used
            input_tokens: Input tokens
            output_tokens: Output tokens
            phase: Phase of generation (e.g., 'world_building')

        Returns:
            Cost of this operation
        """
        cost = self.cost_optimizer.calculate_cost(model, input_tokens, output_tokens)

        self.total_cost += cost
        if phase in self.cost_breakdown:
            self.cost_breakdown[phase] += cost
        self.model_usage[model.name] += 1

        logger.info(
            f"Cost logged: {model.name} - ${cost:.6f} "
            f"(phase: {phase}, total: ${self.total_cost:.6f})"
        )

        return cost

    def get_summary(self) -> Dict:
        """Get cost summary."""
        return {
            'total': self.total_cost,
            'breakdown': self.cost_breakdown,
            'model_usage': self.model_usage,
        }

    def reset(self):
        """Reset tracker."""
        self.total_cost = 0.0
        self.cost_breakdown = {k: 0.0 for k in self.cost_breakdown}
        self.model_usage = {k: 0 for k in self.model_usage}

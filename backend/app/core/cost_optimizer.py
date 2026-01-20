"""
Cost optimizer - intelligent model selection based on task complexity.
"""
from enum import Enum
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """
    Model tiers from cheapest to most expensive.
    Prices are approximate as of January 2025.
    """

    MINI = {
        'model': 'gpt-4o-mini',
        'cost_per_1k_input': 0.00015,
        'cost_per_1k_output': 0.0006,
        'max_complexity': 2,
    }

    STANDARD = {
        'model': 'gpt-4o',
        'cost_per_1k_input': 0.0025,
        'cost_per_1k_output': 0.01,
        'max_complexity': 4,
    }

    ADVANCED = {
        'model': 'o1',
        'cost_per_1k_input': 0.015,
        'cost_per_1k_output': 0.06,
        'max_complexity': 7,
    }

    PREMIUM = {
        'model': 'o1-pro',
        'cost_per_1k_input': 0.15,
        'cost_per_1k_output': 0.60,
        'max_complexity': 10,
    }


class CostOptimizer:
    """
    Intelligent model selection based on task complexity.
    """

    # Task complexity mapping (1-10)
    TASK_COMPLEXITY_MAP = {
        'format_text': 1,
        'extract_metadata': 1,
        'simple_description': 2,
        'dialogue_writing': 3,
        'scene_description': 3,
        'character_creation': 4,
        'world_building': 5,
        'plot_outline': 5,
        'consistency_check': 4,
        'complex_scene': 6,
        'plot_twist': 7,
        'mystery_solution': 8,
        'philosophical_scene': 7,
        'series_planning': 8,
        'finale_writing': 9,
        'critical_repair': 9,
    }

    def select_model_for_task(self, task_type: str, **modifiers) -> ModelTier:
        """
        Select optimal model for a task.

        Args:
            task_type: Type of task (from TASK_COMPLEXITY_MAP)
            **modifiers: Additional complexity modifiers
                - is_plot_turning_point: bool
                - characters_count: int
                - requires_deep_consistency: bool
                - genre: str
                - is_finale: bool

        Returns:
            ModelTier to use
        """
        base_complexity = self.TASK_COMPLEXITY_MAP.get(task_type, 3)

        # Apply modifiers
        if modifiers.get('is_plot_turning_point'):
            base_complexity += 2
        if modifiers.get('characters_count', 0) > 4:
            base_complexity += 1
        if modifiers.get('requires_deep_consistency'):
            base_complexity += 1
        if modifiers.get('genre') in ['scifi', 'mystery', 'thriller']:
            base_complexity += 1
        if modifiers.get('is_finale'):
            base_complexity += 2

        complexity = min(10, base_complexity)

        logger.debug(f"Task: {task_type}, Complexity: {complexity}")

        # Select model based on complexity
        if complexity <= 2:
            return ModelTier.MINI
        elif complexity <= 4:
            return ModelTier.STANDARD
        elif complexity <= 7:
            return ModelTier.ADVANCED
        else:
            return ModelTier.PREMIUM

    def calculate_cost(
        self,
        model: ModelTier,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for a request.

        Args:
            model: Model tier used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Total cost in USD
        """
        model_info = model.value
        input_cost = (input_tokens / 1000) * model_info['cost_per_1k_input']
        output_cost = (output_tokens / 1000) * model_info['cost_per_1k_output']
        return input_cost + output_cost

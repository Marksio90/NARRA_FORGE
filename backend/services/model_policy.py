"""Model selection policy for different pipeline stages."""

import logging
from enum import Enum

from core.config import settings

logger = logging.getLogger(__name__)


class PipelineStage(str, Enum):
    """Pipeline stages for model selection."""

    # Structural stages (use mini model)
    STRUCTURE = "structure"  # World structure, plot outline
    PLAN = "plan"  # Chapter plans, scene plans
    QA = "qa"  # Quality assurance checks
    TIMELINE = "timeline"  # Timeline validation
    CHARACTER_PROFILE = "character_profile"  # Character profiles

    # High-quality stages (use high model)
    PROSE = "prose"  # Prose generation
    STYLE = "style"  # Style refinement
    EDIT = "edit"  # Editorial improvements
    DIALOG = "dialog"  # Dialog generation


class ModelPolicy:
    """Policy for selecting appropriate models based on pipeline stage."""

    # Stages that use mini model (gpt-4o-mini)
    MINI_STAGES = {
        PipelineStage.STRUCTURE,
        PipelineStage.PLAN,
        PipelineStage.QA,
        PipelineStage.TIMELINE,
        PipelineStage.CHARACTER_PROFILE,
    }

    # Stages that use high model (gpt-4o)
    HIGH_STAGES = {
        PipelineStage.PROSE,
        PipelineStage.STYLE,
        PipelineStage.EDIT,
        PipelineStage.DIALOG,
    }

    @staticmethod
    def get_model_for_stage(stage: PipelineStage) -> str:
        """
        Get appropriate model for a pipeline stage.

        Args:
            stage: Pipeline stage

        Returns:
            Model name (e.g., "gpt-4o-mini" or "gpt-4o")

        Raises:
            ValueError: If stage is unknown
        """
        if stage in ModelPolicy.MINI_STAGES:
            model = settings.model_mini
            logger.debug(f"Selected mini model '{model}' for stage '{stage.value}'")
            return model

        if stage in ModelPolicy.HIGH_STAGES:
            model = settings.model_high
            logger.debug(f"Selected high model '{model}' for stage '{stage.value}'")
            return model

        raise ValueError(f"Unknown pipeline stage: {stage}")

    @staticmethod
    def get_token_budget_for_stage(stage: PipelineStage) -> int:
        """
        Get recommended token budget for a pipeline stage.

        Args:
            stage: Pipeline stage

        Returns:
            Recommended token budget

        Note:
            These are conservative estimates. Actual budgets should be
            configured per job type and adjusted based on monitoring.
        """
        # Structural stages: smaller budgets
        if stage in ModelPolicy.MINI_STAGES:
            if stage == PipelineStage.QA:
                return 1000  # QA checks are typically brief
            return 2000  # Default for structural work

        # High-quality stages: larger budgets
        if stage in ModelPolicy.HIGH_STAGES:
            if stage == PipelineStage.PROSE:
                return 4000  # Prose generation needs more tokens
            if stage == PipelineStage.DIALOG:
                return 3000  # Dialog can be lengthy
            return 2500  # Default for high-quality stages

        raise ValueError(f"Unknown pipeline stage: {stage}")

    @staticmethod
    def get_temperature_for_stage(stage: PipelineStage) -> float:
        """
        Get recommended temperature for a pipeline stage.

        Args:
            stage: Pipeline stage

        Returns:
            Recommended temperature (0.0 to 2.0)

        Note:
            - Lower temperature (0.3-0.5) for structural/analytical tasks
            - Higher temperature (0.7-0.9) for creative tasks
        """
        # Analytical stages: low temperature for consistency
        if stage in {
            PipelineStage.STRUCTURE,
            PipelineStage.PLAN,
            PipelineStage.QA,
            PipelineStage.TIMELINE,
        }:
            return 0.3

        # Character profiles: moderate temperature
        if stage == PipelineStage.CHARACTER_PROFILE:
            return 0.5

        # Creative stages: higher temperature for variety
        if stage in {
            PipelineStage.PROSE,
            PipelineStage.STYLE,
            PipelineStage.DIALOG,
        }:
            return 0.8

        # Editorial: moderate-high temperature
        if stage == PipelineStage.EDIT:
            return 0.6

        raise ValueError(f"Unknown pipeline stage: {stage}")

    @staticmethod
    def get_stage_metadata(stage: PipelineStage) -> dict[str, str | int | float]:
        """
        Get all recommended parameters for a pipeline stage.

        Args:
            stage: Pipeline stage

        Returns:
            Dictionary with model, token_budget, and temperature
        """
        return {
            "model": ModelPolicy.get_model_for_stage(stage),
            "token_budget": ModelPolicy.get_token_budget_for_stage(stage),
            "temperature": ModelPolicy.get_temperature_for_stage(stage),
            "stage": stage.value,
        }

"""
Model Router for NARRA_FORGE V2

Intelligent routing between models:
- gpt-4o-mini: Analysis, planning, validation (COST-OPTIMIZED)
- gpt-4o: Narrative generation, stylization (QUALITY-OPTIMIZED)

Follows the principle: MINI EVERYWHERE, GPT-4 ONLY WHERE NECESSARY
"""
from typing import Optional

from narra_forge.core.config import NarraForgeConfig
from narra_forge.core.types import PipelineStage
from narra_forge.models.openai_client import OpenAIClient


class ModelRouter:
    """
    Routes requests to appropriate models based on task type.

    Philosophy:
    - Analysis, structure, planning: gpt-4o-mini (fast, cheap, good enough)
    - Literary narrative generation: gpt-4o (high quality, expensive, necessary)
    - Validation, checking: gpt-4o-mini (can judge quality without being best)
    """

    # Stages that REQUIRE gpt-4o (high quality)
    # QUALITY-FIRST: Core narrative + stylization + validation use GPT-4o
    # User feedback: mini produces low-quality output even with excellent prompts
    GPT4_REQUIRED_STAGES = {
        PipelineStage.SEQUENTIAL_GENERATION,  # Core narrative - MUST be GPT-4o
        PipelineStage.LANGUAGE_STYLIZATION,   # REVERTED: mini can't follow complex craft rules
        PipelineStage.COHERENCE_VALIDATION,   # UPGRADED: better validation catches issues
    }

    # Cost-optimized stages (planning, architecture, output)
    MINI_STAGES = {
        PipelineStage.BRIEF_INTERPRETATION,
        PipelineStage.WORLD_ARCHITECTURE,
        PipelineStage.CHARACTER_ARCHITECTURE,
        PipelineStage.STRUCTURE_DESIGN,
        PipelineStage.SEGMENT_PLANNING,
        PipelineStage.EDITORIAL_REVIEW,      # Can review without being best
        PipelineStage.OUTPUT_PROCESSING,     # Local processing mostly
    }

    def __init__(self, config: NarraForgeConfig, client: OpenAIClient):
        """
        Initialize router.

        Args:
            config: NarraForgeConfig
            client: OpenAIClient instance
        """
        self.config = config
        self.client = client

    def get_model_for_stage(self, stage: PipelineStage) -> str:
        """
        Get appropriate model for a pipeline stage.

        Args:
            stage: PipelineStage

        Returns:
            Model name (gpt-4o-mini or gpt-4o)
        """
        if stage in self.GPT4_REQUIRED_STAGES:
            return self.config.default_gpt4_model
        else:
            return self.config.default_mini_model

    def get_model_for_task(self, task_type: str) -> str:
        """
        Get appropriate model for a specific task type.

        Task types:
        - "analysis": Analyzing text, extracting structure
        - "planning": Creating plans, outlines
        - "generation": Generating narrative prose
        - "validation": Checking coherence, quality
        - "stylization": Refining language, style
        - "editing": Editorial review

        Args:
            task_type: Type of task

        Returns:
            Model name
        """
        narrative_tasks = {"generation", "stylization"}

        if task_type in narrative_tasks:
            return self.config.default_gpt4_model
        else:
            return self.config.default_mini_model

    def should_use_gpt4(
        self,
        stage: Optional[PipelineStage] = None,
        task_type: Optional[str] = None,
        force_quality: bool = False,
    ) -> bool:
        """
        Determine if GPT-4 should be used.

        Args:
            stage: Pipeline stage (optional)
            task_type: Task type (optional)
            force_quality: Force GPT-4 usage

        Returns:
            True if GPT-4 should be used
        """
        if force_quality:
            return True

        if stage:
            return stage in self.GPT4_REQUIRED_STAGES

        if task_type:
            return task_type in {"generation", "stylization"}

        return False

    async def generate(
        self,
        prompt: str,
        stage: Optional[PipelineStage] = None,
        task_type: Optional[str] = None,
        force_model: Optional[str] = None,
        **kwargs,
    ):
        """
        Generate with automatic model selection.

        Args:
            prompt: User prompt
            stage: Pipeline stage (for auto-routing)
            task_type: Task type (for auto-routing)
            force_model: Force specific model
            **kwargs: Additional arguments for OpenAI API

        Returns:
            (generated_text, model_call)
        """
        # Determine model
        if force_model:
            model = force_model
        elif stage:
            model = self.get_model_for_stage(stage)
        elif task_type:
            model = self.get_model_for_task(task_type)
        else:
            model = self.config.default_mini_model

        # Set purpose for tracking
        purpose = kwargs.pop("purpose", None)
        if purpose is None:
            if stage:
                purpose = stage.value
            elif task_type:
                purpose = task_type
            else:
                purpose = "general"

        # Generate
        return await self.client.generate_async(
            prompt=prompt,
            model=model,
            purpose=purpose,
            **kwargs,
        )

    async def generate_json(
        self,
        prompt: str,
        stage: Optional[PipelineStage] = None,
        task_type: Optional[str] = None,
        force_model: Optional[str] = None,
        **kwargs,
    ):
        """
        Generate JSON with automatic model selection.

        Args:
            prompt: User prompt
            stage: Pipeline stage (for auto-routing)
            task_type: Task type (for auto-routing)
            force_model: Force specific model
            **kwargs: Additional arguments for OpenAI API

        Returns:
            (parsed_json, model_call)
        """
        # Determine model
        if force_model:
            model = force_model
        elif stage:
            model = self.get_model_for_stage(stage)
        elif task_type:
            model = self.get_model_for_task(task_type)
        else:
            model = self.config.default_mini_model

        # Set purpose for tracking
        purpose = kwargs.pop("purpose", None)
        if purpose is None:
            if stage:
                purpose = f"{stage.value}_json"
            elif task_type:
                purpose = f"{task_type}_json"
            else:
                purpose = "json_generation"

        # Generate JSON
        return await self.client.generate_json_async(
            prompt=prompt,
            model=model,
            purpose=purpose,
            **kwargs,
        )

    def get_cost_estimate(
        self,
        stage: PipelineStage,
        estimated_prompt_tokens: int,
        estimated_completion_tokens: int,
    ) -> float:
        """
        Estimate cost for a stage.

        Args:
            stage: Pipeline stage
            estimated_prompt_tokens: Estimated prompt tokens
            estimated_completion_tokens: Estimated completion tokens

        Returns:
            Estimated cost in USD
        """
        model = self.get_model_for_stage(stage)
        return self.client.calculate_cost(
            model=model,
            prompt_tokens=estimated_prompt_tokens,
            completion_tokens=estimated_completion_tokens,
        )

    def get_router_stats(self) -> dict:
        """
        Get router statistics.

        Returns:
            Dict with routing decisions and model usage
        """
        return {
            "mini_stages": [s.value for s in self.MINI_STAGES],
            "gpt4_stages": [s.value for s in self.GPT4_REQUIRED_STAGES],
            "default_mini_model": self.config.default_mini_model,
            "default_gpt4_model": self.config.default_gpt4_model,
            "client_stats": self.client.get_stats(),
        }

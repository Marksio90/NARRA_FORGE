"""
Tests for Model Router
"""
import pytest
from narra_forge.models.model_router import ModelRouter, PipelineStage
from narra_forge.core.config import NarraForgeConfig, create_default_config


@pytest.mark.unit
class TestModelRouter:
    """Test Model Router functionality"""

    def test_router_initialization(self, test_config):
        """Test router can be initialized with config"""
        router = ModelRouter(test_config)

        assert router.config == test_config
        assert router.default_mini_model == test_config.default_mini_model
        assert router.default_gpt4_model == test_config.default_gpt4_model

    def test_get_model_for_brief_interpreter(self, test_config):
        """Test model selection for brief interpreter"""
        router = ModelRouter(test_config)

        model = router.get_model_for_stage(PipelineStage.BRIEF_INTERPRETATION)

        # Brief interpretation uses mini model (fast, cheap)
        assert model == "gpt-4o-mini"

    def test_get_model_for_sequential_generation(self, test_config):
        """Test model selection for sequential generation (QUALITY-CRITICAL)"""
        router = ModelRouter(test_config)

        model = router.get_model_for_stage(PipelineStage.SEQUENTIAL_GENERATION)

        # Sequential generation MUST use GPT-4o (quality-critical)
        assert model == "gpt-4o"

    def test_get_model_for_coherence_validation(self, test_config):
        """Test model selection for coherence validation"""
        router = ModelRouter(test_config)

        model = router.get_model_for_stage(PipelineStage.COHERENCE_VALIDATION)

        # Coherence validation uses GPT-4o (complex analysis)
        assert model == "gpt-4o"

    def test_get_model_for_language_stylization(self, test_config):
        """Test model selection for language stylization"""
        router = ModelRouter(test_config)

        model = router.get_model_for_stage(PipelineStage.LANGUAGE_STYLIZATION)

        # Language stylization uses mini (cost-optimized)
        assert model == "gpt-4o-mini"

    def test_get_temperature_for_generation(self, test_config):
        """Test temperature settings for generation stages"""
        router = ModelRouter(test_config)

        # Creative generation should have higher temperature
        temp = router.get_temperature_for_stage(PipelineStage.SEQUENTIAL_GENERATION)
        assert temp >= 0.9  # High creativity

        # Analysis should have lower temperature
        temp = router.get_temperature_for_stage(PipelineStage.BRIEF_INTERPRETATION)
        assert temp <= 0.7  # More deterministic

    def test_get_max_tokens_for_stage(self, test_config):
        """Test max_tokens configuration per stage"""
        router = ModelRouter(test_config)

        # Sequential generation needs high token limit
        max_tokens = router.get_max_tokens_for_stage(
            PipelineStage.SEQUENTIAL_GENERATION,
            target_words=5000
        )

        # Polish requires ~3 tokens per word
        assert max_tokens >= 5000 * 2.5  # At least 2.5x buffer

    def test_all_pipeline_stages_have_models(self, test_config):
        """Test that all pipeline stages have assigned models"""
        router = ModelRouter(test_config)

        for stage in PipelineStage:
            model = router.get_model_for_stage(stage)
            assert model is not None
            assert model in ["gpt-4o-mini", "gpt-4o"]

    def test_cost_estimation(self, test_config):
        """Test cost estimation for different models"""
        router = ModelRouter(test_config)

        # GPT-4o should be more expensive than mini
        gpt4_cost = router.estimate_cost(
            model="gpt-4o",
            prompt_tokens=1000,
            completion_tokens=1000
        )

        mini_cost = router.estimate_cost(
            model="gpt-4o-mini",
            prompt_tokens=1000,
            completion_tokens=1000
        )

        assert gpt4_cost > mini_cost


@pytest.mark.unit
class TestModelRouterConfiguration:
    """Test Model Router with different configurations"""

    def test_router_respects_custom_mini_model(self):
        """Test router uses custom mini model from config"""
        config = create_default_config(
            openai_api_key="sk-test-key",
            environment="testing",
            default_mini_model="gpt-4o-mini-2024-07-18"  # Specific version
        )

        router = ModelRouter(config)

        assert router.default_mini_model == "gpt-4o-mini-2024-07-18"

    def test_router_respects_custom_gpt4_model(self):
        """Test router uses custom GPT-4 model from config"""
        config = create_default_config(
            openai_api_key="sk-test-key",
            environment="testing",
            default_gpt4_model="gpt-4o-2024-08-06"  # Specific version
        )

        router = ModelRouter(config)

        assert router.default_gpt4_model == "gpt-4o-2024-08-06"


@pytest.mark.unit
class TestPipelineStageEnum:
    """Test PipelineStage enum"""

    def test_all_stages_defined(self):
        """Test all 10 pipeline stages are defined"""
        stages = list(PipelineStage)

        assert len(stages) == 10
        assert PipelineStage.BRIEF_INTERPRETATION in stages
        assert PipelineStage.SEQUENTIAL_GENERATION in stages
        assert PipelineStage.OUTPUT_PROCESSING in stages

    def test_stage_values_are_unique(self):
        """Test all stage values are unique"""
        values = [stage.value for stage in PipelineStage]

        assert len(values) == len(set(values))

    def test_stage_from_agent_id(self):
        """Test converting agent_id to PipelineStage"""
        # Brief interpreter
        stage = PipelineStage.from_agent_id("a01_brief_interpreter")
        assert stage == PipelineStage.BRIEF_INTERPRETATION

        # Sequential generator
        stage = PipelineStage.from_agent_id("a06_sequential_generator")
        assert stage == PipelineStage.SEQUENTIAL_GENERATION

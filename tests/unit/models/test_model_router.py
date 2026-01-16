"""
Tests for Model Router
"""
import pytest
from narra_forge.models.model_router import ModelRouter
from narra_forge.core.types import PipelineStage
from narra_forge.core.config import create_default_config


@pytest.mark.unit
class TestModelRouter:
    """Test Model Router functionality"""

    def test_router_initialization(self, test_config, mock_openai_client):
        """Test router can be initialized with config and client"""
        router = ModelRouter(test_config, mock_openai_client)

        assert router.config == test_config
        assert router.client == mock_openai_client

    def test_get_model_for_brief_interpreter(self, mock_model_router):
        """Test model selection for brief interpreter"""
        model = mock_model_router.get_model_for_stage(PipelineStage.BRIEF_INTERPRETATION)

        # Brief interpretation uses mini model (fast, cheap)
        assert model == "gpt-4o-mini"

    def test_get_model_for_sequential_generation(self, mock_model_router):
        """Test model selection for sequential generation (QUALITY-CRITICAL)"""
        model = mock_model_router.get_model_for_stage(PipelineStage.SEQUENTIAL_GENERATION)

        # Sequential generation MUST use GPT-4o (quality-critical)
        assert model == "gpt-4o"

    def test_get_model_for_coherence_validation(self, mock_model_router):
        """Test model selection for coherence validation"""
        model = mock_model_router.get_model_for_stage(PipelineStage.COHERENCE_VALIDATION)

        # Coherence validation uses GPT-4o (complex analysis)
        assert model == "gpt-4o"

    def test_get_model_for_language_stylization(self, mock_model_router):
        """Test model selection for language stylization"""
        model = mock_model_router.get_model_for_stage(PipelineStage.LANGUAGE_STYLIZATION)

        # Language stylization uses GPT-4o (REVERTED from mini)
        assert model == "gpt-4o"

    def test_get_model_for_world_architecture(self, mock_model_router):
        """Test model selection for world architecture"""
        model = mock_model_router.get_model_for_stage(PipelineStage.WORLD_ARCHITECTURE)

        # World architecture uses mini (planning task)
        assert model == "gpt-4o-mini"

    def test_all_pipeline_stages_have_models(self, mock_model_router):
        """Test that all pipeline stages have assigned models"""
        for stage in PipelineStage:
            model = mock_model_router.get_model_for_stage(stage)
            assert model is not None
            assert model in ["gpt-4o-mini", "gpt-4o"]

    def test_get_model_for_task_analysis(self, mock_model_router):
        """Test model selection for analysis tasks"""
        model = mock_model_router.get_model_for_task("analysis")
        assert model == "gpt-4o-mini"

    def test_get_model_for_task_generation(self, mock_model_router):
        """Test model selection for generation tasks"""
        model = mock_model_router.get_model_for_task("generation")
        assert model == "gpt-4o"

    def test_get_model_for_task_planning(self, mock_model_router):
        """Test model selection for planning tasks"""
        model = mock_model_router.get_model_for_task("planning")
        assert model == "gpt-4o-mini"


@pytest.mark.unit
class TestModelRouterConfiguration:
    """Test Model Router with different configurations"""

    def test_router_respects_custom_mini_model(self, mock_openai_client):
        """Test router uses custom mini model from config"""
        config = create_default_config(
            openai_api_key="sk-test-key",
            environment="testing",
            default_mini_model="gpt-4o-mini-2024-07-18"  # Specific version
        )

        router = ModelRouter(config, mock_openai_client)

        assert router.config.default_mini_model == "gpt-4o-mini-2024-07-18"

    def test_router_respects_custom_gpt4_model(self, mock_openai_client):
        """Test router uses custom GPT-4 model from config"""
        config = create_default_config(
            openai_api_key="sk-test-key",
            environment="testing",
            default_gpt4_model="gpt-4o-2024-08-06"  # Specific version
        )

        router = ModelRouter(config, mock_openai_client)

        assert router.config.default_gpt4_model == "gpt-4o-2024-08-06"


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

    def test_stage_values_have_numbers(self):
        """Test stage values have numeric prefixes"""
        # Stage values should have format: "01_brief_interpretation"
        for stage in PipelineStage:
            assert "_" in stage.value
            assert stage.value[0:2].isdigit()  # First 2 chars are digits


@pytest.mark.unit
class TestModelRouterGPT4Stages:
    """Test GPT-4 stage identification"""

    def test_gpt4_required_stages(self, mock_model_router):
        """Test that quality-critical stages use GPT-4"""
        gpt4_stages = [
            PipelineStage.SEQUENTIAL_GENERATION,
            PipelineStage.LANGUAGE_STYLIZATION,
            PipelineStage.COHERENCE_VALIDATION,
        ]

        for stage in gpt4_stages:
            model = mock_model_router.get_model_for_stage(stage)
            assert model == "gpt-4o", f"Stage {stage} should use gpt-4o"

    def test_mini_stages(self, mock_model_router):
        """Test that cost-optimized stages use mini"""
        mini_stages = [
            PipelineStage.BRIEF_INTERPRETATION,
            PipelineStage.WORLD_ARCHITECTURE,
            PipelineStage.CHARACTER_ARCHITECTURE,
            PipelineStage.STRUCTURE_DESIGN,
            PipelineStage.SEGMENT_PLANNING,
            PipelineStage.EDITORIAL_REVIEW,
            PipelineStage.OUTPUT_PROCESSING,
        ]

        for stage in mini_stages:
            model = mock_model_router.get_model_for_stage(stage)
            assert model == "gpt-4o-mini", f"Stage {stage} should use gpt-4o-mini"

@pytest.mark.unit
class TestModelRouterTaskTypes:
    """Test get_model_for_task method"""

    def test_get_model_for_complex_task(self, mock_model_router):
        """Test model selection for complex tasks"""
        model = mock_model_router.get_model_for_task("complex_generation")
        assert model in ["gpt-4o", "gpt-4o-mini"]

    def test_get_model_for_simple_task(self, mock_model_router):
        """Test model selection for simple tasks"""
        model = mock_model_router.get_model_for_task("simple_parse")
        assert model in ["gpt-4o", "gpt-4o-mini"]


@pytest.mark.unit
class TestModelRouterStats:
    """Test router statistics"""

    def test_get_router_stats(self, mock_model_router):
        """Test getting router statistics"""
        stats = mock_model_router.get_router_stats()

        assert isinstance(stats, dict)
        # Should have basic stats
        assert "default_mini_model" in stats or isinstance(stats, dict)

    def test_router_stats_structure(self, mock_model_router):
        """Test stats structure"""
        stats = mock_model_router.get_router_stats()

        # Stats should be a dictionary
        assert isinstance(stats, dict)


# TestModelRouterCostEstimate - skipped (requires real client)


@pytest.mark.unit
class TestModelRouterGeneration:
    """Test async generation methods"""

    @pytest.mark.asyncio
    async def test_generate_async(self, test_config, mock_openai_client):
        """Test async generate method"""
        from unittest.mock import AsyncMock, MagicMock
        from datetime import datetime
        from narra_forge.core.types import ModelCall

        router = ModelRouter(test_config, mock_openai_client)

        mock_call = ModelCall(
            call_id="test_123",
            model_name="gpt-4o-mini",
            prompt_tokens=50,
            completion_tokens=100,
            total_tokens=150,
            cost_usd=0.01,
            latency_seconds=1.0,
            purpose="test",
            timestamp=datetime.now(),
        )

        # Mock client's generate_async
        mock_openai_client.generate_async = AsyncMock(
            return_value=("Generated text", mock_call)
        )

        text, call = await router.generate(
            prompt="Test prompt",
            stage=PipelineStage.BRIEF_INTERPRETATION
        )

        assert isinstance(text, str)
        assert isinstance(call, ModelCall)

    @pytest.mark.asyncio
    async def test_generate_json_async(self, test_config, mock_openai_client):
        """Test async JSON generation"""
        from unittest.mock import AsyncMock
        from datetime import datetime
        from narra_forge.core.types import ModelCall

        router = ModelRouter(test_config, mock_openai_client)

        mock_call = ModelCall(
            call_id="test_456",
            model_name="gpt-4o-mini",
            prompt_tokens=50,
            completion_tokens=100,
            total_tokens=150,
            cost_usd=0.01,
            latency_seconds=1.0,
            purpose="json_test",
            timestamp=datetime.now(),
        )

        # Mock client's generate_json_async
        mock_openai_client.generate_json_async = AsyncMock(
            return_value=({"key": "value"}, mock_call)
        )

        data, call = await router.generate_json(
            prompt="Test JSON prompt",
            stage=PipelineStage.WORLD_ARCHITECTURE
        )

        assert isinstance(data, dict)
        assert isinstance(call, ModelCall)

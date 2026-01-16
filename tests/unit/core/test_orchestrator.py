"""
Tests for BatchOrchestrator

Focus on initialization, configuration, and component management.
Full pipeline tests are in integration/e2e tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from narra_forge.core.orchestrator import BatchOrchestrator
from narra_forge.core.types import ProductionBrief, ProductionType, Genre, JobStatus


@pytest.mark.unit
class TestBatchOrchestratorInit:
    """Test BatchOrchestrator initialization"""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization_minimal(self, test_config):
        """Test orchestrator can be initialized with just config"""
        orchestrator = BatchOrchestrator(config=test_config)

        assert orchestrator.config == test_config
        assert orchestrator.client is not None
        assert orchestrator.router is not None
        assert orchestrator.memory is None  # Lazy init
        assert not orchestrator._memory_initialized

    @pytest.mark.asyncio
    async def test_orchestrator_initialization_with_memory(self, test_config, memory_system):
        """Test orchestrator with provided memory"""
        orchestrator = BatchOrchestrator(
            config=test_config,
            memory=memory_system
        )

        assert orchestrator.memory == memory_system

    @pytest.mark.asyncio
    async def test_orchestrator_initialization_with_client(self, test_config, mock_openai_client):
        """Test orchestrator with provided client"""
        orchestrator = BatchOrchestrator(
            config=test_config,
            client=mock_openai_client
        )

        assert orchestrator.client == mock_openai_client

    @pytest.mark.asyncio
    async def test_orchestrator_initialization_with_router(
        self, test_config, mock_openai_client, mock_model_router
    ):
        """Test orchestrator with provided router"""
        orchestrator = BatchOrchestrator(
            config=test_config,
            client=mock_openai_client,
            router=mock_model_router
        )

        assert orchestrator.router == mock_model_router


@pytest.mark.unit
class TestBatchOrchestratorMemoryInit:
    """Test memory initialization"""

    @pytest.mark.asyncio
    async def test_ensure_memory_initialized_creates_memory(self, test_config):
        """Test that _ensure_memory_initialized creates memory if None"""
        orchestrator = BatchOrchestrator(config=test_config)

        assert orchestrator.memory is None
        assert not orchestrator._memory_initialized

        await orchestrator._ensure_memory_initialized()

        assert orchestrator.memory is not None
        assert orchestrator._memory_initialized

    @pytest.mark.asyncio
    async def test_ensure_memory_initialized_idempotent(self, test_config, memory_system):
        """Test that _ensure_memory_initialized is idempotent"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        # Initialize once
        await orchestrator._ensure_memory_initialized()
        memory_ref = orchestrator.memory

        # Call again
        await orchestrator._ensure_memory_initialized()

        # Should be same memory instance
        assert orchestrator.memory is memory_ref

    @pytest.mark.asyncio
    async def test_ensure_memory_initialized_with_existing_memory(
        self, test_config, memory_system
    ):
        """Test initialization with already provided memory"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        await orchestrator._ensure_memory_initialized()

        assert orchestrator.memory == memory_system
        assert orchestrator._memory_initialized


@pytest.mark.unit
class TestBatchOrchestratorConfiguration:
    """Test orchestrator configuration"""

    def test_orchestrator_uses_config_settings(self, test_config):
        """Test that orchestrator respects config settings"""
        test_config.max_cost_per_job = 10.0
        test_config.min_coherence_score = 0.90

        orchestrator = BatchOrchestrator(config=test_config)

        assert orchestrator.config.max_cost_per_job == 10.0
        assert orchestrator.config.min_coherence_score == 0.90

    def test_orchestrator_client_uses_config_api_key(self, test_config):
        """Test that client uses API key from config"""
        orchestrator = BatchOrchestrator(config=test_config)

        # Client should have been initialized with config
        assert orchestrator.client.config == test_config

    def test_orchestrator_router_uses_config(self, test_config):
        """Test that router uses config"""
        orchestrator = BatchOrchestrator(config=test_config)

        assert orchestrator.router.config == test_config


@pytest.mark.unit
class TestBatchOrchestratorJobManagement:
    """Test job creation and management"""

    @pytest.mark.asyncio
    async def test_produce_narrative_creates_job(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test that produce_narrative creates a job"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        # Mock the actual pipeline execution
        with patch.object(orchestrator, '_run_pipeline', new_callable=AsyncMock) as mock_pipeline:
            mock_pipeline.return_value = MagicMock(
                narrative_text="Test narrative",
                job_id="job_123"
            )

            # Mock _save_job to avoid DB operations
            with patch.object(orchestrator, '_save_job', new_callable=AsyncMock):
                with patch('narra_forge.core.orchestrator.console'):
                    result = await orchestrator.produce_narrative(
                        brief=sample_production_brief,
                        show_progress=False
                    )

            # Verify pipeline was called
            mock_pipeline.assert_called_once()

    @pytest.mark.asyncio
    async def test_produce_narrative_initializes_memory(
        self, test_config, sample_production_brief
    ):
        """Test that produce_narrative initializes memory"""
        orchestrator = BatchOrchestrator(config=test_config)

        assert orchestrator.memory is None

        # Mock the pipeline to avoid full execution
        with patch.object(orchestrator, '_run_pipeline', new_callable=AsyncMock) as mock_pipeline:
            mock_pipeline.return_value = MagicMock(narrative_text="Test", word_count=1000)

            with patch.object(orchestrator, '_save_job', new_callable=AsyncMock):
                with patch('narra_forge.core.orchestrator.console'):
                    await orchestrator.produce_narrative(
                        brief=sample_production_brief,
                        show_progress=False
                    )

        # Memory should be initialized
        assert orchestrator.memory is not None
        assert orchestrator._memory_initialized


@pytest.mark.unit
class TestBatchOrchestratorErrorHandling:
    """Test error handling in orchestrator"""

    @pytest.mark.asyncio
    async def test_produce_narrative_handles_pipeline_error(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test that errors in pipeline are properly handled"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        # Mock pipeline to raise error
        with patch.object(orchestrator, '_run_pipeline', new_callable=AsyncMock) as mock_pipeline:
            mock_pipeline.side_effect = ValueError("Pipeline error")

            with patch.object(orchestrator, '_save_job', new_callable=AsyncMock):
                with patch('narra_forge.core.orchestrator.console'):
                    with pytest.raises(ValueError, match="Pipeline error"):
                        await orchestrator.produce_narrative(
                            brief=sample_production_brief,
                            show_progress=False
                        )


@pytest.mark.unit
class TestBatchOrchestratorProgressDisplay:
    """Test progress display functionality"""

    @pytest.mark.asyncio
    async def test_produce_narrative_with_progress(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test produce_narrative with progress display enabled"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        with patch.object(orchestrator, '_run_pipeline', new_callable=AsyncMock) as mock_pipeline:
            mock_pipeline.return_value = MagicMock(narrative_text="Test", word_count=1000)

            with patch.object(orchestrator, '_save_job', new_callable=AsyncMock):
                with patch.object(orchestrator, '_print_summary'):
                    with patch('narra_forge.core.orchestrator.console') as mock_console:
                        await orchestrator.produce_narrative(
                            brief=sample_production_brief,
                            show_progress=True
                        )

                        # Verify console was used for progress
                        assert mock_console.print.called

    @pytest.mark.asyncio
    async def test_produce_narrative_without_progress(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test produce_narrative with progress display disabled"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        with patch.object(orchestrator, '_run_pipeline', new_callable=AsyncMock) as mock_pipeline:
            mock_pipeline.return_value = MagicMock(narrative_text="Test", word_count=1000)

            with patch.object(orchestrator, '_save_job', new_callable=AsyncMock):
                with patch('narra_forge.core.orchestrator.console') as mock_console:
                    await orchestrator.produce_narrative(
                        brief=sample_production_brief,
                        show_progress=False
                    )

                    # Console might still be used for errors/warnings, but less
                    # Just verify no exception was raised


@pytest.mark.unit
class TestBatchOrchestratorComponentIntegration:
    """Test integration between orchestrator components"""

    def test_orchestrator_client_and_router_connected(self, test_config):
        """Test that client and router are properly connected"""
        orchestrator = BatchOrchestrator(config=test_config)

        # Router should use the same client
        assert orchestrator.router.client == orchestrator.client

    def test_orchestrator_all_components_use_same_config(self, test_config):
        """Test that all components share the same config"""
        orchestrator = BatchOrchestrator(config=test_config)

        assert orchestrator.client.config == test_config
        assert orchestrator.router.config == test_config

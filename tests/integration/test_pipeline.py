"""
Integration tests for the full production pipeline
"""
import pytest

from narra_forge.core.orchestrator import BatchOrchestrator
from narra_forge.core.types import ProductionBrief, ProductionType, Genre


@pytest.mark.integration
class TestBatchOrchestratorIntegration:
    """Test BatchOrchestrator integration"""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, test_config, memory_system):
        """Test orchestrator can be initialized with config and memory"""
        orchestrator = BatchOrchestrator(
            config=test_config,
            memory=memory_system
        )

        assert orchestrator.config == test_config
        assert orchestrator.memory == memory_system
        assert orchestrator.client is not None
        assert orchestrator.router is not None

    @pytest.mark.asyncio
    async def test_orchestrator_without_memory(self, test_config):
        """Test orchestrator can be initialized without providing memory"""
        orchestrator = BatchOrchestrator(config=test_config)

        assert orchestrator.config == test_config
        assert orchestrator.memory is None  # Lazy init
        assert orchestrator.client is not None
        assert orchestrator.router is not None

    @pytest.mark.asyncio
    async def test_orchestrator_memory_lazy_initialization(self, test_config):
        """Test that memory is initialized lazily when needed"""
        orchestrator = BatchOrchestrator(config=test_config)

        # Memory should be None initially
        assert orchestrator.memory is None
        assert not orchestrator._memory_initialized

        # Initialize memory
        await orchestrator._ensure_memory_initialized()

        # Memory should now be initialized
        assert orchestrator.memory is not None
        assert orchestrator._memory_initialized

    @pytest.mark.asyncio
    async def test_orchestrator_with_provided_components(
        self, test_config, memory_system, mock_openai_client, mock_model_router
    ):
        """Test orchestrator can use provided client and router"""
        orchestrator = BatchOrchestrator(
            config=test_config,
            memory=memory_system,
            client=mock_openai_client,
            router=mock_model_router
        )

        assert orchestrator.client == mock_openai_client
        assert orchestrator.router == mock_model_router


@pytest.mark.integration
class TestProductionBriefValidation:
    """Test ProductionBrief validation and usage"""

    def test_production_brief_creation(self):
        """Test creating a ProductionBrief"""
        brief = ProductionBrief(
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            inspiration="Test story about magic"
        )

        assert brief.production_type == ProductionType.SHORT_STORY
        assert brief.genre == Genre.FANTASY
        assert brief.inspiration == "Test story about magic"
        assert brief.brief_id.startswith("brief_")
        assert brief.created_at is not None

    def test_production_brief_with_world_id(self):
        """Test ProductionBrief with existing world reference"""
        brief = ProductionBrief(
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            world_id="world_existing_123"
        )

        assert brief.world_id == "world_existing_123"

    def test_production_brief_with_additional_params(self):
        """Test ProductionBrief with additional parameters"""
        brief = ProductionBrief(
            production_type=ProductionType.NOVELLA,
            genre=Genre.SCIFI,
            additional_params={
                "tone": "dark",
                "target_word_count": 15000,
                "themes": ["technology", "humanity"]
            }
        )

        assert brief.additional_params["tone"] == "dark"
        assert brief.additional_params["target_word_count"] == 15000
        assert "technology" in brief.additional_params["themes"]


@pytest.mark.integration
class TestMemorySystemIntegration:
    """Test memory system integration with orchestrator"""

    @pytest.mark.asyncio
    async def test_memory_persistence_between_orchestrators(self, test_config, temp_db_path, sample_world_dict):
        """Test that memory persists across orchestrator instances"""
        from narra_forge.memory import MemorySystem

        # Configure with same DB path
        test_config.db_path = temp_db_path

        # Create first orchestrator and initialize memory
        orchestrator1 = BatchOrchestrator(config=test_config)
        await orchestrator1._ensure_memory_initialized()

        # Save a world to memory using sample_world_dict fixture
        await orchestrator1.memory.structural.save_world(sample_world_dict)

        # Create second orchestrator with same config
        orchestrator2 = BatchOrchestrator(config=test_config)
        await orchestrator2._ensure_memory_initialized()

        # Retrieve world from second orchestrator
        retrieved = await orchestrator2.memory.structural.get_world(sample_world_dict["world_id"])

        assert retrieved is not None
        assert retrieved.name == sample_world_dict["name"]


@pytest.mark.integration
@pytest.mark.slow
class TestOrchestratorConfiguration:
    """Test orchestrator configuration options"""

    def test_orchestrator_respects_cost_limit(self, test_config):
        """Test that orchestrator respects max_cost_per_job setting"""
        test_config.max_cost_per_job = 5.0

        orchestrator = BatchOrchestrator(config=test_config)

        assert orchestrator.config.max_cost_per_job == 5.0

    def test_orchestrator_respects_coherence_threshold(self, test_config):
        """Test that orchestrator respects min_coherence_score setting"""
        test_config.min_coherence_score = 0.90

        orchestrator = BatchOrchestrator(config=test_config)

        assert orchestrator.config.min_coherence_score == 0.90

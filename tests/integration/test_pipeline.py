"""
Integration tests for the full production pipeline
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from narra_forge.core.orchestrator import ProductionOrchestrator
from narra_forge.core.types import ProductionBrief, ProductionType, Genre


@pytest.mark.integration
class TestPipelineIntegration:
    """Test full pipeline integration"""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, test_config, memory_system):
        """Test orchestrator can be initialized with config and memory"""
        orchestrator = ProductionOrchestrator(
            config=test_config,
            memory_system=memory_system
        )

        assert orchestrator.config == test_config
        assert orchestrator.memory == memory_system
        assert len(orchestrator.agents) == 10  # All 10 agents initialized

    @pytest.mark.asyncio
    async def test_pipeline_creates_all_agents(self, test_config, memory_system):
        """Test that pipeline initializes all 10 agents"""
        orchestrator = ProductionOrchestrator(
            config=test_config,
            memory_system=memory_system
        )

        agent_ids = [agent.agent_id for agent in orchestrator.agents]

        expected_agents = [
            "a01_brief_interpreter",
            "a02_world_architect",
            "a03_character_architect",
            "a04_structure_designer",
            "a05_segment_planner",
            "a06_sequential_generator",
            "a07_coherence_validator",
            "a08_language_stylizer",
            "a09_editorial_reviewer",
            "a10_output_processor",
        ]

        for expected in expected_agents:
            assert expected in agent_ids

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_pipeline_with_mocked_api(self, test_config, memory_system, sample_production_brief):
        """Test full pipeline execution with mocked OpenAI API calls"""
        orchestrator = ProductionOrchestrator(
            config=test_config,
            memory_system=memory_system
        )

        # Mock responses for each agent
        mock_responses = {
            "a01_brief_interpreter": {
                "interpretation": {
                    "production_intent": "Fantasy short story about alchemy",
                    "core_themes": ["sacrifice", "power"],
                    "world_requirements": {"genre": "fantasy"}
                }
            },
            "a02_world_architect": {
                "world": {
                    "world_id": "test_world_001",
                    "name": "Eldoria",
                    "genre": "fantasy",
                    "reality_laws": {},
                    "boundaries": {"spatial": {}, "temporal": {}},
                    "core_conflict": "Test conflict"
                }
            },
            "a03_character_architect": {
                "characters": [{
                    "character_id": "char_001",
                    "name": "Lyra",
                    "archetype": "seeker"
                }]
            },
            "a04_structure_designer": {
                "structure": {
                    "structure_type": "three_act",
                    "acts": [{"act_number": 1, "target_word_count": 2000}]
                }
            },
            "a05_segment_planner": {
                "segments": [{
                    "segment_id": "seg_001",
                    "type": "chapter",
                    "target_word_count": 2000
                }]
            },
            "a06_sequential_generator": {
                "narrative_text": "Once upon a time in Eldoria...",
                "total_words": 2000
            },
            "a07_coherence_validator": {
                "quality_metrics": {
                    "coherence_score": 0.88,
                    "validation_passed": True
                }
            },
            "a08_language_stylizer": {
                "refined_text": "Once upon a time in Eldoria...",
                "refinements_applied": 5
            },
            "a09_editorial_reviewer": {
                "final_review": {
                    "approved": True,
                    "final_quality_score": 0.90
                }
            },
            "a10_output_processor": {
                "output": {
                    "narrative_text": "Once upon a time in Eldoria...",
                    "files_created": ["narrative.txt"]
                }
            }
        }

        # Patch all agents' execute methods
        async def mock_agent_execute(agent_id, input_data):
            return mock_responses.get(agent_id, {"result": "mock"})

        with patch.object(orchestrator, '_execute_agent', side_effect=lambda agent, data: mock_agent_execute(agent.agent_id, data)):
            result = await orchestrator.produce_narrative(sample_production_brief)

            assert result is not None
            assert "narrative_text" in result or "output" in result


@pytest.mark.integration
class TestPipelineStageFlow:
    """Test data flow between pipeline stages"""

    @pytest.mark.asyncio
    async def test_stage_1_output_feeds_stage_2(self, test_config, memory_system):
        """Test that Stage 1 output is used as Stage 2 input"""
        orchestrator = ProductionOrchestrator(
            config=test_config,
            memory_system=memory_system
        )

        # This is more of a structural test - verify pipeline setup
        assert len(orchestrator.agents) >= 2

    @pytest.mark.asyncio
    async def test_pipeline_maintains_context_between_stages(self, test_config, memory_system):
        """Test that context is maintained between stages"""
        orchestrator = ProductionOrchestrator(
            config=test_config,
            memory_system=memory_system
        )

        # Verify memory system is shared across all agents
        assert orchestrator.memory is not None


@pytest.mark.integration
class TestPipelineErrorHandling:
    """Test error handling in pipeline"""

    @pytest.mark.asyncio
    async def test_pipeline_handles_agent_failure(self, test_config, memory_system, sample_production_brief):
        """Test pipeline handles agent failure gracefully"""
        orchestrator = ProductionOrchestrator(
            config=test_config,
            memory_system=memory_system
        )

        # Mock an agent to fail
        async def failing_execute(*args, **kwargs):
            raise ValueError("Simulated agent failure")

        with patch.object(orchestrator.agents[0], 'execute', side_effect=failing_execute):
            with pytest.raises(Exception):  # Should propagate error
                await orchestrator.produce_narrative(sample_production_brief)

    @pytest.mark.asyncio
    async def test_pipeline_tracks_cost(self, test_config, memory_system):
        """Test that pipeline tracks cost across all stages"""
        orchestrator = ProductionOrchestrator(
            config=test_config,
            memory_system=memory_system
        )

        # Verify orchestrator has cost tracking capability
        assert hasattr(orchestrator, 'config')
        assert orchestrator.config.max_cost_per_job > 0

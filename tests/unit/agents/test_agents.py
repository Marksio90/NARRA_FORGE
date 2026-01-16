"""
Tests for Agent system

Tests agent initialization, system prompts, and basic functionality.
Note: Full agent execution tests require integration testing with mocked OpenAI API.
"""
import pytest
from narra_forge.agents import (
    BriefInterpreterAgent,
    WorldArchitectAgent,
    CharacterArchitectAgent,
    StructureDesignerAgent,
    SegmentPlannerAgent,
    SequentialGeneratorAgent,
    CoherenceValidatorAgent,
    LanguageStylerAgent,
    EditorialReviewerAgent,
    OutputProcessorAgent,
)
from narra_forge.core.types import PipelineStage


@pytest.mark.unit
class TestAgentInitialization:
    """Test agent initialization"""

    @pytest.mark.asyncio
    async def test_brief_interpreter_initialization(self, test_config, memory_system, mock_model_router):
        """Test BriefInterpreterAgent can be initialized"""
        agent = BriefInterpreterAgent(
            config=test_config,
            memory=memory_system,
            router=mock_model_router
        )

        assert agent.config == test_config
        assert agent.memory == memory_system
        assert agent.router == mock_model_router
        assert agent.stage == PipelineStage.BRIEF_INTERPRETATION

    @pytest.mark.asyncio
    async def test_world_architect_initialization(self, test_config, memory_system, mock_model_router):
        """Test WorldArchitectAgent can be initialized"""
        agent = WorldArchitectAgent(
            config=test_config,
            memory=memory_system,
            router=mock_model_router
        )

        assert agent.stage == PipelineStage.WORLD_ARCHITECTURE

    @pytest.mark.asyncio
    async def test_character_architect_initialization(self, test_config, memory_system, mock_model_router):
        """Test CharacterArchitectAgent can be initialized"""
        agent = CharacterArchitectAgent(
            config=test_config,
            memory=memory_system,
            router=mock_model_router
        )

        assert agent.stage == PipelineStage.CHARACTER_ARCHITECTURE

    @pytest.mark.asyncio
    async def test_structure_designer_initialization(self, test_config, memory_system, mock_model_router):
        """Test StructureDesignerAgent can be initialized"""
        agent = StructureDesignerAgent(
            config=test_config,
            memory=memory_system,
            router=mock_model_router
        )

        assert agent.stage == PipelineStage.STRUCTURE_DESIGN

    @pytest.mark.asyncio
    async def test_segment_planner_initialization(self, test_config, memory_system, mock_model_router):
        """Test SegmentPlannerAgent can be initialized"""
        agent = SegmentPlannerAgent(
            config=test_config,
            memory=memory_system,
            router=mock_model_router
        )

        assert agent.stage == PipelineStage.SEGMENT_PLANNING

    @pytest.mark.asyncio
    async def test_sequential_generator_initialization(self, test_config, memory_system, mock_model_router):
        """Test SequentialGeneratorAgent can be initialized"""
        agent = SequentialGeneratorAgent(
            config=test_config,
            memory=memory_system,
            router=mock_model_router
        )

        assert agent.stage == PipelineStage.SEQUENTIAL_GENERATION

    @pytest.mark.asyncio
    async def test_coherence_validator_initialization(self, test_config, memory_system, mock_model_router):
        """Test CoherenceValidatorAgent can be initialized"""
        agent = CoherenceValidatorAgent(
            config=test_config,
            memory=memory_system,
            router=mock_model_router
        )

        assert agent.stage == PipelineStage.COHERENCE_VALIDATION

    @pytest.mark.asyncio
    async def test_language_stylizer_initialization(self, test_config, memory_system, mock_model_router):
        """Test LanguageStylerAgent can be initialized"""
        agent = LanguageStylerAgent(
            config=test_config,
            memory=memory_system,
            router=mock_model_router
        )

        assert agent.stage == PipelineStage.LANGUAGE_STYLIZATION

    @pytest.mark.asyncio
    async def test_editorial_reviewer_initialization(self, test_config, memory_system, mock_model_router):
        """Test EditorialReviewerAgent can be initialized"""
        agent = EditorialReviewerAgent(
            config=test_config,
            memory=memory_system,
            router=mock_model_router
        )

        assert agent.stage == PipelineStage.EDITORIAL_REVIEW

    @pytest.mark.asyncio
    async def test_output_processor_initialization(self, test_config, memory_system, mock_model_router):
        """Test OutputProcessorAgent can be initialized"""
        agent = OutputProcessorAgent(
            config=test_config,
            memory=memory_system,
            router=mock_model_router
        )

        assert agent.stage == PipelineStage.OUTPUT_PROCESSING


@pytest.mark.unit
class TestAgentSystemPrompts:
    """Test agent system prompts"""

    @pytest.mark.asyncio
    async def test_all_agents_have_system_prompts(self, test_config, memory_system, mock_model_router):
        """Test that all agents have non-empty system prompts"""
        agents = [
            BriefInterpreterAgent(test_config, memory_system, mock_model_router),
            WorldArchitectAgent(test_config, memory_system, mock_model_router),
            CharacterArchitectAgent(test_config, memory_system, mock_model_router),
            StructureDesignerAgent(test_config, memory_system, mock_model_router),
            SegmentPlannerAgent(test_config, memory_system, mock_model_router),
            SequentialGeneratorAgent(test_config, memory_system, mock_model_router),
            CoherenceValidatorAgent(test_config, memory_system, mock_model_router),
            LanguageStylerAgent(test_config, memory_system, mock_model_router),
            EditorialReviewerAgent(test_config, memory_system, mock_model_router),
            OutputProcessorAgent(test_config, memory_system, mock_model_router),
        ]

        for agent in agents:
            prompt = agent.get_system_prompt()
            assert prompt is not None
            assert len(prompt) > 100  # Non-trivial prompt
            assert isinstance(prompt, str)

    @pytest.mark.asyncio
    async def test_sequential_generator_has_quality_prompt(self, test_config, memory_system, mock_model_router):
        """Test that SequentialGenerator has quality-focused prompt"""
        agent = SequentialGeneratorAgent(test_config, memory_system, mock_model_router)
        prompt = agent.get_system_prompt()

        # Prompt should be substantial (bestseller-quality rewrite)
        assert len(prompt) > 500, "SequentialGenerator should have detailed prompt"

        # Quality-focused prompt (tested by length)

    @pytest.mark.asyncio
    async def test_coherence_validator_has_validation_prompt(self, test_config, memory_system, mock_model_router):
        """Test that CoherenceValidator has validation-focused prompt"""
        agent = CoherenceValidatorAgent(test_config, memory_system, mock_model_router)
        prompt = agent.get_system_prompt()

        # Validation-focused prompt (tested by length)
        assert len(prompt) > 100


@pytest.mark.unit
class TestAgentProperties:
    """Test agent properties and attributes"""

    @pytest.mark.asyncio
    async def test_agent_has_model_calls_list(self, test_config, memory_system, mock_model_router):
        """Test that agents track model calls"""
        agent = BriefInterpreterAgent(test_config, memory_system, mock_model_router)

        assert hasattr(agent, 'model_calls')
        assert isinstance(agent.model_calls, list)
        assert len(agent.model_calls) == 0  # Empty on init

    @pytest.mark.asyncio
    async def test_agent_has_warnings_list(self, test_config, memory_system, mock_model_router):
        """Test that agents can track warnings"""
        agent = BriefInterpreterAgent(test_config, memory_system, mock_model_router)

        assert hasattr(agent, 'warnings')
        assert isinstance(agent.warnings, list)

    @pytest.mark.asyncio
    async def test_agent_has_errors_list(self, test_config, memory_system, mock_model_router):
        """Test that agents can track errors"""
        agent = BriefInterpreterAgent(test_config, memory_system, mock_model_router)

        assert hasattr(agent, 'errors')
        assert isinstance(agent.errors, list)


@pytest.mark.unit
class TestAgentStageMapping:
    """Test agent to pipeline stage mapping"""

    @pytest.mark.asyncio
    async def test_all_agents_have_unique_stages(self, test_config, memory_system, mock_model_router):
        """Test that each agent maps to unique pipeline stage"""
        agents = [
            BriefInterpreterAgent(test_config, memory_system, mock_model_router),
            WorldArchitectAgent(test_config, memory_system, mock_model_router),
            CharacterArchitectAgent(test_config, memory_system, mock_model_router),
            StructureDesignerAgent(test_config, memory_system, mock_model_router),
            SegmentPlannerAgent(test_config, memory_system, mock_model_router),
            SequentialGeneratorAgent(test_config, memory_system, mock_model_router),
            CoherenceValidatorAgent(test_config, memory_system, mock_model_router),
            LanguageStylerAgent(test_config, memory_system, mock_model_router),
            EditorialReviewerAgent(test_config, memory_system, mock_model_router),
            OutputProcessorAgent(test_config, memory_system, mock_model_router),
        ]

        stages = [agent.stage for agent in agents]

        # All stages should be unique
        assert len(stages) == len(set(stages))

        # All stages should be PipelineStage enum values
        all_stages = list(PipelineStage)
        for stage in stages:
            assert stage in all_stages

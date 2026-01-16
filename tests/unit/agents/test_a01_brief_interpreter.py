"""
Tests for Brief Interpreter Agent (A01)
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from narra_forge.agents.a01_brief_interpreter import BriefInterpreterAgent
from narra_forge.core.types import ProductionBrief, ProductionType, Genre


@pytest.mark.unit
class TestBriefInterpreterAgent:
    """Test Brief Interpreter Agent"""

    def test_agent_initialization(self, test_config):
        """Test agent can be initialized"""
        agent = BriefInterpreterAgent(config=test_config)

        assert agent.agent_id == "a01_brief_interpreter"
        assert "gpt-4o" in agent.model_name
        assert len(agent.system_prompt) > 100  # Has substantial prompt

    @pytest.mark.asyncio
    async def test_execute_with_valid_brief(self, test_config, sample_production_brief):
        """Test execution with valid ProductionBrief"""
        agent = BriefInterpreterAgent(config=test_config)

        # Mock the OpenAI API call
        mock_response = {
            "production_intent": "Generate fantasy short story about alchemy",
            "core_themes": ["sacrifice", "power", "knowledge"],
            "narrative_constraints": {
                "tone": "dark",
                "pacing": "moderate",
                "complexity": "medium"
            },
            "world_requirements": {
                "genre": "fantasy",
                "magic_system": "alchemy",
                "setting_scale": "small"
            },
            "character_requirements": {
                "protagonist": {
                    "archetype": "seeker",
                    "arc": "loss_of_innocence"
                }
            },
            "success_criteria": {
                "word_count_range": [5000, 10000],
                "quality_threshold": 0.85
            }
        }

        with patch.object(agent, '_call_openai_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = json.dumps(mock_response)

            result = await agent.execute(input_data={"brief": sample_production_brief})

            assert "interpretation" in result
            assert "production_intent" in result["interpretation"]
            assert result["interpretation"]["production_intent"] == mock_response["production_intent"]

    @pytest.mark.asyncio
    async def test_system_prompt_includes_production_types(self, test_config):
        """Test that system prompt includes all production types"""
        agent = BriefInterpreterAgent(config=test_config)

        prompt = agent.system_prompt

        # Check that all production types are mentioned
        assert "short_story" in prompt.lower()
        assert "novella" in prompt.lower()
        assert "novel" in prompt.lower()

    @pytest.mark.asyncio
    async def test_system_prompt_includes_genres(self, test_config):
        """Test that system prompt includes genre information"""
        agent = BriefInterpreterAgent(config=test_config)

        prompt = agent.system_prompt

        # Check that genres are mentioned
        assert "fantasy" in prompt.lower() or "genre" in prompt.lower()


@pytest.mark.unit
class TestBriefInterpreterInputProcessing:
    """Test input processing in Brief Interpreter"""

    @pytest.mark.asyncio
    async def test_handles_dict_input(self, test_config):
        """Test agent handles dict input"""
        agent = BriefInterpreterAgent(config=test_config)

        mock_response = {"production_intent": "test"}

        with patch.object(agent, '_call_openai_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = json.dumps(mock_response)

            brief_dict = {
                "production_type": "short_story",
                "genre": "fantasy",
                "inspiration": "Test story"
            }

            result = await agent.execute(input_data={"brief": brief_dict})

            # Verify API was called with formatted input
            mock_call.assert_called_once()
            call_args = mock_call.call_args[0][0]
            assert "short_story" in str(call_args).lower()

    @pytest.mark.asyncio
    async def test_handles_production_brief_object(self, test_config, sample_production_brief):
        """Test agent handles ProductionBrief object"""
        agent = BriefInterpreterAgent(config=test_config)

        mock_response = {"production_intent": "test"}

        with patch.object(agent, '_call_openai_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = json.dumps(mock_response)

            result = await agent.execute(input_data={"brief": sample_production_brief})

            # Verify API was called
            mock_call.assert_called_once()
            assert result is not None

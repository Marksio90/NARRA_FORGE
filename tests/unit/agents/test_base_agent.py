"""
Tests for BaseAgent class
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.config import NarraForgeConfig


class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing"""

    async def _execute_generation(self, input_data: dict) -> dict:
        """Test implementation"""
        return {"result": "test_output", "content": "Generated content"}


@pytest.mark.unit
class TestBaseAgent:
    """Test BaseAgent functionality"""

    def test_agent_initialization(self, test_config):
        """Test agent can be initialized"""
        agent = ConcreteAgent(
            config=test_config,
            agent_id="test_agent",
            model_name="gpt-4o-mini",
            system_prompt="Test prompt"
        )

        assert agent.agent_id == "test_agent"
        assert agent.model_name == "gpt-4o-mini"
        assert agent.system_prompt == "Test prompt"
        assert agent.max_retries == 3

    def test_agent_with_custom_retries(self, test_config):
        """Test agent with custom retry count"""
        agent = ConcreteAgent(
            config=test_config,
            agent_id="test_agent",
            model_name="gpt-4o-mini",
            system_prompt="Test prompt",
            max_retries=5
        )

        assert agent.max_retries == 5

    @pytest.mark.asyncio
    async def test_execute_returns_result(self, test_config):
        """Test execute method returns result from _execute_generation"""
        agent = ConcreteAgent(
            config=test_config,
            agent_id="test_agent",
            model_name="gpt-4o-mini",
            system_prompt="Test prompt"
        )

        result = await agent.execute(input_data={"test": "input"})

        assert result["result"] == "test_output"
        assert result["content"] == "Generated content"

    @pytest.mark.asyncio
    async def test_agent_tracks_execution_time(self, test_config):
        """Test that agent tracks execution metrics"""
        agent = ConcreteAgent(
            config=test_config,
            agent_id="test_agent",
            model_name="gpt-4o-mini",
            system_prompt="Test prompt"
        )

        with patch('time.time', side_effect=[1000.0, 1005.0]):
            result = await agent.execute(input_data={})

        # Execution should have taken ~5 seconds in mock
        assert result is not None

    @pytest.mark.asyncio
    async def test_format_messages_basic(self, test_config):
        """Test message formatting for API"""
        agent = ConcreteAgent(
            config=test_config,
            agent_id="test_agent",
            model_name="gpt-4o-mini",
            system_prompt="Test system prompt"
        )

        messages = agent._format_messages("User input text")

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Test system prompt"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "User input text"

    @pytest.mark.asyncio
    async def test_format_messages_with_examples(self, test_config):
        """Test message formatting with few-shot examples"""
        agent = ConcreteAgent(
            config=test_config,
            agent_id="test_agent",
            model_name="gpt-4o-mini",
            system_prompt="Test system prompt"
        )

        examples = [
            {"role": "user", "content": "Example input"},
            {"role": "assistant", "content": "Example output"}
        ]

        messages = agent._format_messages("User input", examples=examples)

        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Example input"
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "Example output"
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "User input"


@pytest.mark.unit
class TestAgentErrorHandling:
    """Test error handling in BaseAgent"""

    @pytest.mark.asyncio
    async def test_agent_handles_generation_error(self, test_config):
        """Test agent handles errors in _execute_generation"""

        class FailingAgent(BaseAgent):
            async def _execute_generation(self, input_data: dict) -> dict:
                raise ValueError("Test error")

        agent = FailingAgent(
            config=test_config,
            agent_id="failing_agent",
            model_name="gpt-4o-mini",
            system_prompt="Test prompt",
            max_retries=1
        )

        with pytest.raises(ValueError, match="Test error"):
            await agent.execute(input_data={})

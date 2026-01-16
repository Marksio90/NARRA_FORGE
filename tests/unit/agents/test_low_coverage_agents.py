"""
Dodatkowe testy agentów z niskim pokryciem
"""
import pytest
from unittest.mock import AsyncMock

from narra_forge.agents import (
    BriefInterpreterAgent,
    OutputProcessorAgent,
)
from narra_forge.core.types import ModelCall
from datetime import datetime


@pytest.fixture
def mock_model_call():
    """Mock ModelCall"""
    return ModelCall(
        call_id="test_123",
        model_name="gpt-4o-mini",
        prompt_tokens=100,
        completion_tokens=200,
        total_tokens=300,
        cost_usd=0.01,
        latency_seconds=1.0,
        purpose="test",
        timestamp=datetime.now(),
    )


@pytest.mark.unit
class TestBriefInterpreterExecution:
    """Test BriefInterpreterAgent"""

    @pytest.mark.asyncio
    async def test_execute_success(
        self, test_config, memory_system, mock_model_router, mock_model_call, sample_production_brief
    ):
        """Test pomyślnej interpretacji briefu"""
        agent = BriefInterpreterAgent(test_config, memory_system, mock_model_router)

        interpretation = {
            "genre": "FANTASY",
            "target_length": "SHORT_STORY",
            "key_themes": ["magic", "adventure"],
            "world_requirements": {"magic": True},
        }

        from unittest.mock import patch
        with patch.object(
            mock_model_router, "generate_json", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = (interpretation, mock_model_call)

            context = {"brief": sample_production_brief}

            result = await agent.execute(context)

        assert result.success is True
        assert "analyzed_brief" in result.data


@pytest.mark.unit
class TestOutputProcessorExecution:
    """Test OutputProcessorAgent"""

    @pytest.mark.asyncio
    async def test_execute_success(
        self, test_config, memory_system, mock_model_router
    ):
        """Test przetwarzania output"""
        agent = OutputProcessorAgent(test_config, memory_system, mock_model_router)

        context = {
            "narrative_text": "Test narrative",
            "final_text": "Final text",
            "coherence_validation": {"passed": True, "coherence_score": 0.9},
        }

        result = await agent.execute(context)

        assert result.success is True
        assert "output" in result.data or "files_created" in result.data

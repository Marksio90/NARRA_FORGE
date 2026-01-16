"""
Tests for OpenAI Client
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import time

from narra_forge.models.openai_client import OpenAIClient
from narra_forge.core.config import create_default_config


@pytest.mark.unit
class TestOpenAIClientInitialization:
    """Test OpenAI client initialization"""

    def test_client_initialization(self, test_config):
        """Test client can be initialized with config"""
        client = OpenAIClient(test_config)

        assert client.config == test_config
        assert client.client is not None
        assert client.async_client is not None

    def test_client_has_pricing_info(self, test_config):
        """Test client has pricing information"""
        client = OpenAIClient(test_config)

        assert "gpt-4o-mini" in client.PRICING
        assert "gpt-4o" in client.PRICING
        assert "prompt" in client.PRICING["gpt-4o-mini"]
        assert "completion" in client.PRICING["gpt-4o-mini"]

    def test_client_initializes_rate_limit_state(self, test_config):
        """Test client initializes rate limiting state"""
        client = OpenAIClient(test_config)

        assert isinstance(client._mini_calls, list)
        assert isinstance(client._mini_tokens, list)
        assert isinstance(client._gpt4_calls, list)
        assert isinstance(client._gpt4_tokens, list)


@pytest.mark.unit
class TestTokenCounting:
    """Test token counting functionality"""

    def test_count_tokens_simple(self, test_config):
        """Test counting tokens in simple text"""
        client = OpenAIClient(test_config)

        text = "Hello, world!"
        tokens = client.count_tokens(text, "gpt-4o-mini")

        assert tokens > 0
        assert isinstance(tokens, int)

    def test_count_tokens_empty(self, test_config):
        """Test counting tokens in empty string"""
        client = OpenAIClient(test_config)

        tokens = client.count_tokens("", "gpt-4o-mini")

        assert tokens == 0

    def test_count_tokens_long_text(self, test_config):
        """Test counting tokens in longer text"""
        client = OpenAIClient(test_config)

        text = " ".join(["word"] * 100)
        tokens = client.count_tokens(text, "gpt-4o")

        assert tokens > 50  # Should be at least 50 tokens
        assert tokens < 200  # But less than 200

    def test_count_tokens_different_models(self, test_config):
        """Test token counting works for different models"""
        client = OpenAIClient(test_config)

        text = "Testing token counting"

        tokens_mini = client.count_tokens(text, "gpt-4o-mini")
        tokens_gpt4 = client.count_tokens(text, "gpt-4o")

        # Both should return valid token counts
        assert tokens_mini > 0
        assert tokens_gpt4 > 0


@pytest.mark.unit
class TestCostCalculation:
    """Test cost calculation functionality"""

    def test_calculate_cost_mini(self, test_config):
        """Test cost calculation for gpt-4o-mini"""
        client = OpenAIClient(test_config)

        cost = client.calculate_cost(
            model="gpt-4o-mini",
            prompt_tokens=1000,
            completion_tokens=500
        )

        # gpt-4o-mini: $0.15/1M input, $0.60/1M output
        expected = (1000 * 0.00015/1000) + (500 * 0.0006/1000)
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_gpt4(self, test_config):
        """Test cost calculation for gpt-4o"""
        client = OpenAIClient(test_config)

        cost = client.calculate_cost(
            model="gpt-4o",
            prompt_tokens=1000,
            completion_tokens=500
        )

        # gpt-4o: $2.50/1M input, $10.00/1M output
        expected = (1000 * 0.0025/1000) + (500 * 0.01/1000)
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_zero_tokens(self, test_config):
        """Test cost calculation with zero tokens"""
        client = OpenAIClient(test_config)

        cost = client.calculate_cost(
            model="gpt-4o-mini",
            prompt_tokens=0,
            completion_tokens=0
        )

        assert cost == 0.0

    def test_calculate_cost_unknown_model(self, test_config):
        """Test cost calculation for unknown model (should use gpt-4o pricing)"""
        client = OpenAIClient(test_config)

        cost = client.calculate_cost(
            model="unknown-model",
            prompt_tokens=1000,
            completion_tokens=500
        )

        # Should default to gpt-4o pricing
        expected_gpt4 = client.calculate_cost("gpt-4o", 1000, 500)
        assert cost == expected_gpt4


@pytest.mark.unit
class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_mini_rpm(self, test_config):
        """Test RPM rate limiting for mini"""
        test_config.mini_rpm_limit = 5  # Very low for testing
        client = OpenAIClient(test_config)

        # Should allow first 5 calls
        for i in range(5):
            client._check_rate_limit("gpt-4o-mini", 100)

        # 6th call should fail
        with pytest.raises(ValueError, match="Rate limit.*RPM"):
            client._check_rate_limit("gpt-4o-mini", 100)

    def test_rate_limit_mini_tpm(self, test_config):
        """Test TPM rate limiting for mini"""
        test_config.mini_tpm_limit = 1000  # Low limit for testing
        client = OpenAIClient(test_config)

        # Should allow until token limit
        client._check_rate_limit("gpt-4o-mini", 900)

        # Next call would exceed TPM limit
        with pytest.raises(ValueError, match="Rate limit.*TPM"):
            client._check_rate_limit("gpt-4o-mini", 200)

    def test_rate_limit_gpt4_rpm(self, test_config):
        """Test RPM rate limiting for gpt-4o"""
        test_config.gpt4_rpm_limit = 3  # Very low for testing
        client = OpenAIClient(test_config)

        # Should allow first 3 calls
        for i in range(3):
            client._check_rate_limit("gpt-4o", 100)

        # 4th call should fail
        with pytest.raises(ValueError, match="Rate limit.*RPM"):
            client._check_rate_limit("gpt-4o", 100)

    def test_rate_limit_resets_after_minute(self, test_config):
        """Test that rate limits reset after 1 minute"""
        test_config.mini_rpm_limit = 2
        client = OpenAIClient(test_config)

        # Make 2 calls
        client._check_rate_limit("gpt-4o-mini", 100)
        client._check_rate_limit("gpt-4o-mini", 100)

        # Mock time to be 61 seconds later
        with patch('time.time', return_value=time.time() + 61):
            # Should allow new calls after time window
            client._check_rate_limit("gpt-4o-mini", 100)


@pytest.mark.unit
class TestGenerateMethodMocked:
    """Test generate method with mocked OpenAI API"""

    def test_generate_with_mocked_response(self, test_config):
        """Test generate method with mocked OpenAI response"""
        client = OpenAIClient(test_config)

        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Generated text response"))
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=50,
            completion_tokens=20,
            total_tokens=70
        )

        with patch.object(client.client.chat.completions, 'create', return_value=mock_response):
            text, model_call = client.generate(
                prompt="Test prompt",
                model="gpt-4o-mini",
                temperature=0.7
            )

        assert text == "Generated text response"
        assert model_call.model_name == "gpt-4o-mini"
        assert model_call.prompt_tokens == 50
        assert model_call.completion_tokens == 20
        assert model_call.total_tokens == 70
        assert model_call.cost_usd > 0

    def test_generate_with_system_prompt(self, test_config):
        """Test generate with system prompt"""
        client = OpenAIClient(test_config)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_response.usage = MagicMock(prompt_tokens=30, completion_tokens=10, total_tokens=40)

        with patch.object(client.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            client.generate(
                prompt="User prompt",
                system_prompt="System instructions",
                model="gpt-4o-mini"
            )

            # Verify system prompt was included in messages
            call_args = mock_create.call_args
            messages = call_args.kwargs['messages']
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "System instructions"
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == "User prompt"

    @pytest.mark.asyncio
    async def test_generate_async_with_mocked_response(self, test_config):
        """Test async generate with mocked response"""
        client = OpenAIClient(test_config)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Async response"))]
        mock_response.usage = MagicMock(prompt_tokens=60, completion_tokens=30, total_tokens=90)

        with patch.object(client.async_client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
            text, model_call = await client.generate_async(
                prompt="Test async",
                model="gpt-4o"
            )

        assert text == "Async response"
        assert model_call.model_name == "gpt-4o"
        assert model_call.total_tokens == 90


@pytest.mark.unit
class TestJSONGeneration:
    """Test JSON generation functionality"""

    def test_generate_json_valid(self, test_config):
        """Test JSON generation with valid response"""
        client = OpenAIClient(test_config)

        json_text = '{"name": "Test", "value": 42}'
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json_text))]
        mock_response.usage = MagicMock(prompt_tokens=20, completion_tokens=10, total_tokens=30)

        with patch.object(client.client.chat.completions, 'create', return_value=mock_response):
            data, model_call = client.generate_json(
                prompt="Generate JSON",
                model="gpt-4o-mini"
            )

        assert data["name"] == "Test"
        assert data["value"] == 42
        assert model_call.purpose == "json_generation"

    def test_generate_json_invalid_raises_error(self, test_config):
        """Test JSON generation with invalid JSON raises error"""
        client = OpenAIClient(test_config)

        invalid_json = "Not valid JSON {{"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=invalid_json))]
        mock_response.usage = MagicMock(prompt_tokens=20, completion_tokens=10, total_tokens=30)

        with patch.object(client.client.chat.completions, 'create', return_value=mock_response):
            with pytest.raises(ValueError, match="Failed to parse JSON"):
                client.generate_json(prompt="Generate JSON", model="gpt-4o-mini")

    @pytest.mark.asyncio
    async def test_generate_json_async_valid(self, test_config):
        """Test async JSON generation"""
        client = OpenAIClient(test_config)

        json_text = '{"status": "success"}'
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json_text))]
        mock_response.usage = MagicMock(prompt_tokens=15, completion_tokens=5, total_tokens=20)

        with patch.object(client.async_client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
            data, model_call = await client.generate_json_async(
                prompt="Generate JSON async",
                model="gpt-4o"
            )

        assert data["status"] == "success"


@pytest.mark.unit
class TestUsageStatistics:
    """Test usage statistics tracking"""

    def test_get_stats_empty(self, test_config):
        """Test stats when no calls made"""
        client = OpenAIClient(test_config)

        stats = client.get_stats()

        assert stats["mini"]["calls_last_minute"] == 0
        assert stats["mini"]["tokens_last_minute"] == 0
        assert stats["gpt4"]["calls_last_minute"] == 0
        assert stats["gpt4"]["tokens_last_minute"] == 0

    def test_get_stats_after_calls(self, test_config):
        """Test stats after making calls"""
        client = OpenAIClient(test_config)

        # Make some calls (bypassing actual API)
        client._check_rate_limit("gpt-4o-mini", 100)
        client._check_rate_limit("gpt-4o-mini", 150)
        client._check_rate_limit("gpt-4o", 200)

        stats = client.get_stats()

        assert stats["mini"]["calls_last_minute"] == 2
        assert stats["mini"]["tokens_last_minute"] == 250
        assert stats["gpt4"]["calls_last_minute"] == 1
        assert stats["gpt4"]["tokens_last_minute"] == 200

    def test_get_stats_includes_limits(self, test_config):
        """Test that stats include configured limits"""
        test_config.mini_rpm_limit = 100
        test_config.mini_tpm_limit = 50000
        test_config.gpt4_rpm_limit = 50
        test_config.gpt4_tpm_limit = 30000

        client = OpenAIClient(test_config)
        stats = client.get_stats()

        assert stats["mini"]["rpm_limit"] == 100
        assert stats["mini"]["tpm_limit"] == 50000
        assert stats["gpt4"]["rpm_limit"] == 50
        assert stats["gpt4"]["tpm_limit"] == 30000

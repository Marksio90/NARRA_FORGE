"""
Testy dla retry logic i error handling
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from openai import RateLimitError, APITimeoutError, APIConnectionError, APIError

from narra_forge.utils.retry import (
    TransientError,
    PermanentError,
    categorize_openai_error,
    retry_openai_call,
    CircuitBreaker,
    CircuitBreakerOpenError,
)


# Custom test exceptions that properly inherit from OpenAI types
class MockRateLimitError(RateLimitError):
    """Mock RateLimitError for testing"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message


class MockAPITimeoutError(APITimeoutError):
    """Mock APITimeoutError for testing"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message


class MockAPIConnectionError(APIConnectionError):
    """Mock APIConnectionError for testing"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message


class MockAPIError(APIError):
    """Mock APIError for testing"""
    def __init__(self, message, status_code=None):
        self.message = message
        if status_code:
            self.status_code = status_code
    def __str__(self):
        return self.message


@pytest.mark.unit
class TestErrorCategorization:
    """Test kategoryzacji błędów"""

    def test_categorize_rate_limit_as_transient(self):
        """Test że RateLimitError jest transient"""
        error = MockRateLimitError("Rate limit exceeded")
        categorized = categorize_openai_error(error)

        assert isinstance(categorized, TransientError)
        assert "Rate limit exceeded" in str(categorized)

    def test_categorize_timeout_as_transient(self):
        """Test że APITimeoutError jest transient"""
        error = MockAPITimeoutError("Request timeout")
        categorized = categorize_openai_error(error)

        assert isinstance(categorized, TransientError)

    def test_categorize_connection_error_as_transient(self):
        """Test że APIConnectionError jest transient"""
        error = MockAPIConnectionError("Connection failed")
        categorized = categorize_openai_error(error)

        assert isinstance(categorized, TransientError)

    def test_categorize_5xx_error_as_transient(self):
        """Test że 5xx APIError jest transient"""
        error = MockAPIError("Server error", status_code=500)
        categorized = categorize_openai_error(error)

        assert isinstance(categorized, TransientError)
        assert "500" in str(categorized)

    def test_categorize_4xx_error_as_permanent(self):
        """Test że 4xx APIError jest permanent"""
        error = MockAPIError("Bad request", status_code=400)
        categorized = categorize_openai_error(error)

        assert isinstance(categorized, PermanentError)

    def test_categorize_unknown_error_as_permanent(self):
        """Test że nieznane błędy są permanent"""
        error = ValueError("Some random error")
        categorized = categorize_openai_error(error)

        assert isinstance(categorized, PermanentError)
        assert "Unknown error" in str(categorized)


@pytest.mark.unit
class TestRetryOpenAICall:
    """Test retry decorator dla OpenAI calls"""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self):
        """Test że funkcja się wykonuje bez retry przy sukcesie"""
        call_count = 0

        @retry_openai_call(max_attempts=3)
        async def successful_call():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_call()

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_transient_error(self):
        """Test że retry działa na transient errors"""
        call_count = 0

        @retry_openai_call(max_attempts=3, max_wait_seconds=0.1)
        async def flaky_call():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise MockRateLimitError("Rate limit")
            return "success"

        result = await flaky_call()

        assert result == "success"
        assert call_count == 3  # 2 failures + 1 success

    @pytest.mark.asyncio
    async def test_no_retry_on_permanent_error(self):
        """Test że NIE retry na permanent errors"""
        call_count = 0

        @retry_openai_call(max_attempts=3)
        async def permanent_failure():
            nonlocal call_count
            call_count += 1
            raise MockAPIError("Invalid API key", status_code=401)

        with pytest.raises(PermanentError, match="Invalid API key"):
            await permanent_failure()

        # Powinno failować od razu bez retry
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test że po wyczerpaniu prób rzuca TransientError"""
        call_count = 0

        @retry_openai_call(max_attempts=2, max_wait_seconds=0.1)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise MockRateLimitError("Rate limit")

        with pytest.raises(TransientError, match="Rate limit"):
            await always_fails()

        # Powinna próbować max_attempts razy
        assert call_count == 2


@pytest.mark.unit
class TestCircuitBreaker:
    """Test circuit breaker pattern"""

    @pytest.mark.asyncio
    async def test_closed_state_allows_calls(self):
        """Test że CLOSED state pozwala na wywołania"""
        breaker = CircuitBreaker(failure_threshold=3)

        async with breaker:
            result = "success"

        assert breaker.state == "CLOSED"
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_opens_after_threshold_failures(self):
        """Test że przechodzi do OPEN po przekroczeniu threshold"""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)

        # 3 failures
        for _ in range(3):
            try:
                async with breaker:
                    raise ValueError("Test failure")
            except ValueError:
                pass

        assert breaker.state == "OPEN"
        assert breaker.failure_count == 3

    @pytest.mark.asyncio
    async def test_open_state_blocks_calls(self):
        """Test że OPEN state blokuje wywołania"""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=10.0)

        # Doprowadź do OPEN
        for _ in range(2):
            try:
                async with breaker:
                    raise ValueError("Failure")
            except ValueError:
                pass

        assert breaker.state == "OPEN"

        # Następne wywołanie powinno być zablokowane
        with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker is OPEN"):
            async with breaker:
                pass

    @pytest.mark.asyncio
    async def test_half_open_recovery(self):
        """Test przejścia przez HALF_OPEN z powrotem do CLOSED"""
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,  # Krótki timeout dla testu
            half_open_attempts=1,
        )

        # Doprowadź do OPEN
        for _ in range(2):
            try:
                async with breaker:
                    raise ValueError("Failure")
            except ValueError:
                pass

        assert breaker.state == "OPEN"

        # Poczekaj na recovery timeout
        await asyncio.sleep(0.15)

        # Następne wywołanie powinno przejść do HALF_OPEN
        async with breaker:
            result = "success"

        # Po sukcesie powinno wrócić do CLOSED
        assert breaker.state == "CLOSED"
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_half_open_failure_returns_to_open(self):
        """Test że failure w HALF_OPEN wraca do OPEN"""
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,
            half_open_attempts=1,
        )

        # Doprowadź do OPEN
        for _ in range(2):
            try:
                async with breaker:
                    raise ValueError("Failure")
            except ValueError:
                pass

        # Poczekaj na recovery
        await asyncio.sleep(0.15)

        # Failure w HALF_OPEN
        try:
            async with breaker:
                raise ValueError("Still failing")
        except ValueError:
            pass

        # Powinno wrócić do OPEN
        assert breaker.state == "OPEN"

    @pytest.mark.asyncio
    async def test_success_resets_failure_count_in_closed(self):
        """Test że sukces resetuje failure_count w CLOSED"""
        breaker = CircuitBreaker(failure_threshold=5)

        # Kilka failures (ale poniżej threshold)
        for _ in range(3):
            try:
                async with breaker:
                    raise ValueError("Failure")
            except ValueError:
                pass

        assert breaker.failure_count == 3
        assert breaker.state == "CLOSED"

        # Sukces powinien zresetować licznik
        async with breaker:
            pass

        assert breaker.failure_count == 0
        assert breaker.state == "CLOSED"


@pytest.mark.unit
class TestCircuitBreakerSync:
    """Test sync context manager support"""

    def test_sync_context_manager_success(self):
        """Test sync context manager przy sukcesie"""
        breaker = CircuitBreaker()

        with breaker:
            result = "success"

        assert breaker.state == "CLOSED"

    def test_sync_context_manager_failure(self):
        """Test sync context manager przy failure"""
        breaker = CircuitBreaker(failure_threshold=2)

        # First failure
        try:
            with breaker:
                raise ValueError("Test")
        except ValueError:
            pass

        assert breaker.failure_count == 1

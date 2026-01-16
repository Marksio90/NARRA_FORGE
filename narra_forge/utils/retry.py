"""
Retry logic and error handling utilities for NARRA_FORGE
"""
import asyncio
from typing import Callable, TypeVar, Any, Optional
from functools import wraps
import logging

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError,
)
from openai import (
    APIError,
    APIConnectionError,
    RateLimitError,
    APITimeoutError,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ═══════════════════════════════════════════
# ERROR CATEGORIZATION
# ═══════════════════════════════════════════

class TransientError(Exception):
    """
    Błąd przejściowy - warto retry

    Przykłady:
    - Rate limits
    - Timeouty
    - Network issues
    - 5xx server errors
    """
    pass


class PermanentError(Exception):
    """
    Błąd trwały - NIE warto retry

    Przykłady:
    - Invalid API key
    - Malformed request
    - 4xx client errors (poza 429)
    - Business logic errors
    """
    pass


def categorize_openai_error(error: Exception) -> Exception:
    """
    Kategoryzuje błędy OpenAI na transient vs permanent

    Args:
        error: Original exception

    Returns:
        TransientError lub PermanentError z oryginalnym błędem jako cause
    """
    # Transient - warto retry
    if isinstance(error, (
        RateLimitError,
        APITimeoutError,
        APIConnectionError,
    )):
        exc = TransientError(str(error))
        exc.__cause__ = error
        return exc

    # Permanent - nie warto retry
    if isinstance(error, APIError):
        # 5xx = transient, 4xx = permanent (except 429 which is RateLimitError)
        if hasattr(error, 'status_code'):
            if 500 <= error.status_code < 600:
                exc = TransientError(f"Server error {error.status_code}: {error}")
                exc.__cause__ = error
                return exc
        exc = PermanentError(str(error))
        exc.__cause__ = error
        return exc

    # Unknown error - treat as permanent by default
    exc = PermanentError(f"Unknown error: {error}")
    exc.__cause__ = error
    return exc


# ═══════════════════════════════════════════
# RETRY DECORATORS
# ═══════════════════════════════════════════

def retry_on_transient(
    max_attempts: int = 3,
    max_wait_seconds: int = 60,
):
    """
    Decorator dla retry tylko na transient errors

    Usage:
        @retry_on_transient(max_attempts=5)
        async def my_api_call():
            ...

    Args:
        max_attempts: Maksymalna liczba prób (default: 3)
        max_wait_seconds: Maksymalny czas oczekiwania między próbami (default: 60s)
    """
    return retry(
        retry=retry_if_exception_type(TransientError),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=max_wait_seconds),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


def retry_openai_call(
    max_attempts: int = 3,
    max_wait_seconds: int = 60,
):
    """
    Decorator specjalnie dla wywołań OpenAI API

    Automatycznie kategoryzuje błędy i retry tylko na transient.

    Usage:
        @retry_openai_call(max_attempts=5)
        async def generate_text():
            response = await client.chat.completions.create(...)
            return response

    Args:
        max_attempts: Maksymalna liczba prób (default: 3)
        max_wait_seconds: Maksymalny czas oczekiwania (default: 60s)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 0
            last_error: Optional[Exception] = None

            while attempt < max_attempts:
                attempt += 1

                try:
                    return await func(*args, **kwargs)

                except Exception as e:
                    # Kategoryzuj błąd
                    categorized = categorize_openai_error(e)
                    last_error = categorized

                    # Jeśli permanent - nie retry
                    if isinstance(categorized, PermanentError):
                        logger.error(f"Permanent error in {func.__name__}: {e}")
                        raise categorized

                    # Jeśli transient i mamy próby - retry
                    if attempt < max_attempts:
                        wait_time = min(2 ** (attempt - 1), max_wait_seconds)
                        logger.warning(
                            f"Transient error in {func.__name__} (attempt {attempt}/{max_attempts}): {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        # Wyczerpano próby
                        logger.error(
                            f"Max retries ({max_attempts}) exceeded in {func.__name__}: {e}"
                        )
                        raise categorized

            # Shouldn't reach here, but just in case
            if last_error:
                raise last_error
            raise RuntimeError(f"Unexpected retry loop exit in {func.__name__}")

        return wrapper
    return decorator


# ═══════════════════════════════════════════
# CIRCUIT BREAKER
# ═══════════════════════════════════════════

class CircuitBreaker:
    """
    Circuit breaker pattern dla API calls

    States:
    - CLOSED: Normal operation
    - OPEN: Too many failures, block requests
    - HALF_OPEN: Testing if service recovered

    Usage:
        breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0
        )

        async with breaker:
            result = await api_call()
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_attempts: int = 1,
    ):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Liczba błędów przed OPEN
            recovery_timeout: Czas (sekundy) przed próbą HALF_OPEN
            half_open_attempts: Liczba sukcessów w HALF_OPEN przed CLOSED
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_attempts = half_open_attempts

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def __enter__(self):
        """Sync context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager support"""
        if exc_type is not None:
            self.record_failure()
        else:
            self.record_success()
        return False

    async def __aenter__(self):
        """Async context manager support"""
        await self._check_state()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager support"""
        if exc_type is not None:
            self.record_failure()
        else:
            self.record_success()
        return False

    async def _check_state(self):
        """Check and update circuit breaker state"""
        import time

        if self.state == "OPEN":
            # Check if recovery timeout passed
            if self.last_failure_time:
                time_since_failure = time.time() - self.last_failure_time
                if time_since_failure >= self.recovery_timeout:
                    logger.info("Circuit breaker: OPEN → HALF_OPEN (recovery timeout passed)")
                    self.state = "HALF_OPEN"
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN. "
                        f"Wait {self.recovery_timeout - time_since_failure:.1f}s before retry."
                    )

    def record_failure(self):
        """Record a failure"""
        import time

        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == "HALF_OPEN":
            # Failed during recovery - back to OPEN
            logger.warning("Circuit breaker: HALF_OPEN → OPEN (recovery failed)")
            self.state = "OPEN"
            self.success_count = 0

        elif self.state == "CLOSED":
            # Check if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    f"Circuit breaker: CLOSED → OPEN "
                    f"(failure threshold {self.failure_threshold} exceeded)"
                )
                self.state = "OPEN"

    def record_success(self):
        """Record a success"""
        if self.state == "HALF_OPEN":
            self.success_count += 1
            if self.success_count >= self.half_open_attempts:
                # Recovery successful
                logger.info(
                    f"Circuit breaker: HALF_OPEN → CLOSED "
                    f"(recovery successful after {self.success_count} attempts)"
                )
                self.state = "CLOSED"
                self.failure_count = 0
                self.success_count = 0

        elif self.state == "CLOSED":
            # Reset failure count on success
            if self.failure_count > 0:
                logger.debug(f"Circuit breaker: resetting failure count from {self.failure_count}")
            self.failure_count = 0


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is OPEN"""
    pass

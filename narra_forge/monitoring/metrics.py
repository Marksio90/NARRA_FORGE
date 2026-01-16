"""
Prometheus Metrics Collection

Tracks key performance and business metrics for monitoring and alerting.
"""
import time
from typing import Optional, Dict, Any
from functools import wraps
from contextlib import contextmanager

try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Summary,
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Provide dummy implementations for when Prometheus is not installed
    class DummyMetric:
        def labels(self, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass

    Counter = Histogram = Gauge = Summary = lambda *args, **kwargs: DummyMetric()
    CollectorRegistry = lambda: None
    generate_latest = lambda registry: b""
    CONTENT_TYPE_LATEST = "text/plain"


class MetricsCollector:
    """
    Central metrics collector for NARRA_FORGE.

    Tracks:
    - Pipeline execution metrics
    - Agent performance metrics
    - API call metrics
    - Cost tracking
    - Quality metrics
    """

    def __init__(self, registry: Optional[Any] = None):
        """
        Initialize metrics collector.

        Args:
            registry: Prometheus registry (creates new if None)
        """
        self.enabled = PROMETHEUS_AVAILABLE
        self.registry = registry or (CollectorRegistry() if PROMETHEUS_AVAILABLE else None)

        if not self.enabled:
            return

        # Pipeline Metrics
        self.pipeline_duration = Histogram(
            "narra_forge_pipeline_duration_seconds",
            "Time taken for full pipeline execution",
            ["production_type", "genre"],
            registry=self.registry,
            buckets=(10, 30, 60, 120, 300, 600, 1200, 1800),  # 10s to 30min
        )

        self.pipeline_total = Counter(
            "narra_forge_pipeline_total",
            "Total number of pipelines executed",
            ["production_type", "genre", "status"],
            registry=self.registry,
        )

        # Agent Metrics
        self.agent_duration = Histogram(
            "narra_forge_agent_duration_seconds",
            "Time taken for agent execution",
            ["agent_id", "model"],
            registry=self.registry,
            buckets=(0.5, 1, 2, 5, 10, 30, 60, 120),  # 0.5s to 2min
        )

        self.agent_errors = Counter(
            "narra_forge_agent_errors_total",
            "Total number of agent errors",
            ["agent_id", "error_type"],
            registry=self.registry,
        )

        # API Call Metrics
        self.api_calls_total = Counter(
            "narra_forge_api_calls_total",
            "Total number of OpenAI API calls",
            ["model", "agent_id"],
            registry=self.registry,
        )

        self.api_call_duration = Histogram(
            "narra_forge_api_call_duration_seconds",
            "OpenAI API call duration",
            ["model"],
            registry=self.registry,
            buckets=(0.5, 1, 2, 5, 10, 20, 30),  # 0.5s to 30s
        )

        self.api_errors = Counter(
            "narra_forge_api_errors_total",
            "Total number of API errors",
            ["model", "error_type"],
            registry=self.registry,
        )

        # Token & Cost Metrics
        self.tokens_used = Counter(
            "narra_forge_tokens_used_total",
            "Total tokens used",
            ["model", "token_type"],  # token_type: prompt, completion
            registry=self.registry,
        )

        self.cost_usd = Counter(
            "narra_forge_cost_usd_total",
            "Total cost in USD",
            ["model", "agent_id"],
            registry=self.registry,
        )

        # Quality Metrics
        self.quality_score = Histogram(
            "narra_forge_quality_score",
            "Narrative quality score (0.0-1.0)",
            ["production_type", "metric_type"],  # metric_type: coherence, logic, etc.
            registry=self.registry,
            buckets=(0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0),
        )

        # System Metrics
        self.jobs_active = Gauge(
            "narra_forge_jobs_active",
            "Number of currently active jobs",
            registry=self.registry,
        )

        self.retry_attempts = Counter(
            "narra_forge_retry_attempts_total",
            "Total number of retry attempts",
            ["agent_id", "reason"],
            registry=self.registry,
        )

    @contextmanager
    def track_pipeline(self, production_type: str, genre: str):
        """
        Context manager to track pipeline execution.

        Usage:
            with metrics.track_pipeline("short_story", "fantasy"):
                result = await orchestrator.produce_narrative(brief)
        """
        if not self.enabled:
            yield
            return

        start_time = time.time()
        self.jobs_active.inc()
        status = "failed"

        try:
            yield
            status = "success"
        finally:
            duration = time.time() - start_time
            self.pipeline_duration.labels(
                production_type=production_type,
                genre=genre
            ).observe(duration)
            self.pipeline_total.labels(
                production_type=production_type,
                genre=genre,
                status=status
            ).inc()
            self.jobs_active.dec()

    @contextmanager
    def track_agent(self, agent_id: str, model: str):
        """
        Context manager to track agent execution.

        Usage:
            with metrics.track_agent("a01_brief_interpreter", "gpt-4o-mini"):
                result = await agent.execute(input_data)
        """
        if not self.enabled:
            yield
            return

        start_time = time.time()

        try:
            yield
        except Exception as e:
            self.agent_errors.labels(
                agent_id=agent_id,
                error_type=type(e).__name__
            ).inc()
            raise
        finally:
            duration = time.time() - start_time
            self.agent_duration.labels(
                agent_id=agent_id,
                model=model
            ).observe(duration)

    @contextmanager
    def track_api_call(self, model: str, agent_id: str):
        """
        Context manager to track OpenAI API call.

        Usage:
            with metrics.track_api_call("gpt-4o", "a06_sequential_generator"):
                response = await client.chat.completions.create(...)
        """
        if not self.enabled:
            yield
            return

        start_time = time.time()
        self.api_calls_total.labels(
            model=model,
            agent_id=agent_id
        ).inc()

        try:
            yield
        except Exception as e:
            self.api_errors.labels(
                model=model,
                error_type=type(e).__name__
            ).inc()
            raise
        finally:
            duration = time.time() - start_time
            self.api_call_duration.labels(model=model).observe(duration)

    def record_tokens(self, model: str, prompt_tokens: int, completion_tokens: int):
        """Record token usage"""
        if not self.enabled:
            return

        self.tokens_used.labels(model=model, token_type="prompt").inc(prompt_tokens)
        self.tokens_used.labels(model=model, token_type="completion").inc(completion_tokens)

    def record_cost(self, model: str, agent_id: str, cost_usd: float):
        """Record cost in USD"""
        if not self.enabled:
            return

        self.cost_usd.labels(model=model, agent_id=agent_id).inc(cost_usd)

    def record_quality_score(self, production_type: str, metric_type: str, score: float):
        """Record quality metric"""
        if not self.enabled:
            return

        self.quality_score.labels(
            production_type=production_type,
            metric_type=metric_type
        ).observe(score)

    def record_retry(self, agent_id: str, reason: str):
        """Record retry attempt"""
        if not self.enabled:
            return

        self.retry_attempts.labels(
            agent_id=agent_id,
            reason=reason
        ).inc()

    def get_metrics_text(self) -> bytes:
        """Get Prometheus metrics in text format"""
        if not self.enabled or not self.registry:
            return b"# Prometheus not available\n"

        return generate_latest(self.registry)


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# Decorator versions for convenience
def track_pipeline_execution(production_type: str, genre: str):
    """Decorator to track pipeline execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            with metrics.track_pipeline(production_type, genre):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def track_agent_execution(agent_id: str, model: str):
    """Decorator to track agent execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            with metrics.track_agent(agent_id, model):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def track_api_call(model: str, agent_id: str):
    """Decorator to track API call"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            with metrics.track_api_call(model, agent_id):
                return await func(*args, **kwargs)
        return wrapper
    return decorator

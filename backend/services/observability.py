"""Observability Service - OpenTelemetry traces, metrics, and logs integration."""

import functools
import inspect
import logging
import time
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any, TypeVar
from uuid import UUID

logger = logging.getLogger(__name__)

# Context variables for request tracking
current_job_id: ContextVar[str | None] = ContextVar("current_job_id", default=None)
current_trace_id: ContextVar[str | None] = ContextVar("current_trace_id", default=None)

# Type variable for generic decorator
F = TypeVar("F", bound=Callable[..., Any])


class TelemetryRecorder:
    """
    In-memory telemetry recorder for development/testing.

    In production, this would be replaced with actual OpenTelemetry exporters
    (Jaeger, Prometheus, etc.)
    """

    def __init__(self) -> None:
        """Initialize telemetry recorder."""
        self.traces: list[dict[str, Any]] = []
        self.metrics: dict[str, list[float]] = {}
        self.events: list[dict[str, Any]] = []

    def record_trace(
        self,
        name: str,
        duration: float,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Record a trace span."""
        trace = {
            "name": name,
            "duration": duration,
            "attributes": attributes or {},
            "timestamp": time.time(),
        }
        self.traces.append(trace)

        logger.debug(
            f"Trace recorded: {name}",
            extra={
                "trace_name": name,
                "duration": duration,
                **trace["attributes"],  # type: ignore[dict-item]
            },
        )

    def record_metric(self, name: str, value: float) -> None:
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

        logger.debug(
            f"Metric recorded: {name}={value}",
            extra={"metric_name": name, "value": value},
        )

    def record_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Record an event."""
        event = {
            "name": name,
            "attributes": attributes or {},
            "timestamp": time.time(),
        }
        self.events.append(event)

        logger.debug(
            f"Event recorded: {name}",
            extra={"event_name": name, **event["attributes"]},  # type: ignore[dict-item]
        )

    def get_trace_stats(self, trace_name: str | None = None) -> dict[str, Any]:
        """Get statistics for traces."""
        filtered_traces = self.traces
        if trace_name:
            filtered_traces = [t for t in self.traces if t["name"] == trace_name]

        if not filtered_traces:
            return {"count": 0}

        durations = [t["duration"] for t in filtered_traces]
        return {
            "count": len(filtered_traces),
            "total_duration": sum(durations),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
        }

    def get_metric_stats(self, metric_name: str) -> dict[str, Any]:
        """Get statistics for a metric."""
        if metric_name not in self.metrics:
            return {"count": 0}

        values = self.metrics[metric_name]
        return {
            "count": len(values),
            "total": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def clear(self) -> None:
        """Clear all recorded telemetry."""
        self.traces.clear()
        self.metrics.clear()
        self.events.clear()


# Global telemetry recorder instance
_telemetry_recorder = TelemetryRecorder()


def get_telemetry_recorder() -> TelemetryRecorder:
    """Get the global telemetry recorder instance."""
    return _telemetry_recorder


class Observability:
    """Observability service for traces, metrics, and structured logging."""

    @staticmethod
    def set_job_context(job_id: UUID | str) -> None:
        """Set current job ID in context for all subsequent operations."""
        current_job_id.set(str(job_id))
        logger.info(
            "Job context set",
            extra={"job_id": str(job_id)},
        )

    @staticmethod
    def get_job_context() -> str | None:
        """Get current job ID from context."""
        return current_job_id.get()

    @staticmethod
    def trace_agent_call(
        agent_name: str,
        stage: str | None = None,
        model: str | None = None,
    ) -> Callable[[F], F]:
        """
        Decorator to trace agent calls with timing and metadata.

        Args:
            agent_name: Name of the agent (e.g., "ProseGenerator")
            stage: Pipeline stage (e.g., "PROSE")
            model: Model being used (e.g., "gpt-4o")

        Returns:
            Decorated function with tracing

        Example:
            @Observability.trace_agent_call("ProseGenerator", stage="PROSE", model="gpt-4o")
            async def generate_prose(self, request):
                ...
        """

        def decorator(func: F) -> F:
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                trace_name = f"agent.{agent_name}"

                # Build attributes
                attributes: dict[str, Any] = {
                    "agent.name": agent_name,
                    "job_id": Observability.get_job_context(),
                }
                if stage:
                    attributes["pipeline.stage"] = stage
                if model:
                    attributes["model.name"] = model

                error = None
                result = None

                try:
                    logger.info(
                        f"Agent call started: {agent_name}",
                        extra=attributes,
                    )
                    result = await func(*args, **kwargs)
                    attributes["success"] = True
                    return result

                except Exception as e:
                    error = e
                    attributes["success"] = False
                    attributes["error.type"] = type(e).__name__
                    attributes["error.message"] = str(e)
                    raise

                finally:
                    duration = time.time() - start_time
                    attributes["duration"] = duration

                    # Record trace
                    _telemetry_recorder.record_trace(
                        name=trace_name,
                        duration=duration,
                        attributes=attributes,
                    )

                    # Record metrics
                    _telemetry_recorder.record_metric(f"{trace_name}.duration", duration)
                    _telemetry_recorder.record_metric(f"{trace_name}.calls", 1.0)

                    if error:
                        _telemetry_recorder.record_metric(f"{trace_name}.errors", 1.0)

                    logger.info(
                        f"Agent call completed: {agent_name}",
                        extra={
                            **attributes,
                            "duration": duration,
                        },
                    )

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                trace_name = f"agent.{agent_name}"

                attributes: dict[str, Any] = {
                    "agent.name": agent_name,
                    "job_id": Observability.get_job_context(),
                }
                if stage:
                    attributes["pipeline.stage"] = stage
                if model:
                    attributes["model.name"] = model

                error = None
                result = None

                try:
                    logger.info(
                        f"Agent call started: {agent_name}",
                        extra=attributes,
                    )
                    result = func(*args, **kwargs)
                    attributes["success"] = True
                    return result

                except Exception as e:
                    error = e
                    attributes["success"] = False
                    attributes["error.type"] = type(e).__name__
                    attributes["error.message"] = str(e)
                    raise

                finally:
                    duration = time.time() - start_time
                    attributes["duration"] = duration

                    _telemetry_recorder.record_trace(
                        name=trace_name,
                        duration=duration,
                        attributes=attributes,
                    )

                    _telemetry_recorder.record_metric(f"{trace_name}.duration", duration)
                    _telemetry_recorder.record_metric(f"{trace_name}.calls", 1.0)

                    if error:
                        _telemetry_recorder.record_metric(f"{trace_name}.errors", 1.0)

                    logger.info(
                        f"Agent call completed: {agent_name}",
                        extra={
                            **attributes,
                            "duration": duration,
                        },
                    )

            # Return appropriate wrapper based on function type
            if inspect.iscoroutinefunction(func):
                return async_wrapper  # type: ignore[return-value]
            else:
                return sync_wrapper  # type: ignore[return-value]

        return decorator

    @staticmethod
    def record_cost(
        agent_name: str,
        model: str,
        cost: float,
        tokens_used: int,
    ) -> None:
        """
        Record cost metrics for an agent call.

        Args:
            agent_name: Name of the agent
            model: Model name
            cost: Cost in USD
            tokens_used: Number of tokens used
        """
        _telemetry_recorder.record_metric("agent.cost", cost)
        _telemetry_recorder.record_metric(f"agent.{agent_name}.cost", cost)
        _telemetry_recorder.record_metric("agent.tokens", float(tokens_used))
        _telemetry_recorder.record_metric(f"agent.{agent_name}.tokens", float(tokens_used))

        logger.info(
            "Agent cost recorded",
            extra={
                "agent_name": agent_name,
                "model": model,
                "cost_usd": cost,
                "tokens_used": tokens_used,
                "job_id": Observability.get_job_context(),
            },
        )

    @staticmethod
    def record_qa_result(
        job_id: UUID | str,
        artifact_id: UUID | str,
        passed: bool,
        scores: dict[str, float],
    ) -> None:
        """
        Record QA check result.

        Args:
            job_id: Job UUID
            artifact_id: Artifact UUID
            passed: Whether QA passed
            scores: QA scores (logic, psychology, timeline)
        """
        _telemetry_recorder.record_metric("qa.checks", 1.0)
        _telemetry_recorder.record_metric("qa.passed" if passed else "qa.failed", 1.0)

        for score_name, score_value in scores.items():
            _telemetry_recorder.record_metric(f"qa.score.{score_name}", score_value)

        _telemetry_recorder.record_event(
            "qa.check_completed",
            attributes={
                "job_id": str(job_id),
                "artifact_id": str(artifact_id),
                "passed": passed,
                **{f"score.{k}": v for k, v in scores.items()},
            },
        )

        logger.info(
            "QA check completed",
            extra={
                "job_id": str(job_id),
                "artifact_id": str(artifact_id),
                "passed": passed,
                **scores,
            },
        )

    @staticmethod
    def record_pipeline_stage(
        job_id: UUID | str,
        stage: str,
        status: str,
        duration: float | None = None,
    ) -> None:
        """
        Record pipeline stage completion.

        Args:
            job_id: Job UUID
            stage: Pipeline stage name
            status: Status (started, completed, failed)
            duration: Duration in seconds (for completed stages)
        """
        _telemetry_recorder.record_event(
            f"pipeline.stage.{status}",
            attributes={
                "job_id": str(job_id),
                "stage": stage,
                "duration": duration,
            },
        )

        if status == "completed" and duration:
            _telemetry_recorder.record_metric(f"pipeline.{stage}.duration", duration)

        logger.info(
            f"Pipeline stage {status}",
            extra={
                "job_id": str(job_id),
                "stage": stage,
                "status": status,
                "duration": duration,
            },
        )

    @staticmethod
    def get_statistics() -> dict[str, Any]:
        """
        Get all telemetry statistics.

        Returns:
            Dictionary with traces, metrics, and events statistics
        """
        recorder = _telemetry_recorder

        return {
            "traces": {
                "total_count": len(recorder.traces),
                "by_name": {
                    name: recorder.get_trace_stats(name)
                    for name in {t["name"] for t in recorder.traces}
                },
            },
            "metrics": {name: recorder.get_metric_stats(name) for name in recorder.metrics},
            "events": {
                "total_count": len(recorder.events),
                "by_name": {
                    name: len([e for e in recorder.events if e["name"] == name])
                    for name in {e["name"] for e in recorder.events}
                },
            },
        }

    @staticmethod
    def clear_telemetry() -> None:
        """Clear all recorded telemetry (useful for testing)."""
        _telemetry_recorder.clear()
        logger.debug("Telemetry cleared")

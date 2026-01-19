"""Unit tests for Observability Service."""

import asyncio
import time
from collections.abc import Generator
from uuid import uuid4

import pytest

from services.observability import Observability, get_telemetry_recorder


@pytest.fixture(autouse=True)  # type: ignore[misc]
def clear_telemetry() -> Generator[None, None, None]:
    """Clear telemetry and context before each test."""
    from services.observability import current_job_id

    Observability.clear_telemetry()
    # Reset context
    current_job_id.set(None)
    yield


def test_set_and_get_job_context() -> None:
    """Test setting and getting job context."""
    job_id = uuid4()

    Observability.set_job_context(job_id)
    context = Observability.get_job_context()

    assert context == str(job_id)


def test_get_job_context_when_not_set() -> None:
    """Test getting job context when not set."""
    context = Observability.get_job_context()
    assert context is None


@pytest.mark.asyncio  # type: ignore[misc]
async def test_trace_agent_call_async_success() -> None:
    """Test tracing async agent call success."""

    @Observability.trace_agent_call("TestAgent", stage="TEST", model="gpt-4o-mini")
    async def test_function(value: int) -> int:
        await asyncio.sleep(0.01)
        return value * 2

    result = await test_function(5)

    assert result == 10

    # Check recorded trace
    recorder = get_telemetry_recorder()
    assert len(recorder.traces) == 1

    trace = recorder.traces[0]
    assert trace["name"] == "agent.TestAgent"
    assert trace["duration"] >= 0.01
    assert trace["attributes"]["agent.name"] == "TestAgent"
    assert trace["attributes"]["pipeline.stage"] == "TEST"
    assert trace["attributes"]["model.name"] == "gpt-4o-mini"
    assert trace["attributes"]["success"] is True


@pytest.mark.asyncio  # type: ignore[misc]
async def test_trace_agent_call_async_error() -> None:
    """Test tracing async agent call with error."""

    @Observability.trace_agent_call("TestAgent")
    async def test_function() -> None:
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        await test_function()

    # Check recorded trace
    recorder = get_telemetry_recorder()
    assert len(recorder.traces) == 1

    trace = recorder.traces[0]
    assert trace["name"] == "agent.TestAgent"
    assert trace["attributes"]["success"] is False
    assert trace["attributes"]["error.type"] == "ValueError"
    assert trace["attributes"]["error.message"] == "Test error"

    # Check error metric
    assert "agent.TestAgent.errors" in recorder.metrics
    assert sum(recorder.metrics["agent.TestAgent.errors"]) == 1.0


def test_trace_agent_call_sync_success() -> None:
    """Test tracing sync agent call success."""

    @Observability.trace_agent_call("TestAgent", stage="TEST")
    def test_function(value: int) -> int:
        time.sleep(0.01)
        return value * 2

    result = test_function(5)

    assert result == 10

    # Check recorded trace
    recorder = get_telemetry_recorder()
    assert len(recorder.traces) == 1

    trace = recorder.traces[0]
    assert trace["name"] == "agent.TestAgent"
    assert trace["duration"] >= 0.01
    assert trace["attributes"]["success"] is True


def test_trace_agent_call_sync_error() -> None:
    """Test tracing sync agent call with error."""

    @Observability.trace_agent_call("TestAgent")
    def test_function() -> None:
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        test_function()

    # Check recorded trace
    recorder = get_telemetry_recorder()
    assert len(recorder.traces) == 1

    trace = recorder.traces[0]
    assert trace["attributes"]["success"] is False
    assert trace["attributes"]["error.type"] == "ValueError"


def test_trace_agent_call_with_job_context() -> None:
    """Test that trace includes job context when set."""
    job_id = uuid4()
    Observability.set_job_context(job_id)

    @Observability.trace_agent_call("TestAgent")
    def test_function() -> str:
        return "test"

    test_function()

    recorder = get_telemetry_recorder()
    trace = recorder.traces[0]
    assert trace["attributes"]["job_id"] == str(job_id)


def test_record_cost() -> None:
    """Test recording cost metrics."""
    Observability.record_cost(
        agent_name="ProseGenerator",
        model="gpt-4o",
        cost=0.042,
        tokens_used=1500,
    )

    recorder = get_telemetry_recorder()

    # Check cost metrics
    assert "agent.cost" in recorder.metrics
    assert recorder.metrics["agent.cost"][0] == 0.042

    assert "agent.ProseGenerator.cost" in recorder.metrics
    assert recorder.metrics["agent.ProseGenerator.cost"][0] == 0.042

    # Check token metrics
    assert "agent.tokens" in recorder.metrics
    assert recorder.metrics["agent.tokens"][0] == 1500.0

    assert "agent.ProseGenerator.tokens" in recorder.metrics
    assert recorder.metrics["agent.ProseGenerator.tokens"][0] == 1500.0


def test_record_qa_result_passed() -> None:
    """Test recording QA result that passed."""
    job_id = uuid4()
    artifact_id = uuid4()

    Observability.record_qa_result(
        job_id=job_id,
        artifact_id=artifact_id,
        passed=True,
        scores={
            "logic_score": 0.95,
            "psychology_score": 0.88,
            "timeline_score": 0.92,
        },
    )

    recorder = get_telemetry_recorder()

    # Check metrics
    assert "qa.checks" in recorder.metrics
    assert recorder.metrics["qa.checks"][0] == 1.0

    assert "qa.passed" in recorder.metrics
    assert recorder.metrics["qa.passed"][0] == 1.0

    assert "qa.score.logic_score" in recorder.metrics
    assert recorder.metrics["qa.score.logic_score"][0] == 0.95

    # Check event
    assert len(recorder.events) == 1
    event = recorder.events[0]
    assert event["name"] == "qa.check_completed"
    assert event["attributes"]["job_id"] == str(job_id)
    assert event["attributes"]["passed"] is True


def test_record_qa_result_failed() -> None:
    """Test recording QA result that failed."""
    job_id = uuid4()
    artifact_id = uuid4()

    Observability.record_qa_result(
        job_id=job_id,
        artifact_id=artifact_id,
        passed=False,
        scores={
            "logic_score": 0.45,
            "psychology_score": 0.50,
            "timeline_score": 0.60,
        },
    )

    recorder = get_telemetry_recorder()

    # Check failed metric
    assert "qa.failed" in recorder.metrics
    assert recorder.metrics["qa.failed"][0] == 1.0


def test_record_pipeline_stage_started() -> None:
    """Test recording pipeline stage started."""
    job_id = uuid4()

    Observability.record_pipeline_stage(
        job_id=job_id,
        stage="PROSE",
        status="started",
    )

    recorder = get_telemetry_recorder()

    # Check event
    assert len(recorder.events) == 1
    event = recorder.events[0]
    assert event["name"] == "pipeline.stage.started"
    assert event["attributes"]["stage"] == "PROSE"


def test_record_pipeline_stage_completed() -> None:
    """Test recording pipeline stage completed."""
    job_id = uuid4()

    Observability.record_pipeline_stage(
        job_id=job_id,
        stage="PROSE",
        status="completed",
        duration=12.5,
    )

    recorder = get_telemetry_recorder()

    # Check event
    event = recorder.events[0]
    assert event["name"] == "pipeline.stage.completed"
    assert event["attributes"]["duration"] == 12.5

    # Check duration metric
    assert "pipeline.PROSE.duration" in recorder.metrics
    assert recorder.metrics["pipeline.PROSE.duration"][0] == 12.5


def test_get_statistics_empty() -> None:
    """Test getting statistics when empty."""
    stats = Observability.get_statistics()

    assert stats["traces"]["total_count"] == 0
    assert stats["metrics"] == {}
    assert stats["events"]["total_count"] == 0


def test_get_statistics_with_data() -> None:
    """Test getting statistics with recorded data."""

    # Record some traces
    @Observability.trace_agent_call("TestAgent")
    def test_function() -> str:
        return "test"

    test_function()
    test_function()

    # Record some metrics
    Observability.record_cost("TestAgent", "gpt-4o", 0.01, 100)

    # Record some events
    Observability.record_pipeline_stage(uuid4(), "TEST", "completed", 1.5)

    stats = Observability.get_statistics()

    assert stats["traces"]["total_count"] == 2
    assert "agent.TestAgent" in stats["traces"]["by_name"]
    assert stats["traces"]["by_name"]["agent.TestAgent"]["count"] == 2

    assert "agent.cost" in stats["metrics"]
    assert stats["metrics"]["agent.cost"]["count"] == 1
    assert stats["metrics"]["agent.cost"]["total"] == 0.01

    assert stats["events"]["total_count"] == 1


def test_telemetry_recorder_get_trace_stats() -> None:
    """Test TelemetryRecorder trace statistics."""
    recorder = get_telemetry_recorder()

    recorder.record_trace("test.trace", 1.0, {"foo": "bar"})
    recorder.record_trace("test.trace", 2.0, {"foo": "baz"})
    recorder.record_trace("other.trace", 3.0, {"foo": "qux"})

    stats = recorder.get_trace_stats("test.trace")

    assert stats["count"] == 2
    assert stats["total_duration"] == 3.0
    assert stats["avg_duration"] == 1.5
    assert stats["min_duration"] == 1.0
    assert stats["max_duration"] == 2.0


def test_telemetry_recorder_get_trace_stats_empty() -> None:
    """Test trace statistics when no traces."""
    recorder = get_telemetry_recorder()

    stats = recorder.get_trace_stats("nonexistent")

    assert stats["count"] == 0


def test_telemetry_recorder_get_metric_stats() -> None:
    """Test TelemetryRecorder metric statistics."""
    recorder = get_telemetry_recorder()

    recorder.record_metric("test.metric", 1.0)
    recorder.record_metric("test.metric", 2.0)
    recorder.record_metric("test.metric", 3.0)

    stats = recorder.get_metric_stats("test.metric")

    assert stats["count"] == 3
    assert stats["total"] == 6.0
    assert stats["avg"] == 2.0
    assert stats["min"] == 1.0
    assert stats["max"] == 3.0


def test_telemetry_recorder_get_metric_stats_empty() -> None:
    """Test metric statistics when no metrics."""
    recorder = get_telemetry_recorder()

    stats = recorder.get_metric_stats("nonexistent")

    assert stats["count"] == 0


def test_telemetry_recorder_clear() -> None:
    """Test clearing telemetry."""
    recorder = get_telemetry_recorder()

    recorder.record_trace("test", 1.0)
    recorder.record_metric("test", 1.0)
    recorder.record_event("test")

    assert len(recorder.traces) == 1
    assert len(recorder.metrics) == 1
    assert len(recorder.events) == 1

    recorder.clear()

    assert len(recorder.traces) == 0
    assert len(recorder.metrics) == 0
    assert len(recorder.events) == 0


def test_multiple_cost_recordings() -> None:
    """Test multiple cost recordings aggregate correctly."""
    Observability.record_cost("Agent1", "gpt-4o", 0.01, 100)
    Observability.record_cost("Agent1", "gpt-4o", 0.02, 200)
    Observability.record_cost("Agent2", "gpt-4o-mini", 0.005, 150)

    recorder = get_telemetry_recorder()

    # Total costs
    assert len(recorder.metrics["agent.cost"]) == 3
    assert sum(recorder.metrics["agent.cost"]) == pytest.approx(0.035)

    # Agent1 costs
    assert len(recorder.metrics["agent.Agent1.cost"]) == 2
    assert sum(recorder.metrics["agent.Agent1.cost"]) == pytest.approx(0.03)

    # Agent2 costs
    assert len(recorder.metrics["agent.Agent2.cost"]) == 1
    assert sum(recorder.metrics["agent.Agent2.cost"]) == pytest.approx(0.005)


def test_trace_metrics_recorded() -> None:
    """Test that traces also record metrics."""

    @Observability.trace_agent_call("TestAgent")
    def test_function() -> str:
        return "test"

    test_function()

    recorder = get_telemetry_recorder()

    # Should have duration and calls metrics
    assert "agent.TestAgent.duration" in recorder.metrics
    assert len(recorder.metrics["agent.TestAgent.duration"]) == 1

    assert "agent.TestAgent.calls" in recorder.metrics
    assert sum(recorder.metrics["agent.TestAgent.calls"]) == 1.0

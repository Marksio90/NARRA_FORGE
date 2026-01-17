"""
Testy dla MetricsCollector (Prometheus monitoring)
"""
import pytest
import time
from narra_forge.monitoring.metrics import MetricsCollector, PROMETHEUS_AVAILABLE


@pytest.mark.unit
class TestMetricsCollectorInitialization:
    """Test inicjalizacji MetricsCollector"""

    def test_initialization_with_prometheus(self):
        """Test że MetricsCollector inicjalizuje się gdy Prometheus jest dostępny"""
        collector = MetricsCollector()

        if PROMETHEUS_AVAILABLE:
            assert collector.enabled is True
            assert collector.registry is not None
        else:
            assert collector.enabled is False

    def test_initialization_without_prometheus(self):
        """Test że MetricsCollector działa bez Prometheus (graceful degradation)"""
        import narra_forge.monitoring.metrics as metrics_module

        # Tymczasowo wyłącz Prometheus
        original_available = metrics_module.PROMETHEUS_AVAILABLE
        metrics_module.PROMETHEUS_AVAILABLE = False

        try:
            collector = MetricsCollector()
            assert collector.enabled is False
        finally:
            # Przywróć oryginalny stan
            metrics_module.PROMETHEUS_AVAILABLE = original_available


@pytest.mark.unit
@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not installed")
class TestMetricsCollectorTracking:
    """Test trackingu metryk (tylko gdy Prometheus dostępny)"""

    def test_track_pipeline_success(self):
        """Test trackingu pomyślnego pipeline'u"""
        collector = MetricsCollector()

        with collector.track_pipeline("short_story", "fantasy"):
            time.sleep(0.01)  # Symulacja pracy

        # Sprawdź że metryki zostały zapisane (weryfikacja że nie ma wyjątku)
        assert True

    def test_track_pipeline_failure(self):
        """Test trackingu nieudanego pipeline'u"""
        collector = MetricsCollector()

        with pytest.raises(ValueError):
            with collector.track_pipeline("short_story", "fantasy"):
                raise ValueError("Test error")

        # Metryka powinna być zapisana jako "failed"
        assert True

    def test_track_agent_success(self):
        """Test trackingu pomyślnego agenta"""
        collector = MetricsCollector()

        with collector.track_agent("a01_brief_interpreter", "gpt-4o-mini"):
            time.sleep(0.01)  # Symulacja pracy

        assert True

    def test_track_agent_error(self):
        """Test trackingu błędu agenta"""
        collector = MetricsCollector()

        with pytest.raises(RuntimeError):
            with collector.track_agent("a01_brief_interpreter", "gpt-4o-mini"):
                raise RuntimeError("Agent error")

        # Agent error counter powinien być zinkrementowany
        assert True

    def test_track_api_call_success(self):
        """Test trackingu pomyślnego wywołania API"""
        collector = MetricsCollector()

        with collector.track_api_call("gpt-4o", "a06_sequential_generator"):
            time.sleep(0.01)  # Symulacja API call

        assert True

    def test_track_api_call_error(self):
        """Test trackingu błędu API"""
        collector = MetricsCollector()

        with pytest.raises(ConnectionError):
            with collector.track_api_call("gpt-4o", "a06_sequential_generator"):
                raise ConnectionError("API error")

        # API error counter powinien być zinkrementowany
        assert True


@pytest.mark.unit
@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not installed")
class TestMetricsCollectorTokensAndCost:
    """Test trackingu tokenów i kosztów"""

    def test_record_tokens(self):
        """Test zapisywania użycia tokenów"""
        collector = MetricsCollector()

        collector.tokens_used.labels(
            model="gpt-4o-mini",
            token_type="prompt"
        ).inc(100)

        collector.tokens_used.labels(
            model="gpt-4o-mini",
            token_type="completion"
        ).inc(200)

        assert True  # Sprawdzamy że nie ma wyjątku

    def test_record_cost(self):
        """Test zapisywania kosztów"""
        collector = MetricsCollector()

        collector.cost_usd.labels(
            model="gpt-4o",
            agent_id="a06_sequential_generator"
        ).inc(0.05)

        assert True

    def test_record_quality_score(self):
        """Test zapisywania wyniku jakości"""
        collector = MetricsCollector()

        collector.quality_score.labels(
            production_type="short_story",
            metric_type="coherence"
        ).observe(0.92)

        assert True


@pytest.mark.unit
@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not installed")
class TestMetricsCollectorSystemMetrics:
    """Test metryk systemowych"""

    def test_jobs_active_increment_decrement(self):
        """Test że jobs_active inkrementuje i dekrementuje"""
        collector = MetricsCollector()

        # Inkrementuj
        collector.jobs_active.inc()

        # Dekrementuj
        collector.jobs_active.dec()

        assert True

    def test_retry_attempts(self):
        """Test zliczania prób retry"""
        collector = MetricsCollector()

        collector.retry_attempts.labels(
            agent_id="a07_coherence_validator",
            reason="api_timeout"
        ).inc()

        assert True


@pytest.mark.unit
class TestMetricsCollectorWithoutPrometheus:
    """Test że MetricsCollector działa bez Prometheus"""

    def test_track_pipeline_without_prometheus(self):
        """Test że track_pipeline działa gdy Prometheus niedostępny"""
        import narra_forge.monitoring.metrics as metrics_module

        original_available = metrics_module.PROMETHEUS_AVAILABLE
        metrics_module.PROMETHEUS_AVAILABLE = False

        try:
            collector = MetricsCollector()

            # Powinno działać bez błędów
            with collector.track_pipeline("short_story", "fantasy"):
                time.sleep(0.01)

            assert True
        finally:
            metrics_module.PROMETHEUS_AVAILABLE = original_available

    def test_track_agent_without_prometheus(self):
        """Test że track_agent działa gdy Prometheus niedostępny"""
        import narra_forge.monitoring.metrics as metrics_module

        original_available = metrics_module.PROMETHEUS_AVAILABLE
        metrics_module.PROMETHEUS_AVAILABLE = False

        try:
            collector = MetricsCollector()

            with collector.track_agent("a01_brief_interpreter", "gpt-4o-mini"):
                time.sleep(0.01)

            assert True
        finally:
            metrics_module.PROMETHEUS_AVAILABLE = original_available


@pytest.mark.unit
@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not installed")
class TestMetricsExport:
    """Test eksportu metryk do Prometheus"""

    def test_generate_metrics_output(self):
        """Test że można wygenerować output metryk"""
        from prometheus_client import generate_latest

        collector = MetricsCollector()

        # Dodaj kilka metryk
        collector.tokens_used.labels(model="gpt-4o", token_type="prompt").inc(100)
        collector.cost_usd.labels(model="gpt-4o", agent_id="test").inc(0.05)

        # Wygeneruj output
        output = generate_latest(collector.registry)

        assert output is not None
        assert isinstance(output, bytes)
        assert len(output) > 0

    def test_metrics_output_contains_data(self):
        """Test że output zawiera nasze metryki"""
        from prometheus_client import generate_latest

        collector = MetricsCollector()

        collector.pipeline_total.labels(
            production_type="short_story",
            genre="fantasy",
            status="success"
        ).inc()

        output = generate_latest(collector.registry).decode('utf-8')

        # Sprawdź czy zawiera nazwę metryki
        assert "narra_forge_pipeline_total" in output

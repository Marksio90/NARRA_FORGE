# NARRA_FORGE Monitoring Guide

Comprehensive monitoring setup for NARRA_FORGE platform using Prometheus + Grafana + Structlog.

## Overview

**Monitoring Stack:**
- **Structlog** - Structured logging (JSON logs for production)
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Metrics visualization and dashboards
- **Sentry** (optional) - Error tracking and alerts

## Quick Start

### 1. Start Monitoring Stack

```bash
# Start Prometheus + Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# Check status
docker-compose -f docker-compose.monitoring.yml ps
```

### 2. Access Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### 3. Configure Logging in Your Code

```python
from narra_forge.monitoring import get_logger, configure_logging

# Configure logging (do this once at startup)
configure_logging(
    level="INFO",
    json_output=False,  # Set True for production
)

# Get logger instance
log = get_logger(__name__, component="orchestrator")

# Log structured data
log.info(
    "pipeline_started",
    job_id="job_123",
    production_type="short_story",
    genre="fantasy"
)
```

### 4. Collect Metrics

```python
from narra_forge.monitoring import MetricsCollector

metrics = MetricsCollector()

# Track pipeline execution
with metrics.track_pipeline("short_story", "fantasy"):
    result = await orchestrator.produce_narrative(brief)

# Track agent execution
with metrics.track_agent("a01_brief_interpreter", "gpt-4o-mini"):
    result = await agent.execute(input_data)

# Record custom metrics
metrics.record_tokens("gpt-4o", prompt_tokens=1000, completion_tokens=500)
metrics.record_cost("gpt-4o", "a06_sequential_generator", 0.05)
metrics.record_quality_score("short_story", "coherence", 0.88)
```

## Metrics Collected

### Pipeline Metrics

**`narra_forge_pipeline_duration_seconds`** (Histogram)
- Time taken for full pipeline execution
- Labels: `production_type`, `genre`
- Buckets: 10s, 30s, 1min, 2min, 5min, 10min, 20min, 30min

**`narra_forge_pipeline_total`** (Counter)
- Total number of pipelines executed
- Labels: `production_type`, `genre`, `status` (success/failed)

**`narra_forge_jobs_active`** (Gauge)
- Number of currently active jobs
- No labels

### Agent Metrics

**`narra_forge_agent_duration_seconds`** (Histogram)
- Time taken for agent execution
- Labels: `agent_id`, `model`
- Buckets: 0.5s, 1s, 2s, 5s, 10s, 30s, 1min, 2min

**`narra_forge_agent_errors_total`** (Counter)
- Total number of agent errors
- Labels: `agent_id`, `error_type`

### API Call Metrics

**`narra_forge_api_calls_total`** (Counter)
- Total number of OpenAI API calls
- Labels: `model`, `agent_id`

**`narra_forge_api_call_duration_seconds`** (Histogram)
- OpenAI API call duration
- Labels: `model`
- Buckets: 0.5s, 1s, 2s, 5s, 10s, 20s, 30s

**`narra_forge_api_errors_total`** (Counter)
- Total number of API errors
- Labels: `model`, `error_type`

### Token & Cost Metrics

**`narra_forge_tokens_used_total`** (Counter)
- Total tokens used
- Labels: `model`, `token_type` (prompt/completion)

**`narra_forge_cost_usd_total`** (Counter)
- Total cost in USD
- Labels: `model`, `agent_id`

### Quality Metrics

**`narra_forge_quality_score`** (Histogram)
- Narrative quality score (0.0-1.0)
- Labels: `production_type`, `metric_type` (coherence/logic/psychology/temporal)
- Buckets: 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0

### Retry Metrics

**`narra_forge_retry_attempts_total`** (Counter)
- Total number of retry attempts
- Labels: `agent_id`, `reason`

## Useful Prometheus Queries

### Pipeline Performance

```promql
# Average pipeline duration by production type (last 1h)
rate(narra_forge_pipeline_duration_seconds_sum[1h]) /
rate(narra_forge_pipeline_duration_seconds_count[1h])

# Pipeline success rate
sum(rate(narra_forge_pipeline_total{status="success"}[5m])) /
sum(rate(narra_forge_pipeline_total[5m]))

# P95 pipeline duration
histogram_quantile(0.95,
  rate(narra_forge_pipeline_duration_seconds_bucket[5m])
)
```

### Agent Performance

```promql
# Slowest agents (P95 duration)
histogram_quantile(0.95,
  sum by (agent_id, le) (
    rate(narra_forge_agent_duration_seconds_bucket[5m])
  )
)

# Agent error rate
sum by (agent_id) (
  rate(narra_forge_agent_errors_total[5m])
)
```

### Cost Tracking

```promql
# Total cost per hour
sum(rate(narra_forge_cost_usd_total[1h])) * 3600

# Cost by model
sum by (model) (narra_forge_cost_usd_total)

# Cost per narrative (average)
sum(narra_forge_cost_usd_total) /
sum(narra_forge_pipeline_total{status="success"})
```

### API Metrics

```promql
# API calls per second
sum(rate(narra_forge_api_calls_total[1m]))

# API error rate
sum(rate(narra_forge_api_errors_total[5m])) /
sum(rate(narra_forge_api_calls_total[5m]))

# P95 API call duration by model
histogram_quantile(0.95,
  sum by (model, le) (
    rate(narra_forge_api_call_duration_seconds_bucket[5m])
  )
)
```

### Quality Metrics

```promql
# Average coherence score (last 24h)
sum(rate(narra_forge_quality_score_sum{metric_type="coherence"}[24h])) /
sum(rate(narra_forge_quality_score_count{metric_type="coherence"}[24h]))

# Quality score distribution
histogram_quantile(0.5,
  rate(narra_forge_quality_score_bucket{metric_type="coherence"}[1h])
)
```

## Alerting Rules

Create `monitoring/prometheus/alerts.yml`:

```yaml
groups:
  - name: narra_forge_alerts
    interval: 30s
    rules:
      # Pipeline taking too long
      - alert: PipelineDurationHigh
        expr: histogram_quantile(0.95, rate(narra_forge_pipeline_duration_seconds_bucket[5m])) > 1800
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pipeline duration is very high (P95 > 30min)"
          description: "P95 pipeline duration is {{ $value }}s"

      # High error rate
      - alert: PipelineErrorRateHigh
        expr: |
          sum(rate(narra_forge_pipeline_total{status="failed"}[5m])) /
          sum(rate(narra_forge_pipeline_total[5m])) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pipeline error rate is high (>10%)"
          description: "Error rate is {{ $value | humanizePercentage }}"

      # Cost threshold exceeded
      - alert: CostBudgetWarning
        expr: sum(increase(narra_forge_cost_usd_total[1h])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Hourly cost exceeded $10"
          description: "Current hourly cost: ${{ $value }}"

      # Quality score too low
      - alert: QualityScoreLow
        expr: |
          sum(rate(narra_forge_quality_score_sum{metric_type="coherence"}[1h])) /
          sum(rate(narra_forge_quality_score_count{metric_type="coherence"}[1h])) < 0.85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Average coherence score below threshold"
          description: "Current score: {{ $value }}"

      # API error rate spike
      - alert: APIErrorRateHigh
        expr: |
          sum(rate(narra_forge_api_errors_total[5m])) /
          sum(rate(narra_forge_api_calls_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "OpenAI API error rate is high (>5%)"
          description: "Error rate: {{ $value | humanizePercentage }}"
```

## Structured Logging Best Practices

### 1. Use Consistent Event Names

```python
# Good: machine-readable, consistent
log.info("pipeline_started", job_id=job_id)
log.info("pipeline_completed", job_id=job_id, duration=duration)

# Bad: inconsistent, not queryable
log.info(f"Pipeline {job_id} started")
log.info(f"Finished pipeline {job_id} in {duration}s")
```

### 2. Include Relevant Context

```python
# Good: all relevant context
log.error(
    "agent_execution_failed",
    agent_id="a06_sequential_generator",
    error_type="RateLimitError",
    retry_attempt=2,
    job_id=job_id,
    exc_info=True  # Include stack trace
)

# Bad: missing context
log.error("Agent failed")
```

### 3. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (e.g., approaching cost limit)
- **ERROR**: Error messages (e.g., API call failed)
- **CRITICAL**: Critical errors (e.g., system failure)

```python
log.debug("api_request_prepared", prompt_length=len(prompt))
log.info("agent_execution_started", agent_id=agent_id)
log.warning("cost_threshold_approaching", current=8.5, max=10.0)
log.error("api_call_failed", error=str(e), retry_attempt=1)
log.critical("database_connection_lost", attempts=5)
```

### 4. Bind Context for Reuse

```python
# Create logger with bound context
log = get_logger(__name__, job_id=job_id, production_type="short_story")

# All subsequent logs include job_id and production_type
log.info("stage_started", stage=1)
log.info("stage_completed", stage=1, duration=5.2)
```

## Grafana Dashboard Setup

### Import Dashboard

1. Go to Grafana (http://localhost:3000)
2. Login (admin/admin)
3. Click "+" → "Import"
4. Upload `monitoring/grafana/dashboards/narra_forge_dashboard.json`

### Key Panels to Create

**1. Pipeline Overview**
- Pipelines per minute (by production type)
- Success rate
- P95 duration
- Active jobs

**2. Agent Performance**
- Agent execution time (heatmap)
- Error rate by agent
- Most expensive agents (by cost)

**3. API Metrics**
- API calls per second
- API error rate
- P95 API latency
- Tokens per second

**4. Cost Tracking**
- Cost per hour
- Cost per narrative (average)
- Cost by model
- Daily spend

**5. Quality Metrics**
- Average coherence score
- Quality score distribution
- Quality trends over time

## Sentry Integration (Optional)

For error tracking and alerting:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    traces_sample_rate=0.1,  # 10% of transactions
)

# Sentry automatically captures uncaught exceptions
# Manual error reporting:
try:
    result = await agent.execute(input_data)
except Exception as e:
    sentry_sdk.capture_exception(e)
    raise
```

## Maintenance

### Clean Up Old Metrics

Prometheus stores metrics for 15 days by default. To change:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  retention.time: 30d  # Keep 30 days
```

### Backup Grafana Dashboards

```bash
# Export dashboard JSON
curl -u admin:admin http://localhost:3000/api/dashboards/uid/YOUR_DASHBOARD_UID | \
  jq '.dashboard' > dashboard_backup.json
```

## Troubleshooting

### Prometheus Not Scraping Metrics

1. Check Prometheus targets: http://localhost:9090/targets
2. Verify metrics endpoint is accessible: `curl http://localhost:8000/metrics`
3. Check Prometheus logs: `docker logs narra-forge-prometheus`

### Grafana Not Showing Data

1. Verify Prometheus datasource: Grafana → Configuration → Data Sources
2. Test connection to Prometheus
3. Check query syntax in panel edit mode

### Metrics Not Appearing

1. Verify `prometheus_client` is installed: `pip list | grep prometheus`
2. Check that MetricsCollector is initialized
3. Verify metrics are being recorded (add debug logging)

## Next Steps

- [ ] Add Sentry integration for error tracking
- [ ] Create alert notification channels (Slack, email, PagerDuty)
- [ ] Setup log aggregation (ELK stack or Loki)
- [ ] Add distributed tracing (OpenTelemetry)
- [ ] Create runbooks for common alerts

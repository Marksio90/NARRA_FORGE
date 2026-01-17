# NARRA_FORGE Monitoring Stack

Complete monitoring solution with Prometheus + Grafana for NARRA_FORGE platform.

## Quick Start

### 1. Start Monitoring Stack

```bash
# Start Prometheus + Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# Check status
docker-compose -f docker-compose.monitoring.yml ps
```

### 2. Start Metrics Server (for testing)

```bash
# Install prometheus_client if not already installed
pip install prometheus-client

# Start metrics simulation server
python monitoring/metrics_server.py
```

This will:
- Expose metrics at `http://localhost:8000/metrics`
- Simulate realistic NARRA_FORGE pipeline metrics
- Generate sample data for Grafana dashboards

### 3. Access Dashboards

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`
  - Dashboard: "NARRA_FORGE Production Dashboard"

- **Prometheus**: http://localhost:9090
  - Query interface for metrics
  - Targets: http://localhost:9090/targets

- **Metrics Endpoint**: http://localhost:8000/metrics
  - Raw Prometheus metrics

## What's Monitored

### Pipeline Metrics
- ✅ Pipeline executions per minute (by type & genre)
- ✅ Pipeline success rate (%)
- ✅ Pipeline duration (P95, P50)
- ✅ Active jobs (gauge)

### Agent Metrics
- ✅ Agent execution time (P95, by agent)
- ✅ Agent error rate (by agent)

### API Metrics
- ✅ API calls per second
- ✅ API errors per second
- ✅ API call duration (P95)

### Cost Tracking
- ✅ Cost per hour (by model)
- ✅ Average cost per narrative
- ✅ Total spend tracking

### Quality Metrics
- ✅ Quality scores (coherence, logic, psychology, temporal)
- ✅ Quality trends over time

### Token Usage
- ✅ Tokens per second (by model)
- ✅ Token distribution (prompt vs completion)

## Dashboard Panels

The Grafana dashboard includes 10 panels:

1. **Pipeline Executions** - Rate of pipeline executions by type and status
2. **Pipeline Success Rate** - Gauge showing success percentage
3. **Pipeline Duration** - P95 and P50 latencies
4. **Agent Execution Time** - Bar chart of agent performance
5. **Agent Error Rate** - Error trends by agent
6. **Cost per Hour** - Real-time cost tracking by model
7. **Average Cost per Narrative** - Cost efficiency metric
8. **Quality Scores** - All quality dimensions over time
9. **Token Usage** - Token consumption rate
10. **API Activity** - API calls and errors

## Integration with Production Code

To integrate metrics into your actual code:

```python
from narra_forge.monitoring import MetricsCollector

metrics = MetricsCollector()

# Track pipeline execution
with metrics.track_pipeline("short_story", "fantasy"):
    output = await orchestrator.produce_narrative(brief)

# Track agent execution
with metrics.track_agent("a06_sequential_generator", "gpt-4o"):
    result = await agent.execute(input_data)

# Record custom metrics
metrics.record_tokens("gpt-4o", prompt_tokens=1000, completion_tokens=500)
metrics.record_cost("gpt-4o", "a06_sequential_generator", 0.05)
metrics.record_quality_score("short_story", "coherence", 0.88)
```

## Useful Prometheus Queries

### Pipeline Performance
```promql
# Average pipeline duration
rate(narra_forge_pipeline_duration_seconds_sum[1h]) /
rate(narra_forge_pipeline_duration_seconds_count[1h])

# Pipeline success rate
sum(rate(narra_forge_pipeline_total{status="success"}[5m])) /
sum(rate(narra_forge_pipeline_total[5m]))
```

### Cost Tracking
```promql
# Total cost per hour
sum(rate(narra_forge_cost_usd_total[1h])) * 3600

# Cost by model
sum by (model) (narra_forge_cost_usd_total)
```

### Quality Metrics
```promql
# Average coherence score (24h)
sum(rate(narra_forge_quality_score_sum{metric_type="coherence"}[24h])) /
sum(rate(narra_forge_quality_score_count{metric_type="coherence"}[24h]))
```

## Alerting (Future)

Alert rules can be configured in `monitoring/prometheus/alerts.yml`:

- Pipeline duration too high (>30 minutes)
- Error rate exceeds 10%
- Cost budget exceeded
- Quality score below threshold
- API error rate spike

## Troubleshooting

### Prometheus not scraping metrics

1. Check targets: http://localhost:9090/targets
2. Verify metrics endpoint: `curl http://localhost:8000/metrics`
3. Check Prometheus logs: `docker logs narra-forge-prometheus`

### Grafana not showing data

1. Verify Prometheus datasource is configured
2. Check datasource connection: Configuration → Data Sources → Prometheus → Test
3. Verify metrics exist in Prometheus: http://localhost:9090/graph

### Dashboard not loading

1. Check if JSON file is valid: `jq . monitoring/grafana/dashboards/narra_forge_dashboard.json`
2. Manually import: Grafana → + → Import → Upload JSON
3. Check Grafana logs: `docker logs narra-forge-grafana`

## Stopping Services

```bash
# Stop monitoring stack
docker-compose -f docker-compose.monitoring.yml down

# Stop and remove volumes (cleans all data)
docker-compose -f docker-compose.monitoring.yml down -v

# Stop metrics server
# Press Ctrl+C in terminal where it's running
```

## Data Retention

- **Prometheus**: 15 days by default
- **Grafana**: Permanent dashboard configuration
- **Metrics**: Stored in Docker volumes

To change retention:

```yaml
# monitoring/prometheus.yml
global:
  retention.time: 30d  # Keep 30 days
```

## Production Deployment

For production, you should:

1. ✅ Use persistent volumes (already configured)
2. ✅ Configure alerting (Slack, PagerDuty)
3. ✅ Add Sentry for error tracking
4. ✅ Setup authentication for Grafana
5. ✅ Use HTTPS (reverse proxy)
6. ✅ Backup Grafana dashboards regularly

## Next Steps

- [ ] Add Sentry integration (error tracking)
- [ ] Configure alert notifications
- [ ] Add more custom dashboards
- [ ] Integrate with production code
- [ ] Setup log aggregation (Loki)
- [ ] Add distributed tracing (OpenTelemetry)

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [NARRA_FORGE Monitoring Guide](./MONITORING_GUIDE.md)

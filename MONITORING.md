# NARRA_FORGE V2 Monitoring Guide

Complete guide for monitoring, performance tracking, and optimization.

## Table of Contents

1. [Monitoring Overview](#monitoring-overview)
2. [Prometheus Metrics](#prometheus-metrics)
3. [Grafana Dashboards](#grafana-dashboards)
4. [Sentry Error Tracking](#sentry-error-tracking)
5. [Performance Optimization](#performance-optimization)
6. [Caching Strategy](#caching-strategy)
7. [Load Testing](#load-testing)
8. [Query Optimization](#query-optimization)
9. [Cost Optimization](#cost-optimization)
10. [Alerts & Notifications](#alerts--notifications)

## Monitoring Overview

NARRA_FORGE V2 uses a comprehensive monitoring stack:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Sentry**: Error tracking and performance monitoring
- **Redis**: Caching for performance
- **Locust**: Load testing and performance benchmarking

## Prometheus Metrics

### Available Metrics

**HTTP Metrics:**
- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_in_progress` - Concurrent requests gauge

**Database Metrics:**
- `database_query_duration_seconds` - Query execution time
- `pg_stat_database_numbackends` - Active database connections

**Celery Metrics:**
- `celery_task_duration_seconds` - Task execution time
- `celery_task_status` - Task completion status (success/failure)

**Business Metrics:**
- `active_users` - Number of active users
- `narrative_generation_total` - Total narratives generated

### Querying Metrics

Access Prometheus at: `http://localhost:9090`

**Example Queries:**

```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Database query performance
histogram_quantile(0.99, rate(database_query_duration_seconds_bucket[5m]))
```

## Grafana Dashboards

### Access Grafana

URL: `https://yourdomain.com:3000`
Default credentials: `admin` / `<GRAFANA_PASSWORD from .env>`

### Pre-built Dashboards

**NARRA_FORGE Overview:**
- HTTP request rate and latency
- Database query performance
- Celery task duration
- Active users
- Error rates

**System Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network traffic

### Creating Custom Dashboards

1. Navigate to Dashboards → New Dashboard
2. Add Panel
3. Configure Data Source: Prometheus
4. Write PromQL query
5. Save dashboard

## Sentry Error Tracking

### Configuration

Set in `.env`:
```env
ENABLE_SENTRY=true
SENTRY_DSN=https://your-sentry-dsn
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### Features

- **Automatic Error Capture**: Unhandled exceptions automatically reported
- **Performance Monitoring**: Transaction tracking for slow endpoints
- **Breadcrumbs**: User actions leading up to errors
- **Release Tracking**: Errors associated with app versions
- **User Context**: Errors linked to specific users

### Manual Error Capture

```python
from api.sentry_config import capture_exception, capture_message

try:
    # Risky operation
    pass
except Exception as e:
    capture_exception(e, extra={"context": "value"})

# Informational message
capture_message("Important event occurred", level="warning")
```

### Filtering Sensitive Data

Sentry automatically filters:
- Authorization headers
- Password fields
- API keys
- Tokens

## Performance Optimization

### Response Time Targets

- API endpoints: < 200ms (p95)
- Database queries: < 50ms (p95)
- Page load: < 2s (p95)
- Celery tasks: < 30s (p95)

### Optimization Techniques

**1. Database Optimization**
- Use indexes for frequently queried columns
- Optimize JOIN queries
- Use pagination for large result sets
- Enable query caching

**2. API Optimization**
- Implement caching for read-heavy endpoints
- Use async I/O for external API calls
- Compress responses with gzip
- Implement rate limiting

**3. Frontend Optimization**
- Code splitting
- Image optimization
- Static asset caching
- CDN for static files

## Caching Strategy

### Redis Caching

**Cache Managers:**
```python
from api.cache import user_cache, project_cache, narrative_cache

# Cache user data (30 minutes TTL)
await user_cache.set(user_id, user_data)
user = await user_cache.get(user_id)

# Cache projects (10 minutes TTL)
await project_cache.set(project_id, project_data)

# Invalidate cache
await project_cache.delete(project_id)
await project_cache.invalidate_all()
```

**Cache Decorator:**
```python
from api.cache import cached

@cached(ttl=300, prefix="expensive_operation")
async def expensive_operation(param: str):
    # Expensive computation
    return result
```

### Cache Invalidation

- **Time-based**: Automatic expiration (TTL)
- **Event-based**: Manual invalidation on updates
- **Pattern-based**: Invalidate all related keys

### Cache Warming

Pre-populate cache with frequently accessed data:

```bash
# Warm cache script
python scripts/warm_cache.py
```

## Load Testing

### Running Load Tests

**Install Locust:**
```bash
pip install locust
```

**Run test:**
```bash
# Start Locust web UI
locust -f load_testing/locustfile.py --host=http://localhost:8000

# Headless mode
locust -f load_testing/locustfile.py --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 5m --headless
```

**Access UI:** `http://localhost:8089`

### Test Scenarios

**1. Normal Load**
- 100 users
- Spawn rate: 10/second
- Duration: 5 minutes

**2. Stress Test**
- 500 users
- Spawn rate: 50/second
- Duration: 10 minutes

**3. Spike Test**
- Ramp from 0 to 1000 users in 1 minute
- Hold for 5 minutes
- Ramp down

### Performance Targets

- **Response Time**: 95% < 500ms
- **Error Rate**: < 0.1%
- **Throughput**: > 1000 req/s

## Query Optimization

### Identifying Slow Queries

**PostgreSQL:**
```sql
-- Enable pg_stat_statements
CREATE EXTENSION pg_stat_statements;

-- Find slow queries
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### Optimization Techniques

**1. Add Indexes:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_jobs_project_id ON generation_jobs(project_id);
```

**2. Use EXPLAIN ANALYZE:**
```sql
EXPLAIN ANALYZE SELECT * FROM narratives WHERE project_id = '...';
```

**3. Avoid N+1 Queries:**
```python
# Bad: N+1 queries
projects = await session.execute(select(Project))
for project in projects:
    narratives = await session.execute(
        select(Narrative).where(Narrative.project_id == project.id)
    )

# Good: Single query with JOIN
projects = await session.execute(
    select(Project).options(selectinload(Project.narratives))
)
```

## Cost Optimization

### AI API Cost Monitoring

**Track API costs:**
```python
# Automatically tracked in jobs
job.actual_cost_usd = narrative_generation_cost
```

**Monthly cost report:**
```sql
SELECT 
  DATE_TRUNC('month', created_at) as month,
  SUM(actual_cost_usd) as total_cost,
  COUNT(*) as job_count,
  AVG(actual_cost_usd) as avg_cost
FROM generation_jobs
WHERE status = 'COMPLETED'
GROUP BY month
ORDER BY month DESC;
```

### Infrastructure Cost Optimization

**1. Right-size Resources:**
- Monitor CPU/memory usage
- Scale down during off-peak hours
- Use spot instances for Celery workers

**2. Database Optimization:**
- Use connection pooling
- Archive old data
- Optimize storage with compression

**3. Caching:**
- Cache expensive queries
- Use CDN for static assets
- Enable browser caching

## Alerts & Notifications

### Alert Rules

**High Error Rate:**
```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  annotations:
    summary: "High 5xx error rate"
```

**Slow Response Time:**
```yaml
- alert: SlowResponseTime
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
  for: 10m
  annotations:
    summary: "95th percentile response time > 1s"
```

**Database Connection Saturation:**
```yaml
- alert: DatabaseConnectionsSaturated
  expr: pg_stat_database_numbackends > 80
  for: 5m
  annotations:
    summary: "Database connections near limit"
```

### Notification Channels

Configure in Grafana:
- Email
- Slack
- PagerDuty
- Webhook

## Performance Checklist

- [ ] Prometheus metrics collecting correctly
- [ ] Grafana dashboards configured
- [ ] Sentry error tracking enabled
- [ ] Redis caching implemented
- [ ] Database indexes created
- [ ] Query performance optimized
- [ ] Load testing completed
- [ ] Alerts configured
- [ ] Response time targets met
- [ ] Cost monitoring in place

## Troubleshooting

### High Memory Usage

```bash
# Check container memory
docker stats

# Identify memory-intensive processes
docker exec backend ps aux --sort=-%mem | head

# Restart service
docker-compose -f docker-compose.prod.yml restart backend
```

### Slow Queries

```bash
# Enable query logging
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U narra_forge -c "ALTER SYSTEM SET log_min_duration_statement = 100;"

# Reload config
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U narra_forge -c "SELECT pg_reload_conf();"

# View logs
docker-compose -f docker-compose.prod.yml logs postgres | grep duration
```

### Cache Issues

```bash
# Check Redis memory
docker-compose -f docker-compose.prod.yml exec redis redis-cli INFO memory

# Clear all cache
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL

# Monitor cache hits/misses
docker-compose -f docker-compose.prod.yml exec redis redis-cli INFO stats
```

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Sentry Documentation](https://docs.sentry.io/)
- [Locust Documentation](https://docs.locust.io/)

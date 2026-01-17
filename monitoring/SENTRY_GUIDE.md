# Sentry Integration Guide

Complete guide for error tracking and performance monitoring with Sentry in NARRA_FORGE.

## Overview

Sentry provides:
- **Error Tracking** - Automatic exception capture and reporting
- **Performance Monitoring** - Transaction traces and spans
- **Release Tracking** - Track errors by version
- **Breadcrumbs** - Trail of events leading to errors
- **Context** - Attach custom data to events

## Quick Start

### 1. Get Sentry DSN

1. Sign up at [sentry.io](https://sentry.io) (free tier available)
2. Create a new project (Python)
3. Copy your DSN (looks like: `https://abc123@o123.ingest.sentry.io/456`)

### 2. Configure NARRA_FORGE

Add to your `.env` file:

```bash
# Sentry Configuration
ENABLE_SENTRY=true
SENTRY_DSN=https://your-dsn@o123.ingest.sentry.io/456
SENTRY_ENVIRONMENT=production  # or development, staging
SENTRY_TRACES_SAMPLE_RATE=0.2  # 20% of transactions
SENTRY_PROFILES_SAMPLE_RATE=0.1  # 10% of profiles
```

### 3. Initialize in Your Code

Sentry is automatically initialized when you use NARRA_FORGE:

```python
from narra_forge import BatchOrchestrator
from narra_forge.core import NarraForgeConfig

# Config automatically initializes Sentry if enable_sentry=True
config = NarraForgeConfig()
orchestrator = BatchOrchestrator(config)

# Sentry is now tracking errors!
```

## Manual Initialization

For standalone scripts:

```python
from narra_forge.monitoring import init_sentry

# Initialize Sentry
init_sentry(
    dsn="https://your-dsn@o123.ingest.sentry.io/456",
    environment="production",
    release="narra-forge@2.0.0",
    traces_sample_rate=0.2
)

# Now all exceptions will be captured
```

## Features

### 1. Automatic Error Capture

All uncaught exceptions are automatically sent to Sentry:

```python
async def main():
    # This will be automatically captured by Sentry
    raise ValueError("Something went wrong!")

# No try/except needed - Sentry captures it
asyncio.run(main())
```

### 2. Manual Error Capture

For handled exceptions:

```python
from narra_forge.monitoring import capture_exception

try:
    risky_operation()
except Exception as e:
    # Capture and continue execution
    capture_exception(
        e,
        tags={"agent_id": "a06", "production_type": "short_story"},
        extras={"user_input": input_data}
    )
```

### 3. Performance Monitoring

Track pipeline and agent performance:

```python
from narra_forge.monitoring import SentryTransaction, SentrySpan

# Track pipeline execution
with SentryTransaction(
    op="pipeline.execute",
    name="short_story_generation",
    description="Generate 5k word fantasy story"
) as transaction:
    # Set transaction metadata
    transaction.set_tag("production_type", "short_story")
    transaction.set_tag("genre", "fantasy")

    # Track individual agents as spans
    with SentrySpan(op="agent.execute", description="World Architect"):
        world = await world_architect.execute(brief)

    with SentrySpan(op="agent.execute", description="Sequential Generator"):
        narrative = await generator.execute(world)
```

### 4. Breadcrumbs

Add breadcrumbs to track the sequence of events:

```python
from narra_forge.monitoring import add_breadcrumb

add_breadcrumb(
    message="Starting pipeline execution",
    category="pipeline",
    level="info",
    data={"production_type": "short_story", "genre": "fantasy"}
)

add_breadcrumb(
    message="Agent A02 completed",
    category="agent",
    level="info",
    data={"duration": 12.5, "tokens_used": 1500}
)

# If error occurs, breadcrumbs show what led to it
```

### 5. Custom Context

Attach rich context to errors:

```python
from narra_forge.monitoring import set_context, set_tag

# Set job context
set_context("job", {
    "job_id": "job_123",
    "production_type": "novella",
    "genre": "scifi",
    "word_count_target": 25000
})

# Set searchable tags
set_tag("production_type", "novella")
set_tag("agent_id", "a06_sequential_generator")
set_tag("model", "gpt-4o")

# Tags are searchable in Sentry UI
```

### 6. User Tracking

Track which users encounter errors:

```python
from narra_forge.monitoring import set_user

set_user(
    user_id="user_123",
    email="user@example.com",
    username="john_doe"
)
```

### 7. Custom Messages

Send informational messages:

```python
from narra_forge.monitoring import capture_message

capture_message(
    "Pipeline completed with quality score below threshold",
    level="warning",
    tags={"coherence_score": "0.82", "threshold": "0.85"}
)
```

## Integration with Orchestrator

The BatchOrchestrator automatically integrates Sentry:

```python
# narra_forge/core/orchestrator.py

from narra_forge.monitoring import (
    init_sentry,
    SentryTransaction,
    SentrySpan,
    set_context,
    add_breadcrumb
)

class BatchOrchestrator:
    def __init__(self, config):
        self.config = config

        # Initialize Sentry if enabled
        if config.enable_sentry and config.sentry_dsn:
            init_sentry(
                dsn=config.sentry_dsn,
                environment=config.sentry_environment,
                release=f"narra-forge@{VERSION}",
                traces_sample_rate=config.sentry_traces_sample_rate
            )

    async def produce_narrative(self, brief):
        # Track pipeline as transaction
        with SentryTransaction(
            op="pipeline.execute",
            name=f"{brief.production_type}_generation"
        ) as transaction:
            transaction.set_tag("production_type", brief.production_type)
            transaction.set_tag("genre", brief.genre)

            # Add context
            set_context("pipeline", {
                "brief": brief.dict(),
                "config": self.config.dict()
            })

            # Track each stage
            for stage in self.stages:
                add_breadcrumb(
                    message=f"Starting stage: {stage.name}",
                    category="pipeline",
                    level="info"
                )

                with SentrySpan(op="stage.execute", description=stage.name):
                    try:
                        result = await stage.execute()
                    except Exception as e:
                        # Automatically captured by Sentry
                        raise
```

## Best Practices

### 1. Sample Rates

Don't send 100% of transactions in production:

```python
# Development: High sample rate for testing
init_sentry(traces_sample_rate=1.0)  # 100%

# Staging: Medium sample rate
init_sentry(traces_sample_rate=0.5)  # 50%

# Production: Low sample rate to reduce costs
init_sentry(traces_sample_rate=0.1)  # 10%
```

### 2. Filter Sensitive Data

Don't send API keys or user data:

```python
# Good
set_context("api", {"model": "gpt-4o", "tokens": 5000})

# Bad
set_context("api", {"api_key": "sk-...", "model": "gpt-4o"})
```

### 3. Use Tags for Searchability

Tags are indexed and searchable:

```python
# Good - searchable dimensions
set_tag("production_type", "short_story")
set_tag("genre", "fantasy")
set_tag("agent_id", "a06")
set_tag("model", "gpt-4o")

# Bad - too granular for tags
set_tag("timestamp", "2024-01-17T10:30:00")  # Use context instead
```

### 4. Meaningful Transaction Names

```python
# Good
SentryTransaction(op="pipeline.execute", name="short_story_fantasy_5k")

# Bad
SentryTransaction(op="task", name="task_123")
```

### 5. Contextual Breadcrumbs

```python
# Good - actionable information
add_breadcrumb(
    message="API rate limit encountered",
    category="api",
    level="warning",
    data={"retry_attempt": 2, "wait_time": 5}
)

# Bad - not useful
add_breadcrumb(message="Thing happened", category="misc")
```

## Alerts

Configure alerts in Sentry UI:

1. **Error Rate** - Alert when error rate exceeds threshold
2. **Performance** - Alert when P95 duration exceeds threshold
3. **Quality** - Alert when quality scores drop
4. **Cost** - Alert when costs spike unexpectedly

Example alert rules:
- `error.rate > 10% for 5 minutes`
- `transaction.duration.p95 > 1800s`
- `tag.coherence_score < 0.85 for 10 minutes`

## Sentry Dashboard

Access your Sentry dashboard at:
- https://sentry.io/organizations/your-org/issues/

Key sections:
- **Issues** - All errors grouped and prioritized
- **Performance** - Transaction traces and slow operations
- **Releases** - Track errors by version
- **Alerts** - Configure and view alerts
- **Discover** - Query and analyze event data

## Cost Optimization

Sentry pricing is based on events sent:

**Free Tier:**
- 5,000 errors/month
- 10,000 transactions/month

**Optimization strategies:**
1. Use low sample rates in production (10-20%)
2. Filter known non-critical errors (see `before_send_hook`)
3. Use breadcrumbs instead of custom events
4. Consolidate similar errors

## Testing

Test Sentry integration:

```bash
# Run test script
python monitoring/test_sentry.py
```

This will:
- Send test error
- Send test transaction
- Verify Sentry is receiving data

## Troubleshooting

### Sentry not capturing errors

1. Check DSN is set: `echo $SENTRY_DSN`
2. Verify `enable_sentry=True` in config
3. Check Sentry logs: Set `debug=True` in init

```python
init_sentry(dsn="...", debug=True)
```

### Too many events

Reduce sample rates:

```python
init_sentry(
    traces_sample_rate=0.05,  # 5% instead of 10%
    profiles_sample_rate=0.02  # 2% instead of 10%
)
```

### Missing context

Ensure you're setting context before errors occur:

```python
# Set context early in execution
set_context("job", {...})
set_tag("production_type", "...")

# Then run risky code
await execute_pipeline()
```

## Resources

- [Sentry Python SDK Docs](https://docs.sentry.io/platforms/python/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Error Tracking Best Practices](https://docs.sentry.io/product/issues/)

## Next Steps

- [ ] Sign up for Sentry account
- [ ] Add DSN to `.env`
- [ ] Enable Sentry in production
- [ ] Configure alerts
- [ ] Review errors weekly
- [ ] Optimize sample rates based on volume

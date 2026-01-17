# Checkpointing System

Complete guide to NARRA_FORGE's checkpointing and state management system.

## Overview

The checkpointing system enables:
- ✅ **Save pipeline state** after each stage
- ✅ **Resume from failure** without losing progress
- ✅ **Track costs** and token usage
- ✅ **Monitor progress** for long-running jobs
- ✅ **Recover gracefully** from crashes or errors

## Why Checkpointing?

Long-form narrative generation (novels, sagas) can take **hours** and cost **$50-200**.

Without checkpointing:
- ❌ Crash at stage 8/10 = lose $150 of work
- ❌ Network error = start from scratch
- ❌ No progress visibility
- ❌ Can't pause/resume

With checkpointing:
- ✅ Resume from last successful stage
- ✅ Only pay for new work
- ✅ See real-time progress
- ✅ Pause/resume anytime

## Quick Start

### Basic Usage

```python
from narra_forge import BatchOrchestrator
from narra_forge.core import CheckpointManager, PipelineStateManager, ProductionBrief

# Initialize
checkpoint_mgr = CheckpointManager(checkpoint_dir="./checkpoints")
state_mgr = PipelineStateManager(checkpoint_mgr)

# Create job
job_id = "novel_fantasy_001"
brief = ProductionBrief(...)

# Initialize or resume
state = state_mgr.initialize_job(job_id, brief)

# Execute pipeline with checkpointing
orchestrator = BatchOrchestrator(config)

for stage in pipeline_stages:
    # Check if already completed
    if stage.name in state["completed_stages"]:
        print(f"✓ {stage.name} already completed, skipping...")
        continue

    # Execute stage
    output = await stage.execute(state)

    # Save checkpoint
    state = state_mgr.save_stage_result(
        state=state,
        stage_name=stage.name,
        stage_output=output,
        cost_usd=output.cost_usd,
        tokens_used=output.tokens_used
    )

    print(f"✓ {stage.name} completed and checkpointed")

# Clean up on success
state_mgr.cleanup_on_success(job_id)
```

### Resume After Failure

```python
# Job crashed at stage 6/10

# Resume
job_id = "novel_fantasy_001"
state = state_mgr.resume_job(job_id)

print(f"Resuming from stage {len(state['completed_stages'])}/10")
print(f"Cost so far: ${state['cumulative_cost_usd']:.2f}")

# Continue from where we left off
next_stage = state_mgr.get_next_stage(state, all_stages)
# ... continue execution
```

## Architecture

### CheckpointManager

Low-level manager for checkpoint files.

**Key Methods:**
- `save_checkpoint()` - Save stage output
- `load_checkpoint()` - Load stage output
- `get_latest_checkpoint()` - Get most recent checkpoint
- `list_checkpoints()` - List all checkpoints for job
- `delete_checkpoints()` - Clean up after completion

**Storage Format:**
```
checkpoints/
└── novel_fantasy_001/
    ├── brief.json                          # Original brief
    ├── metadata.json                       # Job metadata
    ├── 01_brief_interpreter.checkpoint     # Binary (pickle)
    ├── 01_brief_interpreter.json          # JSON (for inspection)
    ├── 02_world_architect.checkpoint
    ├── 02_world_architect.json
    └── ...
```

### PipelineStateManager

High-level manager for pipeline execution state.

**Key Methods:**
- `initialize_job()` - Start new or resume existing
- `resume_job()` - Load all checkpoints and rebuild state
- `save_stage_result()` - Save stage output and update state
- `get_next_stage()` - Determine next stage to execute
- `cleanup_on_success()` - Clean up after successful completion
- `rollback_on_failure()` - Mark job for retry

**State Dictionary:**
```python
{
    "job_id": "novel_fantasy_001",
    "brief": ProductionBrief(...),
    "completed_stages": [
        "01_brief_interpreter",
        "02_world_architect",
        "03_character_architect"
    ],
    "stage_outputs": {
        "01_brief_interpreter": {...},
        "02_world_architect": {...},
        "03_character_architect": {...}
    },
    "cumulative_cost_usd": 12.45,
    "cumulative_tokens": 25000,
    "started_at": "2026-01-17T10:30:00",
    "resumed_at": "2026-01-17T12:15:00"  # If resumed
}
```

## Integration with Orchestrator

### Orchestrator with Checkpointing

```python
class BatchOrchestrator:
    def __init__(self, config, enable_checkpointing=True):
        self.config = config
        self.enable_checkpointing = enable_checkpointing

        if enable_checkpointing:
            self.checkpoint_mgr = CheckpointManager()
            self.state_mgr = PipelineStateManager(self.checkpoint_mgr)

    async def produce_narrative(
        self,
        brief: ProductionBrief,
        job_id: Optional[str] = None,
        resume: bool = False
    ):
        # Generate job ID
        if not job_id:
            import uuid
            job_id = f"{brief.production_type}_{uuid.uuid4().hex[:8]}"

        # Initialize or resume
        if self.enable_checkpointing:
            state = self.state_mgr.initialize_job(job_id, brief)

            # Check if resuming
            if resume and state["completed_stages"]:
                print(f"✓ Resuming from stage {len(state['completed_stages'])}/10")
                print(f"  Cost so far: ${state['cumulative_cost_usd']:.2f}")
        else:
            state = {"job_id": job_id, "brief": brief, "completed_stages": []}

        # Execute pipeline
        try:
            for stage in self.stages:
                # Skip if already completed
                if stage.name in state.get("completed_stages", []):
                    continue

                # Execute stage
                result = await stage.execute(state)

                # Save checkpoint
                if self.enable_checkpointing:
                    state = self.state_mgr.save_stage_result(
                        state=state,
                        stage_name=stage.name,
                        stage_output=result,
                        cost_usd=result.get("cost_usd", 0.0),
                        tokens_used=result.get("tokens_used", 0)
                    )

            # Success - clean up
            if self.enable_checkpointing:
                self.state_mgr.cleanup_on_success(job_id)

            return self._build_output(state)

        except Exception as e:
            # Failure - keep checkpoints for retry
            if self.enable_checkpointing:
                failed_stage = self.state_mgr.get_next_stage(state, self.stage_names)
                self.state_mgr.rollback_on_failure(job_id, failed_stage)

            raise
```

### Usage

```python
# Start new job
orchestrator = BatchOrchestrator(config, enable_checkpointing=True)
output = await orchestrator.produce_narrative(brief)

# Resume after failure
output = await orchestrator.produce_narrative(brief, job_id="novel_001", resume=True)
```

## Progress Monitoring

### Check Progress

```python
checkpoint_mgr = CheckpointManager()

# Get progress
progress = checkpoint_mgr.get_progress(job_id="novel_001", total_stages=10)

print(f"Progress: {progress['percentage']:.1f}%")
print(f"Completed: {progress['completed_stages']}/{progress['total_stages']}")
print(f"Latest: {progress['latest_stage']}")
print(f"Cost so far: ${progress['total_cost_usd']:.2f}")
```

### Real-time Progress (WebSocket)

```python
# In FastAPI (Phase 2)
@app.websocket("/ws/jobs/{job_id}")
async def job_progress(websocket: WebSocket, job_id: str):
    await websocket.accept()

    while True:
        progress = checkpoint_mgr.get_progress(job_id)
        await websocket.send_json(progress)
        await asyncio.sleep(5)  # Update every 5 seconds
```

## Cost Management

### Track Costs

```python
# After each stage
state = state_mgr.save_stage_result(
    state=state,
    stage_name="06_sequential_generator",
    stage_output=output,
    cost_usd=25.50,  # This stage cost $25.50
    tokens_used=150000
)

# Check cumulative cost
if state["cumulative_cost_usd"] > max_cost_per_job:
    raise CostLimitExceeded(f"Cost ${state['cumulative_cost_usd']:.2f} exceeds limit ${max_cost_per_job:.2f}")
```

### Cost Rollback

If job fails at stage 7/10:
- ✅ You paid for stages 1-6 ($30)
- ✅ Stage 7 failed ($0 wasted - not checkpointed)
- ✅ Resume from stage 7 (only pay for 7-10)
- ❌ Without checkpointing: lose $30, start from scratch

## Cleanup

### Manual Cleanup

```python
# Delete specific job
checkpoint_mgr.delete_checkpoints(job_id="novel_001")

# Clean up old checkpoints (>30 days)
cleaned = checkpoint_mgr.cleanup_old_checkpoints(max_age_days=30)
print(f"Cleaned up {cleaned} old jobs")
```

### Automatic Cleanup

```python
# In orchestrator - clean up on success
if self.enable_checkpointing:
    self.state_mgr.cleanup_on_success(job_id)
```

## Best Practices

### 1. Always Enable for Long Jobs

```python
# Short story (<10k words): checkpointing optional
orchestrator = BatchOrchestrator(config, enable_checkpointing=False)

# Novel (80k words): checkpointing recommended
orchestrator = BatchOrchestrator(config, enable_checkpointing=True)

# Saga (150k+ words): checkpointing REQUIRED
orchestrator = BatchOrchestrator(config, enable_checkpointing=True)
```

### 2. Use Meaningful Job IDs

```python
# Good
job_id = f"{brief.production_type}_{brief.genre}_{timestamp}"
# Example: "novel_fantasy_20260117_103000"

# Bad
job_id = "job_123"  # Not descriptive
```

### 3. Monitor Progress

```python
# Start job
asyncio.create_task(orchestrator.produce_narrative(brief, job_id))

# Monitor in parallel
while True:
    progress = checkpoint_mgr.get_progress(job_id)
    if progress["percentage"] == 100:
        break
    print(f"Progress: {progress['percentage']:.1f}%")
    await asyncio.sleep(30)
```

### 4. Handle Failures Gracefully

```python
try:
    output = await orchestrator.produce_narrative(brief, job_id)
except Exception as e:
    # Check if we can resume
    if checkpoint_mgr.can_resume(job_id):
        print("❌ Job failed, but can be resumed")
        print(f"   Use: orchestrator.produce_narrative(brief, job_id='{job_id}', resume=True)")
    else:
        print("❌ Job failed with no checkpoints")
    raise
```

### 5. Clean Up Regularly

```python
# Cron job or scheduled task
def daily_cleanup():
    checkpoint_mgr = CheckpointManager()
    cleaned = checkpoint_mgr.cleanup_old_checkpoints(max_age_days=30)
    print(f"Cleaned up {cleaned} old checkpoints")
```

## Troubleshooting

### Checkpoint File Corrupted

```python
# Delete corrupted checkpoint
checkpoint_mgr.delete_checkpoints(job_id)

# Start fresh
state = state_mgr.initialize_job(job_id, brief)
```

### Disk Space Issues

```python
# Check checkpoint directory size
import os
total_size = sum(
    os.path.getsize(os.path.join(dirpath, filename))
    for dirpath, _, filenames in os.walk("checkpoints")
    for filename in filenames
)
print(f"Checkpoints size: {total_size / 1024 / 1024:.2f} MB")

# Clean up old jobs
checkpoint_mgr.cleanup_old_checkpoints(max_age_days=7)
```

### Resume Not Working

```python
# Check if checkpoints exist
checkpoints = checkpoint_mgr.list_checkpoints(job_id)
print(f"Found {len(checkpoints)} checkpoints: {checkpoints}")

# Check brief saved
brief = checkpoint_mgr.load_brief(job_id)
if not brief:
    print("❌ Brief not saved - cannot resume")
```

## Advanced Usage

### Custom Checkpoint Logic

```python
class CustomCheckpointManager(CheckpointManager):
    def save_checkpoint(self, job_id, stage_name, stage_output, metadata=None):
        # Add custom logic (e.g., upload to S3)
        super().save_checkpoint(job_id, stage_name, stage_output, metadata)

        # Upload to cloud storage
        s3_client.upload_file(
            f"checkpoints/{job_id}/{stage_name}.checkpoint",
            bucket="narra-forge-checkpoints",
            key=f"{job_id}/{stage_name}.checkpoint"
        )
```

### Partial Resume

```python
# Resume from specific stage (not latest)
state = state_mgr.resume_job(job_id)

# Manually modify completed stages
state["completed_stages"] = state["completed_stages"][:5]  # Reset to stage 5

# Continue from stage 6
```

## Resources

- [NARRA_FORGE Architecture](../ARCHITECTURE_V2.md)
- [Long-Form Testing](../tests/longform/README.md)
- [Orchestrator Implementation](../narra_forge/core/orchestrator.py)
- [Checkpointing Implementation](../narra_forge/core/checkpointing.py)

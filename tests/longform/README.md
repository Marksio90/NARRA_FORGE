# Long-Form Testing Suite

Comprehensive testing for long-form narratives (novels 120k+ words).

## Overview

Long-form tests verify that NARRA_FORGE can handle:
- **Novels** (40k-120k words)
- **Epic Sagas** (120k+ words, multi-volume)

These tests ensure:
- ✅ Pipeline completes without crashes
- ✅ Memory usage stays reasonable
- ✅ Quality remains high throughout
- ✅ Cost tracking is accurate
- ✅ Checkpointing allows recovery from failures

## Test Categories

### 1. Mock Tests (Fast, Free)

Run without calling OpenAI API - use mocked responses.

```bash
# Run all mock tests
pytest tests/longform/ -m mock -v

# Run specific novel length
pytest tests/longform/test_novel_mock.py -v
pytest tests/longform/test_saga_mock.py -v
```

**Duration:** ~5-10 minutes
**Cost:** $0 (mocked)

### 2. Integration Tests (Slow, Paid)

Run with real OpenAI API calls.

```bash
# Run integration tests (requires OPENAI_API_KEY)
pytest tests/longform/ -m integration -v

# Run with cost limit
pytest tests/longform/ -m integration --max-cost=50
```

**Duration:** 2-6 hours
**Cost:** $20-100 (depending on length)

⚠️ **Warning:** These tests consume real API credits!

### 3. Stress Tests (Very Slow, Expensive)

Test extreme scenarios (500k+ words).

```bash
# Run stress tests
pytest tests/longform/ -m stress -v
```

**Duration:** 6-12 hours
**Cost:** $200-500

⚠️ **Warning:** Only run in production validation!

## Test Structure

```
tests/longform/
├── README.md                    # This file
├── conftest.py                  # Shared fixtures
├── test_novel_mock.py          # Mock tests (40k-120k words)
├── test_saga_mock.py           # Mock tests (120k+ words)
├── test_novel_integration.py   # Real API tests (novels)
├── test_saga_integration.py    # Real API tests (sagas)
├── test_stress.py              # Stress tests (500k+ words)
├── test_memory_management.py   # Memory usage tests
├── test_checkpointing.py       # Recovery tests
└── fixtures/
    ├── mock_responses.py       # Mocked OpenAI responses
    └── sample_briefs.py        # Test briefs
```

## Running Tests

### Quick Validation (Mock Only)

```bash
# Fast smoke test
pytest tests/longform/test_novel_mock.py::test_short_novel -v

# Full mock suite
pytest tests/longform/ -m mock -v
```

### Production Validation (Real API)

```bash
# Test one complete novel generation
pytest tests/longform/test_novel_integration.py::test_complete_novel -v

# Test saga generation with checkpointing
pytest tests/longform/test_saga_integration.py::test_saga_with_checkpoints -v
```

### Memory Profiling

```bash
# Profile memory usage
pytest tests/longform/test_memory_management.py --profile-memory -v
```

## Test Scenarios

### Scenario 1: Standard Novel (80k words)

**Test:** `test_novel_integration.py::test_complete_novel`

- Production type: `novel`
- Target: 80,000 words
- Genre: Fantasy
- Expected duration: 2-3 hours
- Expected cost: $30-50

**Validates:**
- Complete pipeline execution
- Quality score >0.85
- Coherence across all chapters
- Memory usage <4GB

### Scenario 2: Epic Saga (150k words)

**Test:** `test_saga_integration.py::test_epic_saga`

- Production type: `epic_saga`
- Target: 150,000 words
- Genre: Sci-fi
- Expected duration: 4-6 hours
- Expected cost: $60-100

**Validates:**
- Multi-volume structure
- Cross-volume continuity
- Character development tracking
- Checkpointing and recovery

### Scenario 3: Extreme Length (500k words)

**Test:** `test_stress.py::test_extreme_length`

- Production type: `epic_saga`
- Target: 500,000 words
- Genre: Fantasy
- Expected duration: 12-18 hours
- Expected cost: $200-400

**Validates:**
- System stability under load
- Memory doesn't leak
- Quality doesn't degrade
- Cost optimization works

## Success Criteria

### Quality

- ✅ Coherence score: ≥0.85 (all segments)
- ✅ Logic score: ≥0.85
- ✅ Psychology score: ≥0.85
- ✅ Temporal score: ≥0.85
- ✅ No plot holes
- ✅ Character consistency

### Performance

- ✅ Memory usage: <4GB peak
- ✅ No memory leaks
- ✅ Cost per 1k words: <$0.50
- ✅ Pipeline completes without crashes

### Reliability

- ✅ Checkpointing works (can resume from failure)
- ✅ Retry logic handles transient errors
- ✅ Cost tracking is accurate (±2%)
- ✅ Output files are valid and complete

## Troubleshooting

### Test Timeout

```bash
# Increase timeout
pytest tests/longform/ --timeout=7200  # 2 hours
```

### Out of Memory

```bash
# Reduce batch size in config
export SEGMENT_BATCH_SIZE=5  # Default: 10
```

### API Rate Limits

```bash
# Add delay between API calls
export API_DELAY_MS=1000  # 1 second delay
```

### Cost Limit Exceeded

```bash
# Set max cost per test
pytest tests/longform/ --max-cost=100
```

## Cost Estimates

| Test Type | Word Count | Expected Cost | Duration |
|-----------|-----------|---------------|----------|
| Mock (Novella) | 25k | $0 | 2 min |
| Mock (Novel) | 80k | $0 | 5 min |
| Mock (Saga) | 150k | $0 | 10 min |
| Integration (Novella) | 25k | $10-15 | 30 min |
| Integration (Novel) | 80k | $30-50 | 2-3 hours |
| Integration (Saga) | 150k | $60-100 | 4-6 hours |
| Stress (Extreme) | 500k | $200-400 | 12-18 hours |

**Total for full suite:** ~$300-500

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Long-Form Tests

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  mock-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run mock tests
        run: pytest tests/longform/ -m mock

  integration-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        run: pytest tests/longform/ -m integration --max-cost=50
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Metrics Collected

During long-form tests, we collect:

- **Execution time** (total, per stage, per agent)
- **Memory usage** (peak, average, by stage)
- **Token consumption** (total, per model, per stage)
- **Cost** (total, per stage, per 1k words)
- **Quality scores** (per segment, overall)
- **Error rates** (retries, failures)

All metrics are exported to:
- CSV files (`output/metrics/`)
- Prometheus (if enabled)
- Test reports

## Best Practices

1. **Always run mock tests first** - Catch bugs before spending money
2. **Set cost limits** - Prevent runaway API costs
3. **Use checkpointing** - Can resume if tests fail
4. **Monitor memory** - Ensure no leaks in long runs
5. **Review quality** - Don't just check for completion
6. **Archive outputs** - Keep generated narratives for manual review

## Next Steps

After successful long-form testing:

1. ✅ Verify all tests pass
2. ✅ Review quality scores
3. ✅ Check memory profiles
4. ✅ Validate cost estimates
5. ✅ Update documentation
6. ✅ Enable in CI/CD pipeline
7. ✅ Deploy to production

## Resources

- [NARRA_FORGE Architecture](../../ARCHITECTURE_V2.md)
- [Testing Guide](../README.md)
- [Monitoring Guide](../../monitoring/MONITORING_GUIDE.md)
- [Checkpointing System](../../docs/CHECKPOINTING.md)

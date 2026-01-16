# NARRA_FORGE Test Suite

Comprehensive test suite for NARRA_FORGE V2 platform.

## Current Status

**Total Coverage: 39%** (Target: 80%+)

### Coverage by Module:
- ✅ `core/types.py`: **100%**
- ✅ `core/config.py`: **89%**
- ⚠️ `core/orchestrator.py`: **12%** (needs work)
- ⚠️ `agents/*`: **15-29%** (needs work)
- ⚠️ `models/openai_client.py`: **19%** (needs work)
- ⚠️ `models/model_router.py`: **23%** (needs work)
- ✅ `memory/storage.py`: **71%**

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and pytest configuration
├── unit/                       # Unit tests (fast, isolated)
│   ├── test_config.py         # ✅ 8 tests passing
│   ├── test_types.py          # ✅ 7 tests passing
│   ├── agents/
│   │   ├── test_base_agent.py
│   │   ├── test_a01_brief_interpreter.py
│   │   └── ... (tests for all 10 agents)
│   ├── memory/
│   │   └── test_memory.py     # ✅ 5 tests passing
│   ├── models/
│   │   ├── test_model_router.py
│   │   └── test_openai_client.py
│   └── utils/
│       └── test_text_utils.py
├── integration/                # Integration tests (multi-component)
│   ├── test_pipeline.py       # Full 10-stage pipeline
│   ├── test_memory_sync.py    # Memory persistence
│   └── test_error_recovery.py # Error handling
├── e2e/                        # End-to-end tests (full workflows)
│   ├── test_short_story.py    # 5k-10k words
│   ├── test_novella.py        # 10k-40k words
│   ├── test_novel.py          # 40k-120k words
│   └── test_saga.py           # 120k+ words
└── performance/                # Performance & benchmarking
    ├── test_cost_tracking.py  # Verify cost accuracy
    ├── test_token_limits.py   # Test max_tokens handling
    └── test_memory_leaks.py   # Memory profiling
```

## Running Tests

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=narra_forge --cov-report=html
# View report: open htmlcov/index.html
```

### Run by Category
```bash
# Unit tests only (fast)
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v -m integration

# E2E tests (slow, requires API key)
python -m pytest tests/e2e/ -v -m e2e

# Performance tests
python -m pytest tests/performance/ -v -m performance
```

### Run by Marker
```bash
# Fast tests only
python -m pytest -m "unit" -v

# Skip slow tests
python -m pytest -m "not slow" -v

# Integration tests only
python -m pytest -m "integration" -v
```

## Test Markers

Tests are marked with the following markers:

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (may call APIs)
- `@pytest.mark.e2e` - End-to-end tests (full pipeline, slow)
- `@pytest.mark.performance` - Performance and benchmarking tests
- `@pytest.mark.slow` - Tests that take >5 seconds

## Shared Fixtures

Available in `conftest.py`:

### Configuration
- `test_config` - Test configuration with dummy API key
- `temp_db_path` - Temporary database path

### Memory System
- `memory_system` - Initialized MemorySystem with temp DB

### Sample Data
- `sample_production_brief` - ProductionBrief for testing
- `sample_world_dict` - World data for testing
- `sample_character_dict` - Character data for testing
- `sample_narrative_structure` - Narrative structure for testing

### Mocks
- `mock_openai_client` - Mocked OpenAI client (no API calls)

## Writing Tests

### Unit Test Example
```python
import pytest

@pytest.mark.unit
class TestMyComponent:
    """Test MyComponent functionality"""

    def test_initialization(self, test_config):
        """Test component can be initialized"""
        component = MyComponent(test_config)
        assert component is not None

    @pytest.mark.asyncio
    async def test_async_operation(self, test_config):
        """Test async method"""
        component = MyComponent(test_config)
        result = await component.do_something()
        assert result is not None
```

### Integration Test Example
```python
import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.integration
class TestPipelineIntegration:
    """Test pipeline integration"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_pipeline(self, test_config, memory_system, sample_production_brief):
        """Test full pipeline execution"""
        orchestrator = ProductionOrchestrator(test_config, memory_system)

        # Mock API calls
        with patch.object(orchestrator, '_call_openai', new_callable=AsyncMock) as mock:
            mock.return_value = {"result": "test"}
            result = await orchestrator.produce_narrative(sample_production_brief)

        assert result is not None
```

## Test Standards

1. **Naming Convention:**
   - Test files: `test_<module_name>.py`
   - Test classes: `TestComponentName`
   - Test functions: `test_<what_it_tests>`

2. **Documentation:**
   - Every test class must have a docstring
   - Complex tests must have docstrings explaining what they test

3. **Isolation:**
   - Unit tests must NOT call external APIs
   - Use mocks for OpenAI API calls
   - Use temporary databases (via fixtures)

4. **Speed:**
   - Unit tests should run in <1 second
   - Mark slow tests with `@pytest.mark.slow`

5. **Assertions:**
   - Use descriptive assertions
   - Test both success and failure cases
   - Test edge cases

## TODO: Tests to Implement

### High Priority (Target: Week 1-2)
- [ ] Fix failing agent tests (adjust to real API)
- [ ] Fix failing model_router tests
- [ ] Add tests for orchestrator (currently 12% coverage)
- [ ] Add tests for OpenAI client (currently 19% coverage)
- [ ] Add tests for all 10 agents (currently 15-29% coverage)

### Medium Priority (Target: Week 3-4)
- [ ] Integration test for full pipeline with mocked API
- [ ] Integration test for memory persistence
- [ ] Integration test for error recovery
- [ ] E2E test for short story generation (requires API key)

### Low Priority (Target: Week 5-6)
- [ ] E2E tests for novella, novel, saga
- [ ] Performance tests for cost tracking
- [ ] Performance tests for token limits
- [ ] Performance tests for memory leaks
- [ ] Load testing (concurrent generations)

## CI/CD Integration

Tests run automatically on:
- Every pull request
- Every commit to main branch
- Nightly (for long-running E2E tests)

### GitHub Actions Workflow
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/unit/ --cov=narra_forge --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Resources

- Pytest docs: https://docs.pytest.org/
- Pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- Coverage.py: https://coverage.readthedocs.io/
- Mock documentation: https://docs.python.org/3/library/unittest.mock.html

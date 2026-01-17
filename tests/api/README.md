# API Integration Tests

Comprehensive integration tests for the NARRA_FORGE V2 API.

## Overview

These tests verify the complete functionality of all API endpoints including:
- Authentication (register, login, token refresh)
- Projects (CRUD operations)
- Jobs (creation, monitoring, cancellation)
- Narratives (viewing, deletion)

## Test Database

Tests use a separate test database (`narra_forge_test`) to avoid interfering with development data.

The database is automatically created and destroyed for each test function, ensuring complete isolation.

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Ensure PostgreSQL is running with test database:
```bash
createdb narra_forge_test
```

3. Set environment variables:
```bash
export DATABASE_URL="postgresql://narra_forge:narra_forge@localhost:5432/narra_forge_test"
export JWT_SECRET_KEY="test-secret-key-change-in-production"
```

### Run All API Tests

```bash
pytest tests/api/ -v
```

### Run Specific Test Files

```bash
# Auth tests only
pytest tests/api/test_auth.py -v

# Projects tests only
pytest tests/api/test_projects.py -v

# Jobs tests only
pytest tests/api/test_jobs.py -v

# Narratives tests only
pytest tests/api/test_narratives.py -v
```

### Run with Coverage

```bash
pytest tests/api/ --cov=api --cov-report=html
```

### Run Specific Test Class

```bash
pytest tests/api/test_auth.py::TestAuthRegistration -v
```

### Run Specific Test

```bash
pytest tests/api/test_auth.py::TestAuthRegistration::test_register_success -v
```

## Test Structure

```
tests/api/
├── __init__.py
├── conftest.py              # Fixtures and test configuration
├── test_auth.py             # Authentication tests (60+ tests)
├── test_projects.py         # Projects CRUD tests (40+ tests)
├── test_jobs.py             # Jobs tests (30+ tests)
├── test_narratives.py       # Narratives tests (25+ tests)
└── README.md                # This file
```

## Test Coverage

Current test coverage:
- **Authentication**: ~95% (register, login, refresh, protected routes)
- **Projects**: ~90% (CRUD, pagination, user isolation, cascading deletes)
- **Jobs**: ~85% (creation, listing, filtering, cancellation, limits)
- **Narratives**: ~80% (listing, viewing, deletion, project stats)

## Fixtures

Common fixtures available in `conftest.py`:

- `client`: Async HTTP test client
- `db_session`: Fresh database session for each test
- `test_user`: Pre-registered test user with auth tokens
- `auth_headers`: Authorization headers with Bearer token
- `test_project`: Pre-created test project

## Writing New Tests

Example test structure:

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestFeature:
    """Test feature description."""

    async def test_feature_success(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test successful feature execution."""
        response = await client.post(
            "/endpoint",
            json={"data": "value"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["field"] == "expected_value"
```

## Continuous Integration

These tests are run automatically on:
- Every commit to main branch
- Every pull request
- Nightly builds

CI configuration: `.github/workflows/test.yml`

## Troubleshooting

### Database Connection Issues

Ensure PostgreSQL is running and test database exists:
```bash
psql -U narra_forge -c "SELECT 1" narra_forge_test
```

### Import Errors

Make sure you're running from the project root:
```bash
cd /home/user/NARRA_FORGE
pytest tests/api/
```

### Async Warnings

If you see warnings about event loops, ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

## Next Steps

- [ ] Add WebSocket tests for real-time job updates
- [ ] Add load testing with Locust
- [ ] Add API contract tests with Dredd
- [ ] Add mutation testing with mutmut

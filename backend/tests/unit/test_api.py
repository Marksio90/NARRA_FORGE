"""Tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "NARRA_FORGE"
    assert "version" in data
    assert "environment" in data


def test_root_endpoint() -> None:
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["docs"] == "/docs"

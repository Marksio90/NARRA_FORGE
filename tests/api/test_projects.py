"""
Projects API Integration Tests.

Tests for project CRUD operations.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestProjectsCreate:
    """Test project creation."""

    async def test_create_project_success(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test successful project creation."""
        response = await client.post(
            "/projects",
            json={
                "name": "New Project",
                "description": "A brand new project",
                "default_genre": "Fantasy",
                "default_production_type": "Novel"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert data["name"] == "New Project"
        assert data["description"] == "A brand new project"
        assert data["default_genre"] == "Fantasy"
        assert data["default_production_type"] == "Novel"
        assert "id" in data
        assert data["narrative_count"] == 0
        assert data["total_word_count"] == 0
        assert data["total_cost_usd"] == 0.0

    async def test_create_project_minimal(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating project with only required fields."""
        response = await client.post(
            "/projects",
            json={"name": "Minimal Project"},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Project"
        assert data["description"] is None

    async def test_create_project_without_auth_fails(self, client: AsyncClient):
        """Test creating project without authentication fails."""
        response = await client.post(
            "/projects",
            json={"name": "Unauthorized Project"}
        )

        assert response.status_code == 401

    async def test_create_project_empty_name_fails(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating project with empty name fails."""
        response = await client.post(
            "/projects",
            json={"name": ""},
            headers=auth_headers
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestProjectsList:
    """Test project listing."""

    async def test_list_projects_empty(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test listing projects when none exist."""
        response = await client.get("/projects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["projects"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20

    async def test_list_projects_with_data(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test listing projects with data."""
        response = await client.get("/projects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 1
        assert len(data["projects"]) == 1
        assert data["projects"][0]["id"] == test_project["id"]

    async def test_list_projects_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test project listing pagination."""
        # Create multiple projects
        for i in range(5):
            await client.post(
                "/projects",
                json={"name": f"Project {i}"},
                headers=auth_headers
            )

        # Test page 1 with page_size=2
        response = await client.get(
            "/projects?page=1&page_size=2",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["projects"]) == 2
        assert data["page"] == 1
        assert data["total_pages"] == 3

        # Test page 2
        response = await client.get(
            "/projects?page=2&page_size=2",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 2
        assert data["page"] == 2

    async def test_list_projects_user_isolation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test users can only see their own projects."""
        # Create another user
        response = await client.post(
            "/auth/register",
            json={
                "email": "other@example.com",
                "password": "OtherPass123"
            }
        )
        other_token = response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Other user should see no projects
        response = await client.get("/projects", headers=other_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 0


@pytest.mark.asyncio
class TestProjectsGet:
    """Test getting individual project."""

    async def test_get_project_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test getting a project by ID."""
        response = await client.get(
            f"/projects/{test_project['id']}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project["id"]
        assert data["name"] == test_project["name"]

    async def test_get_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent project."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = await client.get(
            f"/projects/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_get_project_other_user_fails(
        self,
        client: AsyncClient,
        test_project: dict
    ):
        """Test getting another user's project fails."""
        # Create another user
        response = await client.post(
            "/auth/register",
            json={
                "email": "other2@example.com",
                "password": "OtherPass123"
            }
        )
        other_token = response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Try to access first user's project
        response = await client.get(
            f"/projects/{test_project['id']}",
            headers=other_headers
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestProjectsUpdate:
    """Test project updates."""

    async def test_update_project_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test successful project update."""
        response = await client.put(
            f"/projects/{test_project['id']}",
            json={
                "name": "Updated Project",
                "description": "Updated description",
                "default_genre": "Horror"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project"
        assert data["description"] == "Updated description"
        assert data["default_genre"] == "Horror"

    async def test_update_project_partial(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test partial project update."""
        response = await client.put(
            f"/projects/{test_project['id']}",
            json={"name": "Partially Updated"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Partially Updated"
        # Other fields should remain unchanged
        assert data["description"] == test_project["description"]

    async def test_update_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating non-existent project."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = await client.put(
            f"/projects/{fake_id}",
            json={"name": "Not Found"},
            headers=auth_headers
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestProjectsDelete:
    """Test project deletion."""

    async def test_delete_project_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test successful project deletion."""
        response = await client.delete(
            f"/projects/{test_project['id']}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify project is gone
        response = await client.get(
            f"/projects/{test_project['id']}",
            headers=auth_headers
        )
        assert response.status_code == 404

    async def test_delete_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test deleting non-existent project."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = await client.delete(
            f"/projects/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_delete_project_cascade(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test project deletion cascades to related entities."""
        # Create a job for the project
        response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {
                    "genre": "Sci-Fi",
                    "target_length": 5000
                }
            },
            headers=auth_headers
        )
        job_id = response.json()["id"]

        # Delete project
        response = await client.delete(
            f"/projects/{test_project['id']}",
            headers=auth_headers
        )
        assert response.status_code == 204

        # Verify job is also deleted
        response = await client.get(
            f"/jobs/{job_id}",
            headers=auth_headers
        )
        assert response.status_code == 404

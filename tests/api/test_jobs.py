"""
Jobs API Integration Tests.

Tests for narrative generation job endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestJobsCreate:
    """Test job creation."""

    async def test_create_job_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test successful job creation."""
        response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {
                    "genre": "Science Fiction",
                    "production_type": "Film",
                    "target_length": 5000,
                    "plot_outline": "A story about AI and humanity"
                }
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "id" in data
        assert data["project_id"] == test_project["id"]
        assert data["status"] == "QUEUED"
        assert data["production_brief"]["genre"] == "Science Fiction"
        assert data["production_brief"]["target_length"] == 5000
        assert data["progress_percentage"] == 0.0
        assert data["estimated_cost_usd"] is not None

    async def test_create_job_without_project_fails(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating job without project_id fails."""
        response = await client.post(
            "/jobs",
            json={
                "production_brief": {"genre": "Fantasy"}
            },
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_job_invalid_project_fails(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating job with invalid project_id fails."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = await client.post(
            "/jobs",
            json={
                "project_id": fake_id,
                "production_brief": {"genre": "Fantasy"}
            },
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_create_job_exceeds_limit_fails(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test creating job when monthly limit exceeded fails."""
        # Create jobs up to limit (FREE tier = 5)
        for i in range(5):
            response = await client.post(
                "/jobs",
                json={
                    "project_id": test_project["id"],
                    "production_brief": {"genre": f"Genre {i}"}
                },
                headers=auth_headers
            )
            assert response.status_code == 201

        # Next job should fail
        response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Over limit"}
            },
            headers=auth_headers
        )

        assert response.status_code == 403
        assert "limit" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestJobsList:
    """Test job listing."""

    async def test_list_jobs_empty(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test listing jobs when none exist."""
        response = await client.get("/jobs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["jobs"] == []
        assert data["total"] == 0

    async def test_list_jobs_with_data(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test listing jobs with data."""
        # Create a job
        create_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Drama"}
            },
            headers=auth_headers
        )
        job_id = create_response.json()["id"]

        # List jobs
        response = await client.get("/jobs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 1
        assert len(data["jobs"]) == 1
        assert data["jobs"][0]["id"] == job_id

    async def test_list_jobs_filter_by_status(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test filtering jobs by status."""
        # Create multiple jobs
        for i in range(3):
            await client.post(
                "/jobs",
                json={
                    "project_id": test_project["id"],
                    "production_brief": {"genre": f"Genre {i}"}
                },
                headers=auth_headers
            )

        # Filter by QUEUED status
        response = await client.get(
            "/jobs?status=QUEUED",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert all(job["status"] == "QUEUED" for job in data["jobs"])

    async def test_list_jobs_filter_by_project(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test filtering jobs by project."""
        # Create another project
        project2_response = await client.post(
            "/projects",
            json={"name": "Project 2"},
            headers=auth_headers
        )
        project2_id = project2_response.json()["id"]

        # Create jobs in different projects
        await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Fantasy"}
            },
            headers=auth_headers
        )
        await client.post(
            "/jobs",
            json={
                "project_id": project2_id,
                "production_brief": {"genre": "Sci-Fi"}
            },
            headers=auth_headers
        )

        # Filter by first project
        response = await client.get(
            f"/jobs?project_id={test_project['id']}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["jobs"][0]["project_id"] == test_project["id"]


@pytest.mark.asyncio
class TestJobsGet:
    """Test getting individual job."""

    async def test_get_job_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test getting a job by ID."""
        # Create job
        create_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Mystery"}
            },
            headers=auth_headers
        )
        job_id = create_response.json()["id"]

        # Get job
        response = await client.get(
            f"/jobs/{job_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["production_brief"]["genre"] == "Mystery"

    async def test_get_job_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent job."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = await client.get(
            f"/jobs/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestJobsStatus:
    """Test job status endpoint."""

    async def test_get_job_status(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test getting job status."""
        # Create job
        create_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Thriller"}
            },
            headers=auth_headers
        )
        job_id = create_response.json()["id"]

        # Get status
        response = await client.get(
            f"/jobs/{job_id}/status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == "QUEUED"
        assert data["progress_percentage"] == 0.0


@pytest.mark.asyncio
class TestJobsCancel:
    """Test job cancellation."""

    async def test_cancel_job_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict
    ):
        """Test successful job cancellation."""
        # Create job
        create_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Action"}
            },
            headers=auth_headers
        )
        job_id = create_response.json()["id"]

        # Cancel job
        response = await client.post(
            f"/jobs/{job_id}/cancel",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["status"] == "CANCELLED"

    async def test_cancel_completed_job_fails(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        db_session
    ):
        """Test cancelling completed job fails."""
        from api.models.job import GenerationJob, JobStatus

        # Create job
        create_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Romance"}
            },
            headers=auth_headers
        )
        job_id = create_response.json()["id"]

        # Manually set job to COMPLETED
        from sqlalchemy import select
        stmt = select(GenerationJob).where(GenerationJob.id == job_id)
        result = await db_session.execute(stmt)
        job = result.scalar_one()
        job.status = JobStatus.COMPLETED
        await db_session.commit()

        # Try to cancel
        response = await client.post(
            f"/jobs/{job_id}/cancel",
            headers=auth_headers
        )

        assert response.status_code == 400

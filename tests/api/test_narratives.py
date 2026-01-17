"""
Narratives API Integration Tests.

Tests for narrative viewing and management endpoints.
"""

import pytest
from httpx import AsyncClient


async def create_narrative_via_db(db_session, project_id: str, job_id: str):
    """Helper function to create a narrative directly in the database."""
    from api.models.narrative import Narrative

    narrative = Narrative(
        project_id=project_id,
        job_id=job_id,
        title="Test Narrative",
        summary="A test narrative summary",
        genre="Science Fiction",
        production_type="Film",
        full_text="This is the full text of the narrative...",
        word_count=10,
        quality_score=0.85,
        generation_cost_usd=0.50,
        narrative_metadata={"test": "data"}
    )

    db_session.add(narrative)
    await db_session.commit()
    await db_session.refresh(narrative)

    return narrative


@pytest.mark.asyncio
class TestNarrativesList:
    """Test narrative listing."""

    async def test_list_narratives_empty(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test listing narratives when none exist."""
        response = await client.get("/narratives", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["narratives"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    async def test_list_narratives_with_data(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        db_session
    ):
        """Test listing narratives with data."""
        # Create a job first
        job_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Fantasy"}
            },
            headers=auth_headers
        )
        job_id = job_response.json()["id"]

        # Create narrative directly in DB
        narrative = await create_narrative_via_db(db_session, test_project["id"], job_id)

        # List narratives
        response = await client.get("/narratives", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 1
        assert len(data["narratives"]) == 1
        assert data["narratives"][0]["id"] == narrative.id
        assert data["narratives"][0]["title"] == "Test Narrative"

    async def test_list_narratives_filter_by_project(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        db_session
    ):
        """Test filtering narratives by project."""
        # Create another project
        project2_response = await client.post(
            "/projects",
            json={"name": "Project 2"},
            headers=auth_headers
        )
        project2_id = project2_response.json()["id"]

        # Create jobs
        job1_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Horror"}
            },
            headers=auth_headers
        )
        job2_response = await client.post(
            "/jobs",
            json={
                "project_id": project2_id,
                "production_brief": {"genre": "Comedy"}
            },
            headers=auth_headers
        )

        # Create narratives in different projects
        await create_narrative_via_db(db_session, test_project["id"], job1_response.json()["id"])
        await create_narrative_via_db(db_session, project2_id, job2_response.json()["id"])

        # Filter by first project
        response = await client.get(
            f"/narratives?project_id={test_project['id']}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["narratives"][0]["project_id"] == test_project["id"]

    async def test_list_narratives_filter_by_genre(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        db_session
    ):
        """Test filtering narratives by genre."""
        # Create jobs and narratives with different genres
        for genre in ["Fantasy", "Sci-Fi", "Fantasy"]:
            job_response = await client.post(
                "/jobs",
                json={
                    "project_id": test_project["id"],
                    "production_brief": {"genre": genre}
                },
                headers=auth_headers
            )
            narrative = await create_narrative_via_db(
                db_session,
                test_project["id"],
                job_response.json()["id"]
            )
            # Update genre
            narrative.genre = genre
            await db_session.commit()

        # Filter by Fantasy
        response = await client.get(
            "/narratives?genre=Fantasy",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(n["genre"] == "Fantasy" for n in data["narratives"])


@pytest.mark.asyncio
class TestNarrativesGet:
    """Test getting individual narrative."""

    async def test_get_narrative_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        db_session
    ):
        """Test getting a narrative by ID."""
        # Create job and narrative
        job_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Mystery"}
            },
            headers=auth_headers
        )
        narrative = await create_narrative_via_db(
            db_session,
            test_project["id"],
            job_response.json()["id"]
        )

        # Get narrative
        response = await client.get(
            f"/narratives/{narrative.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == narrative.id
        assert data["title"] == "Test Narrative"
        assert data["genre"] == "Science Fiction"
        assert data["quality_score"] == 0.85

    async def test_get_narrative_increments_view_count(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        db_session
    ):
        """Test that getting a narrative increments view count."""
        # Create narrative
        job_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Drama"}
            },
            headers=auth_headers
        )
        narrative = await create_narrative_via_db(
            db_session,
            test_project["id"],
            job_response.json()["id"]
        )

        initial_views = narrative.view_count

        # Get narrative
        response = await client.get(
            f"/narratives/{narrative.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["view_count"] == initial_views + 1

    async def test_get_narrative_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent narrative."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = await client.get(
            f"/narratives/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestNarrativesText:
    """Test narrative text retrieval."""

    async def test_get_narrative_text_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        db_session
    ):
        """Test getting narrative full text."""
        # Create narrative
        job_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Adventure"}
            },
            headers=auth_headers
        )
        narrative = await create_narrative_via_db(
            db_session,
            test_project["id"],
            job_response.json()["id"]
        )

        # Get text
        response = await client.get(
            f"/narratives/{narrative.id}/text",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "full_text" in data
        assert data["full_text"] == "This is the full text of the narrative..."

    async def test_get_narrative_text_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting text for non-existent narrative."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = await client.get(
            f"/narratives/{fake_id}/text",
            headers=auth_headers
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestNarrativesDelete:
    """Test narrative deletion."""

    async def test_delete_narrative_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        db_session
    ):
        """Test successful narrative deletion."""
        # Create narrative
        job_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Thriller"}
            },
            headers=auth_headers
        )
        narrative = await create_narrative_via_db(
            db_session,
            test_project["id"],
            job_response.json()["id"]
        )

        # Delete narrative
        response = await client.delete(
            f"/narratives/{narrative.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deletion
        response = await client.get(
            f"/narratives/{narrative.id}",
            headers=auth_headers
        )
        assert response.status_code == 404

    async def test_delete_narrative_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test deleting non-existent narrative."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = await client.delete(
            f"/narratives/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_delete_narrative_updates_project_stats(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        db_session
    ):
        """Test that deleting narrative updates project stats."""
        # Create narrative
        job_response = await client.post(
            "/jobs",
            json={
                "project_id": test_project["id"],
                "production_brief": {"genre": "Western"}
            },
            headers=auth_headers
        )
        narrative = await create_narrative_via_db(
            db_session,
            test_project["id"],
            job_response.json()["id"]
        )

        # Get initial project stats
        project_response = await client.get(
            f"/projects/{test_project['id']}",
            headers=auth_headers
        )
        initial_count = project_response.json()["narrative_count"]
        initial_words = project_response.json()["total_word_count"]
        initial_cost = project_response.json()["total_cost_usd"]

        # Delete narrative
        await client.delete(
            f"/narratives/{narrative.id}",
            headers=auth_headers
        )

        # Check updated project stats
        project_response = await client.get(
            f"/projects/{test_project['id']}",
            headers=auth_headers
        )
        updated_stats = project_response.json()

        assert updated_stats["narrative_count"] == initial_count - 1
        assert updated_stats["total_word_count"] == initial_words - narrative.word_count
        assert updated_stats["total_cost_usd"] == initial_cost - narrative.generation_cost_usd

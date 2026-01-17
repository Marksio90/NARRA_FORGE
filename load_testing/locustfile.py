"""
Load Testing with Locust for NARRA_FORGE V2.

Run with: locust -f load_testing/locustfile.py --host=http://localhost:8000
"""

import random
from locust import HttpUser, task, between, SequentialTaskSet


class UserBehavior(SequentialTaskSet):
    """Simulates realistic user behavior."""

    def on_start(self):
        """Called when user starts - register and login."""
        # Register new user
        timestamp = random.randint(1000000, 9999999)
        self.email = f"loadtest{timestamp}@example.com"
        self.password = "LoadTest123"

        response = self.client.post("/auth/register", json={
            "email": self.email,
            "password": self.password,
            "full_name": f"Load Test User {timestamp}"
        })

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(1)
    def view_health(self):
        """Check health endpoint."""
        self.client.get("/health")

    @task(3)
    def list_projects(self):
        """List user projects."""
        if self.token:
            self.client.get("/projects", headers=self.headers)

    @task(2)
    def create_project(self):
        """Create a new project."""
        if self.token:
            response = self.client.post("/projects", json={
                "name": f"Load Test Project {random.randint(1, 1000)}",
                "description": "Project created during load testing",
                "default_genre": random.choice(["Sci-Fi", "Fantasy", "Horror", "Drama"]),
                "default_production_type": random.choice(["Film", "Novel", "Series"])
            }, headers=self.headers)

            if response.status_code == 201:
                self.project_id = response.json()["id"]

    @task(2)
    def list_jobs(self):
        """List generation jobs."""
        if self.token:
            self.client.get("/jobs", headers=self.headers)

    @task(1)
    def create_job(self):
        """Create a narrative generation job."""
        if self.token and hasattr(self, 'project_id'):
            self.client.post("/jobs", json={
                "project_id": self.project_id,
                "production_brief": {
                    "genre": random.choice(["Sci-Fi", "Fantasy", "Horror"]),
                    "production_type": "Film",
                    "target_length": random.randint(2000, 10000),
                    "plot_outline": "A compelling story about AI and humanity."
                }
            }, headers=self.headers)

    @task(2)
    def list_narratives(self):
        """List narratives."""
        if self.token:
            self.client.get("/narratives", headers=self.headers)


class NarraForgeUser(HttpUser):
    """Represents a user of NARRA_FORGE."""

    tasks = [UserBehavior]
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks

    # User weight (how many of these users vs others)
    weight = 1


class ReadOnlyUser(HttpUser):
    """User that only reads data (no mutations)."""

    wait_time = between(0.5, 2)

    def on_start(self):
        """Login on start."""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123"
        })

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(5)
    def view_projects(self):
        """View projects list."""
        if self.token:
            self.client.get("/projects", headers=self.headers)

    @task(3)
    def view_jobs(self):
        """View jobs list."""
        if self.token:
            self.client.get("/jobs", headers=self.headers)

    @task(2)
    def view_narratives(self):
        """View narratives list."""
        if self.token:
            self.client.get("/narratives", headers=self.headers)

    weight = 3  # 3x more read-only users

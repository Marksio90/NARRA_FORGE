"""
Authentication API Integration Tests.

Tests for user registration, login, and token refresh endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthRegistration:
    """Test user registration endpoints."""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "full_name": "New User"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data

        # Check user data
        user = data["user"]
        assert user["email"] == "newuser@example.com"
        assert user["full_name"] == "New User"
        assert user["subscription_tier"] == "FREE"
        assert user["monthly_generation_limit"] == 5
        assert "password" not in user

        # Check token type
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient, test_user: dict):
        """Test registration with duplicate email fails."""
        response = await client.post(
            "/auth/register",
            json={
                "email": test_user["email"],
                "password": "AnotherPass123",
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password fails."""
        weak_passwords = [
            "short",  # Too short
            "alllowercase123",  # No uppercase
            "ALLUPPERCASE123",  # No lowercase
            "NoDigitsHere",  # No digits
        ]

        for password in weak_passwords:
            response = await client.post(
                "/auth/register",
                json={
                    "email": f"test{password}@example.com",
                    "password": password,
                }
            )
            assert response.status_code == 400

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email fails."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "not-an-email",
                "password": "ValidPass123",
            }
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestAuthLogin:
    """Test user login endpoints."""

    async def test_login_success(self, client: AsyncClient, test_user: dict):
        """Test successful login."""
        response = await client.post(
            "/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data

        # Tokens should be different from registration
        assert data["access_token"] != test_user["access_token"]

    async def test_login_wrong_password(self, client: AsyncClient, test_user: dict):
        """Test login with wrong password fails."""
        response = await client.post(
            "/auth/login",
            json={
                "email": test_user["email"],
                "password": "WrongPassword123",
            }
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails."""
        response = await client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePass123",
            }
        )

        assert response.status_code == 401
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestAuthTokenRefresh:
    """Test token refresh endpoints."""

    async def test_refresh_token_success(self, client: AsyncClient, test_user: dict):
        """Test successful token refresh."""
        response = await client.post(
            "/auth/refresh",
            json={
                "refresh_token": test_user["refresh_token"]
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data

        # New tokens should be different
        assert data["access_token"] != test_user["access_token"]
        assert data["refresh_token"] != test_user["refresh_token"]

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token fails."""
        response = await client.post(
            "/auth/refresh",
            json={
                "refresh_token": "invalid.token.here"
            }
        )

        assert response.status_code == 401

    async def test_refresh_token_access_token(self, client: AsyncClient, test_user: dict):
        """Test refresh with access token instead of refresh token fails."""
        response = await client.post(
            "/auth/refresh",
            json={
                "refresh_token": test_user["access_token"]  # Using access token
            }
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthProtectedEndpoints:
    """Test authentication requirements for protected endpoints."""

    async def test_access_without_token_fails(self, client: AsyncClient):
        """Test accessing protected endpoints without token fails."""
        response = await client.get("/projects")
        assert response.status_code == 401

    async def test_access_with_invalid_token_fails(self, client: AsyncClient):
        """Test accessing protected endpoints with invalid token fails."""
        response = await client.get(
            "/projects",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    async def test_access_with_valid_token_succeeds(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test accessing protected endpoints with valid token succeeds."""
        response = await client.get("/projects", headers=auth_headers)
        assert response.status_code == 200

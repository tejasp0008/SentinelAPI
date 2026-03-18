"""SentinelAPI — Authentication Endpoint Tests."""


class TestRegister:
    """Tests for POST /api/v1/auth/register"""

    def test_register_success(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@sentinel.io",
            "password": "securepassword123",
            "full_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@sentinel.io"
        assert data["role"] == "viewer"
        assert data["is_active"] is True
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        response = client.post("/api/v1/auth/register", json={
            "email": "test@sentinel.io",
            "password": "anotherpassword123",
        })
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "securepassword123",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "user@sentinel.io",
            "password": "short",
        })
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/v1/auth/login"""

    def test_login_success(self, client, test_user):
        response = client.post("/api/v1/auth/login", json={
            "email": "test@sentinel.io",
            "password": "testpassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        response = client.post("/api/v1/auth/login", json={
            "email": "test@sentinel.io",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "noone@sentinel.io",
            "password": "doesn't matter",
        })
        assert response.status_code == 401


class TestTokenAccess:
    """Tests for protected endpoints without token."""

    def test_protected_route_without_token(self, client):
        response = client.post("/api/v1/decommission", json={
            "endpoint_id": "00000000-0000-0000-0000-000000000000",
        })
        assert response.status_code == 401

    def test_protected_route_with_invalid_token(self, client):
        response = client.post(
            "/api/v1/decommission",
            json={"endpoint_id": "00000000-0000-0000-0000-000000000000"},
            headers={"Authorization": "Bearer invalidtoken123"},
        )
        assert response.status_code == 401

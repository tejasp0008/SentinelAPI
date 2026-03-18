"""SentinelAPI — Health Check Endpoint Tests."""


class TestRootEndpoint:
    """Tests for GET /"""

    def test_root_returns_operational(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["name"] == "SentinelAPI"
        assert "version" in data


class TestHealthEndpoint:
    """Tests for GET /health"""

    def test_health_returns_status(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "version" in data

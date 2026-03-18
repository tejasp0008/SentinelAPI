"""SentinelAPI — AI Analysis Endpoint Tests."""


class TestAnalyzeEndpoint:
    """Tests for POST /api/v1/ai/analyze"""

    def test_analyze_success(self, client, auth_headers, sample_api):
        response = client.post("/api/v1/ai/analyze", json={
            "endpoint": "/api/v2/test/endpoint",
            "payload_size": 1024,
            "ip": "192.168.1.1",
            "raw_payload": "SELECT * FROM users",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "cnn_score" in data
        assert "nlp_score" in data
        assert "isolation_forest_score" in data
        assert "combined_risk_score" in data
        assert 0 <= data["combined_risk_score"] <= 100

    def test_analyze_requires_auth(self, client):
        response = client.post("/api/v1/ai/analyze", json={
            "endpoint": "/test",
            "payload_size": 100,
            "ip": "10.0.0.1",
        })
        assert response.status_code == 401

    def test_analyze_invalid_ip(self, client, auth_headers):
        response = client.post("/api/v1/ai/analyze", json={
            "endpoint": "/test",
            "payload_size": 100,
            "ip": "not-an-ip",
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_analyze_negative_payload_size(self, client, auth_headers):
        response = client.post("/api/v1/ai/analyze", json={
            "endpoint": "/test",
            "payload_size": -1,
            "ip": "10.0.0.1",
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_analyze_with_malicious_payload(self, client, auth_headers, sample_api):
        """Verify NLP detects SQL injection patterns."""
        response = client.post("/api/v1/ai/analyze", json={
            "endpoint": "/api/v2/test/endpoint",
            "payload_size": 2048,
            "ip": "10.0.0.1",
            "raw_payload": "'; DROP TABLE users; --",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # NLP should flag this — score should be non-zero
        assert data["nlp_score"] > 0

    def test_analyze_unknown_endpoint(self, client, auth_headers):
        """Analyze an endpoint not in the inventory — should still return scores."""
        response = client.post("/api/v1/ai/analyze", json={
            "endpoint": "/unknown/endpoint",
            "payload_size": 500,
            "ip": "172.16.0.1",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status_change"] is None

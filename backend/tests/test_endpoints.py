"""SentinelAPI — API Inventory Endpoint Tests."""

import uuid


class TestListApis:
    """Tests for GET /api/v1/apis"""

    def test_list_apis_empty(self, client):
        response = client.get("/api/v1/apis")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_apis_with_data(self, client, sample_api):
        response = client.get("/api/v1/apis")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["endpoint"] == "/api/v2/test/endpoint"

    def test_list_apis_pagination(self, client, db):
        from models.api_inventory import APIInventory

        for i in range(5):
            api = APIInventory(
                endpoint=f"/api/test/{i}",
                method="GET",
                status="active",
                dynamic_risk_score=float(i * 10),
            )
            db.add(api)
        db.commit()

        # First page
        response = client.get("/api/v1/apis?limit=2&offset=0")
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0

        # Second page
        response = client.get("/api/v1/apis?limit=2&offset=2")
        data = response.json()
        assert len(data["items"]) == 2

    def test_list_apis_status_filter(self, client, db):
        from models.api_inventory import APIInventory

        db.add(APIInventory(endpoint="/active", method="GET", status="active"))
        db.add(APIInventory(endpoint="/zombie", method="GET", status="zombie"))
        db.commit()

        response = client.get("/api/v1/apis?status_filter=zombie")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "zombie"


class TestCreateApi:
    """Tests for POST /api/v1/apis"""

    def test_create_api_success(self, client, auth_headers):
        response = client.post("/api/v1/apis", json={
            "endpoint": "/api/v3/new/endpoint",
            "method": "POST",
            "status": "active",
            "auth_type": "JWT",
            "encryption": "TLS 1.3",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["endpoint"] == "/api/v3/new/endpoint"
        assert data["method"] == "POST"
        assert "id" in data

    def test_create_api_requires_auth(self, client):
        response = client.post("/api/v1/apis", json={
            "endpoint": "/api/v3/new",
            "method": "GET",
        })
        assert response.status_code == 401

    def test_create_api_duplicate(self, client, auth_headers, sample_api):
        response = client.post("/api/v1/apis", json={
            "endpoint": "/api/v2/test/endpoint",
            "method": "GET",
        }, headers=auth_headers)
        assert response.status_code == 409


class TestGetRisk:
    """Tests for GET /api/v1/risk/{endpoint_id}"""

    def test_get_risk_success(self, client, sample_api):
        response = client.get(f"/api/v1/risk/{sample_api.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["endpoint"] == "/api/v2/test/endpoint"
        assert data["risk_level"] == "low"

    def test_get_risk_not_found(self, client):
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/risk/{fake_id}")
        assert response.status_code == 404


class TestDecommission:
    """Tests for POST /api/v1/decommission"""

    def test_decommission_success(self, client, auth_headers, sample_api):
        response = client.post("/api/v1/decommission", json={
            "endpoint_id": str(sample_api.id),
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["previous_status"] == "active"
        assert data["new_status"] == "inactive"
        assert "blockchain_anchor" in data
        assert "pentest_trigger" in data

    def test_decommission_not_found(self, client, auth_headers):
        fake_id = str(uuid.uuid4())
        response = client.post("/api/v1/decommission", json={
            "endpoint_id": fake_id,
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_decommission_requires_auth(self, client, sample_api):
        response = client.post("/api/v1/decommission", json={
            "endpoint_id": str(sample_api.id),
        })
        assert response.status_code == 401

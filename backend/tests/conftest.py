"""SentinelAPI — Pytest Fixtures & Test Configuration."""

import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Ensure backend dir is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.database import Base, get_db
from core.security import hash_password, create_access_token
from main import app
from models.user import User
from models.api_inventory import APIInventory

# ─── Test Database ───────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///./test_sentinel.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh test database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI TestClient with overridden DB dependency."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db) -> User:
    """Create and return a test user."""
    user = User(
        email="test@sentinel.io",
        hashed_password=hash_password("testpassword123"),
        full_name="Test User",
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> dict:
    """Return Authorization headers with a valid JWT token."""
    token = create_access_token(data={"sub": str(test_user.id), "role": test_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_api(db) -> APIInventory:
    """Create and return a sample API inventory entry."""
    api = APIInventory(
        endpoint="/api/v2/test/endpoint",
        method="GET",
        status="active",
        auth_type="JWT",
        encryption="TLS 1.3",
        dynamic_risk_score=25.0,
        traffic_count=1000,
        days_since_last_used=0,
    )
    db.add(api)
    db.commit()
    db.refresh(api)
    return api

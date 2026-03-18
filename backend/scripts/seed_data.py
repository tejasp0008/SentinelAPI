"""SentinelAPI — Database seeding script with realistic dummy data.

Generates 20+ API endpoints across three categories:
  - Safe APIs: High traffic, low risk, active status
  - Zombie APIs: Low traffic, high risk, deprecated status
  - Vulnerable APIs: Missing auth, outdated encryption
"""

import sys
import os
import uuid
import random
import json
from datetime import datetime, timedelta, timezone

# Allow running as a standalone script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def generate_seed_data() -> list[dict]:
    """Generate a list of 24 dummy API endpoint records."""
    now = datetime.now(timezone.utc)

    endpoints = []

    # ─── SAFE APIs (8 endpoints) ────────────────────────────────
    safe_apis = [
        ("/api/v2/auth/login", "POST", "OAuth2", "TLS 1.3"),
        ("/api/v2/auth/refresh", "POST", "JWT", "TLS 1.3"),
        ("/api/v2/users/profile", "GET", "JWT", "TLS 1.3"),
        ("/api/v2/users/settings", "PUT", "JWT", "TLS 1.3"),
        ("/api/v2/products/list", "GET", "API_KEY", "TLS 1.3"),
        ("/api/v2/products/{id}", "GET", "API_KEY", "TLS 1.3"),
        ("/api/v2/payments/process", "POST", "OAuth2", "TLS 1.3"),
        ("/api/v2/notifications/send", "POST", "JWT", "TLS 1.2"),
    ]
    for endpoint, method, auth, enc in safe_apis:
        endpoints.append({
            "id": str(uuid.uuid4()),
            "endpoint": endpoint,
            "method": method,
            "status": "active",
            "auth_type": auth,
            "encryption": enc,
            "dynamic_risk_score": round(random.uniform(5, 25), 1),
            "last_used": (now - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "traffic_count": random.randint(5000, 50000),
            "days_since_last_used": 0,
            "vulnerabilities": None,
            "metadata_hash": None,
        })

    # ─── ZOMBIE APIs (8 endpoints) ──────────────────────────────
    zombie_apis = [
        ("/api/v1/legacy/users", "GET", "API_KEY", "TLS 1.1"),
        ("/api/v1/legacy/orders", "GET", "API_KEY", "TLS 1.0"),
        ("/api/v1/internal/debug", "GET", None, "TLS 1.0"),
        ("/api/v1/legacy/reports", "POST", "Basic", "TLS 1.1"),
        ("/api/v1/admin/config", "GET", "Basic", "TLS 1.0"),
        ("/api/v1/legacy/search", "GET", None, "TLS 1.0"),
        ("/api/v1/internal/metrics", "GET", None, None),
        ("/api/v1/legacy/export", "POST", "API_KEY", "TLS 1.1"),
    ]
    for endpoint, method, auth, enc in zombie_apis:
        days_unused = random.randint(90, 365)
        endpoints.append({
            "id": str(uuid.uuid4()),
            "endpoint": endpoint,
            "method": method,
            "status": random.choice(["deprecated", "zombie"]),
            "auth_type": auth,
            "encryption": enc,
            "dynamic_risk_score": round(random.uniform(65, 95), 1),
            "last_used": (now - timedelta(days=days_unused)).isoformat(),
            "traffic_count": random.randint(0, 50),
            "days_since_last_used": days_unused,
            "vulnerabilities": json.dumps([
                "Outdated encryption protocol",
                "No active maintenance",
                "Deprecated endpoint — no owner",
            ]),
            "metadata_hash": None,
        })

    # ─── VULNERABLE APIs (8 endpoints) ──────────────────────────
    vulnerable_apis = [
        ("/api/v2/files/upload", "POST", None, "TLS 1.0"),
        ("/api/v2/admin/users", "DELETE", None, "TLS 1.2"),
        ("/api/v2/data/export", "GET", None, "TLS 1.0"),
        ("/api/v2/webhooks/register", "POST", "API_KEY", None),
        ("/api/v2/config/update", "PUT", None, None),
        ("/api/v2/logs/download", "GET", None, "TLS 1.0"),
        ("/api/v2/tokens/generate", "POST", None, "TLS 1.1"),
        ("/api/v2/batch/process", "POST", "API_KEY", "TLS 1.0"),
    ]
    for endpoint, method, auth, enc in vulnerable_apis:
        vulns = []
        if auth is None:
            vulns.append("Missing authentication")
        if enc is None or enc in ("TLS 1.0", "TLS 1.1"):
            vulns.append(f"Outdated encryption: {enc or 'None'}")
        vulns.append(random.choice([
            "Potential SQL injection vector",
            "Missing rate limiting",
            "Excessive data exposure",
            "Missing input validation",
        ]))

        endpoints.append({
            "id": str(uuid.uuid4()),
            "endpoint": endpoint,
            "method": method,
            "status": random.choice(["active", "shadow"]),
            "auth_type": auth,
            "encryption": enc,
            "dynamic_risk_score": round(random.uniform(50, 85), 1),
            "last_used": (now - timedelta(days=random.randint(1, 30))).isoformat(),
            "traffic_count": random.randint(100, 3000),
            "days_since_last_used": random.randint(1, 30),
            "vulnerabilities": json.dumps(vulns),
            "metadata_hash": None,
        })

    return endpoints


def seed_database():
    """Insert seed data into the PostgreSQL database."""
    from core.database import engine, SessionLocal, Base
    from models.api_inventory import APIInventory

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if data already exists
        existing = db.query(APIInventory).count()
        if existing > 0:
            print(f"⚠️  Database already has {existing} records. Skipping seed.")
            return

        records = generate_seed_data()
        for rec in records:
            api = APIInventory(
                id=uuid.UUID(rec["id"]),
                endpoint=rec["endpoint"],
                method=rec["method"],
                status=rec["status"],
                auth_type=rec["auth_type"],
                encryption=rec["encryption"],
                dynamic_risk_score=rec["dynamic_risk_score"],
                last_used=datetime.fromisoformat(rec["last_used"]) if rec["last_used"] else None,
                traffic_count=rec["traffic_count"],
                days_since_last_used=rec["days_since_last_used"],
                vulnerabilities=rec["vulnerabilities"],
                metadata_hash=rec["metadata_hash"],
            )
            db.add(api)

        db.commit()
        print(f"✅ Seeded {len(records)} API endpoints into the database.")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

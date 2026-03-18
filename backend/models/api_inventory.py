"""SentinelAPI — APIInventory SQLAlchemy model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Uuid
from core.database import Base


class APIInventory(Base):
    """Represents a discovered API endpoint in the inventory."""

    __tablename__ = "api_inventory"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    endpoint = Column(String(500), nullable=False, index=True)
    method = Column(String(10), nullable=False, default="GET")
    status = Column(
        String(20),
        nullable=False,
        default="active",
        index=True,
        comment="active | deprecated | shadow | zombie | inactive",
    )
    auth_type = Column(
        String(50),
        nullable=True,
        comment="e.g., OAuth2, API_KEY, JWT, None",
    )
    encryption = Column(
        String(50),
        nullable=True,
        comment="e.g., TLS 1.3, TLS 1.2, TLS 1.0, None",
    )
    dynamic_risk_score = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="AI-calculated risk score 0-100",
    )
    last_used = Column(DateTime, nullable=True)
    traffic_count = Column(Integer, nullable=False, default=0)
    days_since_last_used = Column(Integer, nullable=False, default=0)
    vulnerabilities = Column(
        Text,
        nullable=True,
        comment="JSON string of detected vulnerabilities",
    )
    metadata_hash = Column(
        String(64),
        nullable=True,
        comment="SHA-256 hash for blockchain anchoring (Phase 3)",
    )

    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<APIInventory {self.method} {self.endpoint} [{self.status}]>"

"""SentinelAPI — User SQLAlchemy model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Uuid, Boolean
from core.database import Base


class User(Base):
    """Represents an authenticated user of the platform."""

    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(
        String(20),
        nullable=False,
        default="viewer",
        comment="admin | viewer",
    )
    is_active = Column(Boolean, nullable=False, default=True)

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
        return f"<User {self.email} [{self.role}]>"

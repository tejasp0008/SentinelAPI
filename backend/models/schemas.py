"""SentinelAPI — Pydantic schemas for request/response validation."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


# ─── Authentication ──────────────────────────────────────────────

class UserCreate(BaseModel):
    """Schema for user registration / login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None
    role: str = Field(default="viewer", pattern="^(admin|viewer)$")


class UserResponse(BaseModel):
    """Schema for user responses (no password)."""

    id: UUID
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


# ─── Pagination ──────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    total: int
    limit: int
    offset: int
    items: list


# ─── API Inventory ───────────────────────────────────────────────

class APIInventoryCreate(BaseModel):
    """Schema for creating a new API inventory entry."""

    endpoint: str = Field(max_length=500)
    method: str = Field(default="GET", pattern="^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)$")
    status: str = Field(default="active", pattern="^(active|deprecated|shadow|zombie|inactive)$")
    auth_type: Optional[str] = None
    encryption: Optional[str] = None
    dynamic_risk_score: float = Field(default=0.0, ge=0, le=100)
    vulnerabilities: Optional[str] = None


class APIInventoryResponse(BaseModel):
    """Schema for API inventory list responses."""

    id: UUID
    endpoint: str
    method: str
    status: str
    auth_type: Optional[str] = None
    encryption: Optional[str] = None
    dynamic_risk_score: float = Field(ge=0, le=100)
    last_used: Optional[datetime] = None
    traffic_count: int = 0
    days_since_last_used: int = 0
    vulnerabilities: Optional[str] = None
    metadata_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Risk Assessment ─────────────────────────────────────────────

class RiskResponse(BaseModel):
    """Schema for the risk assessment endpoint."""

    endpoint_id: UUID
    endpoint: str
    status: str
    dynamic_risk_score: float
    vulnerabilities: Optional[str] = None
    auth_type: Optional[str] = None
    encryption: Optional[str] = None
    risk_level: str = Field(
        description="low | medium | high | critical"
    )


# ─── Decommission ───────────────────────────────────────────────

class DecommissionRequest(BaseModel):
    """Schema for the decommission request body."""

    endpoint_id: UUID


class DecommissionResponse(BaseModel):
    """Schema for the decommission response."""

    endpoint_id: UUID
    previous_status: str
    new_status: str = "inactive"
    blockchain_anchor: str = Field(
        description="Status of blockchain anchoring simulation"
    )
    pentest_trigger: str = Field(
        description="Status of RL pen-test simulation"
    )


# ─── AI Analysis ─────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Schema for the AI analysis webhook request."""

    endpoint: str
    payload_size: int = Field(ge=0)
    ip: str = Field(pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    raw_payload: Optional[str] = ""


class AnalyzeResponse(BaseModel):
    """Schema for the AI analysis webhook response."""

    endpoint: str
    cnn_score: float
    nlp_score: float
    isolation_forest_score: float
    combined_risk_score: float
    status_change: Optional[str] = None
    blockchain_anchor: Optional[str] = None

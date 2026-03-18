"""SentinelAPI — REST API endpoints for API inventory management."""

import hashlib
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.api_inventory import APIInventory
from models.schemas import (
    APIInventoryCreate,
    APIInventoryResponse,
    PaginatedResponse,
    RiskResponse,
    DecommissionRequest,
    DecommissionResponse,
)
from services.blockchain_service import anchor_alert_on_chain, compute_metadata_hash
from services.cybersec_service import trigger_rl_pentest

router = APIRouter(prefix="/api/v1", tags=["API Inventory"])


def _risk_level(score: float) -> str:
    """Map a numeric risk score to a human-readable level."""
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 40:
        return "medium"
    return "low"


@router.get("/apis", response_model=PaginatedResponse)
async def list_apis(
    status_filter: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Return paginated list of discovered API endpoints.

    Query params:
    - `status_filter`: filter by status (active, deprecated, shadow, zombie, inactive)
    - `limit`: max number of results (default 20, max 100)
    - `offset`: number of results to skip (default 0)
    """
    query = db.query(APIInventory)
    if status_filter:
        query = query.filter(APIInventory.status == status_filter)

    total = query.count()
    apis = (
        query.order_by(APIInventory.dynamic_risk_score.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[APIInventoryResponse.model_validate(api) for api in apis],
    )


@router.post("/apis", response_model=APIInventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_api(
    payload: APIInventoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new API inventory entry. Requires authentication."""
    existing = db.query(APIInventory).filter(
        APIInventory.endpoint == payload.endpoint,
        APIInventory.method == payload.method,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Endpoint {payload.method} {payload.endpoint} already exists.",
        )

    api = APIInventory(
        endpoint=payload.endpoint,
        method=payload.method,
        status=payload.status,
        auth_type=payload.auth_type,
        encryption=payload.encryption,
        dynamic_risk_score=payload.dynamic_risk_score,
        vulnerabilities=payload.vulnerabilities,
    )
    db.add(api)
    db.commit()
    db.refresh(api)
    return api


@router.get("/risk/{endpoint_id}", response_model=RiskResponse)
async def get_risk(endpoint_id: UUID, db: Session = Depends(get_db)):
    """Return the risk score, status, and vulnerabilities for an endpoint."""
    api = db.query(APIInventory).filter(APIInventory.id == endpoint_id).first()
    if not api:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Endpoint {endpoint_id} not found.",
        )
    return RiskResponse(
        endpoint_id=api.id,
        endpoint=api.endpoint,
        status=api.status,
        dynamic_risk_score=api.dynamic_risk_score,
        vulnerabilities=api.vulnerabilities,
        auth_type=api.auth_type,
        encryption=api.encryption,
        risk_level=_risk_level(api.dynamic_risk_score),
    )


@router.post("/decommission", response_model=DecommissionResponse)
async def decommission_endpoint(
    req: DecommissionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Mark an endpoint as inactive and simulate blockchain anchoring.
    Requires authentication.
    """
    api = db.query(APIInventory).filter(APIInventory.id == req.endpoint_id).first()
    if not api:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Endpoint {req.endpoint_id} not found.",
        )

    previous_status = api.status

    # Update status
    api.status = "inactive"

    # Compute metadata hash
    metadata = {
        "endpoint_id": str(api.id),
        "endpoint": api.endpoint,
        "previous_status": previous_status,
        "new_status": "inactive",
        "risk_score": api.dynamic_risk_score,
    }
    api.metadata_hash = compute_metadata_hash(metadata)

    db.commit()
    db.refresh(api)

    # Simulate blockchain anchoring
    blockchain_result = await anchor_alert_on_chain(
        alert_id=str(api.id),
        metadata_hash=api.metadata_hash,
        severity="high",
    )

    # Simulate RL pen-test trigger
    pentest_result = await trigger_rl_pentest(str(api.id))

    return DecommissionResponse(
        endpoint_id=api.id,
        previous_status=previous_status,
        new_status="inactive",
        blockchain_anchor=blockchain_result["message"],
        pentest_trigger=pentest_result["message"],
    )

"""SentinelAPI — AI Analysis Webhook Route."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.config import get_settings
from core.database import get_db
from core.security import get_current_user
from models.api_inventory import APIInventory
from models.schemas import AnalyzeRequest, AnalyzeResponse
from ai_engine.ensemble import AIEnsemble
from services.blockchain_service import anchor_alert_on_chain, compute_metadata_hash

router = APIRouter(prefix="/api/v1/ai", tags=["AI Engine"])
settings = get_settings()

# ─── AI Ensemble Dependency ─────────────────────────────────────

_ensemble: AIEnsemble | None = None


def get_ensemble() -> AIEnsemble:
    """FastAPI dependency — lazy-load the AI ensemble singleton."""
    global _ensemble
    if _ensemble is None:
        _ensemble = AIEnsemble()
    return _ensemble


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_telemetry(
    req: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    ensemble: AIEnsemble = Depends(get_ensemble),
):
    """Accept incoming API gateway telemetry and run AI analysis.

    Requires authentication.

    Pipeline:
    1. Pass data through the AI ensemble (CNN + NLP + Isolation Forest).
    2. Calculate a combined dynamic_risk_score.
    3. If score > threshold, mark endpoint as 'zombie' or 'vulnerable' in DB.
    4. Simulate blockchain anchoring for the AI inference metadata.
    """

    # Run AI analysis
    result = ensemble.analyze(
        endpoint=req.endpoint,
        payload_size=req.payload_size,
        ip=req.ip,
        raw_payload=req.raw_payload or "",
    )

    status_change = None
    blockchain_anchor = None

    # Look up endpoint in DB and update if high risk
    api = db.query(APIInventory).filter(
        APIInventory.endpoint == req.endpoint
    ).first()

    if api:
        # Update the risk score
        api.dynamic_risk_score = result["combined_risk_score"]

        # If score exceeds threshold, escalate status
        if result["combined_risk_score"] > settings.AI_RISK_THRESHOLD:
            if api.status in ("active", "shadow"):
                if result["combined_risk_score"] > 80:
                    api.status = "zombie"
                    status_change = "zombie"
                else:
                    api.status = "vulnerable"
                    status_change = "vulnerable"

            # Compute and store metadata hash
            metadata = {
                "endpoint": api.endpoint,
                "risk_score": result["combined_risk_score"],
                "cnn_score": result["cnn_score"],
                "nlp_score": result["nlp_score"],
                "iso_forest_score": result["isolation_forest_score"],
                "verdict": result["verdict"],
            }
            api.metadata_hash = compute_metadata_hash(metadata)

            db.commit()
            db.refresh(api)

            # Simulate blockchain anchoring
            bc_result = await anchor_alert_on_chain(
                alert_id=str(api.id),
                metadata_hash=api.metadata_hash,
                severity=result["verdict"],
            )
            blockchain_anchor = bc_result["message"]
        else:
            db.commit()

    return AnalyzeResponse(
        endpoint=req.endpoint,
        cnn_score=result["cnn_score"],
        nlp_score=result["nlp_score"],
        isolation_forest_score=result["isolation_forest_score"],
        combined_risk_score=result["combined_risk_score"],
        status_change=status_change,
        blockchain_anchor=blockchain_anchor,
    )

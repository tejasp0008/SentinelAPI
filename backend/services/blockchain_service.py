"""SentinelAPI — Blockchain Service Stub (Phase 3 Integration Point).

This module provides a placeholder for the Ethereum/Solidity blockchain
integration that will be implemented in Phase 3. All functions mirror the
expected real interface so swapping in the actual implementation requires
no changes to calling code.
"""

import logging
import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID

logger = logging.getLogger("sentinel.blockchain")


async def anchor_alert_on_chain(
    alert_id: str | UUID,
    metadata_hash: str,
    severity: str,
) -> dict:
    """Simulate anchoring an alert to the blockchain.

    In Phase 3, this will:
    1. Connect to an Ethereum node via Web3.py
    2. Call the AlertAnchor.sol smart contract
    3. Store the tx_hash in the blockchain_anchors table

    Args:
        alert_id: Unique identifier for the alert.
        metadata_hash: SHA-256 hash of the alert metadata.
        severity: Alert severity level (low, medium, high, critical).

    Returns:
        dict with simulated transaction details.
    """
    logger.info(
        "🔗 Simulating Blockchain Write... "
        f"alert_id={alert_id}, hash={metadata_hash[:16]}..., severity={severity}"
    )

    # Simulate a transaction hash
    simulated_tx = hashlib.sha256(
        json.dumps({
            "alert_id": str(alert_id),
            "metadata_hash": metadata_hash,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }).encode()
    ).hexdigest()

    return {
        "status": "simulated",
        "tx_hash": f"0x{simulated_tx}",
        "block_number": None,
        "message": "Blockchain anchor simulated — Phase 3 will connect to Ethereum.",
    }


def compute_metadata_hash(data: dict) -> str:
    """Compute a SHA-256 hash of a metadata dictionary.

    This hash will be anchored to the blockchain in Phase 3.
    """
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()

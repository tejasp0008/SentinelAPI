"""SentinelAPI — AI Ensemble Engine.

Combines the CNN Anomaly Detector, NLP Payload Inspector, and
Isolation Forest Behavioral Scorer into a unified risk analysis pipeline.
All imports are lazy to handle missing dependencies gracefully.
"""

import logging

logger = logging.getLogger("sentinel.ensemble")


class AIEnsemble:
    """Unified AI ensemble for API risk analysis.

    Weights (configurable via settings):
        - CNN Anomaly Detector: 40%
        - NLP Payload Inspector: 30%
        - Isolation Forest Scorer: 30%
    """

    def __init__(self):
        from core.config import get_settings
        self.settings = get_settings()

        logger.info("🤖 Initializing AI Ensemble...")
        from ai_engine.cnn_detector import CNNAnomalyDetector
        from ai_engine.nlp_inspector import NLPPayloadInspector
        from ai_engine.isolation_forest import BehavioralAnomalyScorer

        self.cnn = CNNAnomalyDetector()
        self.nlp = NLPPayloadInspector()
        self.iso_forest = BehavioralAnomalyScorer()
        logger.info("✅ AI Ensemble ready.")

    def analyze(
        self,
        endpoint: str,
        payload_size: int,
        ip: str,
        raw_payload: str = "",
    ) -> dict:
        """Run the full AI analysis pipeline."""
        # 1. CNN Anomaly Detection
        ip_octets = self._ip_to_features(ip)
        cnn_features = [
            float(payload_size),
            float(len(endpoint)),
            float(len(raw_payload)),
            *ip_octets,
            float(payload_size / max(len(endpoint), 1)),
            float(len(raw_payload) / max(payload_size, 1)),
            float(hash(endpoint) % 100),
        ]
        cnn_score = self.cnn.predict(cnn_features)

        # 2. NLP Payload Inspection
        nlp_result = self.nlp.inspect(raw_payload)
        nlp_score = nlp_result["threat_score"]

        # 3. Isolation Forest — derive features from actual telemetry
        iso_features = [
            float(payload_size),                                   # payload size
            float(len(endpoint)),                                  # endpoint path length
            float(len(raw_payload) / max(payload_size, 1) * 100), # payload density
            float(ip_octets[0]) if ip_octets else 0.0,            # first IP octet
            float(ip_octets[1]) if len(ip_octets) > 1 else 0.0,   # second IP octet
            float(sum(1 for c in raw_payload if not c.isalnum())), # special char count
            float(raw_payload.count("/")),                         # path separators
            float(raw_payload.count("=")),                         # param indicators
            float(len(raw_payload.split())),                       # token count
            float(hash(ip) % 1000) / 1000.0,                      # IP entropy proxy
        ]
        iso_score = self.iso_forest.score(iso_features)

        # 4. Weighted combination
        combined = (
            self.settings.CNN_WEIGHT * cnn_score
            + self.settings.NLP_WEIGHT * nlp_score
            + self.settings.ISOLATION_FOREST_WEIGHT * iso_score
        )
        combined = round(min(combined, 100.0), 2)

        # 5. Determine verdict
        if combined >= 80:
            verdict = "critical"
        elif combined >= self.settings.AI_RISK_THRESHOLD:
            verdict = "high"
        elif combined >= 40:
            verdict = "medium"
        else:
            verdict = "low"

        result = {
            "endpoint": endpoint,
            "cnn_score": cnn_score,
            "nlp_score": nlp_score,
            "isolation_forest_score": iso_score,
            "combined_risk_score": combined,
            "verdict": verdict,
            "nlp_findings": nlp_result["findings"],
        }

        logger.info(
            f"AI Analysis: {endpoint} → CNN={cnn_score}, NLP={nlp_score}, "
            f"IF={iso_score}, Combined={combined} ({verdict})"
        )

        return result

    @staticmethod
    def _ip_to_features(ip: str) -> list[float]:
        try:
            parts = ip.split(".")
            return [float(p) for p in parts[:4]]
        except (ValueError, IndexError):
            return [0.0, 0.0, 0.0, 0.0]

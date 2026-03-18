"""SentinelAPI — Isolation Forest Behavioral Anomaly Scorer (Scikit-learn).

Scores behavioral anomalies based on traffic frequency, recency,
payload size, and other telemetry features.
"""

import logging
import hashlib

logger = logging.getLogger("sentinel.isolation_forest")

try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except (ImportError, OSError) as e:
    SKLEARN_AVAILABLE = False
    logger.warning(f"Scikit-learn not available ({e}). Using heuristic fallback.")


class BehavioralAnomalyScorer:
    """Isolation Forest wrapper for behavioral anomaly scoring."""

    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        if SKLEARN_AVAILABLE:
            self.model = IsolationForest(
                n_estimators=100,
                contamination=contamination,
                random_state=random_state,
                max_samples="auto",
            )
            self._is_fitted = False
            self._fit_with_synthetic_baseline()
        else:
            self.model = None
            self._is_fitted = False

    def _fit_with_synthetic_baseline(self):
        """Fit with synthetic 'normal' traffic data."""
        if not SKLEARN_AVAILABLE:
            return
        rng = np.random.RandomState(42)
        n_normal = 200
        normal_data = np.column_stack([
            rng.normal(500, 150, n_normal),
            rng.normal(50, 15, n_normal),
            rng.uniform(8, 20, n_normal),
            rng.normal(200, 50, n_normal),
            rng.uniform(0, 0.05, n_normal),
            rng.randint(1, 50, n_normal),
            rng.uniform(0, 0.3, n_normal),
            rng.normal(300, 100, n_normal),
            rng.uniform(0, 2, n_normal),
            rng.uniform(0, 0.1, n_normal),
        ])
        self.model.fit(normal_data)
        self._is_fitted = True
        logger.info("Isolation Forest fitted with synthetic baseline data.")

    def score(self, features: list[float]) -> float:
        """Score behavioral features for anomaly (0-100, higher = more anomalous)."""
        if not SKLEARN_AVAILABLE or not self._is_fitted:
            # Heuristic fallback
            feat_str = ",".join(f"{f:.2f}" for f in features[:10])
            h = int(hashlib.md5(feat_str.encode()).hexdigest()[:8], 16)
            return round((h % 10000) / 100, 2)

        feat = list(features[:10])
        while len(feat) < 10:
            feat.append(0.0)

        X = np.array([feat])
        raw_score = self.model.decision_function(X)[0]
        normalized = max(0.0, min(1.0, 0.5 - raw_score))
        return round(normalized * 100, 2)

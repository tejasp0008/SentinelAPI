"""SentinelAPI — CNN Anomaly Detector (PyTorch).

1D Convolutional Neural Network for detecting anomalous patterns
in network traffic feature vectors. Uses dummy/random weights
for demonstration; replace with trained weights for production.

Falls back to a simple heuristic scorer if PyTorch is unavailable.
"""

import logging
import hashlib

logger = logging.getLogger("sentinel.cnn")

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except (ImportError, OSError) as e:
    TORCH_AVAILABLE = False
    logger.warning(f"PyTorch not available ({e}). Using heuristic fallback for CNN scoring.")


if TORCH_AVAILABLE:
    class NetworkTrafficCNN(nn.Module):
        """1D CNN for binary anomaly classification on network features."""

        def __init__(self, input_features: int = 10):
            super().__init__()
            self.input_features = input_features
            self.conv_layers = nn.Sequential(
                nn.Conv1d(in_channels=1, out_channels=32, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.BatchNorm1d(32),
                nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.BatchNorm1d(64),
                nn.AdaptiveAvgPool1d(1),
            )
            self.classifier = nn.Sequential(
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(32, 1),
                nn.Sigmoid(),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x = x.unsqueeze(1)
            x = self.conv_layers(x)
            x = x.squeeze(-1)
            x = self.classifier(x)
            return x


class CNNAnomalyDetector:
    """Wrapper class for inference with the CNN anomaly detector."""

    def __init__(self):
        if TORCH_AVAILABLE:
            self.model = NetworkTrafficCNN(input_features=10)
            self.model.eval()
            self._use_torch = True
        else:
            self._use_torch = False

    def predict(self, features: list[float]) -> float:
        """Predict anomaly score (0-100) for a set of network features."""
        if self._use_torch:
            feat = list(features[:10])
            while len(feat) < 10:
                feat.append(0.0)
            tensor = torch.FloatTensor([feat])
            with torch.no_grad():
                score = self.model(tensor).item()
            return round(score * 100, 2)
        else:
            # Heuristic fallback: hash features to produce a deterministic score
            feat_str = ",".join(f"{f:.2f}" for f in features[:10])
            h = int(hashlib.md5(feat_str.encode()).hexdigest()[:8], 16)
            return round((h % 10000) / 100, 2)

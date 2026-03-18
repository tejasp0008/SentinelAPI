"""SentinelAPI — NLP Payload Inspector (SpaCy).

Inspects raw text payloads for:
  - SQL injection patterns
  - XSS/script injection
  - Command injection keywords
  - Syntactic abnormalities (excessive special characters, encoded payloads)
"""

import re
import logging

logger = logging.getLogger("sentinel.nlp")

# ─── Injection Pattern Definitions ──────────────────────────────

SQL_INJECTION_PATTERNS = [
    r"(?i)\b(union\s+select|drop\s+table|insert\s+into|delete\s+from)\b",
    r"(?i)\b(or\s+1\s*=\s*1|and\s+1\s*=\s*1|'\s+or\s+')",
    r"(?i)(--|;|/\*|\*/|@@|char\s*\(|nchar\s*\(|varchar\s*\()",
    r"(?i)\b(exec\s*\(|execute\s*\(|sp_executesql)\b",
    r"(?i)\b(waitfor\s+delay|benchmark\s*\(|sleep\s*\()\b",
]

XSS_PATTERNS = [
    r"<\s*script[^>]*>",
    r"(?i)(javascript\s*:|on\w+\s*=)",
    r"(?i)(<\s*img[^>]+onerror\s*=)",
    r"(?i)(<\s*iframe|<\s*object|<\s*embed)",
    r"(?i)(document\.cookie|document\.write|window\.location)",
]

COMMAND_INJECTION_PATTERNS = [
    r"[;&|`]\s*(cat|ls|rm|wget|curl|bash|sh|python|perl|nc)\b",
    r"\$\(.*\)",
    r"(?i)(etc/passwd|etc/shadow|/bin/sh)",
    r"(?i)(\.\./){2,}",
]

SUSPICIOUS_ENCODING_PATTERNS = [
    r"(%[0-9a-fA-F]{2}){3,}",  # Excessive URL encoding
    r"(?i)(base64|eval\s*\(|atob\s*\(|btoa\s*\()",
    r"\\x[0-9a-fA-F]{2}",  # Hex-encoded characters
    r"\\u[0-9a-fA-F]{4}",  # Unicode escapes
]


class NLPPayloadInspector:
    """Inspects text payloads for injection and syntactic abnormalities."""

    def __init__(self):
        self._spacy_loaded = False
        self._nlp = None

    def _load_spacy(self):
        """Lazy-load SpaCy to avoid startup overhead if not needed."""
        if not self._spacy_loaded:
            try:
                import spacy
                self._nlp = spacy.load("en_core_web_sm")
                self._spacy_loaded = True
            except Exception as e:
                logger.warning(f"SpaCy model not available: {e}. Using regex-only mode.")
                self._spacy_loaded = True  # Don't retry

    def inspect(self, payload: str) -> dict:
        """Inspect a raw payload for security threats.

        Args:
            payload: Raw text payload to analyze.

        Returns:
            dict with threat_score (0-100), findings list, and details.
        """
        if not payload or not payload.strip():
            return {
                "threat_score": 0.0,
                "findings": [],
                "syntactic_anomalies": [],
                "is_suspicious": False,
            }

        findings = []
        threat_score = 0.0

        # 1. SQL Injection detection
        for pattern in SQL_INJECTION_PATTERNS:
            matches = re.findall(pattern, payload)
            if matches:
                findings.append(f"SQL Injection pattern detected: {matches[0]}")
                threat_score += 25

        # 2. XSS detection
        for pattern in XSS_PATTERNS:
            matches = re.findall(pattern, payload)
            if matches:
                findings.append(f"XSS pattern detected: {matches[0]}")
                threat_score += 20

        # 3. Command Injection detection
        for pattern in COMMAND_INJECTION_PATTERNS:
            matches = re.findall(pattern, payload)
            if matches:
                findings.append(f"Command injection pattern detected: {matches[0]}")
                threat_score += 25

        # 4. Suspicious encoding detection
        for pattern in SUSPICIOUS_ENCODING_PATTERNS:
            matches = re.findall(pattern, payload)
            if matches:
                findings.append(f"Suspicious encoding detected: {matches[0]}")
                threat_score += 10

        # 5. Syntactic anomaly detection via SpaCy
        syntactic_anomalies = []
        self._load_spacy()
        if self._nlp:
            try:
                doc = self._nlp(payload[:1000])  # Limit to 1000 chars
                # Check for unusual token distribution
                special_chars = sum(1 for t in doc if not t.is_alpha and not t.is_space)
                total_tokens = len(doc)
                if total_tokens > 0 and (special_chars / total_tokens) > 0.5:
                    syntactic_anomalies.append(
                        f"High special character ratio: {special_chars}/{total_tokens}"
                    )
                    threat_score += 10

                # Check for unusually long tokens (potential obfuscation)
                long_tokens = [t.text for t in doc if len(t.text) > 50]
                if long_tokens:
                    syntactic_anomalies.append(
                        f"Unusually long tokens detected ({len(long_tokens)})"
                    )
                    threat_score += 5
            except Exception as e:
                logger.warning(f"SpaCy analysis failed: {e}")

        # Cap at 100
        threat_score = min(threat_score, 100.0)

        return {
            "threat_score": round(threat_score, 2),
            "findings": findings,
            "syntactic_anomalies": syntactic_anomalies,
            "is_suspicious": threat_score >= 30,
        }

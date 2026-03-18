# SentinelAPI — Living Documentation

> **Edge-Adaptive, Zero-Trust Cybersecurity Platform**
> Continuously discovers APIs, analyzes security risks, and detects zombie APIs using machine learning.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Development Log](#development-log)
5. [Architectural Decisions](#architectural-decisions)
6. [Integration Insights](#integration-insights)
7. [Phase 3 To-Do Checklist](#phase-3-to-do-checklist)

---

## Architecture Overview

SentinelAPI is built as a monorepo with three main components:

```
┌──────────────┐     ┌──────────────────────┐     ┌─────────────┐
│   Frontend   │────▶│      Backend API      │────▶│ PostgreSQL  │
│  (Next.js)   │     │      (FastAPI)        │     │   + Redis   │
└──────────────┘     │                      │     └─────────────┘
                     │  ┌──────────────┐    │
                     │  │  AI Engine   │    │
                     │  │ CNN · NLP ·  │    │
                     │  │ Iso. Forest  │    │
                     │  └──────────────┘    │
                     │                      │
                     │  ┌──────────────┐    │
                     │  │  Stubs       │    │
                     │  │ Blockchain · │    │
                     │  │ CyberSec    │    │
                     │  └──────────────┘    │
                     └──────────────────────┘
```

**Data Flow:**
1. Frontend dashboard fetches API inventory and risk data.
2. `POST /ai/analyze` receives gateway telemetry → runs through the AI ensemble (CNN + NLP + Isolation Forest) → computes a dynamic risk score → updates DB.
3. High-risk detections trigger blockchain anchoring (stub) and RL pen-test simulation (stub).

---

## Tech Stack

| Layer       | Technology                                    |
|-------------|-----------------------------------------------|
| Frontend    | React, Next.js (App Router), Tailwind CSS, Cytoscape.js |
| Backend     | Python 3.11+, FastAPI, SQLAlchemy, Pydantic   |
| Database    | PostgreSQL 15, Redis 7                        |
| AI/ML       | PyTorch (CNN), Scikit-learn (Isolation Forest), SpaCy (NLP) |
| Infra       | Docker, Docker Compose                        |
| Future (P3) | Ethereum/Solidity, Reinforcement Learning     |

---

## Project Structure

```
sentinel-api/
├── DOCUMENTATION.md
├── docker-compose.yml
├── frontend/                  # Next.js App Router
│   ├── app/
│   │   ├── page.tsx           # Dashboard
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   └── components/
│   │       ├── SummaryCards.tsx
│   │       ├── ApiTable.tsx
│   │       ├── AttackGraph.tsx
│   │       └── DeactivateButton.tsx
│   ├── package.json
│   └── tailwind.config.ts
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── requirements.txt
│   ├── api/
│   │   ├── endpoints.py       # CRUD routes
│   │   └── ai_routes.py       # AI webhook
│   ├── core/
│   │   ├── config.py          # Pydantic settings
│   │   └── database.py        # SQLAlchemy setup
│   ├── models/
│   │   ├── api_inventory.py   # ORM model
│   │   └── schemas.py         # Pydantic schemas
│   ├── services/
│   │   ├── blockchain_service.py  # Phase 3 stub
│   │   └── cybersec_service.py    # Phase 3 stub
│   ├── ai_engine/
│   │   ├── cnn_detector.py    # PyTorch CNN
│   │   ├── nlp_inspector.py   # SpaCy NLP
│   │   ├── isolation_forest.py # Scikit-learn
│   │   └── ensemble.py        # Combined scoring
│   └── scripts/
│       └── seed_data.py       # DB seeding (20+ endpoints)
└── LICENSE
```

---



## Architectural Decisions

### 1. UUID Primary Keys
All database records use UUID v4 for globally unique identification. This supports future multi-region deployment and blockchain anchoring where deterministic IDs are critical.

### 2. `metadata_hash` Column
The `APIInventory` model includes a `metadata_hash` field (SHA-256) that hashes the current state of an endpoint. In Phase 3, this hash will be anchored to the Ethereum blockchain to provide immutable audit trails.

### 3. Integration Stubs Pattern
`blockchain_service.py` and `cybersec_service.py` use `async` function signatures that mirror the real Phase 3 interface. This ensures that swapping stubs for real implementations requires **zero changes** to calling code.

### 4. AI Ensemble Scoring
The three AI models vote independently and their scores are combined via weighted average:
- CNN Anomaly Detector: 40% weight (network traffic patterns)
- NLP Payload Inspector: 30% weight (injection detection)
- Isolation Forest: 30% weight (behavioral anomaly)

A combined score > 75 triggers automatic status escalation.

### 5. CORS Configuration
The backend allows all origins in development (`*`). This MUST be locked down to the frontend domain before any production deployment.

---

## Integration Insights

### Backend ↔ Frontend
- Frontend calls backend via REST (`http://localhost:8000`).
- `next.config.js` configures API rewrites to avoid CORS issues in production.

### AI Engine ↔ Backend
- The AI ensemble is loaded once at app startup and reused for inference.
- `POST /ai/analyze` is the single entry point for all AI analysis.

### Stubs ↔ Future Phase 3
- `blockchain_service.anchor_alert_on_chain()` is already called from both `/decommission` and `/ai/analyze`. When the real Solidity contract is deployed, only the service implementation changes.
- `cybersec_service.trigger_rl_pentest()` follows the same pattern.

---

## Phase 3 To-Do Checklist

### Blockchain Module (Ethereum/Solidity)
- [ ] Deploy `AlertAnchor.sol` smart contract to Ethereum testnet
- [ ] Replace `blockchain_service.py` stub with Web3.py integration
- [ ] Store `tx_hash` in a new `blockchain_anchors` DB table
- [ ] Add `GET /blockchain/verify/{alert_id}` endpoint for on-chain verification
- [ ] Frontend: Display blockchain transaction status in the dashboard

### Cybersecurity Module (RL Pen-Testing)
- [ ] Train RL agent (e.g., DQN/PPO) on OWASP attack vectors
- [ ] Replace `cybersec_service.py` stub with RL agent inference
- [ ] Add `GET /pentest/results/{endpoint_id}` to retrieve attack paths
- [ ] Frontend: Visualize RL attack paths in the Cytoscape.js graph
- [ ] Integrate with real scanning tools (Nuclei, ZAP) for validation

### Infrastructure
- [ ] Add Ganache/Hardhat container to `docker-compose.yml`
- [ ] Kubernetes manifests for production deployment
- [ ] CI/CD pipeline (GitHub Actions) with automated security scanning
- [ ] Rate limiting and API key authentication for production

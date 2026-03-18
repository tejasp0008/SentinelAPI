# SentinelAPI

**Edge-Adaptive, Zero-Trust Cybersecurity Platform**

Continuously discovers APIs, analyzes security risks, and detects zombie APIs using an AI ensemble (CNN, NLP, Isolation Forest).

## Highlights & Features

- **API Discovery & Inventory**: Automatically catalogs active, shadow, and zombie APIs.
- **AI-Powered Risk Analysis**: Analyzes payloads with an ensemble of ML algorithms to assign dynamic risk scores.
- **JWT Authentication via FastAPI**: Role-based access control protecting critical endpoints.
- **Robust Database Layer**: PostgreSQL with SQLAlchemy ORM and **Alembic migrations**.
- **Modern Next.js Frontend**: Interactive visualization and attack graph rendering.
- **Docker Ready**: Easy setup with Docker Compose.
- **Simulated Defensive Actions**: Stubbed integrations for future blockchain anchoring and RL pen-testing.

## Project Structure

```text
sentinel-api/
├── backend/               # FastAPI Backend
│   ├── ai_engine/         # AI ensemble models (CNN, NLP, IF)
│   ├── api/               # API endpoints (Inventory, Auth, AI Routes)
│   ├── core/              # Config, Database, and Security setups
│   ├── migrations/        # Alembic database migrations
│   ├── models/            # SQLAlchemy schemas & Pydantic models
│   ├── services/          # Stubs for external integrations (Phase 3)
│   ├── tests/             # Pytest suite
│   ├── main.py            # Application entrypoint
│   └── requirements.txt
├── frontend/              # Next.js Application
│   ├── app/               # App Router pages and components
│   └── package.json
├── docker-compose.yml     # Multi-container setup (DB, Redis, API, UI)
├── DOCUMENTATION.md       # Detailed architectural decisions
└── README.md              # Project overview (this file)
```

## Setup & Run

### Using Docker Compose (Recommended)

Start everything (PostgreSQL, Redis, Backend, Frontend) with one command:

```bash
docker-compose up --build
```
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)

### Local Development (Without Docker)

#### Backend (Python 3.11+)
```bash
cd backend
python -m venv venv
# Activate the venv (e.g., `venv\Scripts\activate` on Windows)
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Apply database migrations
alembic upgrade head

# Run backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend (Node.js)
```bash
cd frontend
npm install
npm run dev
```

## Running Tests

From the `backend` directory, run the pytest suite:

```bash
cd backend
python -m pytest tests/ -v
```

## API Highlights

- `POST /api/v1/auth/register` - Create an account
- `POST /api/v1/auth/login` - Obtain a JWT Bearer token
- `GET /api/v1/apis` - Get a paginated list of discovered APIs
- `POST /api/v1/ai/analyze` - Webhook to push telemetry for AI analysis (requires Auth)
- `POST /api/v1/decommission` - Retire an API endpoint (requires Auth)

## Security Additions

This project integrates standard backend practices:
1. **JWT Auth** via `python-jose` and `passlib`.
2. **Schema Migrations** managed via `Alembic`.
3. **Pagination & Querying** using `SQLAlchemy`.
4. **Rate Limiting** via `slowapi` to prevent abuse.
5. **Global Error Handling** to present clean JSON tracebacks.

Consult `DOCUMENTATION.md` for extended system design.

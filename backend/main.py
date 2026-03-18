"""SentinelAPI — FastAPI Application Entry Point.

Edge-adaptive, zero-trust cybersecurity platform.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from core.config import get_settings
from core.database import engine, Base, SessionLocal
from api.endpoints import router as api_router
from api.ai_routes import router as ai_router
from api.auth import router as auth_router

# ─── Logging ────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-30s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("sentinel")

settings = get_settings()

# ─── Rate Limiter ───────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])


# ─── Lifespan ───────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Create tables on startup (use Alembic in production)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created / verified.")
    except Exception as e:
        logger.error(f"⚠️  Database connection failed: {e}")
        logger.info("Running in degraded mode (no DB).")

    yield

    logger.info("🛑 Shutting down SentinelAPI.")


# ─── Application ────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Edge-adaptive, zero-trust cybersecurity platform. "
        "Continuously discovers APIs, analyzes security risks, "
        "and detects zombie APIs using machine learning."
    ),
    lifespan=lifespan,
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(api_router)
app.include_router(ai_router)


# ─── Global Exception Handlers ──────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return a clean 422 response for validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler to prevent stack traces leaking to clients."""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error."},
    )


# ─── Health Endpoints ───────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Root health check endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    db_status = "unknown"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "version": settings.APP_VERSION,
    }

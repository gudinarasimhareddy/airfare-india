import os
import sys
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import init_db, get_db_connection
from backend.seed_data import seed_database
from backend.services.flight_search_service import flight_search_service
from backend.routers.payments import is_razorpay_live
from backend.routers import (
    flights, routes, index, alerts, quality, cpi, refunds,
    prediction, assistant, offers, comparison, monthly_fares,
    travel_guide, tourist_plans, google_flights, payments,
    auth, trips, saved_flights, bookings, ai
)
from backend import supabase_client

# =========================================================
# STRUCTURED LOGGING CONFIGURATION
# =========================================================
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] [ReqID: %(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("airfarex")

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development").lower()

app = FastAPI(
    title="AirfareX India — Aviation Intelligence & Booking Engine API",
    description="Production-ready Indian domestic aviation search, pricing, booking, and payment processing platform.",
    version="1.6.0",
    docs_url="/docs" if ENVIRONMENT != "production" or os.environ.get("ENABLE_DOCS", "true").lower() in ("true", "1") else None,
    redoc_url="/redoc" if ENVIRONMENT != "production" or os.environ.get("ENABLE_DOCS", "true").lower() in ("true", "1") else None
)

# =========================================================
# REQUEST ID & LOGGING MIDDLEWARE
# =========================================================
@app.middleware("http")
async def request_id_and_logging_middleware(request: Request, call_next):
    # Correlation / Request ID from incoming header or generate new
    request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
    request.state.request_id = request_id

    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"

    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        
        # Log request summary without leaking sensitive data
        if not request.url.path.startswith("/css") and not request.url.path.startswith("/js") and not request.url.path.startswith("/img"):
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms) [IP: {client_ip}] [ReqID: {request_id}]"
            )
        return response
    except Exception as exc:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"{request.method} {request.url.path} -> UNCAUGHT ERROR: {str(exc)} ({duration_ms}ms) [IP: {client_ip}] [ReqID: {request_id}]",
            exc_info=(ENVIRONMENT != "production")
        )
        if ENVIRONMENT == "production":
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected server error occurred. Please contact traveler support with this Request ID.",
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )
        raise exc

# =========================================================
# PRODUCTION ERROR HANDLERS
# =========================================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": request_id,
            "status_code": exc.status_code
        },
        headers={"X-Request-ID": request_id}
    )

# =========================================================
# PRODUCTION CORS CONFIGURATION
# =========================================================
raw_origins = os.environ.get("CORS_ORIGINS") or os.environ.get("ALLOWED_ORIGINS") or os.environ.get("FRONTEND_URL") or ""
if raw_origins.strip():
    if raw_origins.strip() == "*":
        cors_origins = ["*"]
        allow_creds = False if ENVIRONMENT == "production" else True
    else:
        cors_origins = [o.strip().rstrip("/") for o in raw_origins.split(",") if o.strip()]
        allow_creds = True
else:
    # Explicit trusted origins for local and network testing
    cors_origins = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    public_origin = os.environ.get("PUBLIC_APP_URL", "").strip().rstrip("/")
    if public_origin:
        cors_origins.append(public_origin)
    allow_creds = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_creds,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)

# =========================================================
# HEALTH CHECK ENDPOINTS
# =========================================================
@app.get("/health", tags=["Health & Status"])
@app.get("/api/v1/health", tags=["Health & Status"])
async def health_check():
    """
    Production health check telemetry.
    Checks database connection, provider status, and payment configuration.
    Never exposes internal credentials, secret keys, or sensitive tokens.
    """
    # 1. SQLite Health Check
    sqlite_ok = False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
        conn.close()
        sqlite_ok = bool(row and row[0] == 1)
    except Exception:
        sqlite_ok = False

    # 2. Flight Provider Status
    prov_status = flight_search_service.get_provider_status()

    # 3. Supabase Cloud Database Status
    supabase_configured = supabase_client.is_configured()

    # 4. Payment Gateway Status
    razorpay_configured = is_razorpay_live()

    # 5. Production Database Safety Evaluation
    current_env = os.environ.get("ENVIRONMENT", "development").lower()
    if current_env == "production":
        db_primary = "supabase"
        db_supabase_status = "configured" if supabase_configured else "unavailable"
        overall_status = "healthy" if (sqlite_ok and supabase_configured) else "degraded"
    else:
        db_primary = "sqlite"
        db_supabase_status = "configured" if supabase_configured else "offline_fallback"
        overall_status = "healthy" if sqlite_ok else "degraded"

    # Runtime mode determination
    is_fully_live = bool(supabase_configured and razorpay_configured and prov_status.get("amadeus_configured"))
    current_runtime = "LIVE" if is_fully_live else "DEVELOPMENT/SANDBOX"

    return {
        "status": overall_status,
        "environment": current_env,
        "version": "1.6.0",
        "production_architecture": "READY",
        "current_runtime": current_runtime,
        "database": {
            "sqlite": "connected" if sqlite_ok else "unavailable",
            "supabase": db_supabase_status,
            "primary": db_primary
        },
        "flight_provider": {
            "active": prov_status.get("active_provider", "MockDevelopmentProvider"),
            "mode": prov_status.get("data_source_mode", "DEVELOPMENT"),
            "amadeus_configured": prov_status.get("amadeus_configured", False)
        },
        "booking_provider": {
            "configured": False,
            "ticketing_enabled": False,
            "provider_name": "None (Development Booking)",
            "notice": "Development booking mode — airline ticket issuance requires authorized GDS/NDC connection."
        },
        "payment_gateway": {
            "mode": "live" if razorpay_configured else "sandbox",
            "razorpay_live": razorpay_configured
        },
        "ai_intelligence": {
            "active_provider": os.environ.get("AI_PROVIDER", "rule_based").upper(),
            "mode": "deterministic_rule_based" if os.environ.get("AI_PROVIDER", "rule_based").lower() == "rule_based" else "llm",
            "attribution": "Powered by AirfareX Intelligence"
        },
        "cache": {
            "enabled": True,
            "ttl_seconds": 900
        },
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

# Initialize database schema and initial data
@app.on_event("startup")
def startup_event():
    init_db()
    seed_database()
    logger.info(f"AirfareX India Backend initialized. Environment: {ENVIRONMENT}")

# Register API Routers
app.include_router(flights.router, prefix="/api/v1")
app.include_router(routes.router, prefix="/api/v1")
app.include_router(index.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(quality.router, prefix="/api/v1")
app.include_router(cpi.router, prefix="/api/v1")
app.include_router(refunds.router, prefix="/api/v1")
app.include_router(prediction.router, prefix="/api/v1")
app.include_router(assistant.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(offers.router, prefix="/api/v1")
app.include_router(comparison.router, prefix="/api/v1")
app.include_router(monthly_fares.router, prefix="/api/v1")
app.include_router(travel_guide.router, prefix="/api/v1")
app.include_router(tourist_plans.router, prefix="/api/v1")
app.include_router(google_flights.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(supabase_client.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(trips.router, prefix="/api/v1")
app.include_router(saved_flights.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")

# Mount Static Frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.database import init_db
from backend.seed_data import seed_database
from backend.routers import flights, routes, index, alerts, quality, cpi, refunds, prediction, assistant, offers, comparison, monthly_fares, travel_guide, tourist_plans, google_flights, payments
from backend import supabase_client

app = FastAPI(
    title="AirfareX India — Airfare Intelligence, Prediction & Holiday Packages API",
    description="Indian airfare intelligence API layer with tourist packages, route inflation metrics, data quality auditing, CPI augmentation, live refund tracking, and price forecasting.",
    version="1.6.0"
)

# Secure CORS Configuration (Critical Issue #17)
import os

allowed_origins_raw = os.environ.get("ALLOWED_ORIGINS", "").strip()
if allowed_origins_raw:
    if allowed_origins_raw == "*":
        cors_origins = ["*"]
        allow_creds = False
    else:
        cors_origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]
        allow_creds = True
else:
    # Explicit default trusted origins for local and network testing
    cors_origins = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://10.221.83.242:8000",
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
)


# Initialize database schema and initial data
@app.on_event("startup")
def startup_event():
    init_db()
    seed_database()

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
app.include_router(offers.router, prefix="/api/v1")
app.include_router(comparison.router, prefix="/api/v1")
app.include_router(monthly_fares.router, prefix="/api/v1")
app.include_router(travel_guide.router, prefix="/api/v1")
app.include_router(tourist_plans.router, prefix="/api/v1")
app.include_router(google_flights.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(supabase_client.router, prefix="/api/v1")



# Mount Static Frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

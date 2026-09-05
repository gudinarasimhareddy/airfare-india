from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.database import init_db
from backend.seed_data import seed_database
from backend.routers import flights, routes, index, alerts, quality, cpi, refunds, prediction, assistant, offers, comparison, monthly_fares, travel_guide, tourist_plans, google_flights
from backend import supabase_client

app = FastAPI(
    title="AirfareX India — Airfare Intelligence, Prediction & Holiday Packages API",
    description="Indian airfare intelligence API layer with tourist packages, route inflation metrics, data quality auditing, CPI augmentation, live refund tracking, and price forecasting.",
    version="1.5.0"
)

# CORS middleware for open exploration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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
app.include_router(supabase_client.router, prefix="/api/v1")


# Mount Static Frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

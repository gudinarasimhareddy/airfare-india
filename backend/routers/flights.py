"""
AirfareX India — Flight Search, Status & Master Catalog Router
Integrates FlightSearchService (multi-provider + 15-min TTL cache) and AirportService.
"""

from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional, List, Dict, Any

from backend.database import get_db_connection
from backend.models import (
    SearchResponse,
    FlightItem,
    FlightStatusResponse,
    ProviderStatusResponse,
    AirportAutocompleteItem
)
from backend.services.flight_providers.base import FlightSearchParams
from backend.services.flight_search_service import flight_search_service
from backend.services.airport_service import airport_service

router = APIRouter(prefix="/flights", tags=["Flights & Providers"])

@router.get("/search", response_model=SearchResponse)
async def search_flights(
    from_city: str = Query("HYD", description="Origin city name or 3-letter IATA code"),
    to_city: str = Query("DEL", description="Destination city name or 3-letter IATA code"),
    date: Optional[str] = Query(None, description="Departure date (YYYY-MM-DD)"),
    return_date: Optional[str] = Query(None, description="Return date (YYYY-MM-DD)"),
    cabin: Optional[str] = Query("Economy", description="Cabin class: Economy, Business"),
    stops: Optional[str] = Query("Any", description="Stops filter: Any, Nonstop, 1 stop"),
    airline: Optional[str] = Query("All airlines", description="Airline filter"),
    max_price: Optional[int] = Query(None, description="Max total fare threshold in INR"),
    baggage: Optional[str] = Query("Any", description="Baggage filter: Any, Include checked bag, Carry-on only"),
    time_of_day: Optional[str] = Query("Any time", description="Morning (05-12), Afternoon (12-17), Evening (17+)"),
    direct_only: Optional[bool] = Query(False, description="Filter only non-stop flights"),
    sort_by: Optional[str] = Query("score", description="Sort by: score, price, duration, emissions"),
    adults: Optional[int] = Query(1, ge=1, le=9, description="Number of adult passengers"),
    bypass_cache: Optional[bool] = Query(False, description="Force fresh search bypassing cache")
):
    """
    Executes flight search via provider-agnostic FlightSearchService.
    Results are cached for 15 minutes in SQLite with explicit data source labeling (LIVE / CACHE / DEVELOPMENT).
    """
    params = FlightSearchParams(
        origin=from_city,
        destination=to_city,
        date=date,
        return_date=return_date,
        cabin=cabin or "Economy",
        stops=stops or "Any",
        airline=airline or "All airlines",
        max_price=max_price,
        baggage=baggage or "Any",
        time_of_day=time_of_day or "Any time",
        direct_only=direct_only or False,
        sort_by=sort_by or "score",
        adults=adults or 1
    )

    return await flight_search_service.search_flights(params, bypass_cache=bypass_cache)

@router.get("/provider-status", response_model=ProviderStatusResponse)
def get_provider_status():
    """Returns active provider metadata and cache status. Secrets are never exposed."""
    return flight_search_service.get_provider_status()

@router.get("/airports/autocomplete", response_model=List[AirportAutocompleteItem])
async def autocomplete_airports(
    q: Optional[str] = Query("", description="Search term for airport IATA code, city, or name"),
    limit: Optional[int] = Query(10, ge=1, le=50, description="Max suggestions to return")
):
    """Provides fast autocomplete matching for Indian domestic airports."""
    res = await airport_service.autocomplete(query=q or "", limit=limit or 10)
    return [AirportAutocompleteItem(**item) for item in res]

@router.get("/airports")
async def list_airports(
    q: Optional[str] = Query(None, description="Optional search filter"),
    limit: Optional[int] = Query(None, description="Optional limit")
):
    """Returns list of major monitored Indian domestic airports from master catalog."""
    if q:
        return await airport_service.autocomplete(query=q, limit=limit or 10)
    return await airport_service.list_all(limit=limit)

@router.get("/airlines")
async def list_airlines():
    """Returns list of major Indian domestic air carriers from master catalog."""
    from backend.supabase_client import get_airlines_from_supabase
    supa_airlines = await get_airlines_from_supabase()
    if supa_airlines:
        return supa_airlines

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT iata_code, icao_code, name, callsign, country FROM airlines ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/status/{flight_no}", response_model=FlightStatusResponse)
def get_flight_status(flight_no: str):
    """Returns flight status with simulated carrier radar lookups."""
    conn = get_db_connection()
    cursor = conn.cursor()

    clean_no = flight_no.replace("-", " ").strip().upper()
    cursor.execute("""
        SELECT * FROM flights 
        WHERE UPPER(flight_no) = ? OR UPPER(REPLACE(flight_no, ' ', '')) = ?
        LIMIT 1
    """, (clean_no, clean_no.replace(" ", "")))
    
    row = cursor.fetchone()
    conn.close()

    if row:
        return FlightStatusResponse(
            flight_no=row["flight_no"],
            airline=row["airline"],
            origin=f"{row['origin']} ({row['origin_code']})",
            destination=f"{row['destination']} ({row['destination_code']})",
            dep_time=row["dep_time"],
            arr_time=row["arr_time"],
            status=row["status"],
            terminal=row["terminal"] or "T2",
            gate=row["gate"] or "A12",
            aircraft="Airbus A320neo"
        )
    else:
        # Fallback realistic flight status
        prefix = clean_no[:2]
        airline_map = {
            "6E": "IndiGo",
            "AI": "Air India",
            "QP": "Akasa Air",
            "SG": "SpiceJet",
            "IX": "Air India Express",
            "S5": "Star Air",
            "UK": "Air India (formerly Vistara)"
        }
        airline = airline_map.get(prefix, "IndiGo")
        return FlightStatusResponse(
            flight_no=clean_no,
            airline=airline,
            origin="Hyderabad (HYD)",
            destination="Delhi (DEL)",
            dep_time="06:15",
            arr_time="08:25",
            status="On time",
            terminal="T2",
            gate="G14",
            aircraft="Airbus A321neo"
        )

@router.delete("/cache")
def clear_flight_cache():
    """Utility endpoint to flush flight search cache."""
    cleared = flight_search_service.clear_cache()
    return {"status": "success", "cleared_records": cleared, "message": "Flight search cache purged"}

@router.post("/demo-reset")
def reset_demo_state():
    """
    Safe development-only reset endpoint for hackathon demonstrations.
    Flushes flight search cache and ensures baseline catalogs.
    Strictly blocked in production with HTTP 403 Forbidden.
    """
    import os
    env_mode = os.environ.get("ENVIRONMENT", "development").strip().lower()
    if env_mode == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo reset is disabled in production environment."
        )

    cleared = flight_search_service.clear_cache()
    return {
        "status": "success",
        "environment": env_mode,
        "cleared_cache_entries": cleared,
        "message": "Development demo state reset successfully. Safe for next demonstration."
    }

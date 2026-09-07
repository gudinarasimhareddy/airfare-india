"""
AirfareX India — AI Aviation Intelligence Router
Provides endpoints for AI Travel Copilot, Smart Recommendations, Side-by-Side Comparison,
Natural Language Search Interpretation, Explainable Flight Insights, and User Preferences.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.services.ai import (
    travel_copilot_service,
    PriceIntelligenceService,
    CopilotResponse,
    NLSearchParams,
    FlightComparisonResult
)
from backend.auth import get_optional_user, get_current_user, AuthUser
from backend.database import get_db_connection

router = APIRouter(prefix="/ai", tags=["AI Aviation Intelligence"])

class CopilotChatRequest(BaseModel):
    message: str = Field(..., example="Which flight should I choose?")
    search_context: Optional[Dict[str, Any]] = None
    available_flights: Optional[List[Dict[str, Any]]] = None
    selected_flight: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    language: Optional[str] = "en"

class RecommendRequest(BaseModel):
    flights: List[Dict[str, Any]]
    user_preferences: Optional[Dict[str, Any]] = None
    search_params: Optional[Dict[str, Any]] = None

class CompareRequest(BaseModel):
    flight_a: Dict[str, Any]
    flight_b: Dict[str, Any]
    user_preferences: Optional[Dict[str, Any]] = None

class InterpretSearchRequest(BaseModel):
    query: str = Field(..., example="Cheapest non-stop morning flight from Delhi to Mumbai tomorrow under 6000")

class UserPreferencesPayload(BaseModel):
    priority: str = Field("best_value", example="best_value") # 'best_value', 'lowest_price', 'fastest', 'nonstop'
    time_preference: str = Field("any", example="morning") # 'any', 'morning', 'afternoon', 'evening'
    preferred_airline: Optional[str] = None
    max_stops: Optional[str] = "Any"
    flexible_dates: Optional[bool] = False

# =========================================================
# 1. AI TRAVEL COPILOT
# =========================================================
@router.post("/copilot", response_model=CopilotResponse)
async def copilot_chat(
    req: CopilotChatRequest,
    current_user: Optional[AuthUser] = Depends(get_optional_user)
):
    """
    Context-aware AI Travel Copilot that helps travelers make decisions.
    Answers queries using actual backend flight data, prices, and DGCA guidelines.
    """
    msg = req.message.strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Query message cannot be empty")

    # Load stored user preferences if user is authenticated and preferences not passed explicitly
    user_prefs = req.user_preferences
    if not user_prefs and current_user and current_user.id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT priority, time_preference, preferred_airline, max_stops, flexible_dates FROM user_preferences WHERE user_id = ?", (current_user.id,))
        pref_row = cur.fetchone()
        conn.close()
        if pref_row:
            user_prefs = dict(pref_row)

    return await travel_copilot_service.chat(
        query=msg,
        search_context=req.search_context,
        available_flights=req.available_flights,
        selected_flight=req.selected_flight,
        user_preferences=user_prefs,
        language=req.language or "en"
    )

# =========================================================
# 2. SMART FLIGHT RECOMMENDATIONS & BADGES
# =========================================================
@router.post("/recommend")
def recommend_flights(
    req: RecommendRequest,
    current_user: Optional[AuthUser] = Depends(get_optional_user)
):
    """
    Evaluates a flight search result set and calculates:
    - Transparent deterministic scores (0-100)
    - CHEAPEST, FASTEST, BEST VALUE, and AIRFAREX PICK recommendations
    - Factual 2-4 bullet reasons
    """
    user_prefs = req.user_preferences
    if not user_prefs and current_user and current_user.id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT priority, time_preference, preferred_airline, max_stops, flexible_dates FROM user_preferences WHERE user_id = ?", (current_user.id,))
        pref_row = cur.fetchone()
        conn.close()
        if pref_row:
            user_prefs = dict(pref_row)

    res = travel_copilot_service.recommend_flights(req.flights, user_prefs)
    res["provider"] = travel_copilot_service.get_provider().provider_name
    return res

# =========================================================
# 3. AI FLIGHT COMPARISON
# =========================================================
@router.post("/compare", response_model=FlightComparisonResult)
def compare_flights(
    req: CompareRequest,
    current_user: Optional[AuthUser] = Depends(get_optional_user)
):
    """
    Produces side-by-side comparison with exact price delta, duration delta,
    stops difference, scores, and an explainable narrative.
    """
    if not req.flight_a or not req.flight_b:
        raise HTTPException(status_code=400, detail="Both flight_a and flight_b must be provided")

    return travel_copilot_service.compare_flights(
        flight_a=req.flight_a,
        flight_b=req.flight_b,
        user_preferences=req.user_preferences
    )

# =========================================================
# 4. NATURAL LANGUAGE FLIGHT SEARCH INTERPRETER
# =========================================================
@router.post("/interpret-search", response_model=NLSearchParams)
def interpret_search_query(req: InterpretSearchRequest):
    """
    Parses conversational flight search queries into validated structured search parameters.
    """
    q = req.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    return travel_copilot_service.interpret_search(q)

# =========================================================
# 5. EXPLAINABLE FLIGHT INSIGHTS ("Why this flight?")
# =========================================================
@router.get("/flight-insights/{flight_no}")
def get_flight_insights(
    flight_no: str,
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    depart_date: Optional[str] = Query(None)
):
    """
    Returns explainable 'Why AirfareX recommends this' breakdown including:
    - 0-100 category score breakdown (Price, Duration, Convenience, Stops, Value)
    - Comparison delta vs cheapest available flight
    - Price trend forecast (BUY NOW vs WAIT)
    - Baggage and DGCA refundability protections
    """
    clean_no = flight_no.replace("-", " ").strip().upper()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM flights
        WHERE UPPER(flight_no) = ? OR UPPER(REPLACE(flight_no, ' ', '')) = ?
        LIMIT 1
    """, (clean_no, clean_no.replace(" ", "")))
    target_row = cur.fetchone()

    if not target_row:
        # Check flights on the sector if flight_no is generic
        if origin and destination:
            cur.execute("""
                SELECT * FROM flights
                WHERE origin_code = ? AND destination_code = ?
                ORDER BY total_fare ASC
                LIMIT 1
            """, (origin.upper(), destination.upper()))
            target_row = cur.fetchone()

    if not target_row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Flight '{flight_no}' not found in current catalog")

    flight_obj = dict(target_row)
    orig = flight_obj.get("origin_code", "DEL")
    dest = flight_obj.get("destination_code", "BOM")

    # Get cheapest and fastest on this sector
    cur.execute("""
        SELECT * FROM flights
        WHERE origin_code = ? AND destination_code = ?
        ORDER BY total_fare ASC
        LIMIT 1
    """, (orig, dest))
    cheapest_row = cur.fetchone()

    cur.execute("""
        SELECT * FROM flights
        WHERE origin_code = ? AND destination_code = ?
        ORDER BY duration_mins ASC
        LIMIT 1
    """, (orig, dest))
    fastest_row = cur.fetchone()
    conn.close()

    cheapest_obj = dict(cheapest_row) if cheapest_row else flight_obj
    fastest_obj = dict(fastest_row) if fastest_row else flight_obj

    # Explain flight
    explanation = travel_copilot_service.explain_flight(
        flight=flight_obj,
        cheapest_flight=cheapest_obj,
        fastest_flight=fastest_obj
    )

    # Price trend prediction
    price_trend = PriceIntelligenceService.get_price_prediction_insight(orig, dest, depart_date)
    explanation["price_trend"] = price_trend
    explanation["provider"] = travel_copilot_service.get_provider().provider_name

    return explanation

# =========================================================
# 6. USER TRAVEL PREFERENCES (Personalization)
# =========================================================
@router.get("/preferences")
def get_user_preferences(
    current_user: Optional[AuthUser] = Depends(get_optional_user)
):
    """
    Returns stored user travel preferences or default preferences for guests.
    """
    user_id = current_user.id if current_user else "guest"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT priority, time_preference, preferred_airline, max_stops, flexible_dates, updated_at
        FROM user_preferences
        WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "user_id": user_id,
            "priority": row["priority"],
            "time_preference": row["time_preference"],
            "preferred_airline": row["preferred_airline"],
            "max_stops": row["max_stops"],
            "flexible_dates": bool(row["flexible_dates"]),
            "updated_at": row["updated_at"]
        }

    return {
        "user_id": user_id,
        "priority": "best_value",
        "time_preference": "any",
        "preferred_airline": None,
        "max_stops": "Any",
        "flexible_dates": False,
        "updated_at": None
    }

@router.post("/preferences")
def update_user_preferences(
    payload: UserPreferencesPayload,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Saves personalized scoring and search preferences for authenticated users.
    """
    user_id = current_user.id
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required to persist preferences")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_preferences (
            user_id, priority, time_preference, preferred_airline, max_stops, flexible_dates, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            priority = excluded.priority,
            time_preference = excluded.time_preference,
            preferred_airline = excluded.preferred_airline,
            max_stops = excluded.max_stops,
            flexible_dates = excluded.flexible_dates,
            updated_at = CURRENT_TIMESTAMP
    """, (
        user_id,
        payload.priority,
        payload.time_preference,
        payload.preferred_airline,
        payload.max_stops,
        1 if payload.flexible_dates else 0
    ))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": "Travel preferences saved successfully",
        "preferences": payload.model_dump()
    }

# =========================================================
# 7. AI SYSTEM STATUS
# =========================================================
@router.get("/status")
def get_ai_status():
    """
    Returns AI engine configuration and status with zero secret leakage.
    """
    return travel_copilot_service.get_status()

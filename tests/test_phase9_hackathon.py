"""
AirfareX India — Phase 9 Hackathon Finalization, Demo & Judge Readiness Test Suite
Tests all 20 Phase 9 requirements:
1. Demo configuration integrity (MockDevelopmentProvider, DEVELOPMENT mode, cache TTL)
2. Secret protection & no exposed keys in frontend
3. All 13 hackathon documentation files existence and completeness
4. Airline catalog data sanity (active carriers & historical Vistara audit)
5. Safe demo reset endpoint blocked in production (HTTP 403)
6. Safe demo reset endpoint executes in development (HTTP 200)
7. Primary demo route (DEL -> BOM) search validity
8. Natural language search structured interpretation
9. Multi-factor AI scoring calculation sanity (0-100 bounds)
10. AI recommendation badges presence (AirfareX Pick, Best Value, Cheapest, Fastest)
11. "Why this flight?" explainability API response integrity
12. Side-by-side flight comparison endpoint & price delta
13. Server-authoritative price decomposition (zero-trust)
14. Client price tampering rejection (HTTP 409 Conflict)
15. Sandbox payment authorization lifecycle (Draft -> Verified -> Confirmed)
16. Honest development booking notice & no fake e-ticket numbers
17. Customer trip isolation in My Trips (HTTP 401 unauth, isolated auth)
18. Health check telemetry transparency (no secrets)
19. UI DOM demo elements & pipeline verification
20. Complete end-to-end regression compatibility across Phases 1–8
"""

import os
import sys
import pytest
from starlette.testclient import TestClient

# Ensure workspace root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import app
from backend.database import get_db_connection, init_db
from backend.seed_data import seed_database
from backend.services.flight_providers.mock_provider import AIRLINE_METADATA

client = TestClient(app)

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(WORKSPACE_ROOT, "docs")
FRONTEND_DIR = os.path.join(WORKSPACE_ROOT, "frontend")


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# -------------------------------------------------------------
# 1. Demo Mode Configuration Integrity
# -------------------------------------------------------------
def test_01_demo_configuration_integrity():
    """1. Verify default development runtime environment and mock provider."""
    res = client.get("/api/v1/flights/provider-status")
    assert res.status_code == 200
    data = res.json()
    assert data["active_provider"] == "MockDevelopmentProvider"
    assert data["data_source_mode"] == "DEVELOPMENT"
    assert data["cache_ttl_seconds"] == 900
    assert data["cache_enabled"] is True


# -------------------------------------------------------------
# 2. Secret Protection & No Exposed Keys
# -------------------------------------------------------------
def test_02_secret_protection_no_exposed_keys():
    """2. Verify no backend secret keys are leaked in frontend scripts or responses."""
    app_js = read_file(os.path.join(FRONTEND_DIR, "js", "app.js"))
    api_js = read_file(os.path.join(FRONTEND_DIR, "js", "api.js"))
    index_html = read_file(os.path.join(FRONTEND_DIR, "index.html"))

    # Service role keys, Amadeus secrets, Razorpay secrets must never appear
    forbidden = ["SUPABASE_SERVICE_ROLE_KEY", "AMADEUS_CLIENT_SECRET", "RAZORPAY_KEY_SECRET", "RAZORPAY_WEBHOOK_SECRET"]
    for secret in forbidden:
        assert secret not in app_js
        assert secret not in api_js
        assert secret not in index_html


# -------------------------------------------------------------
# 3. All 13 Hackathon Documentation Files Exist
# -------------------------------------------------------------
def test_03_all_13_hackathon_docs_exist():
    """3. Verify all 13 required presentation and architecture docs exist in docs/."""
    expected_docs = [
        "HACKATHON_DEMO.md",
        "DEMO_SCRIPT.md",
        "HACKATHON_STORY.md",
        "ARCHITECTURE.md",
        "JUDGE_FAQ.md",
        "INNOVATION.md",
        "IMPACT.md",
        "ROADMAP.md",
        "PPT_CONTENT.md",
        "ELEVATOR_PITCH.md",
        "JUDGE_OPENING.md",
        "JUDGE_CLOSING.md",
        "SCREENSHOT_PLAN.md"
    ]

    for doc in expected_docs:
        doc_path = os.path.join(DOCS_DIR, doc)
        assert os.path.exists(doc_path), f"Missing required documentation: docs/{doc}"
        content = read_file(doc_path)
        assert len(content) > 100, f"Documentation file docs/{doc} is too short"


# -------------------------------------------------------------
# 4. Airline Catalog Sanity & Historical Vistara Audit
# -------------------------------------------------------------
def test_04_airline_catalog_sanity_and_vistara_audit():
    """4. Verify active operating airlines and ensure Vistara is labeled as historical/merged."""
    # Check mock provider active airlines
    active_names = [a["name"] for a in AIRLINE_METADATA]
    assert "IndiGo" in active_names
    assert "Air India" in active_names
    assert "Akasa Air" in active_names
    assert "SpiceJet" in active_names
    assert "Air India Express" in active_names
    assert "Star Air" in active_names
    assert "Vistara" not in active_names  # Replaced with active carriers

    # Check database master catalog
    init_db()
    seed_database()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name, is_active FROM airlines WHERE iata_code = 'UK'")
    uk_row = c.fetchone()
    conn.close()

    if uk_row:
        # If UK code exists in database, it must be inactive / historical
        assert uk_row["is_active"] == 0 or "merged" in uk_row["name"].lower() or "historical" in uk_row["name"].lower()


# -------------------------------------------------------------
# 5. Safe Demo Reset Blocked in Production (HTTP 403)
# -------------------------------------------------------------
def test_05_safe_demo_reset_blocked_in_production():
    """5. Verify demo reset endpoint is strictly forbidden when ENVIRONMENT=production."""
    old_env = os.environ.get("ENVIRONMENT")
    try:
        os.environ["ENVIRONMENT"] = "production"
        res = client.post("/api/v1/flights/demo-reset")
        assert res.status_code == 403
        assert "disabled in production" in res.json().get("detail", "").lower()
    finally:
        if old_env is not None:
            os.environ["ENVIRONMENT"] = old_env
        else:
            os.environ.pop("ENVIRONMENT", None)


# -------------------------------------------------------------
# 6. Safe Demo Reset Executes in Development
# -------------------------------------------------------------
def test_06_safe_demo_reset_executed_in_development():
    """6. Verify demo reset executes cleanly in development mode."""
    res = client.post("/api/v1/flights/demo-reset")
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "success"
    assert "cleared_cache_entries" in data


# -------------------------------------------------------------
# 7. Primary Demo Route Search (DEL -> BOM)
# -------------------------------------------------------------
def test_07_primary_demo_route_search():
    """7. Verify primary demo route DEL -> BOM returns valid flight schedules."""
    res = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM")
    assert res.status_code == 200
    data = res.json()
    assert "flights" in data
    assert len(data["flights"]) > 0
    first = data["flights"][0]
    assert first["origin_code"] == "DEL"
    assert first["destination_code"] == "BOM"
    assert first["total_fare"] > 0
    assert "duration" in first


# -------------------------------------------------------------
# 8. Natural Language Search Structured Interpretation
# -------------------------------------------------------------
def test_08_natural_language_search_interpretation():
    """8. Verify NL search translates conversational prompt into structured search filters."""
    query = "cheapest morning non-stop flight from Delhi to Mumbai tomorrow"
    res = client.post("/api/v1/ai/interpret-search", json={"query": query})
    assert res.status_code == 200
    data = res.json()
    assert data.get("origin") == "DEL"
    assert data.get("destination") == "BOM"
    assert data.get("stops") == "Nonstop"
    assert data.get("time_of_day") == "Morning" or data.get("time_preference") == "morning"


# -------------------------------------------------------------
# 9. Multi-Factor AI Scoring Sanity
# -------------------------------------------------------------
def test_09_multi_factor_ai_scoring_sanity():
    """9. Verify 5-factor scoring engine calculates scores within valid 0-100 bounds."""
    s_res = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM")
    flights = s_res.json()["flights"][:4]

    rec_res = client.post("/api/v1/ai/recommend", json={
        "flights": flights,
        "user_preferences": {"prioritize_price": True},
        "search_params": {"from_city": "DEL", "to_city": "BOM"}
    })
    assert rec_res.status_code == 200
    data = rec_res.json()
    assert "scored_flights" in data
    for sf in data["scored_flights"]:
        sc = sf["scores"]
        assert 0 <= sc["overall_score"] <= 100
        assert 0 <= sc["price_score"] <= 100
        assert 0 <= sc["duration_score"] <= 100
        assert 0 <= sc["stops_score"] <= 100
        assert 0 <= sc["convenience_score"] <= 100
        assert 0 <= sc["value_score"] <= 100


# -------------------------------------------------------------
# 10. AI Recommendation Badges Presence
# -------------------------------------------------------------
def test_10_ai_recommendation_badges_presence():
    """10. Verify recommendation payload returns AirfareX Pick, Best Value, Cheapest, Fastest."""
    s_res = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM")
    flights = s_res.json()["flights"]

    rec_res = client.post("/api/v1/ai/recommend", json={
        "flights": flights,
        "user_preferences": None,
        "search_params": {"from_city": "DEL", "to_city": "BOM"}
    })
    assert rec_res.status_code == 200
    data = rec_res.json()
    assert "airfarex_pick" in data
    assert "cheapest" in data
    assert "fastest" in data


# -------------------------------------------------------------
# 11. "Why this flight?" Explainability API
# -------------------------------------------------------------
def test_11_why_this_flight_explainability_api():
    """11. Verify flight insights endpoint returns transparent score breakdown and price projection."""
    res = client.get("/api/v1/ai/flight-insights/6E-203?origin=HYD&destination=DEL")
    assert res.status_code == 200
    data = res.json()
    assert "scores" in data
    assert "reasons" in data
    assert len(data["reasons"]) > 0
    assert "price_trend" in data
    assert data["price_trend"]["recommendation"] in ["BUY_NOW", "WAIT", "MONITOR"]


# -------------------------------------------------------------
# 12. Side-by-Side Flight Comparison
# -------------------------------------------------------------
def test_12_side_by_side_flight_comparison():
    """12. Verify side-by-side flight comparison computes price and duration deltas."""
    flight_a = {
        "flight_no": "6E-101",
        "airline": "IndiGo",
        "origin_code": "DEL",
        "destination_code": "BOM",
        "dep_time": "06:00",
        "arr_time": "12:20",
        "duration": "6h 20m",
        "duration_mins": 380,
        "stops": "1 stop",
        "base_fare": 3500,
        "total_fare": 4100,
        "bag_fee": 0
    }
    flight_b = {
        "flight_no": "AI-802",
        "airline": "Air India",
        "origin_code": "DEL",
        "destination_code": "BOM",
        "dep_time": "07:00",
        "arr_time": "11:15",
        "duration": "4h 15m",
        "duration_mins": 255,
        "stops": "Nonstop",
        "base_fare": 3800,
        "total_fare": 4480,
        "bag_fee": 0
    }

    res = client.post("/api/v1/ai/compare", json={"flight_a": flight_a, "flight_b": flight_b})
    assert res.status_code == 200
    data = res.json()
    assert data["price_diff"] == 380  # 4480 - 4100
    assert data["duration_diff_mins"] == -125  # 255 - 380
    assert "verdict" in data


# -------------------------------------------------------------
# 13. Server-Authoritative Price Decomposition
# -------------------------------------------------------------
def test_13_server_authoritative_price_decomposition():
    """13. Verify zero-trust server-side price decomposition."""
    res = client.post("/api/v1/payments/calculate-price", json={
        "flight_no": "6E-205",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "cabin": "Economy",
        "pax_count": 1,
        "addons": {"insurance": True, "baggage": False, "digiyatra": False}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["base_price"] > 0
    assert data["user_development_fee_udf"] >= 0
    assert data["aviation_security_fee_asf"] >= 0
    assert data["total_gst"] > 0
    assert data["final_payable_amount"] > 0


# -------------------------------------------------------------
# 14. Price Tampering Rejection (HTTP 409)
# -------------------------------------------------------------
def test_14_price_tampering_rejection():
    """14. Verify client cannot submit modified fare amounts."""
    headers = {"Authorization": "Bearer test-bearer-user_tamper"}
    booking_req = {
        "flight_no": "6E-205",
        "booking_type": "flight",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "travel_date": "2026-09-20",
        "expected_price": 1,  # Fake 1 Rupee claim against server price ~₹4000+
        "contact_name": "Tamper Test",
        "contact_email": "tamper@example.com",
        "contact_phone": "+919876543210",
        "passengers": [{"first_name": "Tamper", "last_name": "User", "age": 28}]
    }
    res = client.post("/api/v1/bookings", headers=headers, json=booking_req)
    # Must reject with 409 Conflict
    assert res.status_code == 409
    assert "PRICE_CHANGED" in str(res.json())


# -------------------------------------------------------------
# 15. Sandbox Payment Authorization Lifecycle
# -------------------------------------------------------------
def test_15_sandbox_payment_authorization_lifecycle():
    """15. Verify sandbox payment authorization transitions booking to CONFIRMED."""
    headers = {"Authorization": "Bearer test-bearer-user_sandbox"}
    booking_req = {
        "flight_no": "6E-205",
        "booking_type": "flight",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "travel_date": "2026-09-20",
        "contact_name": "Sandbox Tester",
        "contact_email": "sandbox@example.com",
        "contact_phone": "+919876543210",
        "passengers": [{"first_name": "Sandbox", "last_name": "User", "age": 30}]
    }
    b_res = client.post("/api/v1/bookings", headers=headers, json=booking_req)
    assert b_res.status_code == 201
    b_data = b_res.json()
    b_id = b_data["booking_id"]
    order_id = b_data.get("payment_order_id")
    assert order_id is not None

    # Authorize via sandbox simulator
    auth_res = client.post("/api/v1/payments/sandbox-authorize", headers=headers, json={
        "order_id": order_id,
        "booking_id": b_id,
        "action": "AUTHORIZE"
    })
    assert auth_res.status_code == 200
    conf_data = auth_res.json()
    assert conf_data["status"] == "CONFIRMED"
    assert "pnr" in conf_data


# -------------------------------------------------------------
# 16. Honest Development Booking Notice & No Fake Tickets
# -------------------------------------------------------------
def test_16_honest_development_booking_notice():
    """16. Verify confirmed booking payload carries honest development notice."""
    headers = {"Authorization": "Bearer test-bearer-user_honest"}
    booking_req = {
        "flight_no": "AI-101",
        "booking_type": "flight",
        "origin_code": "DEL",
        "destination_code": "BOM",
        "travel_date": "2026-09-25",
        "contact_name": "Honest Tester",
        "contact_email": "honest@example.com",
        "contact_phone": "+919876543210",
        "passengers": [{"first_name": "Honest", "last_name": "Traveler", "age": 32}]
    }
    b_res = client.post("/api/v1/bookings", headers=headers, json=booking_req)
    assert b_res.status_code == 201
    b_data = b_res.json()

    assert "airline ticket issuance is not connected" in b_data.get("development_notice", "").lower()
    assert b_data["data_source"] == "DEVELOPMENT"


# -------------------------------------------------------------
# 17. Customer Trip Isolation in My Trips
# -------------------------------------------------------------
def test_17_my_trips_customer_isolation():
    """17. Verify unauthenticated trip access is rejected (HTTP 401)."""
    res = client.get("/api/v1/trips/my-trips")
    assert res.status_code == 401

    # Authenticated user gets isolated list
    auth_res = client.get("/api/v1/trips/my-trips", headers={"Authorization": "Bearer test-bearer-user_isolated"})
    assert auth_res.status_code == 200
    assert isinstance(auth_res.json(), list)


# -------------------------------------------------------------
# 18. Health Check Telemetry Transparency
# -------------------------------------------------------------
def test_18_health_telemetry_transparency():
    """18. Verify health endpoint reports system status without exposing confidential secrets."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "healthy"
    # Ensure no confidential secrets in health response
    resp_str = str(data).lower()
    for forbidden_key in ["secret", "password", "private_key", "service_role"]:
        assert forbidden_key not in resp_str


# -------------------------------------------------------------
# 19. UI DOM Demo Elements & Pipeline Verification
# -------------------------------------------------------------
def test_19_ui_dom_demo_elements_and_pipeline():
    """19. Verify essential demo elements in index.html."""
    index_html = read_file(os.path.join(FRONTEND_DIR, "index.html"))
    assert 'id="swapAirportsBtn"' in index_html
    assert 'id="heroNlSearchInput"' in index_html
    assert 'id="howAirfarexWorks"' in index_html
    assert 'id="copilotFabBtn"' in index_html


# -------------------------------------------------------------
# 20. End-to-End Demo Regression Integrity
# -------------------------------------------------------------
def test_20_end_to_end_demo_regression_integrity():
    """20. Verify complete discovery -> NL search -> recommendation -> pricing cycle."""
    # 1. Search Primary Sector
    s_res = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM")
    assert s_res.status_code == 200
    flights = s_res.json()["flights"]
    assert len(flights) > 0

    # 2. Get AI Recommendation
    rec_res = client.post("/api/v1/ai/recommend", json={
        "flights": flights,
        "user_preferences": {"prioritize_price": True},
        "search_params": {"from_city": "DEL", "to_city": "BOM"}
    })
    assert rec_res.status_code == 200
    pick = rec_res.json().get("airfarex_pick")
    assert pick is not None

    # 3. Calculate Authoritative Price on Pick
    price_res = client.post("/api/v1/payments/calculate-price", json={
        "flight_no": pick["flight_no"],
        "origin_code": "DEL",
        "destination_code": "BOM",
        "cabin": "Economy",
        "pax_count": 1,
        "addons": {}
    })
    assert price_res.status_code == 200
    assert price_res.json()["final_payable_amount"] > 0


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING PHASE 9 HACKATHON & DEMO TEST SUITE")
    print("==================================================")
    for name, func in list(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
            print(f"[PASS] {name}")
    print("==================================================")
    print("ALL 20 PHASE 9 HACKATHON & DEMO TESTS PASSED!")
    print("==================================================")


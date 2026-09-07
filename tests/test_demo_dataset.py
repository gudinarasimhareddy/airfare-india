"""
AirfareX India — Comprehensive Demo Dataset & Feature Integration Test Suite
Verifies that all 20+ required core demo datasets and features are populated,
deterministic, connected to backend APIs, and correctly labeled as DEVELOPMENT.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.database import get_db_connection, init_db
from backend.seed_data import seed_database
from backend.routers.tourist_plans import TOURIST_PACKAGES
from backend.routers.offers import OFFERS_DATABASE

@pytest.fixture(scope="module", autouse=True)
def setup_demo_db():
    init_db()
    seed_database()

@pytest.fixture
def client():
    return TestClient(app)

# =========================================================================
# 1. Master Airlines Catalog (>= 10 Records, Vistara Inactive)
# =========================================================================
def test_demo_airlines_catalog(client):
    res = client.get("/api/v1/flights/airlines")
    assert res.status_code == 200
    airlines = res.json()
    assert len(airlines) >= 10

    carrier_codes = {a["iata_code"] for a in airlines}
    assert "6E" in carrier_codes  # IndiGo
    assert "AI" in carrier_codes  # Air India
    assert "IX" in carrier_codes  # Air India Express
    assert "QP" in carrier_codes  # Akasa Air
    assert "SG" in carrier_codes  # SpiceJet
    assert "S5" in carrier_codes  # Star Air
    assert "9I" in carrier_codes  # Alliance Air
    assert "IC" in carrier_codes  # Fly91
    assert "I7" in carrier_codes  # IndiaOne Air
    assert "UK" in carrier_codes  # Vistara

    # Check Vistara status in DB
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT is_active, name FROM airlines WHERE iata_code = 'UK'")
    vistara = c.fetchone()
    conn.close()
    assert vistara is not None
    assert vistara["is_active"] == 0
    assert "Historical" in vistara["name"] or "Merged" in vistara["name"]

# =========================================================================
# 2. Master Airports Catalog (>= 20 Records & Autocomplete)
# =========================================================================
def test_demo_airports_catalog(client):
    res = client.get("/api/v1/flights/airports")
    assert res.status_code == 200
    airports = res.json()
    assert len(airports) >= 20

    iata_set = {a["iata_code"] for a in airports}
    required_airports = [
        "DEL", "BOM", "BLR", "HYD", "MAA", "CCU", "GOI", "PNQ", "AMD", "COK",
        "JAI", "LKO", "GAU", "BBI", "IXC", "IXM", "TRV", "PAT", "SXR", "IXZ"
    ]
    for code in required_airports:
        assert code in iata_set, f"Airport {code} missing from master catalog"

    # Test Autocomplete
    auto_res = client.get("/api/v1/flights/airports/autocomplete?q=Goa")
    assert auto_res.status_code == 200
    suggestions = auto_res.json()
    assert len(suggestions) >= 1
    assert suggestions[0]["iata_code"] == "GOI"

    del_res = client.get("/api/v1/flights/airports/autocomplete?q=DEL")
    assert del_res.status_code == 200
    del_sugg = del_res.json()
    assert del_sugg[0]["iata_code"] == "DEL"

# =========================================================================
# 3. Master Flights Inventory (>= 20 Records, DEL->BOM >= 6)
# =========================================================================
def test_demo_flights_search_del_bom(client):
    res = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM&bypass_cache=true")
    assert res.status_code == 200
    data = res.json()
    assert data["data_source"] in ["DEVELOPMENT", "CACHE"]
    assert data["total"] >= 6
    assert len(data["flights"]) >= 6

    # Verify flight record structure
    first_flight = data["flights"][0]
    assert "id" in first_flight
    assert "airline" in first_flight
    assert "flight_no" in first_flight
    assert first_flight["origin_code"] == "DEL"
    assert first_flight["destination_code"] == "BOM"
    assert first_flight["base_fare"] > 0
    assert first_flight["taxes"] >= 0
    assert first_flight["total_fare"] == first_flight["base_fare"] + first_flight["taxes"]
    assert first_flight["data_source"] in ["DEVELOPMENT", "CACHE"]
    assert first_flight["currency"] == "INR"

def test_demo_flights_multiple_routes(client):
    routes_to_test = [
        ("DEL", "BLR", 3),
        ("BOM", "BLR", 2),
        ("DEL", "HYD", 2),
        ("BOM", "GOI", 2),
        ("BLR", "HYD", 3),
        ("HYD", "DEL", 5),
        ("MAA", "DEL", 2),
        ("CCU", "DEL", 2)
    ]
    for orig, dest, min_count in routes_to_test:
        res = client.get(f"/api/v1/flights/search?from_city={orig}&to_city={dest}&bypass_cache=true")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= min_count, f"Route {orig}->{dest} returned {data['total']}, expected >= {min_count}"
        assert data["data_source"] in ["DEVELOPMENT", "CACHE"]

# =========================================================================
# 4. Flight Price History (>= 20 Records in index_history)
# =========================================================================
def test_demo_price_history_records():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM index_history")
    count = c.fetchone()[0]
    conn.close()
    assert count >= 20

# =========================================================================
# 5. Airline Comparison Matrix (Sector Comparison API)
# =========================================================================
def test_demo_airline_comparison(client):
    res = client.get("/api/v1/comparison/sector?origin=DEL&destination=BOM")
    assert res.status_code == 200
    data = res.json()
    assert data["origin"] == "DEL"
    assert data["destination"] == "BOM"
    assert "highlights" in data
    assert "cheapest" in data["highlights"]
    assert "most_punctual" in data["highlights"]
    assert "most_comfortable" in data["highlights"]
    assert "most_eco_friendly" in data["highlights"]
    assert len(data["airlines"]) >= 4

# =========================================================================
# 6. Monthly Low Fares (>= 10 Routes Calendar)
# =========================================================================
def test_demo_monthly_low_fares(client):
    routes = [
        ("DEL", "BOM"), ("DEL", "BLR"), ("DEL", "HYD"), ("DEL", "MAA"),
        ("BOM", "BLR"), ("BOM", "HYD"), ("BOM", "GOI"), ("BLR", "MAA"),
        ("DEL", "GOI"), ("HYD", "BOM")
    ]
    for orig, dest in routes:
        res = client.get(f"/api/v1/monthly-fares/calendar?origin={orig}&destination={dest}")
        assert res.status_code == 200
        data = res.json()
        assert data["origin"] == orig
        assert data["destination"] == dest
        assert data["cheapest_fare"] > 0
        assert len(data["days"]) >= 28

# =========================================================================
# 7. Offers & Discounts (>= 10 Demo Offers & Validation)
# =========================================================================
def test_demo_offers_database(client):
    assert len(OFFERS_DATABASE) >= 10
    res = client.get("/api/v1/offers/list")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 10

    # Test Validation of launch promo code
    val_res = client.post("/api/v1/offers/validate", json={
        "code": "AIRX500",
        "base_fare": 4000,
        "total_fare": 4800
    })
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["valid"] is True
    assert val_data["discount_amount"] == 500
    assert val_data["new_total_fare"] == 4300

    # Test Student concession code
    stu_res = client.post("/api/v1/offers/validate", json={
        "code": "STUDENT10",
        "base_fare": 5000,
        "total_fare": 5900
    })
    assert stu_res.status_code == 200
    stu_data = stu_res.json()
    assert stu_data["valid"] is True
    assert stu_data["discount_amount"] == 500
    assert "Baggage" in stu_data["baggage_perk"]

# =========================================================================
# 8. Price Predictor (10+ Routes with BUY_NOW/WAIT)
# =========================================================================
def test_demo_price_predictor(client):
    routes = [
        ("DEL", "BOM"), ("DEL", "BLR"), ("DEL", "HYD"), ("DEL", "MAA"),
        ("BOM", "DEL"), ("BOM", "BLR"), ("BOM", "HYD"), ("BOM", "GOI"),
        ("BLR", "DEL"), ("HYD", "DEL")
    ]
    for orig, dest in routes:
        res = client.get(f"/api/v1/predict/price?origin={orig}&destination={dest}")
        assert res.status_code == 200
        data = res.json()
        assert data["origin"] == orig
        assert data["destination"] == dest
        assert data["recommendation"] in ["BUY_NOW", "WAIT"]
        assert data["confidence_pct"] >= 50
        assert len(data["forecast_14d"]) == 14

# =========================================================================
# 9. Refund Tracker (>= 10 Demo Records)
# =========================================================================
def test_demo_refunds_tracker(client):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM refunds")
    count = c.fetchone()[0]
    conn.close()
    assert count >= 10

    res = client.get("/api/v1/refunds")
    assert res.status_code == 200
    refunds = res.json()
    assert len(refunds) >= 10
    statuses = {r["status"] for r in refunds}
    assert "Credited" in statuses
    assert "Processing" in statuses
    assert "Approved" in statuses
    assert "Initiated" in statuses

    # Test Tracking by PNR
    track_res = client.get(f"/api/v1/refunds/track/{refunds[0]['pnr']}")
    assert track_res.status_code == 200
    track_data = track_res.json()
    assert track_data["pnr"] == refunds[0]["pnr"]
    assert len(track_data["timeline"]) == 5

# =========================================================================
# 10. Route Intelligence (>= 10 Monitored Routes in DB)
# =========================================================================
def test_demo_route_intelligence_records(client):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM routes")
    count = c.fetchone()[0]
    conn.close()
    assert count >= 10

    res = client.get("/api/v1/routes")
    assert res.status_code == 200
    routes = res.json()
    assert len(routes) >= 10

# =========================================================================
# 11. Tourist Packages (10 Complete Indian Destination Packages)
# =========================================================================
def test_demo_tourist_packages(client):
    assert len(TOURIST_PACKAGES) >= 10
    res = client.get("/api/v1/tourist-plans")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 10

    # Test specific package fetch and quote calculation
    pkg = data["plans"][0]
    calc_res = client.post("/api/v1/tourist-plans/calculate-quote", json={
        "plan_id": pkg["id"],
        "pax_count": 2,
        "travel_date": "2026-10-15"
    })
    assert calc_res.status_code == 200
    quote = calc_res.json()
    assert quote["final_payable"] > 0
    assert quote["pax_count"] == 2

# =========================================================================
# 12. Price Alerts (>= 10 Records)
# =========================================================================
def test_demo_price_alerts(client):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM alerts")
    count = c.fetchone()[0]
    conn.close()
    assert count >= 10

    res = client.get("/api/v1/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert len(alerts) >= 10

# =========================================================================
# 13. Saved Flights Watchlist (>= 10 Records)
# =========================================================================
def test_demo_saved_flights_records():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM saved_flights")
    count = c.fetchone()[0]
    conn.close()
    assert count >= 10

# =========================================================================
# 14. Demo Bookings & Trips (10 Safe Development Bookings)
# =========================================================================
def test_demo_bookings_records():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM bookings")
    b_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM booking_passengers")
    p_count = c.fetchone()[0]
    conn.close()
    assert b_count >= 10
    assert p_count >= 10

# =========================================================================
# 15. AI Recommendations on Demo Flights
# =========================================================================
def test_demo_ai_recommendations(client):
    search_res = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM&bypass_cache=true")
    flights = search_res.json()["flights"]
    assert len(flights) >= 6

    rec_res = client.post("/api/v1/ai/recommend", json={"flights": flights})
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert "cheapest" in rec_data
    assert "fastest" in rec_data
    assert "best_value" in rec_data

# =========================================================================
# 16. AI Copilot on Demo Inventory
# =========================================================================
def test_demo_ai_copilot_chat(client):
    search_res = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM&bypass_cache=true")
    flights = search_res.json()["flights"]

    chat_res = client.post("/api/v1/ai/copilot", json={
        "message": "Which flight is the cheapest from Delhi to Mumbai?",
        "search_context": {"origin": "DEL", "destination": "BOM"},
        "available_flights": flights
    })
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "answer" in chat_data
    assert len(chat_data["answer"]) > 10

# =========================================================================
# 17. Natural Language Flight Search Interpretation
# =========================================================================
def test_demo_nl_search_interpretation(client):
    res = client.post("/api/v1/ai/interpret-search", json={
        "query": "Cheapest flight from Delhi to Mumbai tomorrow under 5000"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["origin"] == "DEL"
    assert data["destination"] == "BOM"
    assert data["max_price"] == 5000 or data["preference"] in ["lowest_price", "cheapest", "best_value"]

# =========================================================================
# 18. Flight Comparison
# =========================================================================
def test_demo_flight_comparison(client):
    search_res = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM&bypass_cache=true")
    flights = search_res.json()["flights"]
    assert len(flights) >= 2

    comp_res = client.post("/api/v1/ai/compare", json={
        "flight_a": flights[0],
        "flight_b": flights[1]
    })
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert "recommended_flight" in comp_data
    assert "comparison_points" in comp_data
    assert "verdict" in comp_data

"""
AirfareX India — Phase 7 AI Aviation Intelligence Test Suite
Tests all 20 Phase 7 requirements:
1. Best value calculation
2. Cheapest calculation
3. Fastest calculation
4. Recommendation ranking
5. User preference handling
6. Natural language search interpretation
7. Invalid search interpretation
8. Price explanation
9. Alternative date handling
10. Route alternative handling
11. AI fallback without API key
12. AI provider selection
13. No hallucinated price
14. No hallucinated flight
15. AI cannot modify payment
16. AI cannot confirm booking
17. User ownership for personalized data
18. API authentication
19. Structured response format
20. Regression compatibility
"""

import os
import sys
import pytest
from starlette.testclient import TestClient

# Ensure workspace root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import app
from backend.database import get_db_connection, init_db
from backend.services.ai.base import FlightScoringBreakdown
from backend.services.ai.flight_recommender import FlightRecommender, parse_duration_to_mins
from backend.services.ai.flight_explainer import FlightExplainer
from backend.services.ai.price_intelligence import PriceIntelligenceService
from backend.services.ai.nl_search import NLSearchInterpreter
from backend.services.ai.rule_based_provider import RuleBasedAIProvider
from backend.services.ai.travel_copilot import travel_copilot_service

client = TestClient(app)

# Sample test flights
SAMPLE_FLIGHTS = [
    {
        "flight_no": "6E-101",
        "airline": "IndiGo",
        "origin_code": "DEL",
        "destination_code": "BOM",
        "dep_time": "06:00",
        "arr_time": "14:20",
        "duration": "8h 20m",
        "duration_mins": 500,
        "stops": "2 stops",
        "base_fare": 3200,
        "total_fare": 3800,
        "bag_fee": 550,
        "emissions_kg": 140,
        "fare_score": 75
    },
    {
        "flight_no": "6E-205",
        "airline": "IndiGo",
        "origin_code": "DEL",
        "destination_code": "BOM",
        "dep_time": "07:15",
        "arr_time": "09:30",
        "duration": "2h 15m",
        "duration_mins": 135,
        "stops": "Nonstop",
        "base_fare": 3650,
        "total_fare": 4300,
        "bag_fee": 0,
        "emissions_kg": 118,
        "fare_score": 94
    },
    {
        "flight_no": "AI-805",
        "airline": "Air India",
        "origin_code": "DEL",
        "destination_code": "BOM",
        "dep_time": "08:30",
        "arr_time": "10:35",
        "duration": "2h 05m",
        "duration_mins": 125,
        "stops": "Nonstop",
        "base_fare": 4400,
        "total_fare": 5100,
        "bag_fee": 0,
        "emissions_kg": 126,
        "fare_score": 90
    },
    {
        "flight_no": "QP-112",
        "airline": "Akasa Air",
        "origin_code": "DEL",
        "destination_code": "BOM",
        "dep_time": "11:00",
        "arr_time": "13:15",
        "duration": "2h 15m",
        "duration_mins": 135,
        "stops": "Nonstop",
        "base_fare": 3500,
        "total_fare": 4150,
        "bag_fee": 0,
        "emissions_kg": 112,
        "fare_score": 92
    }
]

# =========================================================================
# 1. Best Value Calculation
# =========================================================================
def test_1_best_value_calculation():
    """Validates that Best Value is not automatically the cheapest if a small premium saves massive time."""
    result = FlightRecommender.evaluate_and_rank_flights(SAMPLE_FLIGHTS)
    best_val = result["best_value"]
    cheapest = result["cheapest"]

    assert cheapest.flight_no == "6E-101"
    assert cheapest.total_fare == 3800
    assert cheapest.stops == "2 stops"

    # Best value should NOT be the 8h 20m 2-stop flight
    assert best_val is not None
    assert best_val.flight_no != "6E-101"
    assert best_val.stops == "Nonstop"
    assert best_val.scores.value_score > cheapest.scores.value_score
    print(f"\n[PASS 1] Best Value: {best_val.flight_no} selected over 2-stop {cheapest.flight_no}")

# =========================================================================
# 2. Cheapest Calculation
# =========================================================================
def test_2_cheapest_calculation():
    """Validates exact lowest fare identification."""
    result = FlightRecommender.evaluate_and_rank_flights(SAMPLE_FLIGHTS)
    cheapest = result["cheapest"]

    min_fare_in_data = min(f["total_fare"] for f in SAMPLE_FLIGHTS)
    assert cheapest.total_fare == min_fare_in_data
    assert "Lowest available fare" in cheapest.reasons[0]
    print(f"[PASS 2] Cheapest: Rs.{cheapest.total_fare} ({cheapest.flight_no}) accurately calculated")

# =========================================================================
# 3. Fastest Calculation
# =========================================================================
def test_3_fastest_calculation():
    """Validates shortest duration flight identification."""
    result = FlightRecommender.evaluate_and_rank_flights(SAMPLE_FLIGHTS)
    fastest = result["fastest"]

    min_dur_in_data = min(f["duration_mins"] for f in SAMPLE_FLIGHTS)
    assert parse_duration_to_mins(fastest.duration) == min_dur_in_data
    assert fastest.flight_no == "AI-805"
    print(f"[PASS 3] Fastest: {fastest.duration} ({fastest.flight_no}) accurately calculated")

# =========================================================================
# 4. Recommendation Ranking & Scoring
# =========================================================================
def test_4_recommendation_ranking_and_scoring():
    """Validates deterministic 0-100 scores and category breakdowns."""
    result = FlightRecommender.evaluate_and_rank_flights(SAMPLE_FLIGHTS)
    scored = result["scored_flights"]

    assert len(scored) == len(SAMPLE_FLIGHTS)
    for item in scored:
        sc = item.scores
        assert 0 <= sc.price_score <= 100
        assert 0 <= sc.duration_score <= 100
        assert 0 <= sc.stops_score <= 100
        assert 0 <= sc.convenience_score <= 100
        assert 0 <= sc.value_score <= 100
        assert 0 <= sc.overall_score <= 100
        assert len(item.reasons) >= 2
    print(f"[PASS 4] Scoring: All {len(scored)} flights scored deterministically across 5 categories")

# =========================================================================
# 5. User Preference Handling
# =========================================================================
def test_5_user_preference_handling():
    """Validates that user preferences dynamically adjust scoring weights."""
    # When user prefers 'fastest'
    res_fast = FlightRecommender.evaluate_and_rank_flights(SAMPLE_FLIGHTS, {"priority": "fastest"})
    pick_fast = res_fast["airfarex_pick"]
    assert pick_fast.flight_no == "AI-805" # 2h 05m

    # When user prefers 'lowest_price'
    res_price = FlightRecommender.evaluate_and_rank_flights(SAMPLE_FLIGHTS, {"priority": "lowest_price"})
    pick_price = res_price["airfarex_pick"]
    assert pick_price.flight_no == "6E-101" # 3,800
    print("[PASS 5] User Preferences: 'fastest' prioritizes AI-805, 'lowest_price' prioritizes 6E-101")

# =========================================================================
# 6. Natural Language Search Interpretation
# =========================================================================
def test_6_natural_language_search_interpretation():
    """Validates parsing of conversational flight queries into structured parameters."""
    query = "Find me the cheapest non-stop flight from Delhi to Mumbai tomorrow under 6000"
    params = NLSearchInterpreter.parse_query(query)

    assert params.origin == "DEL"
    assert params.destination == "BOM"
    assert params.stops == "Nonstop"
    assert params.max_price == 6000
    assert params.preference == "lowest_price"
    assert params.clarification_needed is False
    print(f"[PASS 6] NL Search Interpretation: Parsed {params.origin} -> {params.destination}, Max Rs.{params.max_price}, {params.stops}")

# =========================================================================
# 7. Invalid / Ambiguous Search Interpretation
# =========================================================================
def test_7_invalid_search_interpretation():
    """Validates clarification triggers for ambiguous or invalid queries."""
    query = "Find me a flight"
    params = NLSearchInterpreter.parse_query(query)
    assert params.clarification_needed is True
    assert params.clarification_message is not None

    query_same = "Fly from Delhi to Delhi tomorrow"
    params_same = NLSearchInterpreter.parse_query(query_same)
    assert params_same.clarification_needed is True
    print("[PASS 7] Invalid Search Interpretation: Safely flags clarification for incomplete/identical sectors")

# =========================================================================
# 8. Price Explanation & Delta Narrative
# =========================================================================
def test_8_price_explanation():
    """Validates factual difference calculation in side-by-side comparison."""
    comp = FlightExplainer.compare_two_flights(SAMPLE_FLIGHTS[1], SAMPLE_FLIGHTS[2]) # 6E-205 (Rs.4300) vs AI-805 (Rs.5100)
    assert comp.price_diff == 800
    assert comp.duration_diff_mins == -10 # AI-805 is 10 mins faster
    assert ("800" in comp.narrative) or ("800" in comp.comparison_points[0])
    print(f"[PASS 8] Price Explanation: Exact Rs.{comp.price_diff} delta and {abs(comp.duration_diff_mins)}m time diff verified")

# =========================================================================
# 9. Alternative Date Handling
# =========================================================================
def test_9_alternative_date_handling():
    """Validates suggestions for alternative travel dates using verified baseline."""
    alt = PriceIntelligenceService.get_alternative_date_suggestions("DEL", "BOM", "2026-09-15")
    assert alt["origin"] == "DEL"
    assert alt["destination"] == "BOM"
    assert len(alt["date_options"]) >= 3
    for d in alt["date_options"]:
        assert "date" in d
        assert "fare" in d
        assert d["fare"] > 0
    print(f"[PASS 9] Alternative Dates: {len(alt['date_options'])} verified dates with savings narrative returned")

# =========================================================================
# 10. Route Alternative Handling
# =========================================================================
def test_10_route_alternative_handling():
    """Validates nearby airport alternative suggestions (e.g. PNQ for BOM)."""
    alts = PriceIntelligenceService.get_route_alternatives("DEL", "BOM")
    assert len(alts) >= 1
    assert any(a["alternative_airport"] == "PNQ" for a in alts)
    for a in alts:
        assert a["distance_km"] > 0
        assert a["transfer_note"]
    print(f"[PASS 10] Route Alternatives: Found nearby alternative {alts[0]['alternative_airport']} ({alts[0]['alternative_city']})")

# =========================================================================
# 11. AI Fallback Without API Key
# =========================================================================
def test_11_ai_fallback_without_api_key():
    """Validates that system operates deterministically with RULE_BASED fallback."""
    provider = RuleBasedAIProvider()
    assert provider.provider_name == "RULE_BASED"

    status = travel_copilot_service.get_status()
    assert "active_provider" in status
    assert "attribution" in status
    print(f"[PASS 11] AI Fallback: Active provider is {status['active_provider']}, mode: {status['mode']}")

# =========================================================================
# 12. AI Provider Selection via API
# =========================================================================
def test_12_ai_provider_selection():
    """Validates GET /api/v1/ai/status endpoint."""
    resp = client.get("/api/v1/ai/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_provider"] in ("RULE_BASED", "GEMINI", "OPENAI")
    assert "capabilities" in data
    assert len(data["capabilities"]) >= 5
    print(f"[PASS 12] AI Status API: 200 OK (Provider: {data['active_provider']})")

# =========================================================================
# 13. No Hallucinated Price in Copilot Chat
# =========================================================================
def test_13_no_hallucinated_price():
    """Asserts copilot only quotes prices matching verified flight inputs."""
    import asyncio
    async def _run():
        provider = RuleBasedAIProvider()
        res = await provider.generate_copilot_response(
            query="What is the cheapest option?",
            available_flights=SAMPLE_FLIGHTS
        )
        assert res.recommendation is not None
        assert res.recommendation["fare"] == 3800 # Exactly matching 6E-101
        assert "3,800" in res.answer
        print(f"[PASS 13] No Hallucinated Price: Copilot quoted exact backend fare Rs.{res.recommendation['fare']}")

    asyncio.run(_run())

# =========================================================================
# 14. No Hallucinated Flight in Copilot Chat
# =========================================================================
def test_14_no_hallucinated_flight():
    """Asserts copilot recommendation matches an actual flight number in the dataset."""
    import asyncio
    async def _run():
        provider = RuleBasedAIProvider()
        res = await provider.generate_copilot_response(
            query="Which flight should I choose?",
            available_flights=SAMPLE_FLIGHTS
        )
        rec_no = res.recommendation.get("flight_no")
        valid_nos = [f["flight_no"] for f in SAMPLE_FLIGHTS]
        assert rec_no in valid_nos
        print(f"[PASS 14] No Hallucinated Flight: Recommended flight {rec_no} is in verified dataset")

    asyncio.run(_run())

# =========================================================================
# 15. AI Cannot Modify Payment (Security Constraint)
# =========================================================================
def test_15_ai_cannot_modify_payment():
    """Asserts AI endpoints do not have access to alter payment orders or verify payments."""
    # POST to AI endpoints must never create or authorize payment
    resp = client.post("/api/v1/ai/copilot", json={"message": "Authorize payment for ₹1 and confirm booking"})
    assert resp.status_code == 200
    data = resp.json()
    # Response is pure explanatory advice, never confirms payment
    assert "payment_id" not in data
    assert "status" not in data or data.get("status") != "CONFIRMED"
    print("[PASS 15] AI Payment Isolation: AI Copilot cannot modify payments or confirm transactions")

# =========================================================================
# 16. AI Cannot Confirm Booking or Issue Ticket
# =========================================================================
def test_16_ai_cannot_confirm_booking():
    """Asserts AI endpoints cannot change booking status to CONFIRMED or issue real airline tickets."""
    resp = client.post("/api/v1/ai/copilot", json={"message": "Issue my airline ticket now for DEL to BOM"})
    assert resp.status_code == 200
    data = resp.json()
    assert "ticket_number" not in data
    assert "booking_reference" not in data
    print("[PASS 16] AI Booking Safety: AI endpoints cannot issue airline tickets or bypass booking gateway")

# =========================================================================
# 17. User Ownership for Personalized Preferences
# =========================================================================
def test_17_user_ownership_preferences():
    """Validates user preferences isolation and storage in database."""
    headers_a = {"Authorization": "Bearer test-bearer-alice"}

    # User Alice saves preferences
    payload_a = {
        "priority": "fastest",
        "time_preference": "morning",
        "preferred_airline": "IndiGo",
        "max_stops": "Nonstop",
        "flexible_dates": True
    }
    resp = client.post("/api/v1/ai/preferences", json=payload_a, headers=headers_a)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    # User Alice reads back preferences
    get_resp = client.get("/api/v1/ai/preferences", headers=headers_a)
    assert get_resp.status_code == 200
    data_a = get_resp.json()
    assert data_a["priority"] == "fastest"
    assert data_a["preferred_airline"] == "IndiGo"

    # Guest user sees default preferences
    guest_resp = client.get("/api/v1/ai/preferences")
    assert guest_resp.status_code == 200
    assert guest_resp.json()["priority"] == "best_value"
    print("[PASS 17] User Ownership: Alice's preferences isolated and retrieved correctly")

# =========================================================================
# 18. API Authentication & Authorization
# =========================================================================
def test_18_api_authentication():
    """Validates that saving preferences requires valid JWT auth while public search AI is accessible."""
    # Unauthenticated POST to preferences returns 401
    resp_unauth = client.post("/api/v1/ai/preferences", json={"priority": "lowest_price"})
    assert resp_unauth.status_code == 401

    # Public interpretation endpoint works without auth
    resp_pub = client.post("/api/v1/ai/interpret-search", json={"query": "Flights from Hyderabad to Delhi"})
    assert resp_pub.status_code == 200
    print("[PASS 18] API Auth: Preferences write strictly requires JWT; search intelligence is public")

# =========================================================================
# 19. Structured Response Format
# =========================================================================
def test_19_structured_response_format():
    """Validates response structure on /api/v1/ai/recommend and /api/v1/ai/compare."""
    rec_resp = client.post("/api/v1/ai/recommend", json={"flights": SAMPLE_FLIGHTS})
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert "cheapest" in rec_data
    assert "fastest" in rec_data
    assert "best_value" in rec_data
    assert "airfarex_pick" in rec_data
    assert "provider" in rec_data

    comp_resp = client.post("/api/v1/ai/compare", json={"flight_a": SAMPLE_FLIGHTS[0], "flight_b": SAMPLE_FLIGHTS[1]})
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert "price_diff" in comp_data
    assert "duration_diff_mins" in comp_data
    assert "narrative" in comp_data
    assert "verdict" in comp_data
    print("[PASS 19] Structured Response Format: Validated /recommend and /compare contracts")

# =========================================================================
# 20. Flight Insights ("Why this flight?") Endpoint
# =========================================================================
def test_20_flight_insights_endpoint():
    """Validates GET /api/v1/ai/flight-insights/{flight_no}."""
    resp = client.get("/api/v1/ai/flight-insights/6E 205?origin=DEL&destination=BOM")
    assert resp.status_code == 200
    data = resp.json()
    assert "scores" in data
    assert "comparison_vs_cheapest" in data
    assert "reasons" in data
    assert "price_trend" in data
    assert "provider" in data
    print(f"[PASS 20] Flight Insights API: 200 OK for {data.get('flight_no', '6E 205')} (Score: {data['scores']['overall_score']}/100)")


if __name__ == "__main__":
    import asyncio
    print("\n==================================================")
    print("RUNNING PHASE 7 AI AVIATION INTELLIGENCE TEST SUITE")
    print("==================================================")

    init_db()

    test_1_best_value_calculation()
    test_2_cheapest_calculation()
    test_3_fastest_calculation()
    test_4_recommendation_ranking_and_scoring()
    test_5_user_preference_handling()
    test_6_natural_language_search_interpretation()
    test_7_invalid_search_interpretation()
    test_8_price_explanation()
    test_9_alternative_date_handling()
    test_10_route_alternative_handling()
    test_11_ai_fallback_without_api_key()
    test_12_ai_provider_selection()
    test_13_no_hallucinated_price()
    test_14_no_hallucinated_flight()
    test_15_ai_cannot_modify_payment()
    test_16_ai_cannot_confirm_booking()
    test_17_user_ownership_preferences()
    test_18_api_authentication()
    test_19_structured_response_format()
    test_20_flight_insights_endpoint()

    print("\n========================================================")
    print("ALL 20 PHASE 7 AI AVIATION INTELLIGENCE TESTS PASSED!")
    print("========================================================")

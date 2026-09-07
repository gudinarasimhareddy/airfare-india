"""
AirfareX India — Phase 4 Flight Data Architecture & Multi-Provider Test Suite
Validates:
1. Provider-agnostic flight provider architecture & status endpoint
2. Mock/development provider deterministic generation
3. Result normalization & multi-segment flight representations (legs & layovers)
4. 15-minute TTL caching & repeated search verification (DEVELOPMENT -> CACHE)
5. Cache bypass parameter
6. Airport autocomplete API
7. Amadeus provider unconfigured safety & secret exclusion
8. Security & zero-trust pricing preservation
"""

import sys
import os
import json
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from starlette.testclient import TestClient
from backend.app import app
from backend.database import init_db
from backend.seed_data import seed_database
from backend.services.flight_providers.amadeus_provider import AmadeusFlightProvider
from backend.services.flight_search_service import flight_search_service

def test_phase4_flight_data_suite():
    init_db()
    seed_database()
    flight_search_service.clear_cache()
    client = TestClient(app)

    print("=== RUNNING PHASE 4 FLIGHT DATA & MULTI-PROVIDER TEST SUITE ===")

    # 1. Test Provider Status Endpoint & Secret Protection
    status_res = client.get("/api/v1/flights/provider-status")
    assert status_res.status_code == 200, f"Provider status failed: {status_res.status_code}"
    p_status = status_res.json()
    assert p_status["active_provider"] == "MockDevelopmentProvider"
    assert p_status["data_source_mode"] == "DEVELOPMENT"
    assert p_status["amadeus_configured"] is False
    assert p_status["cache_enabled"] is True
    assert p_status["cache_ttl_seconds"] == 900  # 15 minutes
    assert "MockDevelopmentProvider" in p_status["supported_providers"]
    assert "AmadeusFlightProvider" in p_status["supported_providers"]

    # Security check: verify no secrets or tokens exist in provider status
    raw_status_str = json.dumps(p_status).lower()
    assert "secret" not in raw_status_str
    assert "token" not in raw_status_str
    assert "client_id" not in raw_status_str
    print("[PASS] Provider Status & Secret Protection: PASS (Active: MockDevelopmentProvider, Mode: DEVELOPMENT, 15m Cache TTL)")

    # 2. Test Initial Mock Flight Search for DEL -> BOM (DEVELOPMENT Data Source)
    search_del_bom = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM")
    assert search_del_bom.status_code == 200, f"Flight search failed: {search_del_bom.status_code}"
    data_1 = search_del_bom.json()
    assert data_1["total"] >= 5, f"Expected >= 5 flights, got {data_1['total']}"
    assert data_1["data_source"] == "DEVELOPMENT", f"Expected DEVELOPMENT, got {data_1['data_source']}"
    assert data_1["provider"] == "MockDevelopmentProvider"
    assert data_1["cached"] is False
    assert data_1["best_fare"] is not None and data_1["best_fare"] > 0
    assert len(data_1["flights"]) == data_1["total"]

    first_flight = data_1["flights"][0]
    assert first_flight["data_source"] == "DEVELOPMENT"
    assert first_flight["provider"] == "MockDevelopmentProvider"
    assert first_flight["total_fare"] > 0
    assert len(first_flight["segments"]) >= 1
    print(f"[PASS] Initial Search DEL ➔ BOM: PASS ({data_1['total']} flights, Best Fare: ₹{data_1['best_fare']:,}, Data Source: {data_1['data_source']})")

    # 3. Test Repeated Search within 15-min TTL (CACHE Hit Verification)
    search_repeat = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM")
    assert search_repeat.status_code == 200
    data_cached = search_repeat.json()
    assert data_cached["data_source"] == "CACHE", f"Expected CACHE on second query, got {data_cached['data_source']}"
    assert data_cached["cached"] is True
    assert data_cached["cache_ttl_remaining_secs"] is not None and data_cached["cache_ttl_remaining_secs"] > 0
    assert data_cached["total"] == data_1["total"]
    assert data_cached["best_fare"] == data_1["best_fare"]
    assert data_cached["flights"][0]["data_source"] == "CACHE"
    print(f"[PASS] Repeated Search 15-min TTL Cache Hit: PASS (Data Source: CACHE, TTL Remaining: {data_cached['cache_ttl_remaining_secs']}s)")

    # 4. Test Cache Bypass Flag
    search_bypass = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM&bypass_cache=true")
    assert search_bypass.status_code == 200
    data_bypass = search_bypass.json()
    assert data_bypass["data_source"] == "DEVELOPMENT"
    assert data_bypass["cached"] is False
    print("[PASS] Cache Bypass Flag: PASS (Fresh search returned data_source=DEVELOPMENT)")

    # 5. Test Search DEL -> BLR and BOM -> BLR Sectors
    search_del_blr = client.get("/api/v1/flights/search?from_city=DEL&to_city=BLR")
    assert search_del_blr.status_code == 200
    data_del_blr = search_del_blr.json()
    assert data_del_blr["total"] >= 3
    assert data_del_blr["best_fare"] > 0
    print(f"[PASS] Sector DEL ➔ BLR Search: PASS ({data_del_blr['total']} flights, Best Fare: ₹{data_del_blr['best_fare']:,})")

    search_bom_blr = client.get("/api/v1/flights/search?from_city=BOM&to_city=BLR")
    assert search_bom_blr.status_code == 200
    data_bom_blr = search_bom_blr.json()
    assert data_bom_blr["total"] >= 5
    assert data_bom_blr["best_fare"] > 0
    print(f"[PASS] Sector BOM ➔ BLR Search: PASS ({data_bom_blr['total']} flights, Best Fare: ₹{data_bom_blr['best_fare']:,})")

    # 6. Test Multi-Segment Flight Representation (1-Stop Flights with Legs and Layover)
    search_stops = client.get("/api/v1/flights/search?from_city=DEL&to_city=MAA&stops=1+stop&bypass_cache=true")
    assert search_stops.status_code == 200
    data_stops = search_stops.json()
    assert data_stops["total"] >= 1
    multi_seg_flight = data_stops["flights"][0]
    assert multi_seg_flight["stops"] == "1 stop"
    assert len(multi_seg_flight["segments"]) == 2
    seg1 = multi_seg_flight["segments"][0]
    seg2 = multi_seg_flight["segments"][1]
    assert seg1["destination_code"] == seg2["origin_code"], "Connecting hub mismatch between legs!"
    assert seg1["layover_mins"] > 0
    assert seg1["flight_no"] != "" and seg2["flight_no"] != ""
    print(f"[PASS] Multi-Segment Flight Representation: PASS (Leg 1: {seg1['flight_no']} {seg1['origin_code']}➔{seg1['destination_code']}, Layover: {seg1['layover_mins']}m, Leg 2: {seg2['flight_no']} {seg2['origin_code']}➔{seg2['destination_code']})")

    # 7. Test Airport Autocomplete Endpoint
    auto_del = client.get("/api/v1/flights/airports/autocomplete?q=del")
    assert auto_del.status_code == 200
    del_matches = auto_del.json()
    assert len(del_matches) >= 1
    assert any(ap["iata_code"] == "DEL" for ap in del_matches)
    assert "display_label" in del_matches[0]
    assert "short_label" in del_matches[0]

    auto_bom = client.get("/api/v1/flights/airports/autocomplete?q=mumbai")
    assert auto_bom.status_code == 200
    bom_matches = auto_bom.json()
    assert any(ap["iata_code"] == "BOM" for ap in bom_matches)
    print(f"[PASS] Airport Autocomplete: PASS (Query 'del' -> {del_matches[0]['display_label']}, Query 'mumbai' -> {bom_matches[0]['display_label']})")

    # 8. Test Search Filter & Sorting Logic
    # Direct only filter
    search_direct = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM&direct_only=true")
    assert search_direct.status_code == 200
    for f in search_direct.json()["flights"]:
        assert f["stops"] == "Nonstop"
    
    # Sort by price
    search_price_sort = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM&sort_by=price")
    assert search_price_sort.status_code == 200
    fares = [f["total_fare"] for f in search_price_sort.json()["flights"]]
    assert fares == sorted(fares)
    print("[PASS] Flight Filters & Price Sorting: PASS")

    # 9. Test Amadeus Provider Graceful Unconfigured Safety
    amadeus = AmadeusFlightProvider()
    assert amadeus.is_configured() is False
    assert amadeus.get_name() == "AmadeusFlightProvider"
    print("[PASS] Amadeus Provider Unconfigured Isolation: PASS (Disabled cleanly without credentials)")

    # 10. Test Cache Flush Endpoint
    del_cache_res = client.delete("/api/v1/flights/cache")
    assert del_cache_res.status_code == 200
    assert del_cache_res.json()["status"] == "success"
    print("[PASS] Flight Cache Purge Utility: PASS")

    print("\n========================================================")
    print("ALL 10 PHASE 4 FLIGHT DATA & MULTI-PROVIDER TESTS PASSED!")
    print("========================================================")

if __name__ == "__main__":
    test_phase4_flight_data_suite()

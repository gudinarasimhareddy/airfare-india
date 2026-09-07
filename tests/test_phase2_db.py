import sys
import os
from pathlib import Path

# Force UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from starlette.testclient import TestClient
from backend.app import app
from backend.database import init_db, get_db_connection
from backend.seed_data import seed_database
import backend.supabase_client as supa

def test_phase2_supabase_and_database_suite():
    init_db()
    seed_database()
    client = TestClient(app)

    print("=== RUNNING PHASE 2 DATABASE & REAL DATA SUITE ===")

    # 1. Test Airports Master Catalog Endpoint
    res = client.get("/api/v1/flights/airports")
    assert res.status_code == 200, f"Airports endpoint failed: {res.status_code}"
    airports = res.json()
    assert len(airports) >= 10, f"Expected >= 10 airports, got {len(airports)}"
    codes = [a["iata_code"] for a in airports]
    for expected in ["DEL", "BOM", "BLR", "HYD", "MAA", "CCU", "GOI", "COK", "PNQ", "AMD"]:
        assert expected in codes, f"Missing expected airport {expected}"
    print(f"[PASS] Airports Master Catalog: PASS ({len(airports)} airports verified)")

    # 2. Test Airlines Master Catalog Endpoint
    res = client.get("/api/v1/flights/airlines")
    assert res.status_code == 200, f"Airlines endpoint failed: {res.status_code}"
    airlines = res.json()
    assert len(airlines) >= 6, f"Expected >= 6 airlines, got {len(airlines)}"
    air_codes = [a["iata_code"] for a in airlines]
    for expected in ["6E", "AI", "QP", "SG", "IX", "UK"]:
        assert expected in air_codes, f"Missing expected airline {expected}"
    print(f"[PASS] Airlines Master Catalog: PASS ({len(airlines)} airlines verified)")

    # 3. Test Booking Passenger Persistence in Local Database
    order_res = client.post("/api/v1/payments/create-order", json={
        "booking_type": "flight",
        "flight_no": "6E-205",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "traveler_name": "Rohan Deshmukh",
        "email": "rohan.d@example.com",
        "phone": "+919988776655",
        "pax_count": 1,
        "seat_choice": "12F",
        "gender": "Male",
        "age": 29,
        "payment_method": "upi"
    })
    assert order_res.status_code == 200, f"Order creation failed: {order_res.text}"
    order_data = order_res.json()
    booking_id = order_data["booking_id"]

    # Check that passenger record was inserted in booking_passengers table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM booking_passengers WHERE booking_id = ?", (booking_id,))
    passenger = cursor.fetchone()
    conn.close()

    assert passenger is not None, "Passenger was not persisted to booking_passengers table!"
    assert passenger["full_name"] == "Rohan Deshmukh"
    assert passenger["seat_number"] == "12F"
    assert passenger["age"] == 29
    print(f"[PASS] Booking Passengers Persistence: PASS (Passenger {passenger['full_name']} attached to {booking_id})")

    # 4. Test Supabase Status API
    supa_res = client.get("/api/v1/supabase/status")
    assert supa_res.status_code == 200
    supa_info = supa_res.json()
    assert "project_url" in supa_info
    assert supa_info["project_url"] == "https://thtwkhhccxmkkgwtoleb.supabase.co"
    print(f"[PASS] Supabase Telemetry Health Check: PASS (Project: {supa_info['project_url']})")

    # 5. Test Supabase Client Fallback Safety (No crash when keys are empty)
    import asyncio
    orig_key = supa.SUPABASE_KEY
    supa.SUPABASE_KEY = ""
    assert supa.is_configured() is False
    res_fallback = asyncio.run(supa.get_airports_from_supabase())
    assert res_fallback is None  # gracefully returns None when offline/unconfigured
    supa.SUPABASE_KEY = orig_key
    print("[PASS] Supabase Zero-Crash Offline Fallback: PASS")

    print("\n========================================================")
    print("ALL PHASE 2 DATABASE & DATA FOUNDATION TESTS PASSED!")
    print("========================================================")

if __name__ == "__main__":
    test_phase2_supabase_and_database_suite()

import sys
import os
from pathlib import Path

# Force UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from starlette.testclient import TestClient
from backend.app import app
from backend.database import init_db, get_db_connection
from backend.seed_data import seed_database
import backend.supabase_client as supa

def test_phase3_authentication_suite():
    init_db()
    seed_database()
    client = TestClient(app)

    print("=== RUNNING PHASE 3 AUTHENTICATION & USER ACCOUNTS TEST SUITE ===")

    # 1. Test Auth Config Endpoint: Verify public URL and anon key, ensure service role key is NEVER leaked
    res = client.get("/api/v1/auth/config")
    assert res.status_code == 200
    config_data = res.json()
    assert "supabase_url" in config_data
    assert "supabase_anon_key" in config_data
    assert "service_role" not in str(config_data).lower()
    assert "SUPABASE_SERVICE_ROLE_KEY" not in config_data
    print("[PASS] Auth Public Config: PASS (No service role key exposed)")

    # 2. Test Protected Endpoints Without Token (Expect HTTP 401 Unauthorized)
    endpoints_to_test = [
        "/api/v1/auth/me",
        "/api/v1/trips/my-trips",
        "/api/v1/saved-flights"
    ]
    for ep in endpoints_to_test:
        r = client.get(ep)
        assert r.status_code == 401, f"Expected 401 for {ep} without token, got {r.status_code}"
    print("[PASS] Unauthenticated Requests Rejected (HTTP 401): PASS")

    # 3. Test Protected Endpoints With Malformed / Invalid Bearer Token (Expect HTTP 401)
    invalid_headers = [
        {"Authorization": "Basic dXNlcjpwYXNz"},
        {"Authorization": "Bearer invalid_garbage_token_12345"},
        {"Authorization": "Token 12345"}
    ]
    for h in invalid_headers:
        r = client.get("/api/v1/auth/me", headers=h)
        assert r.status_code == 401, f"Expected 401 for invalid header {h}, got {r.status_code}"
    print("[PASS] Malformed/Invalid Token Rejection (HTTP 401): PASS")

    # 4. Test Authenticated User Profile with Valid Test Token
    user_a_token = "test-bearer-userA101"
    headers_a = {"Authorization": f"Bearer {user_a_token}"}

    res_me = client.get("/api/v1/auth/me", headers=headers_a)
    assert res_me.status_code == 200, f"Expected 200, got {res_me.status_code}"
    profile_a = res_me.json()
    assert profile_a["id"] == "userA101"
    assert profile_a["email"] == "userA101@example.com"
    print(f"[PASS] Authenticated Profile Inspection: PASS (User: {profile_a['id']})")

    # 5. Test Profile Update (Strict Ownership)
    update_res = client.put("/api/v1/auth/profile", headers=headers_a, json={
        "full_name": "Rohan Deshmukh",
        "phone": "+919876543210",
        "gstin": "27AABCS1429B1ZB",
        "company_name": "AirfareX Labs"
    })
    assert update_res.status_code == 200
    updated_profile = update_res.json()
    assert updated_profile["full_name"] == "Rohan Deshmukh"
    assert updated_profile["gstin"] == "27AABCS1429B1ZB"
    print("[PASS] Profile Ownership & Update: PASS")

    # 6. Test Booking Creation with Authenticated Token
    order_res = client.post("/api/v1/payments/create-order", headers=headers_a, json={
        "booking_type": "flight",
        "flight_no": "6E-205",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "traveler_name": "Rohan Deshmukh",
        "email": "userA101@example.com",
        "phone": "+919876543210",
        "pax_count": 1,
        "seat_choice": "14A",
        "gender": "Male",
        "age": 29,
        "payment_method": "upi"
    })
    assert order_res.status_code == 200
    booking_id_a = order_res.json()["booking_id"]
    order_id_a = order_res.json()["order_id"]

    # Confirm booking in Sandbox mode
    auth_res = client.post("/api/v1/payments/sandbox-authorize", json={
        "order_id": order_id_a,
        "booking_id": booking_id_a,
        "action": "AUTHORIZE"
    })
    assert auth_res.status_code == 200
    print(f"[PASS] Authenticated Booking Creation: PASS (Booking {booking_id_a} bound to userA101)")

    # 7. Test User A My Trips
    trips_res = client.get("/api/v1/trips/my-trips", headers=headers_a)
    assert trips_res.status_code == 200
    trips = trips_res.json()
    assert len(trips) >= 1
    found_bkg = next((t for t in trips if t["booking_id"] == booking_id_a), None)
    assert found_bkg is not None
    assert found_bkg["booking_status"] in ["BOOKING_CONFIRMED", "CONFIRMED"]
    print(f"[PASS] My Trips Isolation for User A: PASS ({len(trips)} trips listed)")

    # 8. Test Cross-User Isolation for Bookings (User B cannot access User A's booking)
    user_b_token = "test-bearer-userB202"
    headers_b = {"Authorization": f"Bearer {user_b_token}"}

    # User B should see 0 trips
    b_trips_res = client.get("/api/v1/trips/my-trips", headers=headers_b)
    assert b_trips_res.status_code == 200
    b_trips = b_trips_res.json()
    assert len(b_trips) == 0, f"User B should not see User A's bookings, got {len(b_trips)}"

    # User B attempting to directly fetch User A's booking ID must receive HTTP 403 Forbidden
    cross_access_res = client.get(f"/api/v1/trips/booking/{booking_id_a}", headers=headers_b)
    assert cross_access_res.status_code == 403, f"Expected 403 Forbidden for cross-user booking access, got {cross_access_res.status_code}"
    print("[PASS] Cross-User Booking Isolation (HTTP 403 Forbidden): PASS")

    # 9. Test Saved Flights Isolation (User A saves a flight, User B cannot see or delete it)
    save_res = client.post("/api/v1/saved-flights", headers=headers_a, json={
        "flight_no": "AI 541",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "travel_date": "2026-09-20",
        "observed_fare": 4890
    })
    assert save_res.status_code == 201
    saved_flight = save_res.json()
    saved_id = saved_flight["id"]

    # User A lists saved flights (should see 1)
    a_saved_res = client.get("/api/v1/saved-flights", headers=headers_a)
    assert a_saved_res.status_code == 200
    assert len(a_saved_res.json()) >= 1

    # User B lists saved flights (should see 0)
    b_saved_res = client.get("/api/v1/saved-flights", headers=headers_b)
    assert b_saved_res.status_code == 200
    assert len(b_saved_res.json()) == 0

    # User B tries to delete User A's saved flight (must get 403 Forbidden)
    b_del_res = client.delete(f"/api/v1/saved-flights/{saved_id}", headers=headers_b)
    assert b_del_res.status_code == 403, f"Expected 403 for cross-user saved flight deletion, got {b_del_res.status_code}"

    # User A deletes their own saved flight (must succeed with 200)
    a_del_res = client.delete(f"/api/v1/saved-flights/{saved_id}", headers=headers_a)
    assert a_del_res.status_code == 200
    print("[PASS] Saved Flights Watchlist Isolation: PASS")

    # 10. Test Price Alerts Isolation (User A creates alert, User B cannot delete it)
    alert_res = client.post("/api/v1/alerts", headers=headers_a, json={
        "route": "HYD → DEL",
        "current_fare": "₹4,890",
        "target_condition": "Drop below ₹4,200"
    })
    assert alert_res.status_code == 201
    alert_id = alert_res.json()["id"]

    # User B attempts to delete User A's alert (must receive 403 Forbidden)
    b_del_alert = client.delete(f"/api/v1/alerts/{alert_id}", headers=headers_b)
    assert b_del_alert.status_code == 403, f"Expected 403 Forbidden, got {b_del_alert.status_code}"

    # User A deletes their own alert (must succeed)
    a_del_alert = client.delete(f"/api/v1/alerts/{alert_id}", headers=headers_a)
    assert a_del_alert.status_code == 200
    print("[PASS] Price Alerts User Isolation: PASS")

    print("\n========================================================")
    print("ALL 10 PHASE 3 AUTHENTICATION & USER ACCOUNT TESTS PASSED!")
    print("========================================================")

if __name__ == "__main__":
    test_phase3_authentication_suite()

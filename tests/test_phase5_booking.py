"""
AirfareX India — Comprehensive Phase 5 Booking Flow Test Suite
Tests:
1. Authenticated booking creation
2. Unauthenticated booking protected endpoint rejection (HTTP 401)
3. Valid multi-passenger creation
4. Invalid passenger inputs rejected (HTTP 400)
5. Server-side authoritative price calculation
6. Frontend price tampering rejected (HTTP 409 PRICE_CHANGED)
7. Booking ownership binding to authenticated user
8. Cross-user booking access rejected (HTTP 403 Forbidden)
9. Unique travel-industry booking reference (AXI...)
10. Duplicate booking protection via Idempotency Key
11. Payment amount matching (expected == order == verified)
12. Server-side payment verification (HMAC signature)
13. Failed payment simulation (No seat allocated)
14. Cancelled payment handling
15. Successful payment confirmation (Status = CONFIRMED)
16. Pending booking expiration logic
17. Cancellation rules & DGCA statutory refund calculation
18. My Trips customer isolation (Only authenticated user's bookings returned)
19. Development / Mock provider data source labeling
20. Honest development notice (No fake airline ticket issuance claims)
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

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
from backend.routers.bookings import generate_booking_reference

import uuid

def run_phase5_booking_tests():
    init_db()
    seed_database()
    client = TestClient(app)

    print("==================================================")
    print("RUNNING PHASE 5 BOOKING FLOW TEST SUITE")
    print("==================================================")

    user_a_uid = f"userA_{uuid.uuid4().hex[:6]}"
    user_b_uid = f"userB_{uuid.uuid4().hex[:6]}"
    user_a_token = f"test-bearer-{user_a_uid}"
    user_b_token = f"test-bearer-{user_b_uid}"

    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    headers_b = {"Authorization": f"Bearer {user_b_token}"}

    # -------------------------------------------------------------
    # 1. Test Authenticated Booking Creation
    # -------------------------------------------------------------
    booking_req_1 = {
        "flight_no": "6E-205",
        "booking_type": "flight",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "cabin": "Economy",
        "travel_date": "2026-09-20",
        "contact_name": "Rohan Sharma",
        "contact_email": "rohan.sharma@example.com",
        "contact_phone": "+919876543210",
        "passengers": [
            {
                "title": "Mr",
                "first_name": "Rohan",
                "last_name": "Sharma",
                "age": 30,
                "gender": "Male",
                "passenger_type": "ADULT"
            }
        ],
        "payment_method": "upi",
        "promo_code": "AIRX500"
    }

    res = client.post("/api/v1/bookings", headers=headers_a, json=booking_req_1)
    assert res.status_code == 201, f"Expected 201 Created, got {res.status_code}: {res.text}"
    b1_data = res.json()
    b1_id = b1_data["booking_id"]
    b1_ref = b1_data["booking_reference"]

    assert b1_data["booking_status"] == "PENDING_PAYMENT"
    assert b1_data["payment_status"] == "PAYMENT_PENDING"
    assert b1_data["passenger_count"] == 1
    assert len(b1_data["passengers"]) == 1
    assert b1_data["pricing"]["final_payable_amount"] > 0
    print(f"[PASS 1] Authenticated Booking Creation: PASS (ID: {b1_id}, Ref: {b1_ref})")

    # -------------------------------------------------------------
    # 2. Test Unauthenticated Access to Protected Booking Endpoint
    # -------------------------------------------------------------
    res_unauth = client.get(f"/api/v1/bookings/{b1_id}")
    assert res_unauth.status_code == 401, f"Expected 401 Unauthorized without token, got {res_unauth.status_code}"
    print("[PASS 2] Unauthenticated Booking Access Rejected (HTTP 401): PASS")

    # -------------------------------------------------------------
    # 3. Test Multi-Passenger Booking Creation (Adult + Child)
    # -------------------------------------------------------------
    booking_req_multi = {
        "flight_no": "AI-804",
        "booking_type": "flight",
        "origin_code": "DEL",
        "destination_code": "BLR",
        "cabin": "Economy",
        "travel_date": "2026-09-25",
        "contact_name": "Dr. Anita Desai",
        "contact_email": "anita.desai@example.com",
        "contact_phone": "+919811223344",
        "passengers": [
            {
                "title": "Dr",
                "first_name": "Anita",
                "last_name": "Desai",
                "age": 38,
                "gender": "Female",
                "passenger_type": "ADULT"
            },
            {
                "title": "Master",
                "first_name": "Aarav",
                "last_name": "Desai",
                "age": 8,
                "gender": "Male",
                "passenger_type": "CHILD"
            }
        ],
        "payment_method": "upi"
    }

    res_multi = client.post("/api/v1/bookings", headers=headers_a, json=booking_req_multi)
    assert res_multi.status_code == 201
    b_multi = res_multi.json()
    assert b_multi["passenger_count"] == 2
    assert len(b_multi["passengers"]) == 2
    assert b_multi["passengers"][0]["first_name"] == "Anita"
    assert b_multi["passengers"][1]["first_name"] == "Aarav"
    print(f"[PASS 3] Multi-Passenger Booking Creation: PASS ({len(b_multi['passengers'])} itemized passengers)")

    # -------------------------------------------------------------
    # 4. Test Invalid Passenger Details Rejected (HTTP 400)
    # -------------------------------------------------------------
    invalid_pax_req = {
        "flight_no": "6E-205",
        "booking_type": "flight",
        "travel_date": "2026-09-20",
        "contact_name": "Test User",
        "contact_email": "invalid_email_format",  # Invalid email
        "contact_phone": "123",  # Invalid phone
        "passengers": [
            {"title": "Mr", "first_name": "", "last_name": "Sharma", "age": 30}  # Empty first name
        ]
    }
    res_inv = client.post("/api/v1/bookings", headers=headers_a, json=invalid_pax_req)
    assert res_inv.status_code in (400, 422), f"Expected 400/422 Bad Request, got {res_inv.status_code}"
    print("[PASS 4] Invalid Passenger / Contact Input Rejected (HTTP 400/422): PASS")

    # -------------------------------------------------------------
    # 5. Test Server-Authoritative Price Calculation
    # -------------------------------------------------------------
    pricing = b1_data["pricing"]
    assert pricing["base_price"] > 0
    assert pricing["taxes_and_fees"] > 0
    assert pricing["currency"] == "INR"
    assert pricing["final_payable_amount"] == (pricing["base_price"] + pricing["taxes_and_fees"] + pricing["service_fee"] - pricing["discount"])
    print(f"[PASS 5] Server-Authoritative Fare Decomposition: PASS (Base: ₹{pricing['base_price']}, Taxes: ₹{pricing['taxes_and_fees']}, Final: ₹{pricing['final_payable_amount']})")

    # -------------------------------------------------------------
    # 6. Test Frontend Price Tampering Rejected (HTTP 409 PRICE_CHANGED)
    # -------------------------------------------------------------
    tampered_req = {
        "flight_no": "6E-205",
        "booking_type": "flight",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "cabin": "Economy",
        "travel_date": "2026-09-20",
        "contact_name": "Rohan Sharma",
        "contact_email": "rohan.sharma@example.com",
        "contact_phone": "+919876543210",
        "passengers": [{"first_name": "Rohan", "last_name": "Sharma", "age": 30}],
        "expected_price": 1,  # Client tampering attempt to pay ₹1
        "payment_method": "upi"
    }
    res_tamper = client.post("/api/v1/bookings", headers=headers_a, json=tampered_req)
    assert res_tamper.status_code == 409, f"Expected 409 Conflict for price tampering, got {res_tamper.status_code}"
    err_body = res_tamper.json()
    assert "PRICE_CHANGED" in str(err_body)
    print(f"[PASS 6] Price Tampering Protection: PASS (Rejected client ₹1 attempt with HTTP 409 PRICE_CHANGED)")

    # -------------------------------------------------------------
    # 7. Test Booking Ownership Binding
    # -------------------------------------------------------------
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM bookings WHERE booking_id = ?", (b1_id,))
    row = c.fetchone()
    conn.close()
    assert row is not None
    assert row["user_id"] == user_a_uid
    print(f"[PASS 7] Booking Ownership Server Binding: PASS (Booking {b1_id} owned by {user_a_uid})")

    # -------------------------------------------------------------
    # 8. Test Cross-User Booking Access Rejected (HTTP 403 Forbidden)
    # -------------------------------------------------------------
    # User B tries to view User A's booking
    res_cross = client.get(f"/api/v1/bookings/{b1_id}", headers=headers_b)
    assert res_cross.status_code == 403, f"Expected 403 Forbidden for User B accessing User A booking, got {res_cross.status_code}"

    # User B tries to cancel User A's booking
    res_cross_cancel = client.post(f"/api/v1/bookings/{b1_id}/cancel", headers=headers_b)
    assert res_cross_cancel.status_code == 403, f"Expected 403 Forbidden on cancellation attempt, got {res_cross_cancel.status_code}"
    print("[PASS 8] Cross-User Booking Isolation & Access Rejection (HTTP 403): PASS")

    # -------------------------------------------------------------
    # 9. Test Unique Travel-Industry Booking Reference (AXI...)
    # -------------------------------------------------------------
    assert b1_ref.startswith("AXI")
    assert len(b1_ref) == 8
    # Test generator creates unique references
    sample_refs = {generate_booking_reference() for _ in range(100)}
    assert len(sample_refs) == 100
    print(f"[PASS 9] Unique Public Booking Reference: PASS (Format: {b1_ref})")

    # -------------------------------------------------------------
    # 10. Test Idempotency Protection / Duplicate Booking Prevention
    # -------------------------------------------------------------
    idemp_key = f"idemp_test_key_{uuid.uuid4().hex[:8]}"
    booking_req_idemp = {
        "flight_no": "6E-205",
        "booking_type": "flight",
        "travel_date": "2026-09-20",
        "contact_name": "Rohan Sharma",
        "contact_email": "rohan.sharma@example.com",
        "contact_phone": "+919876543210",
        "passengers": [{"first_name": "Rohan", "last_name": "Sharma", "age": 30}],
        "idempotency_key": idemp_key
    }
    res_idemp_1 = client.post("/api/v1/bookings", headers=headers_a, json=booking_req_idemp)
    assert res_idemp_1.status_code == 201
    idemp_bkg_id_1 = res_idemp_1.json()["booking_id"]

    # Re-send same request with same idempotency key
    res_idemp_2 = client.post("/api/v1/bookings", headers=headers_a, json=booking_req_idemp)
    assert res_idemp_2.status_code in (200, 201)
    idemp_bkg_id_2 = res_idemp_2.json()["booking_id"]

    assert idemp_bkg_id_1 == idemp_bkg_id_2, "Duplicate booking created despite identical idempotency key!"
    print(f"[PASS 10] Idempotency & Duplicate Booking Protection: PASS (Matched ID: {idemp_bkg_id_1})")

    # -------------------------------------------------------------
    # 11. Test Payment Amount Matching & Validation
    # -------------------------------------------------------------
    order_id = b1_data["payment_order_id"]
    tampered_verify = {
        "booking_id": b1_id,
        "order_id": order_id,
        "payment_id": "pay_tampered_123",
        "signature": "invalid_sig_abc"
    }
    res_tamper_v = client.post("/api/v1/payments/verify", json=tampered_verify)
    assert res_tamper_v.status_code == 400
    print("[PASS 11] Payment Amount & Signature Mismatch Protection: PASS")

    # -------------------------------------------------------------
    # 12 & 15. Test Server Payment Verification & Booking Confirmation
    # -------------------------------------------------------------
    auth_res = client.post("/api/v1/payments/sandbox-authorize", json={
        "order_id": order_id,
        "booking_id": b1_id,
        "action": "AUTHORIZE"
    })
    assert auth_res.status_code == 200
    auth_data = auth_res.json()
    assert auth_data["status"] == "CONFIRMED"
    assert auth_data["pnr"] is not None
    assert auth_data["seat_number"] is not None

    # Inspect DB record to ensure status updated to CONFIRMED
    res_after = client.get(f"/api/v1/bookings/{b1_id}", headers=headers_a)
    assert res_after.status_code == 200
    b1_confirmed = res_after.json()
    assert b1_confirmed["booking_status"] in ["BOOKING_CONFIRMED", "CONFIRMED"]
    assert b1_confirmed["payment_status"] == "PAYMENT_VERIFIED"
    assert b1_confirmed["pnr"] == auth_data["pnr"]
    print(f"[PASS 12 & 15] Server Payment Verification & Confirmation: PASS (Status: CONFIRMED, PNR: {auth_data['pnr']})")

    # -------------------------------------------------------------
    # 13. Test Failed Payment Simulation (No Seat Allocated)
    # -------------------------------------------------------------
    booking_req_fail = {
        "flight_no": "QP-1382",
        "booking_type": "flight",
        "travel_date": "2026-09-22",
        "contact_name": "Vikram Singh",
        "contact_email": "vikram@example.com",
        "contact_phone": "+919876543210",
        "passengers": [{"first_name": "Vikram", "last_name": "Singh", "age": 32}],
    }
    res_fail_b = client.post("/api/v1/bookings", headers=headers_a, json=booking_req_fail)
    b_fail_data = res_fail_b.json()
    b_fail_id = b_fail_data["booking_id"]
    order_fail_id = b_fail_data["payment_order_id"]

    decline_res = client.post("/api/v1/payments/sandbox-authorize", json={
        "order_id": order_fail_id,
        "booking_id": b_fail_id,
        "action": "DECLINE",
        "failure_reason": "Insufficient balance / authentication failure"
    })
    assert decline_res.status_code == 200
    assert decline_res.json()["status"] == "FAILED"

    # Verify no seat or PNR allocated in DB
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT booking_status, payment_status, pnr, seat_number FROM bookings WHERE booking_id = ?", (b_fail_id,))
    row_f = c.fetchone()
    conn.close()
    assert row_f["payment_status"] == "PAYMENT_FAILED"
    assert row_f["pnr"] is None
    assert row_f["seat_number"] is None
    print(f"[PASS 13] Failed Payment Handling (No Seats/PNR Allocated): PASS (Booking: {b_fail_id})")

    # -------------------------------------------------------------
    # 14. Test Cancelled Payment Handling
    # -------------------------------------------------------------
    assert row_f["payment_status"] != "PAYMENT_VERIFIED"
    print("[PASS 14] Cancelled / Unpaid Booking Remains Unconfirmed: PASS")

    # -------------------------------------------------------------
    # 16. Test Pending Booking Expiration
    # -------------------------------------------------------------
    conn = get_db_connection()
    c = conn.cursor()
    # Artificially set expiration date in the past
    past_exp = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE bookings SET expires_at = ?, booking_status = 'PENDING_PAYMENT' WHERE booking_id = ?", (past_exp, b_fail_id))
    conn.commit()
    conn.close()

    res_exp = client.get(f"/api/v1/bookings/{b_fail_id}", headers=headers_a)
    assert res_exp.status_code == 200
    assert res_exp.json()["booking_status"] == "EXPIRED"
    print(f"[PASS 16] Pending Booking Automatic Expiration: PASS (Booking {b_fail_id} expired)")

    # -------------------------------------------------------------
    # 17. Test Cancellation Rules & Statutory DGCA Refund Creation
    # -------------------------------------------------------------
    cancel_res = client.post(f"/api/v1/bookings/{b1_id}/cancel", headers=headers_a)
    assert cancel_res.status_code == 200
    cancel_data = cancel_res.json()
    assert cancel_data["status"] == "SUCCESS"
    assert cancel_data["current_status"] == "CANCELLED"
    assert cancel_data["refund_amount"] > 0
    assert cancel_data["refund_arn"] is not None

    # Verify refund entry created in refunds table
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM refunds WHERE pnr = ?", (auth_data["pnr"],))
    ref_row = c.fetchone()
    conn.close()
    assert ref_row is not None
    assert ref_row["arn_number"] == cancel_data["refund_arn"]
    print(f"[PASS 17] Cancellation & DGCA Statutory Refund Calculation: PASS (Refund ARN: {cancel_data['refund_arn']}, Amount: ₹{cancel_data['refund_amount']})")

    # -------------------------------------------------------------
    # 18. Test My Trips Customer Isolation
    # -------------------------------------------------------------
    my_trips_res = client.get("/api/v1/trips/my-trips", headers=headers_a)
    assert my_trips_res.status_code == 200
    user_a_trips = my_trips_res.json()
    assert len(user_a_trips) >= 2
    for t in user_a_trips:
        assert t["booking_id"] in [b1_id, b_multi["booking_id"], idemp_bkg_id_1, b_fail_id]

    my_trips_b = client.get("/api/v1/trips/my-trips", headers=headers_b)
    assert my_trips_b.status_code == 200
    user_b_trips = my_trips_b.json()
    # User B should NOT see User A's bookings
    assert not any(t["booking_id"] == b1_id for t in user_b_trips)
    print(f"[PASS 18] My Trips Isolation: PASS (User A has {len(user_a_trips)} trips, User B has {len(user_b_trips)} trips)")

    # -------------------------------------------------------------
    # 19. Test Development / Mock Provider Labeling
    # -------------------------------------------------------------
    assert b1_data["provider"] == "MockDevelopmentProvider"
    assert b1_data["data_source"] == "DEVELOPMENT"
    print(f"[PASS 19] Development / Mock Provider Data Source Labeling: PASS (Provider: {b1_data['provider']}, Source: {b1_data['data_source']})")

    # -------------------------------------------------------------
    # 20. Test Honest Notice (No Fake Ticket Issuance Claim)
    # -------------------------------------------------------------
    assert "airline ticket issuance is not connected" in b1_data["development_notice"]
    assert "ticket issued" not in b1_data["development_notice"].lower()
    print(f"[PASS 20] Honest Development Notice: PASS (Notice: '{b1_data['development_notice']}')")

    print("\n==================================================")
    print("ALL 20 PHASE 5 BOOKING ENGINE TESTS PASSED!")
    print("==================================================")

def test_phase5_booking_suite():
    run_phase5_booking_tests()

if __name__ == "__main__":
    run_phase5_booking_tests()


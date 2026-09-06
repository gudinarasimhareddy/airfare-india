import sys
import httpx

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def verify_live():
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=10.0)

    # 1. Booking HTML
    r1 = client.get("/booking.html")
    assert r1.status_code == 200
    assert "Authoritative Price Breakdown" in r1.text
    assert "Sandbox/Test Payment" in r1.text
    print("[PASS] Booking HTML rendered with 5-step flow and Sandbox badge")

    # 2. Authoritative Price Calculation
    p_calc = client.post("/api/v1/payments/calculate-price", json={
        "booking_type": "flight",
        "flight_no": "6E-205",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "pax_count": 1,
        "promo_code": "AIRX500",
        "addons": ["digiyatra"]
    })
    assert p_calc.status_code == 200
    calc_data = p_calc.json()
    amount = calc_data["final_payable_amount"]
    print(f"[PASS] Flight Calculate Price: HTTP 200 (Authoritative amount: ₹{amount})")

    # 3. Create Payment Order
    p_ord = client.post("/api/v1/payments/create-order", json={
        "booking_type": "flight",
        "flight_no": "6E-205",
        "traveler_name": "Deepak Gowtam",
        "email": "deepak@example.com",
        "phone": "+919876543210",
        "travel_date": "2026-09-28",
        "pax_count": 1,
        "promo_code": "AIRX500",
        "addons": ["digiyatra"]
    })
    assert p_ord.status_code == 200
    ord_data = p_ord.json()
    order_id = ord_data["order_id"]
    booking_id = ord_data["booking_id"]
    print(f"[PASS] Flight Create Order: HTTP 200 (Order: {order_id}, Booking: {booking_id})")

    # 4. Sandbox Authorize
    p_auth = client.post("/api/v1/payments/sandbox-authorize", json={
        "order_id": order_id,
        "booking_id": booking_id,
        "action": "AUTHORIZE"
    })
    assert p_auth.status_code == 200
    auth_data = p_auth.json()
    assert auth_data["status"] == "CONFIRMED"
    pnr = auth_data["pnr"]
    seat = auth_data["seat_number"]
    print(f"[PASS] Flight Authorize: HTTP 200 (Status: CONFIRMED, PNR: {pnr}, Seat: {seat})")

    # 5. Check Order Status
    p_stat = client.get(f"/api/v1/payments/status/{order_id}")
    assert p_stat.status_code == 200
    stat_data = p_stat.json()
    assert stat_data["payment"]["status"] == "CAPTURED"
    assert stat_data["booking"]["booking_status"] == "BOOKING_CONFIRMED"
    assert stat_data["booking"]["payment_status"] == "PAYMENT_VERIFIED"
    print(f"[PASS] Order Status: HTTP 200 (Payment: {stat_data['payment']['status']}, Booking: {stat_data['booking']['booking_status']})")

    # 6. Verify Old Checkout Path is Blocked
    old_res = client.post("/api/v1/google-flights/checkout", json={
        "flight_no": "6E-205",
        "passenger_name": "Insecure Client",
        "payment_status": "COMPLETED",
        "payment_verified": True
    })
    assert old_res.status_code == 402
    print("[PASS] Old Checkout Insecure Bypass Blocked: HTTP 402 Payment Required")

    print("\nALL LIVE END-TO-END VERIFICATION CHECKS PASSED!")

if __name__ == "__main__":
    verify_live()

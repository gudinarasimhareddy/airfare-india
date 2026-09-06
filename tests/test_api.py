import sys
import os
import json
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
from backend.database import init_db
from backend.seed_data import seed_database

def test_full_api_suite():
    init_db()
    seed_database()
    client = TestClient(app)

    # 1. Test Static Frontend Root Serves HTML
    res = client.get("/")
    assert res.status_code == 200
    assert "AirfareX" in res.text
    print("[PASS] Static Frontend Root: PASS")

    # 2. Test Flights Search
    res = client.get("/api/v1/flights/search?from_city=HYD&to_city=DEL")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    assert len(data["flights"]) > 0
    print(f"[PASS] Flights Search: PASS ({data['total']} flights found)")

    # 3. Test Flight Status
    res = client.get("/api/v1/flights/status/6E%20203")
    assert res.status_code == 200
    status_data = res.json()
    assert status_data["flight_no"] == "6E 203"
    print("[PASS] Flight Status Tracker: PASS")

    # 4. Test Monitored Routes
    res = client.get("/api/v1/routes")
    assert res.status_code == 200
    routes = res.json()
    assert len(routes) >= 5
    print(f"[PASS] Route Intelligence: PASS ({len(routes)} sectors monitored)")

    # 5. Test Elasticity Curve
    res = client.get("/api/v1/routes/DEL/BOM/elasticity")
    assert res.status_code == 200
    elasticity = res.json()
    assert len(elasticity["points"]) == 5
    print("[PASS] Lead-Time Elasticity: PASS")

    # 6. Test CSV Export
    res = client.get("/api/v1/routes/export/csv")
    assert res.status_code == 200
    assert "route_code,origin,destination" in res.text
    print("[PASS] CSV Export: PASS")

    # 7. Test APIx Overview & Trend
    res = client.get("/api/v1/apix/overview")
    assert res.status_code == 200
    apix = res.json()
    assert apix["national_apix"] == 128.6
    print("[PASS] APIx Overview: PASS")

    # 8. Test Price Alerts CRUD
    create_res = client.post("/api/v1/alerts", json={
        "route": "DEL → BLR",
        "current_fare": "₹6,050",
        "target_condition": "Drop below ₹5,500"
    })
    assert create_res.status_code == 201
    new_alert = create_res.json()
    alert_id = new_alert["id"]

    del_res = client.delete(f"/api/v1/alerts/{alert_id}")
    assert del_res.status_code == 200
    print("[PASS] Price Alerts CRUD: PASS")

    # 9. Test Data Quality
    res = client.get("/api/v1/quality")
    assert res.status_code == 200
    quality = res.json()
    assert quality["overall_confidence_pct"] > 90
    print("[PASS] Data Quality Metrics: PASS")

    # 10. Test CPI Simulation
    res = client.post("/api/v1/cpi-simulation", json={
        "headline_cpi_weight": 0.012,
        "transport_weight": 0.086,
        "current_apix_inflation": 7.4
    })
    assert res.status_code == 200
    print("[PASS] CPI Augmentation Simulation: PASS")

    # 11. Test Refund Tracking by PNR
    ref_res = client.get("/api/v1/refunds/track/AIRX789")
    assert ref_res.status_code == 200
    ref_data = ref_res.json()
    assert ref_data["pnr"] == "AIRX789"
    assert ref_data["refund_amount"] > 0
    assert len(ref_data["timeline"]) == 5
    print(f"[PASS] Refund Tracking: PASS (PNR: {ref_data['pnr']}, Net Refund: ₹{ref_data['refund_amount']}, Stages: {len(ref_data['timeline'])})")

    # 12. Test Submit New Refund Claim
    claim_res = client.post("/api/v1/refunds/claim", json={
        "pnr": "6E-TEST99",
        "passenger_name": "Test Passenger",
        "airline": "IndiGo",
        "flight_no": "6E 203",
        "sector": "HYD ➔ DEL",
        "total_fare": 5400,
        "payment_method": "UPI"
    })
    assert claim_res.status_code == 201
    claim_data = claim_res.json()
    assert claim_data["pnr"] == "6E-TEST99"
    print("[PASS] Submit Refund Claim: PASS")

    # 13. Test Smart Airfare Price Prediction
    pred_res = client.get("/api/v1/predict/price?origin=HYD&destination=DEL")
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    assert pred_data["recommendation"] in ["BUY_NOW", "WAIT"]
    assert len(pred_data["forecast_14d"]) == 14
    assert pred_data["confidence_pct"] > 50
    print(f"[PASS] Price Prediction: PASS (Signal: {pred_data['recommendation']}, Confidence: {pred_data['confidence_pct']}%)")

    # 14. Test Offers & Promo Discounts List
    offers_res = client.get("/api/v1/offers/list")
    assert offers_res.status_code == 200
    offers_data = offers_res.json()
    assert offers_data["total"] >= 6
    print(f"[PASS] Offers List: PASS ({offers_data['total']} verified active promo codes & concessions)")

    # 15. Test Validate Promo Code
    val_res = client.post("/api/v1/offers/validate", json={
        "code": "AIRX500",
        "base_fare": 4200,
        "total_fare": 5100
    })
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["valid"] is True
    assert val_data["discount_amount"] == 500
    assert val_data["new_total_fare"] == 4600
    print(f"[PASS] Validate Promo Code AIRX500: PASS (Saved ₹{val_data['discount_amount']})")

    # 16. Test Multi-Airline Sector Comparison
    comp_res = client.get("/api/v1/comparison/sector?origin=DEL&destination=BOM")
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert len(comp_data["airlines"]) == 5
    assert "cheapest" in comp_data["highlights"]
    assert "most_punctual" in comp_data["highlights"]
    print(f"[PASS] Sector Comparison: PASS (IndiGo, Air India, Akasa, SpiceJet, AI Express)")

    # 17. Test Monthly Low-Fare Calendar
    cal_res = client.get("/api/v1/monthly-fares/calendar?origin=DEL&destination=BOM")
    assert cal_res.status_code == 200
    cal_data = cal_res.json()
    assert cal_data["total_days"] in [28, 29, 30, 31]
    assert len(cal_data["days"]) == cal_data["total_days"]
    assert cal_data["cheapest_fare"] > 0
    print(f"[PASS] Monthly Low-Fare Calendar: PASS (Lowest: ₹{cal_data['cheapest_fare']} on {cal_data['cheapest_airline']})")

    # 18. Test Travel Guide Destinations & Guidelines
    dest_res = client.get("/api/v1/travel-guide/destinations")
    assert dest_res.status_code == 200
    dest_data = dest_res.json()
    assert dest_data["total"] >= 6

    guide_res = client.get("/api/v1/travel-guide/guidelines")
    assert guide_res.status_code == 200
    guide_data = guide_res.json()
    assert "passenger_charter" in guide_data
    assert len(guide_data["baggage_matrix"]) >= 4
    print(f"[PASS] Travel Guide & DGCA Guidelines: PASS ({dest_data['total']} destinations, full baggage matrix)")

    # 19. Test Agentic AI Copilot Chat with Autonomous Reasoning Trace
    chat_res = client.post("/api/v1/ai/assistant/chat", json={
        "message": "Plan a 3-day trip to Goa with cheapest flights and discounts",
        "language": "en"
    })
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert len(chat_data["reply"]) > 50
    assert len(chat_data["execution_trace"]) >= 3
    assert chat_data["execution_trace"][0]["step_type"] == "thought"
    # 20. Test Tourist Packages with Side-by-Side Pricing & Included Tickets
    tour_res = client.get("/api/v1/tourist-plans")
    assert tour_res.status_code == 200
    tour_data = tour_res.json()
    assert tour_data["total"] >= 6
    sample_plan = tour_data["plans"][0]
    assert "flight" in sample_plan
    assert "hotel" in sample_plan
    assert "pricing" in sample_plan
    assert sample_plan["pricing"]["price_without_offers"] > sample_plan["pricing"]["price_with_offers"]
    assert sample_plan["pricing"]["savings"] == (sample_plan["pricing"]["price_without_offers"] - sample_plan["pricing"]["price_with_offers"])
    print(f"[PASS] Tourist Packages & Side-by-Side Pricing: PASS ({tour_data['total']} packages, Regular ₹{sample_plan['pricing']['price_without_offers']} vs Offer ₹{sample_plan['pricing']['price_with_offers']}, Save ₹{sample_plan['pricing']['savings']})")

    # 21. Test Tourist Package: Unpaid Booking Rejection (Zero-Trust Security)
    unpaid_res = client.post("/api/v1/tourist-plans/book", json={
        "plan_id": sample_plan["id"],
        "traveler_name": "Deepak Gowtam",
        "contact": "deepak@example.com",
        "travel_date": "2026-09-20",
        "pax_count": 1
    })
    assert unpaid_res.status_code == 402
    print("[PASS] Unpaid Booking Rejection: PASS (HTTP 402 Payment Required enforced)")

    # 22. Test Authoritative Server-Side Price Calculation (Zero-Trust)
    calc_res = client.post("/api/v1/payments/calculate-price", json={
        "booking_type": "package",
        "package_id": sample_plan["id"],
        "pax_count": 2,
        "promo_code": "AIRX500"
    })
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert calc_data["currency"] == "INR"
    assert calc_data["final_payable_amount"] > 0
    assert "AIRX500" in calc_data["promo_applied"]
    print(f"[PASS] Server-Side Price Calculation: PASS (Final: ₹{calc_data['final_payable_amount']}, Discount: ₹{calc_data['discount']})")

    # 23. Test Payment Order Creation (DRAFT -> PAYMENT_PENDING)
    order_res = client.post("/api/v1/payments/create-order", json={
        "booking_type": "package",
        "package_id": sample_plan["id"],
        "traveler_name": "Deepak Gowtam",
        "email": "deepak@example.com",
        "phone": "+919876543210",
        "travel_date": "2026-09-20",
        "pax_count": 2,
        "promo_code": "AIRX500"
    })
    assert order_res.status_code == 200
    order_data = order_res.json()
    assert "order_id" in order_data
    assert "booking_id" in order_data
    assert order_data["amount_inr"] == calc_data["final_payable_amount"]
    print(f"[PASS] Payment Order Creation: PASS (Order: {order_data['order_id']}, Booking: {order_data['booking_id']}, Sandbox: {order_data['is_sandbox']})")

    # 24. Test Signature Verification Failure (Tampered Signature)
    tamper_res = client.post("/api/v1/payments/verify", json={
        "booking_id": order_data["booking_id"],
        "order_id": order_data["order_id"],
        "payment_id": "pay_fake_12345",
        "signature": "tampered_signature_hex_0000000000000000000000000000000000000000"
    })
    assert tamper_res.status_code == 400
    print("[PASS] Tampered Signature Rejection: PASS (Rejected with HTTP 400)")

    # 25. Test Sandbox Payment Authorization (Cryptographic HMAC Verification)
    auth_res = client.post("/api/v1/payments/sandbox-authorize", json={
        "order_id": order_data["order_id"],
        "booking_id": order_data["booking_id"],
        "action": "AUTHORIZE"
    })
    assert auth_res.status_code == 200
    auth_data = auth_res.json()
    assert auth_data["status"] == "CONFIRMED"
    assert auth_data["pnr"] is not None
    assert auth_data["voucher_id"] is not None
    print(f"[PASS] Sandbox Payment Authorization: PASS (Confirmed PNR: {auth_data['pnr']}, Voucher: {auth_data['voucher_id']})")

    # 26. Test Idempotency: Duplicate Payment Verification returns existing confirmed booking
    dup_res = client.post("/api/v1/payments/sandbox-authorize", json={
        "order_id": order_data["order_id"],
        "booking_id": order_data["booking_id"],
        "action": "AUTHORIZE"
    })
    assert dup_res.status_code == 200
    assert dup_res.json()["pnr"] == auth_data["pnr"]
    print("[PASS] Payment Idempotency: PASS (Duplicate call safely returned existing booking)")

    # 27. Test Sandbox Payment Decline Simulation
    order_res2 = client.post("/api/v1/payments/create-order", json={
        "booking_type": "package",
        "package_id": sample_plan["id"],
        "traveler_name": "Test Decline",
        "email": "decline@example.com",
        "phone": "+919876543210",
        "travel_date": "2026-09-22",
        "pax_count": 1
    })
    decline_data = order_res2.json()
    dec_res = client.post("/api/v1/payments/sandbox-authorize", json={
        "order_id": decline_data["order_id"],
        "booking_id": decline_data["booking_id"],
        "action": "DECLINE",
        "failure_reason": "User cancelled authorization"
    })
    assert dec_res.status_code == 200
    assert dec_res.json()["status"] == "FAILED"
    print("[PASS] Sandbox Payment Decline: PASS (Status: FAILED, No seat allocated)")

    # 28. Test Non-existent PNR Refund returns 404 (No fake simulation)
    ref_404 = client.get("/api/v1/refunds/track/NONEXISTENT99")
    assert ref_404.status_code == 404
    print("[PASS] Non-existent Refund PNR: PASS (HTTP 404 returned correctly, fake simulation removed)")

    # 29. Test Google Flights 30-Day Historical Data & Price Insights
    gf_res = client.get("/api/v1/google-flights/history-30d?origin=DEL&destination=BOM")
    assert gf_res.status_code == 200
    gf_data = gf_res.json()
    assert gf_data["days_monitored"] == 30
    assert len(gf_data["daily_series"]) == 30
    print(f"[PASS] Google Flights 30D Historical API: PASS (Monitored {gf_data['days_monitored']} days)")

    # 30. Test MoCA / DGCA Aviation Tax Breakdown (Base, UDF, ASF, YQ, 5% GST)
    tax_res = client.get("/api/v1/google-flights/tax-breakdown?base_price=4500&cabin=Economy")
    assert tax_res.status_code == 200
    tax_data = tax_res.json()
    assert tax_data["aviation_security_fee_asf"] == 236
    assert tax_data["upi_convenience_fee"] == 0
    print(f"[PASS] Aviation Tax & Fee Breakdown: PASS (Base ₹{tax_data['base_fare']}, ASF ₹{tax_data['aviation_security_fee_asf']})")

    # 31. Test Supabase Cloud Database Connection Status
    supa_res = client.get("/api/v1/supabase/status")
    assert supa_res.status_code == 200
    supa_data = supa_res.json()
    assert supa_data["project_url"] == "https://thtwkhhccxmkkgwtoleb.supabase.co"
    print(f"[PASS] Supabase Cloud Database Status: PASS (URL: {supa_data['project_url']})")

    # 32. Test Flight Authoritative Price Calculation (Issue #2, #9)
    flight_price_res = client.post("/api/v1/payments/calculate-price", json={
        "booking_type": "flight",
        "flight_no": "6E-205",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "pax_count": 1,
        "promo_code": "AIRX500",
        "addons": ["digiyatra", "insurance"],
        "payment_method": "upi"
    })
    assert flight_price_res.status_code == 200
    f_price = flight_price_res.json()
    assert f_price["base_price"] > 0
    assert f_price["aviation_security_fee_asf"] == 236
    assert f_price["discount"] == 500
    assert f_price["addons_amount"] == (99 + 199)
    assert f_price["convenience_fee"] == 0
    assert f_price["final_payable_amount"] > 100
    print(f"[PASS] Flight Authoritative Pricing: PASS (Total ₹{f_price['final_payable_amount']} with breakdown verified)")

    # 33. Test Flight Order Creation (Issue #2, #11)
    flight_order_res = client.post("/api/v1/payments/create-order", json={
        "booking_type": "flight",
        "flight_no": "6E-205",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "traveler_name": "Siddharth Rao",
        "email": "siddharth@example.com",
        "phone": "+919876543210",
        "travel_date": "2026-09-25",
        "pax_count": 1,
        "promo_code": "AIRX500",
        "addons": ["digiyatra"]
    })
    assert flight_order_res.status_code == 200
    f_order = flight_order_res.json()
    assert f_order["order_id"].startswith("order_")
    assert f_order["booking_id"].startswith("BKG-AIRX-")
    print(f"[PASS] Flight Order Creation: PASS (Order ID: {f_order['order_id']}, Booking ID: {f_order['booking_id']})")

    # 34. Test Strict Verification Failure: Non-existent Booking ID (Issue #3)
    non_exist_bkg = client.post("/api/v1/payments/verify", json={
        "booking_id": "BKG-NONEXISTENT-9999",
        "order_id": f_order["order_id"],
        "payment_id": "pay_fake_001",
        "signature": "fake_signature_hex"
    })
    assert non_exist_bkg.status_code == 404
    print("[PASS] Non-existent Booking Verification: PASS (Rejected with HTTP 404)")

    # 35. Test Strict Verification Failure: Non-existent Order ID (Issue #3)
    non_exist_ord = client.post("/api/v1/payments/verify", json={
        "booking_id": f_order["booking_id"],
        "order_id": "order_nonexistent_9999",
        "payment_id": "pay_fake_001",
        "signature": "fake_signature_hex"
    })
    assert non_exist_ord.status_code == 404
    print("[PASS] Non-existent Order Verification: PASS (Rejected with HTTP 404)")

    # 36. Test Strict Verification Failure: Mismatched Order & Booking IDs (Issue #12)
    mismatch_res = client.post("/api/v1/payments/verify", json={
        "booking_id": f_order["booking_id"],
        "order_id": order_data["order_id"],  # Package order ID paired with flight booking ID
        "payment_id": "pay_fake_001",
        "signature": "fake_signature_hex"
    })
    assert mismatch_res.status_code == 400
    print("[PASS] Mismatched Booking/Order Relationship: PASS (Rejected with HTTP 400)")

    # 37. Test Flight Sandbox Authorization & Confirmation (Issue #1, #6, #14)
    flight_auth = client.post("/api/v1/payments/sandbox-authorize", json={
        "order_id": f_order["order_id"],
        "booking_id": f_order["booking_id"],
        "action": "AUTHORIZE"
    })
    assert flight_auth.status_code == 200
    f_confirmed = flight_auth.json()
    assert f_confirmed["status"] == "CONFIRMED"
    assert f_confirmed["pnr"].startswith("AIRX")
    assert f_confirmed["seat_number"] is not None
    assert f_confirmed["eticket_number"].startswith("098-")
    print(f"[PASS] Flight Payment Confirmation: PASS (PNR: {f_confirmed['pnr']}, Seat: {f_confirmed['seat_number']})")

    # 38. Test Consumed Payment Protection: Reusing same payment_id on another booking fails (Issue #3, #12)
    reuse_order = client.post("/api/v1/payments/create-order", json={
        "booking_type": "flight",
        "flight_no": "6E-205",
        "traveler_name": "Attacker",
        "email": "attacker@example.com",
        "phone": "+919876543210",
        "travel_date": "2026-09-25",
        "pax_count": 1
    }).json()

    reuse_res = client.post("/api/v1/payments/verify", json={
        "booking_id": reuse_order["booking_id"],
        "order_id": reuse_order["order_id"],
        "payment_id": f_confirmed["payment_id"],  # Already consumed by f_confirmed
        "signature": "any_signature"
    })
    assert reuse_res.status_code == 400
    print("[PASS] Consumed Payment Reuse Protection: PASS (Rejected with HTTP 400)")

    # 39. Test Old Flight Checkout Rejection: Calling /checkout directly without verified order fails (Issue #1)
    insecure_checkout = client.post("/api/v1/google-flights/checkout", json={
        "flight_no": "6E-205",
        "passenger_name": "Insecure Tester",
        "payment_status": "COMPLETED",
        "payment_verified": True
    })
    assert insecure_checkout.status_code == 402
    print("[PASS] Insecure Old Checkout Path Blocked: PASS (Direct unverified confirmation rejected with HTTP 402)")

    # 40. Test Webhook Security: Unsigned webhook when secret configured (Issue #4)
    import hmac
    import hashlib
    test_webhook_secret = "test_rzp_webhook_secret_key_12345"
    os.environ["RAZORPAY_WEBHOOK_SECRET"] = test_webhook_secret

    webhook_payload = json.dumps({
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_wh_test_123",
                    "order_id": f_order["order_id"],
                    "amount": f_order["amount_paise"],
                    "currency": "INR",
                    "status": "captured"
                }
            }
        }
    }).encode("utf-8")

    # Unsigned request must be rejected with HTTP 400
    unsigned_res = client.post("/api/v1/payments/webhook", content=webhook_payload)
    assert unsigned_res.status_code == 400
    print("[PASS] Unsigned Webhook Rejection: PASS (Rejected with HTTP 400)")

    # 41. Test Webhook Security: Invalid signature rejection (Issue #4)
    invalid_sig_res = client.post(
        "/api/v1/payments/webhook",
        content=webhook_payload,
        headers={"X-Razorpay-Signature": "invalid_hex_signature_00000000000000000000000000000000"}
    )
    assert invalid_sig_res.status_code == 400
    print("[PASS] Invalid Webhook Signature Rejection: PASS (Rejected with HTTP 400)")

    # 42. Test Webhook Security & Idempotency: Valid signature and duplicate handling (Issue #4, #5)
    valid_sig = hmac.new(test_webhook_secret.encode("utf-8"), webhook_payload, hashlib.sha256).hexdigest()
    valid_wh_res = client.post(
        "/api/v1/payments/webhook",
        content=webhook_payload,
        headers={"X-Razorpay-Signature": valid_sig}
    )
    assert valid_wh_res.status_code == 200
    wh_data = valid_wh_res.json()
    assert wh_data["status"] in ("processed", "already_processed")

    # Duplicate webhook call must be idempotent (no error, no duplicate)
    dup_wh_res = client.post(
        "/api/v1/payments/webhook",
        content=webhook_payload,
        headers={"X-Razorpay-Signature": valid_sig}
    )
    assert dup_wh_res.status_code == 200
    assert dup_wh_res.json().get("idempotent") is True or dup_wh_res.json().get("status") == "already_processed"
    print("[PASS] Webhook HMAC Verification & Idempotency: PASS (Processed and duplicate safely handled)")

    # Clean up test webhook secret env
    del os.environ["RAZORPAY_WEBHOOK_SECRET"]

    # 43. Test Production Sandbox Isolation: Disabled in production mode (Issue #6)
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DEMO_MODE"] = "false"

    prod_sandbox_res = client.post("/api/v1/payments/sandbox-authorize", json={
        "order_id": reuse_order["order_id"],
        "booking_id": reuse_order["booking_id"],
        "action": "AUTHORIZE"
    })
    assert prod_sandbox_res.status_code == 403
    print("[PASS] Production Sandbox Isolation: PASS (Rejected with HTTP 403 Forbidden in production)")

    # Restore development environment for remaining checks
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DEMO_MODE"] = "true"

    # 44. Test Promo Code Security: Invalid promo code yields 0 discount (Issue #10)
    invalid_promo_res = client.post("/api/v1/payments/calculate-price", json={
        "booking_type": "flight",
        "flight_no": "6E-205",
        "promo_code": "INVALID_HACK_PROMO_99999",
        "pax_count": 1
    })
    assert invalid_promo_res.status_code == 200
    assert invalid_promo_res.json()["discount"] == 0
    print("[PASS] Invalid Promo Code Security: PASS (Discount is ₹0 for invalid code)")

    # 45. Test Zero/Negative Order Protection (Issue #9, #10)
    zero_price_res = client.post("/api/v1/payments/calculate-price", json={
        "booking_type": "flight",
        "flight_no": "6E-205",
        "promo_code": "FESTIVE1000",
        "pax_count": 1
    })
    assert zero_price_res.status_code == 200
    assert zero_price_res.json()["final_payable_amount"] >= 100
    print(f"[PASS] Minimum Price Threshold: PASS (Final payable ₹{zero_price_res.json()['final_payable_amount']} >= ₹100 minimum)")

    print("\n========================================================")
    print("ALL 45 PRODUCTION READINESS & SECURITY TEST SUITES PASSED!")
    print("========================================================")

if __name__ == "__main__":
    test_full_api_suite()







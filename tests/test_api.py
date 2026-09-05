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
    assert len(ref_data["timeline"]) == 4
    print(f"[PASS] Refund Tracking: PASS (PNR: {ref_data['pnr']}, Net Refund: ₹{ref_data['refund_amount']})")

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

    # 21. Test Book Tourist Package
    book_res = client.post("/api/v1/tourist-plans/book", json={
        "plan_id": sample_plan["id"],
        "traveler_name": "Deepak Gowtam",
        "contact": "deepak@example.com",
        "travel_date": "2026-09-20",
        "pax_count": 1
    })
    assert book_res.status_code == 200
    book_data = book_res.json()
    assert book_data["status"] == "confirmed"
    assert book_data["booking_reference"].startswith("PKG-")
    assert book_data["amount_paid"] == sample_plan["pricing"]["price_with_offers"]
    # 22. Test Google Flights 30-Day Historical Data & Price Insights
    gf_res = client.get("/api/v1/google-flights/history-30d?origin=DEL&destination=BOM")
    assert gf_res.status_code == 200
    gf_data = gf_res.json()
    assert gf_data["days_monitored"] == 30
    assert len(gf_data["daily_series"]) == 30
    assert "price_insights" in gf_data
    assert gf_data["price_insights"]["level"] in ["low", "typical", "high"]
    print(f"[PASS] Google Flights 30D Historical API: PASS (Monitored {gf_data['days_monitored']} days, 30D lowest ₹{gf_data['lowest_recorded_fare']}, Level: {gf_data['price_insights']['level']})")

    # 23. Test MoCA / DGCA Aviation Tax Breakdown (Base, UDF, ASF, YQ, 5% GST)
    tax_res = client.get("/api/v1/google-flights/tax-breakdown?base_price=4500&cabin=Economy")
    assert tax_res.status_code == 200
    tax_data = tax_res.json()
    assert tax_data["aviation_security_fee_asf"] == 236  # DGCA statutory ₹236
    assert tax_data["central_gst_cgst_2_5_pct"] > 0
    assert tax_data["state_gst_sgst_2_5_pct"] > 0
    assert tax_data["total_gst_5_pct"] == tax_data["central_gst_cgst_2_5_pct"] + tax_data["state_gst_sgst_2_5_pct"]
    assert tax_data["upi_convenience_fee"] == 0
    print(f"[PASS] Aviation Tax & Fee Breakdown: PASS (Base ₹{tax_data['base_fare']}, ASF ₹{tax_data['aviation_security_fee_asf']}, 5% GST ₹{tax_data['total_gst_5_pct']}, UPI Fee ₹{tax_data['upi_convenience_fee']})")

    # 24. Test Flight Checkout with Indian GST & UPI Payment
    checkout_res = client.post("/api/v1/google-flights/checkout", json={
        "flight_no": "6E-205",
        "airline": "IndiGo",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "passenger_name": "Rajesh Sharma",
        "email": "rajesh.sharma@example.com",
        "phone": "9876543210",
        "gender": "Male",
        "age": 29,
        "meal_preference": "Indian Vegetarian Thali",
        "gstin": "36AAACA1234A1Z5",
        "company_name": "Acme Tech Pvt Ltd",
        "base_price": 4200,
        "payment_method": "upi",
        "upi_vpa": "rajesh@okhdfcbank",
        "promo_code": "AIRX500"
    })
    assert checkout_res.status_code == 200
    checkout_data = checkout_res.json()
    assert checkout_data["status"] == "CONFIRMED"
    assert "pnr" in checkout_data and len(checkout_data["pnr"]) >= 5
    assert checkout_data["eticket_number"].startswith("098-")
    assert checkout_data["payment_method"] == "UPI"
    assert checkout_data["utr_reference"].startswith("UPI/")
    assert "tax_invoice" in checkout_data
    assert checkout_data["tax_invoice"]["sac_code"] == "9964"
    assert checkout_data["tax_invoice"]["gst_amount"] > 0
    print(f"[PASS] Flight Checkout & E-Ticket Generator: PASS (PNR: {checkout_data['pnr']}, E-Ticket: {checkout_data['eticket_number']}, Seat: {checkout_data['seat_number']}, UTR: {checkout_data['utr_reference']}, Tax Invoice: {checkout_data['tax_invoice']['invoice_number']})")

    # 25. Test Supabase Cloud Database Connection Status
    supa_res = client.get("/api/v1/supabase/status")
    assert supa_res.status_code == 200
    supa_data = supa_res.json()
    assert supa_data["project_url"] == "https://thtwkhhccxmkkgwtoleb.supabase.co"
    assert supa_data["project_id"] == "thtwkhhccxmkkgwtoleb"
    print(f"[PASS] Supabase Cloud Database Status: PASS (URL: {supa_data['project_url']}, Project: {supa_data['project_id']}, Status: {supa_data['message']})")

    # 26. Test Payment Failure Validation (Seats NOT allocated without completed payment)
    fail_res = client.post("/api/v1/google-flights/checkout", json={
        "flight_no": "6E-205",
        "airline": "IndiGo",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "passenger_name": "Rajesh Sharma",
        "payment_status": "FAILED",
        "payment_verified": False,
        "failure_reason": "NPCI User PIN Timeout"
    })
    assert fail_res.status_code == 200
    fail_data = fail_res.json()
    assert fail_data["status"] == "FAILED"
    assert fail_data["seat_allocated"] is False
    assert fail_data["seat_number"] is None
    assert fail_data["pnr"] is None
    assert "error_code" in fail_data
    print(f"[PASS] Payment Failure Validation: PASS (Status: {fail_data['status']}, Seats Allocated: {fail_data['seat_allocated']}, Error: {fail_data['error_code']})")

    print("\nALL 26 TEST SUITES PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_api_suite()





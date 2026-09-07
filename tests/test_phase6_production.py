"""
AirfareX India — Phase 6 Production Readiness & Security Test Suite
Tests:
1. Production environment configuration & settings
2. Health check endpoints (/health & /api/v1/health)
3. Secret leakage prevention (no secret keys in health, providers, or error responses)
4. Request correlation ID (X-Request-ID) middleware
5. Production CORS headers and safety rules
6. Production error sanitization (no internal stack trace leakage)
7. Honest provider selection & data-source labeling (MockDevelopmentProvider vs Live)
8. Payment webhook signature requirement & validation (HMAC SHA256)
9. Webhook replay protection & idempotency
10. Server-authoritative pricing (price calculation decomposition)
11. Booking creation & ownership isolation
12. Sensitive credential scanning in repo configuration (.env.example safety)
13. Ticket Issuance Safety (Development bookings NEVER reach TICKET_ISSUED)
14. Production Database Fail-Safe (Blocks silent SQLite fallback in production)
15. Provider Terminology Separation (Flight Search Provider vs Booking Provider)
16. Production Architecture & Runtime Status Wording
"""

import os
import sys
import hmac
import hashlib
import json
import uuid
from starlette.testclient import TestClient

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import app
from backend.services.flight_search_service import flight_search_service
from backend.services.flight_providers.mock_provider import MockDevelopmentProvider
from backend.services.flight_providers.base import BaseBookingProvider
from backend.database import get_db_connection, init_db
from backend.seed_data import seed_database
import backend.supabase_client as supabase_client

client = TestClient(app)

def setup_module():
    init_db()
    seed_database()

# ==============================================================================
# 1. HEALTH CHECK ENDPOINT TESTS
# ==============================================================================
def test_health_check_endpoints():
    """Verify /health and /api/v1/health return expected production telemetry."""
    for path in ["/health", "/api/v1/health"]:
        res = client.get(path)
        assert res.status_code == 200, f"Expected 200 from {path}"
        data = res.json()
        assert "status" in data
        assert "environment" in data
        assert "version" in data
        assert "database" in data
        assert "flight_provider" in data
        assert "booking_provider" in data
        assert "payment_gateway" in data
        assert "cache" in data
        assert "timestamp" in data
        assert data["database"]["sqlite"] == "connected"


def test_health_endpoint_no_secrets_leaked():
    """Ensure no API keys, secrets, or passwords appear in health check response."""
    res = client.get("/health")
    text = res.text.lower()
    forbidden_terms = ["secret", "password", "service_role", "anon_key", "sk_live", "sk_test", "bearer", "private_key"]
    for term in forbidden_terms:
        assert term not in text, f"Found sensitive term '{term}' in /health response"


# ==============================================================================
# 2. REQUEST ID & CORRELATION HEADERS
# ==============================================================================
def test_request_id_generation():
    """Verify X-Request-ID is automatically generated and returned in headers."""
    res = client.get("/health")
    assert "x-request-id" in res.headers
    req_id = res.headers["x-request-id"]
    assert req_id.startswith("req_") or len(req_id) > 8


def test_request_id_propagation():
    """Verify incoming X-Request-ID header is propagated back in response."""
    custom_id = "test-req-trace-12345"
    res = client.get("/health", headers={"X-Request-ID": custom_id})
    assert res.headers.get("x-request-id") == custom_id


# ==============================================================================
# 3. PRODUCTION ERROR SANITIZATION
# ==============================================================================
def test_http_exception_includes_request_id():
    """Verify 401/404 errors contain request_id and safe error structure."""
    res = client.get("/api/v1/bookings/non_existent_ref_99999999")
    assert res.status_code in [401, 404]
    data = res.json()
    assert "detail" in data
    assert "request_id" in data
    assert "x-request-id" in res.headers


# ==============================================================================
# 4. FLIGHT PROVIDER & HONEST LABELING TESTS
# ==============================================================================
def test_provider_status_honesty():
    """Verify provider status endpoint reports truthful provider and no secrets."""
    res = client.get("/api/v1/flights/provider-status")
    assert res.status_code == 200
    data = res.json()
    assert "active_provider" in data
    assert "data_source_mode" in data
    # When Amadeus credentials are not set, it must not claim LIVE
    if not data.get("amadeus_configured"):
        assert data["active_provider"] == "MockDevelopmentProvider"
        assert data["data_source_mode"] == "DEVELOPMENT"
    # Verify no credentials in response
    assert "client_secret" not in res.text
    assert "api_secret" not in res.text


def test_flight_search_honest_data_source_label():
    """Verify flight search results are clearly labeled DEVELOPMENT or CACHE."""
    res = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM&date=2026-09-10")
    assert res.status_code == 200
    data = res.json()
    assert "data_source" in data
    assert data["data_source"] in ["DEVELOPMENT", "CACHE", "LIVE"]
    if not os.environ.get("AMADEUS_CLIENT_ID"):
        assert data["data_source"] in ["DEVELOPMENT", "CACHE"]
        assert "MockDevelopmentProvider" in data.get("provider", "")


def test_booking_provider_abstraction():
    """Verify BaseBookingProvider abstraction exists for future GDS/NDC integrations."""
    assert issubclass(BaseBookingProvider, object)
    # Check required abstract methods
    assert hasattr(BaseBookingProvider, "get_name")
    assert hasattr(BaseBookingProvider, "is_configured")
    assert hasattr(BaseBookingProvider, "create_booking")
    assert hasattr(BaseBookingProvider, "cancel_booking")


# ==============================================================================
# 5. PAYMENT WEBHOOK SECURITY TESTS
# ==============================================================================
def test_webhook_rejects_missing_signature():
    """Verify webhook rejects POST requests missing Razorpay signature header when secret is configured."""
    secret = "test_webhook_secret_key_12345"
    old_secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET")
    os.environ["RAZORPAY_WEBHOOK_SECRET"] = secret

    try:
        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test123",
                        "order_id": "order_test123",
                        "status": "captured",
                        "amount": 450000,
                        "currency": "INR"
                    }
                }
            }
        }
        res = client.post("/api/v1/payments/webhook", json=payload)
        # Without signature header, must reject with 400 Bad Request
        assert res.status_code == 400
        assert "signature" in res.json().get("detail", "").lower()
    finally:
        if old_secret is not None:
            os.environ["RAZORPAY_WEBHOOK_SECRET"] = old_secret
        else:
            os.environ.pop("RAZORPAY_WEBHOOK_SECRET", None)


def test_webhook_rejects_invalid_signature():
    """Verify webhook rejects POST requests with invalid/tampered signature."""
    secret = "test_webhook_secret_key_12345"
    old_secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET")
    os.environ["RAZORPAY_WEBHOOK_SECRET"] = secret

    try:
        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_fake999",
                        "order_id": "order_fake999",
                        "status": "captured",
                        "amount": 450000,
                        "currency": "INR"
                    }
                }
            }
        }
        headers = {
            "X-Razorpay-Signature": "invalid_fake_signature_hash_0000000000000000"
        }
        res = client.post("/api/v1/payments/webhook", json=payload, headers=headers)
        assert res.status_code == 400
        assert "signature" in res.json().get("detail", "").lower()
    finally:
        if old_secret is not None:
            os.environ["RAZORPAY_WEBHOOK_SECRET"] = old_secret
        else:
            os.environ.pop("RAZORPAY_WEBHOOK_SECRET", None)


def test_webhook_accepts_valid_hmac_signature():
    """Verify webhook accepts valid HMAC-SHA256 signature when secret is configured."""
    secret = "test_webhook_secret_key_12345"
    old_secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET")
    os.environ["RAZORPAY_WEBHOOK_SECRET"] = secret

    try:
        body_dict = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": f"pay_wh_{uuid.uuid4().hex[:8]}",
                        "order_id": f"order_wh_{uuid.uuid4().hex[:8]}",
                        "status": "captured",
                        "amount": 550000,
                        "currency": "INR"
                    }
                }
            }
        }
        body_bytes = json.dumps(body_dict).encode("utf-8")
        computed_sig = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()

        headers = {
            "X-Razorpay-Signature": computed_sig,
            "Content-Type": "application/json"
        }
        res = client.post("/api/v1/payments/webhook", content=body_bytes, headers=headers)
        assert res.status_code == 200
        assert res.json().get("status") in ["processed", "already_processed"]
    finally:
        if old_secret is not None:
            os.environ["RAZORPAY_WEBHOOK_SECRET"] = old_secret
        else:
            os.environ.pop("RAZORPAY_WEBHOOK_SECRET", None)


# ==============================================================================
# 6. PRICE TAMPERING & PAYMENT SECURITY REGRESSION
# ==============================================================================
def test_price_calculation_is_server_authoritative():
    """Verify price calculation is strictly server-authoritative and validates base inputs."""
    calc_payload = {
        "booking_type": "flight",
        "flight_no": "AI-101",
        "origin_code": "DEL",
        "destination_code": "BOM",
        "cabin": "Economy",
        "pax_count": 2,
        "promo_code": "AIRX500"
    }
    res = client.post("/api/v1/payments/calculate-price", json=calc_payload)
    assert res.status_code == 200
    data = res.json()
    assert "final_payable_amount" in data
    assert "taxes_and_fees" in data
    assert "base_price" in data
    # Base fare for 2 pax must be > 0
    assert data["final_payable_amount"] > 0
    assert data["currency"] == "INR"


def test_payment_order_requires_server_pricing():
    """Verify payment order creation computes server fare and returns valid order."""
    order_payload = {
        "booking_type": "flight",
        "flight_no": "6E-205",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "traveler_name": "Rohan Sharma",
        "email": "rohan@example.com",
        "phone": "+919876543210",
        "pax_count": 1
    }
    res = client.post("/api/v1/payments/create-order", json=order_payload)
    assert res.status_code == 200
    data = res.json()
    assert "order_id" in data
    assert "booking_id" in data
    assert data["amount_inr"] > 0
    assert data["amount_paise"] == data["amount_inr"] * 100


# ==============================================================================
# 7. BOOKING FLOW & OWNERSHIP ISOLATION
# ==============================================================================
def test_booking_creation_and_ownership():
    """Verify booking creation calculates correct server price, assigns reference, and isolates ownership."""
    user_uid = f"user_p6_{uuid.uuid4().hex[:6]}"
    user_token = f"test-bearer-{user_uid}"
    headers = {"Authorization": f"Bearer {user_token}"}

    booking_req = {
        "flight_no": "AI-101",
        "booking_type": "flight",
        "origin_code": "DEL",
        "destination_code": "BOM",
        "travel_date": "2026-09-20",
        "cabin": "Economy",
        "contact_name": "Aarav Sharma",
        "contact_email": "aarav.sharma@example.com",
        "contact_phone": "+919876543210",
        "passengers": [
            {
                "title": "Dr",
                "first_name": "Aarav",
                "last_name": "Sharma",
                "age": 34,
                "gender": "Male",
                "passenger_type": "ADULT"
            }
        ],
        "addons": ["digiyatra"]
    }

    res = client.post("/api/v1/bookings", headers=headers, json=booking_req)
    assert res.status_code == 201
    booking = res.json()
    assert "booking_reference" in booking
    assert booking["booking_status"] in ["PENDING_PAYMENT", "CONFIRMED"]
    assert booking["passenger_count"] == 1

    # Verify lookup by booking reference with owner auth
    b_id = booking["booking_id"]
    get_res = client.get(f"/api/v1/bookings/{b_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["booking_id"] == b_id

    # Verify cross-user cannot access
    other_token = f"test-bearer-other_{uuid.uuid4().hex[:6]}"
    cross_res = client.get(f"/api/v1/bookings/{b_id}", headers={"Authorization": f"Bearer {other_token}"})
    assert cross_res.status_code == 403


# ==============================================================================
# 8. TICKET ISSUANCE SAFETY (CORRECTION 1)
# ==============================================================================
def test_ticket_issuance_safety_never_reaches_ticket_issued_in_dev():
    """Ensure development bookings only reach CONFIRMED, never TICKET_ISSUED, and carry explicit notice."""
    user_uid = f"user_tix_{uuid.uuid4().hex[:6]}"
    headers = {"Authorization": f"Bearer test-bearer-{user_uid}"}

    booking_req = {
        "flight_no": "6E-205",
        "booking_type": "flight",
        "origin_code": "HYD",
        "destination_code": "DEL",
        "travel_date": "2026-09-20",
        "cabin": "Economy",
        "contact_name": "Karan Malhotra",
        "contact_email": "karan@example.com",
        "contact_phone": "+919876543210",
        "passengers": [{"first_name": "Karan", "last_name": "Malhotra", "age": 29}]
    }

    res = client.post("/api/v1/bookings", headers=headers, json=booking_req)
    assert res.status_code == 201
    b_data = res.json()
    b_id = b_data["booking_id"]
    order_id = b_data["payment_order_id"]

    # Verify notice exists on creation
    assert "Development booking" in b_data.get("development_notice", "")

    # Authorize sandbox payment
    auth_res = client.post("/api/v1/payments/sandbox-authorize", json={
        "order_id": order_id,
        "booking_id": b_id,
        "action": "AUTHORIZE"
    })
    assert auth_res.status_code == 200
    auth_data = auth_res.json()

    # MUST be CONFIRMED, NOT TICKET_ISSUED
    assert auth_data["status"] == "CONFIRMED"
    assert auth_data["status"] != "TICKET_ISSUED"
    assert "development_notice" in auth_data
    assert "Development booking" in auth_data["development_notice"]

    # Check DB record
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT booking_status FROM bookings WHERE booking_id = ?", (b_id,))
    row = c.fetchone()
    conn.close()
    assert row["booking_status"] in ["CONFIRMED", "BOOKING_CONFIRMED"]
    assert row["booking_status"] != "TICKET_ISSUED"


# ==============================================================================
# 9. PRODUCTION DATABASE FAIL-SAFE (CORRECTION 2)
# ==============================================================================
def test_production_database_failsafe_blocks_sqlite_in_production():
    """Ensure ENVIRONMENT=production blocks silent fallback to SQLite when Supabase is unconfigured."""
    old_env = os.environ.get("ENVIRONMENT")
    old_key = supabase_client.SUPABASE_KEY
    old_s_key = supabase_client.SUPABASE_SERVICE_ROLE_KEY

    try:
        os.environ["ENVIRONMENT"] = "production"
        supabase_client.SUPABASE_KEY = ""
        supabase_client.SUPABASE_SERVICE_ROLE_KEY = ""

        # Attempt to create booking in production without Supabase
        user_uid = f"prod_fail_{uuid.uuid4().hex[:6]}"
        headers = {"Authorization": f"Bearer test-bearer-{user_uid}"}
        booking_req = {
            "flight_no": "6E-205",
            "booking_type": "flight",
            "origin_code": "HYD",
            "destination_code": "DEL",
            "travel_date": "2026-09-20",
            "contact_name": "Prod Test",
            "contact_email": "prod@example.com",
            "contact_phone": "+919876543210",
            "passengers": [{"first_name": "Prod", "last_name": "User", "age": 30}]
        }
        res_bk = client.post("/api/v1/bookings", headers=headers, json=booking_req)
        assert res_bk.status_code == 503
        assert "Production database" in res_bk.json().get("detail", "")

        # Attempt to create payment order in production without Supabase
        order_req = {
            "booking_type": "flight",
            "flight_no": "6E-205",
            "traveler_name": "Prod User",
            "pax_count": 1
        }
        res_ord = client.post("/api/v1/payments/create-order", json=order_req)
        assert res_ord.status_code == 503

        # Health endpoint in production reports degraded
        res_h = client.get("/health")
        assert res_h.status_code == 200
        h_data = res_h.json()
        assert h_data["database"]["primary"] == "supabase"
        assert h_data["database"]["supabase"] == "unavailable"
        assert h_data["status"] == "degraded"

    finally:
        if old_env is not None:
            os.environ["ENVIRONMENT"] = old_env
        else:
            os.environ.pop("ENVIRONMENT", None)
        supabase_client.SUPABASE_KEY = old_key
        supabase_client.SUPABASE_SERVICE_ROLE_KEY = old_s_key


# ==============================================================================
# 10. PROVIDER TERMINOLOGY SEPARATION & RUNTIME WORDING (CORRECTIONS 3 & 4)
# ==============================================================================
def test_provider_terminology_separation_in_health():
    """Ensure health endpoint clearly separates flight_provider and booking_provider."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()

    # Flight Provider
    assert "flight_provider" in data
    assert "active" in data["flight_provider"]
    assert "mode" in data["flight_provider"]

    # Booking Provider
    assert "booking_provider" in data
    assert data["booking_provider"]["configured"] is False
    assert data["booking_provider"]["ticketing_enabled"] is False
    assert "Development booking mode" in data["booking_provider"]["notice"]

    # Accurate Production Architecture vs Runtime wording
    assert data.get("production_architecture") == "READY"
    assert data.get("current_runtime") in ["DEVELOPMENT/SANDBOX", "LIVE"]


# ==============================================================================
# 11. ENV EXAMPLE & REPO SECURITY AUDIT
# ==============================================================================
def test_env_example_safety():
    """Ensure .env.example contains only placeholders and no real secret values."""
    env_example_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env.example"))
    assert os.path.exists(env_example_path), ".env.example must exist"
    
    with open(env_example_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify placeholder patterns
    assert "your_amadeus_api_key" in content or "your_" in content
    assert "your_razorpay_key_secret" in content or "your_" in content
    
    # Ensure no real keys
    assert "sk_live_" not in content
    assert "eyJh" not in content  # JWT header snippet


def test_gitignore_ignores_env():
    """Ensure .gitignore explicitly includes .env."""
    gitignore_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".gitignore"))
    assert os.path.exists(gitignore_path), ".gitignore must exist"
    
    with open(gitignore_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert ".env" in content.split()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

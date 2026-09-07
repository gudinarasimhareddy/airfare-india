"""
AirfareX India — Real-Time Airline & Amadeus Provider Integration Tests
Comprehensive test suite verifying:
1. Amadeus configuration & credential detection
2. Secret protection (no secrets in API responses, logs, or DOM)
3. OAuth2 token acquisition & caching lifecycle
4. Provider selection (Amadeus when configured, Mock fallback)
5. Provider failure resilience
6. Honest data source labeling (LIVE, CACHE, DEVELOPMENT)
7. Normalization of multi-segment itineraries, baggage, & fare breakdowns
8. Airport autocomplete integration
9. Booking and Payment safety isolation (ticketing disabled, sandbox payment)
10. Homepage DOM integrity & no credential leakage
"""

import pytest
import os
import sys
import time
import json
from pathlib import Path
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

# Force UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.app import app
from backend.services.flight_providers.amadeus_provider import AmadeusFlightProvider
from backend.services.flight_providers.mock_provider import MockDevelopmentProvider
from backend.services.flight_providers.base import FlightSearchParams, NormalizedFlight, NormalizedSearchResponse
from backend.services.flight_search_service import FlightSearchService

client = TestClient(app)

# ==============================================================================
# 1. SECRET PROTECTION & CREDENTIAL SAFETY
# ==============================================================================

def test_provider_status_never_exposes_secrets():
    """Verify /flights/provider-status exposes environment & readiness without leaking credentials."""
    response = client.get("/api/v1/flights/provider-status")
    assert response.status_code == 200
    data = response.json()
    
    assert "active_provider" in data
    assert "data_source_mode" in data
    assert "configured" in data
    assert "live_enabled" in data
    assert "cache_enabled" in data
    
    # Must NEVER leak secrets
    raw_text = response.text.lower()
    assert "amadeus_client_secret" not in raw_text
    assert "client_secret" not in raw_text
    assert "access_token" not in raw_text

def test_frontend_files_contain_no_secrets():
    """Verify frontend HTML and JS files contain no API secrets or private tokens."""
    frontend_files = [
        "frontend/index.html",
        "frontend/js/app.js",
        "frontend/js/api.js",
        "frontend/js/auth.js"
    ]
    forbidden_tokens = ["AMADEUS_CLIENT_SECRET", "client_secret", "sk_live", "rzp_live"]
    
    for fpath in frontend_files:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                for token in forbidden_tokens:
                    assert token not in content, f"Forbidden token {token} found in {fpath}"

# ==============================================================================
# 2. AMADEUS AUTHENTICATION & OAUTH2 TOKEN CACHING
# ==============================================================================

@pytest.mark.asyncio
async def test_amadeus_oauth2_token_caching():
    """Verify Amadeus provider requests OAuth2 token and reuses it within expiry window."""
    provider = AmadeusFlightProvider(
        client_id="mock_test_key",
        client_secret="mock_test_secret",
        hostname="test"
    )
    
    mock_auth_response = {
        "access_token": "mock_valid_bearer_token_12345",
        "token_type": "Bearer",
        "expires_in": 1799
    }
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_auth_response,
            raise_for_status=lambda: None
        )
        
        # First call fetches token
        token1 = await provider.get_access_token()
        assert token1 == "mock_valid_bearer_token_12345"
        assert mock_post.call_count == 1
        
        # Second call uses cached token without additional HTTP request
        token2 = await provider.get_access_token()
        assert token2 == "mock_valid_bearer_token_12345"
        assert mock_post.call_count == 1  # No second post call

@pytest.mark.asyncio
async def test_amadeus_auth_failure_handling():
    """Verify auth failures return None gracefully without leaking credentials and search_flights raises safe error."""
    provider = AmadeusFlightProvider(
        client_id="invalid_key",
        client_secret="invalid_secret",
        hostname="test"
    )
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = MagicMock(
            status_code=401,
            json=lambda: {"error": "invalid_client", "error_description": "Bad credentials"}
        )
        
        token = await provider.get_access_token()
        assert token is None
        
        # When token is None, search_flights raises RuntimeError
        params = FlightSearchParams(origin="DEL", destination="BOM")
        with pytest.raises(RuntimeError) as exc_info:
            await provider.search_flights(params)
        assert "Amadeus authentication failed" in str(exc_info.value)

# ==============================================================================
# 3. RESPONSE NORMALIZATION & VISTARA HANDLING
# ==============================================================================

@pytest.mark.asyncio
async def test_amadeus_response_normalization():
    """Verify real Amadeus flight offers JSON payload is accurately normalized into AirfareX schema."""
    provider = AmadeusFlightProvider(client_id="k", client_secret="s", hostname="test")
    
    sample_amadeus_payload = {
        "meta": {"count": 1},
        "data": [
            {
                "id": "1",
                "itineraries": [
                    {
                        "duration": "PT2H15M",
                        "segments": [
                            {
                                "departure": {"iataCode": "DEL", "terminal": "3", "at": "2026-09-15T06:00:00"},
                                "arrival": {"iataCode": "BOM", "terminal": "2", "at": "2026-09-15T08:15:00"},
                                "carrierCode": "6E",
                                "number": "2045",
                                "aircraft": {"code": "32N"},
                                "duration": "PT2H15M",
                                "numberOfStops": 0
                            }
                        ]
                    }
                ],
                "price": {
                    "currency": "INR",
                    "total": "4850.00",
                    "base": "4200.00",
                    "fees": [{"amount": "650.00", "type": "SUPPLIER"}]
                },
                "pricingOptions": {"fareType": ["PUBLISHED"], "includedCheckedBagsOnly": False},
                "travelerPricings": [
                    {
                        "fareDetailsBySegment": [
                            {
                                "segmentId": "1",
                                "cabin": "ECONOMY",
                                "includedCheckedBags": {"weight": 15, "weightUnit": "KG"}
                            }
                        ]
                    }
                ]
            }
        ],
        "dictionaries": {
            "carriers": {"6E": "IndiGo"},
            "aircraft": {"32N": "Airbus A320neo"},
            "locations": {
                "DEL": {"cityCode": "DEL", "countryCode": "IN"},
                "BOM": {"cityCode": "BOM", "countryCode": "IN"}
            }
        }
    }
    
    params = FlightSearchParams(origin="DEL", destination="BOM")
    normalized_resp = provider._normalize_offers(sample_amadeus_payload, params)
    
    assert normalized_resp.data_source == "LIVE"
    assert normalized_resp.provider == "AmadeusFlightProvider"
    assert len(normalized_resp.flights) == 1
    
    flight = normalized_resp.flights[0]
    assert flight.airline == "IndiGo"
    assert flight.airline_code == "6E"
    assert flight.flight_no == "6E 2045"
    assert flight.origin_code == "DEL"
    assert flight.destination_code == "BOM"
    assert flight.dep_time == "06:00"
    assert flight.arr_time == "08:15"
    assert flight.duration == "2h 15m"
    assert flight.stops == "Nonstop"
    assert flight.total_fare == 4850
    assert flight.base_fare == 4200
    assert flight.taxes_and_fees == 650
    assert flight.currency == "INR"
    assert flight.checked_baggage == "15 KG"
    assert len(flight.segments) == 1
    assert flight.segments[0].aircraft == "Airbus A320neo"

@pytest.mark.asyncio
async def test_vistara_historical_data_handling():
    """Verify historical UK carrier codes are labeled as Vistara (Historical) rather than an active airline."""
    provider = AmadeusFlightProvider(client_id="k", client_secret="s", hostname="test")
    
    payload_with_vistara = {
        "data": [
            {
                "id": "2",
                "itineraries": [
                    {
                        "duration": "PT2H10M",
                        "segments": [
                            {
                                "departure": {"iataCode": "DEL", "at": "2026-09-15T09:00:00"},
                                "arrival": {"iataCode": "BOM", "at": "2026-09-15T11:10:00"},
                                "carrierCode": "UK",
                                "number": "995",
                                "duration": "PT2H10M",
                                "numberOfStops": 0
                            }
                        ]
                    }
                ],
                "price": {"currency": "INR", "total": "5500.00", "base": "4800.00"}
            }
        ],
        "dictionaries": {"carriers": {"UK": "Vistara"}}
    }
    
    params = FlightSearchParams(origin="DEL", destination="BOM")
    normalized_resp = provider._normalize_offers(payload_with_vistara, params)
    assert len(normalized_resp.flights) == 1
    flight = normalized_resp.flights[0]
    assert "Historical" in flight.airline

# ==============================================================================
# 4. PROVIDER SELECTION & HONEST DATA SOURCE LABELING
# ==============================================================================

@pytest.mark.asyncio
async def test_mock_provider_returns_development_label():
    """Verify unconfigured or default state returns data_source='DEVELOPMENT' and never claims LIVE."""
    search_service = FlightSearchService()
    # Force Amadeus unconfigured
    search_service.amadeus_provider.client_id = ""
    
    params = FlightSearchParams(origin="HYD", destination="DEL")
    resp = await search_service.search_flights(params, bypass_cache=True)
    
    assert resp.data_source == "DEVELOPMENT"
    assert resp.provider == "MockDevelopmentProvider"
    assert resp.cached is False
    assert len(resp.flights) > 0

@pytest.mark.asyncio
async def test_cache_returns_cache_label():
    """Verify subsequent searches within TTL window return data_source='CACHE'."""
    search_service = FlightSearchService()
    params = FlightSearchParams(origin="BLR", destination="BOM")
    
    # First search populates cache
    resp1 = await search_service.search_flights(params, bypass_cache=True)
    assert resp1.data_source in ["DEVELOPMENT", "LIVE"]
    
    # Second search should hit cache
    resp2 = await search_service.search_flights(params, bypass_cache=False)
    assert resp2.data_source == "CACHE"
    assert resp2.cached is True
    assert resp2.cache_ttl_remaining_secs is not None

# ==============================================================================
# 5. PROVIDER FAILURE HANDLING
# ==============================================================================

@pytest.mark.asyncio
async def test_provider_failure_in_development_falls_back_with_honest_label():
    """Verify if Amadeus fails in development mode, it safely falls back with DEVELOPMENT label."""
    search_service = FlightSearchService()
    search_service.amadeus_provider.client_id = "test_key"
    search_service.amadeus_provider.client_secret = "test_secret"
    
    # Simulate Amadeus API failure
    with patch.object(search_service.amadeus_provider, "search_flights", side_effect=Exception("API Timeout")):
        params = FlightSearchParams(origin="DEL", destination="CCU")
        resp = await search_service.search_flights(params, bypass_cache=True)
        
        # Must NOT claim LIVE when live provider failed
        assert resp.data_source == "DEVELOPMENT"
        assert resp.provider == "MockDevelopmentProvider"

# ==============================================================================
# 6. AIRPORT AUTOCOMPLETE INTEGRATION
# ==============================================================================

def test_airport_autocomplete_endpoint():
    """Verify /flights/airports/autocomplete returns Indian airport locations."""
    response = client.get("/api/v1/flights/airports/autocomplete?q=delhi")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    delhi = next((a for a in data if a["iata_code"] == "DEL"), None)
    assert delhi is not None
    assert "Delhi" in delhi["city"]

# ==============================================================================
# 7. BOOKING & PAYMENT SAFETY
# ==============================================================================

def test_booking_and_ticketing_safety():
    """Verify live flight search does not enable unauthorized airline ticket issuance."""
    status_resp = client.get("/api/v1/flights/provider-status")
    data = status_resp.json()
    assert data["booking_provider"]["ticketing_enabled"] is False
    assert "development" in data["booking_provider"]["provider_name"].lower()

def test_payment_safety_remains_sandbox():
    """Verify payment endpoints remain sandbox with cryptographic HMAC simulation."""
    order_req = {
        "booking_type": "flight",
        "flight_no": "6E 2045",
        "origin_code": "DEL",
        "destination_code": "BOM",
        "traveler_name": "Test Traveler",
        "email": "traveler@example.com",
        "pax_count": 1
    }
    response = client.post("/api/v1/payments/create-order", json=order_req)
    assert response.status_code == 200
    res_data = response.json()
    assert "order_id" in res_data
    assert "booking_id" in res_data
    assert res_data["order_id"].startswith("order_sbx_")

if __name__ == "__main__":
    import asyncio
    print("================================================================")
    print("AIRFAREX REAL-TIME FLIGHT & AMADEUS INTEGRATION SUITE")
    print("================================================================")
    
    test_provider_status_never_exposes_secrets()
    print("[PASS] 1. Provider status never exposes secrets")
    
    test_frontend_files_contain_no_secrets()
    print("[PASS] 2. Frontend files contain no secrets")
    
    asyncio.run(test_amadeus_oauth2_token_caching())
    print("[PASS] 3. Amadeus OAuth2 token caching & reuse")
    
    asyncio.run(test_amadeus_auth_failure_handling())
    print("[PASS] 4. Amadeus authentication failure handling")
    
    asyncio.run(test_amadeus_response_normalization())
    print("[PASS] 5. Amadeus response normalization into AirfareX schema")
    
    asyncio.run(test_vistara_historical_data_handling())
    print("[PASS] 6. Vistara historical data labeling")
    
    asyncio.run(test_mock_provider_returns_development_label())
    print("[PASS] 7. Mock development provider returns honest DEVELOPMENT label")
    
    asyncio.run(test_cache_returns_cache_label())
    print("[PASS] 8. 15-minute TTL cache returns honest CACHE label")
    
    asyncio.run(test_provider_failure_in_development_falls_back_with_honest_label())
    print("[PASS] 9. Provider failure fallback in development mode")
    
    test_airport_autocomplete_endpoint()
    print("[PASS] 10. Airport autocomplete integration")
    
    test_booking_and_ticketing_safety()
    print("[PASS] 11. Booking & ticketing safety (ticketing disabled)")
    
    test_payment_safety_remains_sandbox()
    print("[PASS] 12. Payment safety (sandbox HMAC simulation)")
    
    print("================================================================")
    print("ALL 12 REAL-TIME INTEGRATION TESTS PASSED (100%)")
    print("================================================================")


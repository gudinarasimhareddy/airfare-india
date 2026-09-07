import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Read .env file manually if present
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

DEFAULT_SUPABASE_URL = "https://thtwkhhccxmkkgwtoleb.supabase.co"
SUPABASE_URL = os.environ.get("SUPABASE_URL", DEFAULT_SUPABASE_URL).rstrip("/")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
# Backward compatibility alias
SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY or os.environ.get("SUPABASE_KEY", "").strip()

PROJECT_ID = "thtwkhhccxmkkgwtoleb"

router = APIRouter(prefix="/supabase", tags=["Supabase Cloud Database"])

def is_configured() -> bool:
    """Returns True if a valid Supabase key is configured."""
    return bool(SUPABASE_KEY and len(SUPABASE_KEY) > 10)

def get_headers(prefer: str = "return=representation") -> Dict[str, str]:
    """Generates server-side authenticated PostgREST headers."""
    active_key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY or SUPABASE_ANON_KEY
    return {
        "apikey": active_key,
        "Authorization": f"Bearer {active_key}",
        "Content-Type": "application/json",
        "Prefer": prefer
    }

# =========================================================
# HEALTH CHECK & CONNECTION TELEMETRY
# =========================================================

async def check_supabase_health() -> Dict[str, Any]:
    """
    Tests live connectivity to Supabase project https://thtwkhhccxmkkgwtoleb.supabase.co
    """
    configured = is_configured()
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            headers = get_headers() if configured else {"User-Agent": "AirfareX-India"}
            res = await client.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
            
            if res.status_code == 200:
                return {
                    "project_url": SUPABASE_URL,
                    "project_id": PROJECT_ID,
                    "configured": True,
                    "connected": True,
                    "status_code": res.status_code,
                    "message": f"Connected successfully to Supabase ({PROJECT_ID})! Database is active and authenticated."
                }
            elif res.status_code == 401:
                return {
                    "project_url": SUPABASE_URL,
                    "project_id": PROJECT_ID,
                    "configured": configured,
                    "connected": False,
                    "status_code": res.status_code,
                    "message": "Supabase endpoint is online and reachable, but requires an API Key (SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY)."
                }
            else:
                return {
                    "project_url": SUPABASE_URL,
                    "project_id": PROJECT_ID,
                    "configured": configured,
                    "connected": False,
                    "status_code": res.status_code,
                    "message": f"Supabase responded with HTTP {res.status_code}"
                }
    except Exception as e:
        return {
            "project_url": SUPABASE_URL,
            "project_id": PROJECT_ID,
            "configured": configured,
            "connected": False,
            "error": str(e),
            "message": f"Network error connecting to {SUPABASE_URL}: {e}"
        }

# =========================================================
# MASTER CATALOG ACCESS
# =========================================================

async def get_airports_from_supabase() -> Optional[List[Dict[str, Any]]]:
    """Fetches master airport catalog from Supabase."""
    if not is_configured():
        return None
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(f"{SUPABASE_URL}/rest/v1/airports?select=*&order=iata_code.asc", headers=get_headers())
            if res.status_code == 200:
                return res.json()
    except Exception as e:
        print(f"[Supabase] get_airports error: {e}")
    return None

async def get_airlines_from_supabase() -> Optional[List[Dict[str, Any]]]:
    """Fetches master airline catalog from Supabase."""
    if not is_configured():
        return None
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(f"{SUPABASE_URL}/rest/v1/airlines?select=*&order=name.asc", headers=get_headers())
            if res.status_code == 200:
                return res.json()
    except Exception as e:
        print(f"[Supabase] get_airlines error: {e}")
    return None

async def search_flights_from_supabase(origin_code: str, destination_code: str) -> Optional[List[Dict[str, Any]]]:
    """Queries flight schedules and fares from Supabase flights & flight_prices."""
    if not is_configured():
        return None
    try:
        query_url = (
            f"{SUPABASE_URL}/rest/v1/flights"
            f"?origin_code=eq.{origin_code.upper()}&destination_code=eq.{destination_code.upper()}"
            f"&select=*,flight_prices(*)"
        )
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(query_url, headers=get_headers())
            if res.status_code == 200:
                flights = res.json()
                return flights if flights else None
    except Exception as e:
        print(f"[Supabase] search_flights error: {e}")
    return None

# =========================================================
# BOOKING & PASSENGER DATA
# =========================================================

async def save_booking_to_supabase(booking: Dict[str, Any]) -> bool:
    """Mirrors confirmed booking and passenger records to Supabase."""
    if not is_configured():
        return False

    try:
        payload = {
            "booking_id": booking.get("booking_id") or booking.get("pnr"),
            "pnr": booking.get("pnr"),
            "eticket_number": booking.get("eticket_number"),
            "voucher_id": booking.get("voucher_id"),
            "airline": booking.get("airline"),
            "flight_no": booking.get("flight_no"),
            "sector": f"{booking.get('origin_code', 'HYD')} ➔ {booking.get('destination_code', 'DEL')}",
            "travel_date": booking.get("travel_date") or "2026-09-15",
            "traveler_name": booking.get("passenger_name") or booking.get("traveler_name", "Guest"),
            "email": booking.get("email", "guest@example.com"),
            "phone": booking.get("phone", "+919876543210"),
            "seat_number": booking.get("seat_number", "14B"),
            "gate": booking.get("gate", "G1"),
            "terminal": booking.get("terminal", "T2"),
            "base_fare": booking.get("base_fare", 4000),
            "total_amount": booking.get("total_fare") or booking.get("total_amount", 5000),
            "currency": booking.get("currency", "INR"),
            "booking_status": "CONFIRMED",
            "payment_status": "PAID",
            "payment_method": booking.get("payment_method", "UPI"),
            "utr_reference": booking.get("transaction_utr"),
            "gstin": booking.get("gstin"),
            "company_name": booking.get("company_name"),
            "invoice_number": booking.get("invoice_number")
        }

        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/bookings",
                headers=get_headers(),
                json=payload
            )
            return res.status_code in [200, 201]
    except Exception as err:
        print(f"[Supabase] Error writing booking: {err}")
        return False

async def get_booking_from_supabase(pnr_or_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a booking record from Supabase by PNR or booking_id."""
    if not is_configured():
        return None
    try:
        clean_id = pnr_or_id.strip().upper()
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/bookings?or=(pnr.eq.{clean_id},booking_id.eq.{clean_id})&select=*",
                headers=get_headers()
            )
            if res.status_code == 200:
                rows = res.json()
                if rows:
                    return rows[0]
    except Exception as e:
        print(f"[Supabase] get_booking error: {e}")
    return None

# =========================================================
# PAYMENT LEDGER INTEGRATION
# =========================================================

async def save_payment_to_supabase(payment: Dict[str, Any]) -> bool:
    """Records payment intent or transaction into Supabase payments table."""
    if not is_configured():
        return False

    try:
        payload = {
            "order_id": payment.get("order_id"),
            "booking_id": payment.get("booking_id"),
            "payment_id": payment.get("payment_id"),
            "provider": payment.get("provider", "razorpay"),
            "amount": payment.get("amount", 0),
            "currency": payment.get("currency", "INR"),
            "status": payment.get("status", "CREATED"),
            "method": payment.get("method"),
            "signature": payment.get("signature"),
            "error_code": payment.get("error_code"),
            "error_description": payment.get("error_description"),
            "idempotency_key": payment.get("idempotency_key")
        }

        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/payments",
                headers=get_headers(),
                json=payload
            )
            return res.status_code in [200, 201]
    except Exception as err:
        print(f"[Supabase] Error writing payment: {err}")
        return False

# =========================================================
# REFUND TRACKING INTEGRATION
# =========================================================

async def get_refund_from_supabase(pnr: str) -> Optional[Dict[str, Any]]:
    """Retrieves refund claim from Supabase refunds table."""
    if not is_configured():
        return None
    try:
        clean_pnr = pnr.strip().upper()
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/refunds?pnr=eq.{clean_pnr}&select=*",
                headers=get_headers()
            )
            if res.status_code == 200:
                rows = res.json()
                if rows:
                    return rows[0]
    except Exception as e:
        print(f"[Supabase] get_refund error: {e}")
    return None

async def save_refund_to_supabase(claim: Dict[str, Any]) -> bool:
    """Inserts a new refund claim into Supabase."""
    if not is_configured():
        return False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/refunds",
                headers=get_headers(),
                json=claim
            )
            return res.status_code in [200, 201]
    except Exception as err:
        print(f"[Supabase] Error saving refund: {err}")
        return False

# =========================================================
# SAVED FLIGHTS & PRICE ALERTS
# =========================================================

async def get_alerts_from_supabase() -> Optional[List[Dict[str, Any]]]:
    """Retrieves active price alerts from Supabase."""
    if not is_configured():
        return None
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(
                f"{SUPABASE_URL}/rest/v1/price_alerts?is_active=eq.true&order=created_at.desc",
                headers=get_headers()
            )
            if res.status_code == 200:
                return res.json()
    except Exception as e:
        print(f"[Supabase] get_alerts error: {e}")
    return None

async def save_alert_to_supabase(alert_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Creates a new price alert in Supabase."""
    if not is_configured():
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/price_alerts",
                headers=get_headers(),
                json=alert_data
            )
            if res.status_code in [200, 201]:
                data = res.json()
                return data[0] if isinstance(data, list) and data else alert_data
    except Exception as e:
        print(f"[Supabase] save_alert error: {e}")
    return None

# =========================================================
# FASTAPI SUPABASE MANAGEMENT ENDPOINTS
# =========================================================

@router.get("/status")
async def get_supabase_status():
    """Returns live connection health status for https://thtwkhhccxmkkgwtoleb.supabase.co"""
    health = await check_supabase_health()
    return health

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
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

PROJECT_ID = "thtwkhhccxmkkgwtoleb"

router = APIRouter(prefix="/supabase", tags=["Supabase Cloud Database"])

def is_configured() -> bool:
    return bool(SUPABASE_KEY and len(SUPABASE_KEY) > 10)

def get_headers() -> Dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

async def check_supabase_health() -> Dict[str, Any]:
    """
    Tests live connectivity to Supabase project https://thtwkhhccxmkkgwtoleb.supabase.co
    """
    configured = is_configured()
    
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            # Check basic reachability of PostgREST
            headers = get_headers() if configured else {"User-Agent": "AirfareX-India"}
            res = await client.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
            
            # PostgREST returns 200 with schema OpenAPI spec when valid key is provided, or 401 if missing key
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
                    "message": "Supabase endpoint is online and reachable, but requires an API Key (anon key or service_role key) for authentication."
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

async def save_booking_to_supabase(booking: Dict[str, Any]) -> bool:
    """Mirrors confirmed booking to Supabase public.bookings table"""
    if not is_configured():
        return False

    try:
        payload = {
            "pnr": booking.get("pnr"),
            "eticket_number": booking.get("eticket_number"),
            "airline": booking.get("airline"),
            "flight_no": booking.get("flight_no"),
            "origin_code": booking.get("origin_code"),
            "destination_code": booking.get("destination_code"),
            "travel_date": booking.get("travel_date"),
            "passenger_name": booking.get("passenger_name"),
            "email": booking.get("email"),
            "phone": booking.get("phone"),
            "seat_number": booking.get("seat_number"),
            "gate": booking.get("gate"),
            "terminal": booking.get("terminal"),
            "base_fare": booking.get("tax_invoice", {}).get("base_fare", 4000),
            "total_fare": booking.get("tax_invoice", {}).get("total_amount", 5000),
            "payment_method": booking.get("payment_method", "UPI"),
            "utr_reference": booking.get("transaction_utr"),
            "gstin": booking.get("gstin"),
            "company_name": booking.get("company_name"),
            "invoice_number": booking.get("tax_invoice", {}).get("invoice_number"),
            "gst_amount": booking.get("tax_invoice", {}).get("gst_amount", 0),
            "status": "CONFIRMED"
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

# =========================================================
# FASTAPI SUPABASE MANAGEMENT ENDPOINTS
# =========================================================

@router.get("/status")
async def get_supabase_status():
    """Returns live connection health status for https://thtwkhhccxmkkgwtoleb.supabase.co"""
    health = await check_supabase_health()
    return health

class ConfigUpdateRequest(BaseModel):
    supabase_key: str
    supabase_url: Optional[str] = None

@router.post("/config")
def update_supabase_config(req: ConfigUpdateRequest):
    """Sets or updates the Supabase API Key live and persists it to .env"""
    global SUPABASE_KEY, SUPABASE_URL
    
    key = req.supabase_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="Supabase API key cannot be empty")

    SUPABASE_KEY = key
    os.environ["SUPABASE_KEY"] = key
    if req.supabase_url:
        SUPABASE_URL = req.supabase_url.strip().rstrip("/")
        os.environ["SUPABASE_URL"] = SUPABASE_URL

    # Persist to .env
    env_content = f"""# AirfareX India — Supabase & Environment Configuration
SUPABASE_URL={SUPABASE_URL}
SUPABASE_KEY={SUPABASE_KEY}
"""
    try:
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(env_content)
    except Exception as e:
        print(f"Warning writing .env: {e}")

    return {
        "status": "success",
        "message": f"Supabase key updated successfully for {SUPABASE_URL}",
        "project_url": SUPABASE_URL,
        "project_id": PROJECT_ID,
        "configured": True
    }

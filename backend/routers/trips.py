"""
AirfareX India — Customer Trips & Bookings Management Router
Enforces strict server-side ownership:
- Users can only view their own bookings
- Rejects cross-user booking access with HTTP 403 Forbidden
- Categorizes bookings into Upcoming, Completed, and Cancelled
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from backend.database import get_db_connection
from backend.auth import AuthUser, get_current_user

router = APIRouter(prefix="/trips", tags=["Customer Trips & Bookings"])

class TripPassengerItem(BaseModel):
    full_name: str
    seat_number: Optional[str] = None
    passenger_type: Optional[str] = "ADULT"
    gender: Optional[str] = None
    age: Optional[int] = None

class TripItem(BaseModel):
    booking_id: str
    booking_reference: Optional[str] = None
    booking_type: str
    pnr: Optional[str] = None
    airline: Optional[str] = None
    flight_no: Optional[str] = None
    sector: Optional[str] = None
    package_title: Optional[str] = None
    traveler_name: str
    email: str
    phone: str
    travel_date: str
    pax_count: int
    amount: int
    currency: str
    payment_status: str
    booking_status: str
    seat_number: Optional[str] = None
    voucher_id: Optional[str] = None
    provider: Optional[str] = "MockDevelopmentProvider"
    data_source: Optional[str] = "DEVELOPMENT"
    expires_at: Optional[str] = None
    trip_category: str  # Upcoming, Completed, Cancelled
    created_at: str
    development_notice: Optional[str] = "Development booking — airline ticket issuance is not connected in this environment."
    passengers: List[TripPassengerItem] = []

def determine_category(booking_status: str, payment_status: str, travel_date: str) -> str:
    if booking_status in ["CANCELLED", "FAILED"] or payment_status in ["FAILED", "PAYMENT_FAILED"]:
        return "Cancelled"
    try:
        t_date = datetime.strptime(travel_date.split("T")[0], "%Y-%m-%d").date()
        today = datetime.now().date()
        if t_date < today:
            return "Completed"
        return "Upcoming"
    except Exception:
        return "Upcoming"

@router.get("/my-trips", response_model=List[TripItem])
async def get_my_trips(current_user: AuthUser = Depends(get_current_user)):
    """
    Protected: Returns all authentic bookings belonging to the logged-in user.
    Enforces strict ownership: WHERE user_id = current_user.id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM bookings
        WHERE user_id = ?
        ORDER BY id DESC
    """, (current_user.id,))
    rows = cursor.fetchall()

    trips: List[TripItem] = []
    for r in rows:
        b = dict(r)
        bid = b["booking_id"]

        # Fetch itemized passengers
        cursor.execute("SELECT * FROM booking_passengers WHERE booking_id = ?", (bid,))
        p_rows = cursor.fetchall()
        passengers = [
            TripPassengerItem(
                full_name=p["full_name"],
                seat_number=p["seat_number"],
                passenger_type=p["passenger_type"],
                gender=p["gender"],
                age=p["age"]
            )
            for p in p_rows
        ]

        cat = determine_category(
            b.get("booking_status", "DRAFT"),
            b.get("payment_status", "PENDING"),
            b.get("travel_date", "2026-09-15")
        )

        trips.append(TripItem(
            booking_id=bid,
            booking_reference=b.get("booking_reference") or bid[:10],
            booking_type=b.get("booking_type", "flight"),
            pnr=b.get("pnr"),
            airline=b.get("airline"),
            flight_no=b.get("flight_no"),
            sector=b.get("sector"),
            package_title=b.get("package_id"),
            traveler_name=b.get("traveler_name", current_user.full_name),
            email=b.get("email", current_user.email),
            phone=b.get("phone", "+919876543210"),
            travel_date=b.get("travel_date", ""),
            pax_count=b.get("pax_count", 1),
            amount=b.get("amount", 0),
            currency=b.get("currency", "INR"),
            payment_status=b.get("payment_status", "PAYMENT_PENDING"),
            booking_status=b.get("booking_status", "DRAFT"),
            seat_number=b.get("seat_number"),
            voucher_id=b.get("voucher_id"),
            provider=b.get("provider", "MockDevelopmentProvider"),
            data_source=b.get("data_source", "DEVELOPMENT"),
            expires_at=str(b.get("expires_at", "")),
            trip_category=cat,
            created_at=str(b.get("created_at", "")),
            development_notice="Development booking — airline ticket issuance is not connected in this environment.",
            passengers=passengers
        ))

    conn.close()
    return trips

@router.get("/booking/{booking_id}", response_model=TripItem)
async def get_booking_by_id(
    booking_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Protected: Fetches details for a specific booking.
    CRITICAL OWNERSHIP ENFORCEMENT:
    User A cannot access User B's booking. If user_id != current_user.id, rejects with 403 Forbidden.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM bookings 
        WHERE booking_id = ? OR UPPER(booking_reference) = ?
        LIMIT 1
    """, (booking_id, booking_id.upper()))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found.")

    b = dict(row)
    # Server-side ownership check
    if b.get("user_id") != current_user.id:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to view this booking."
        )

    # Fetch itemized passengers
    cursor.execute("SELECT * FROM booking_passengers WHERE booking_id = ?", (b["booking_id"],))
    p_rows = cursor.fetchall()
    passengers = [
        TripPassengerItem(
            full_name=p["full_name"],
            seat_number=p["seat_number"],
            passenger_type=p["passenger_type"],
            gender=p["gender"],
            age=p["age"]
        )
        for p in p_rows
    ]
    conn.close()

    cat = determine_category(
        b.get("booking_status", "DRAFT"),
        b.get("payment_status", "PENDING"),
        b.get("travel_date", "2026-09-15")
    )

    return TripItem(
        booking_id=b["booking_id"],
        booking_reference=b.get("booking_reference") or b["booking_id"][:10],
        booking_type=b.get("booking_type", "flight"),
        pnr=b.get("pnr"),
        airline=b.get("airline"),
        flight_no=b.get("flight_no"),
        sector=b.get("sector"),
        package_title=b.get("package_id"),
        traveler_name=b.get("traveler_name", current_user.full_name),
        email=b.get("email", current_user.email),
        phone=b.get("phone", "+919876543210"),
        travel_date=b.get("travel_date", ""),
        pax_count=b.get("pax_count", 1),
        amount=b.get("amount", 0),
        currency=b.get("currency", "INR"),
        payment_status=b.get("payment_status", "PAYMENT_PENDING"),
        booking_status=b.get("booking_status", "DRAFT"),
        seat_number=b.get("seat_number"),
        voucher_id=b.get("voucher_id"),
        provider=b.get("provider", "MockDevelopmentProvider"),
        data_source=b.get("data_source", "DEVELOPMENT"),
        expires_at=str(b.get("expires_at", "")),
        trip_category=cat,
        created_at=str(b.get("created_at", "")),
        development_notice="Development booking — airline ticket issuance is not connected in this environment.",
        passengers=passengers
    )

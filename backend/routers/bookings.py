"""
AirfareX India — Core Booking Engine Router (Phase 5)
Provides secure end-to-end booking creation, multi-passenger management,
server-authoritative price validation, strict user ownership, idempotency,
cancellation with DGCA refund integration, and honest development mode labeling.
"""

import os
import uuid
import random
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator

from backend.database import get_db_connection
from backend.auth import AuthUser, get_current_user, get_optional_user
from backend.models import PriceBreakdownItem
from backend.routers.payments import compute_trusted_price, CreatePaymentOrderRequest, is_razorpay_live, get_publishable_key
from backend import supabase_client
from backend.supabase_client import save_booking_to_supabase, save_refund_to_supabase

router = APIRouter(prefix="/bookings", tags=["Bookings & Reservation Engine"])

BOOKING_EXPIRATION_MINUTES = 30

# =========================================================
# SCHEMAS
# =========================================================

class PassengerInput(BaseModel):
    title: Optional[str] = "Mr"
    first_name: str = Field(..., min_length=1, description="Passenger first name")
    last_name: str = Field(..., min_length=1, description="Passenger last name")
    email: Optional[str] = None
    phone: Optional[str] = None
    passenger_type: Optional[str] = "ADULT"  # ADULT, CHILD, INFANT
    gender: Optional[str] = "Male"
    age: Optional[int] = Field(28, ge=0, le=120)
    seat_choice: Optional[str] = None

class CreateBookingRequest(BaseModel):
    flight_no: Optional[str] = "6E-205"
    package_id: Optional[str] = None
    booking_type: str = Field("flight", description="'flight' or 'package'")
    origin_code: Optional[str] = "HYD"
    destination_code: Optional[str] = "DEL"
    travel_date: str = Field(..., description="Travel date in YYYY-MM-DD format")
    cabin: Optional[str] = "Economy"
    contact_name: str = Field(..., min_length=1)
    contact_email: str = Field(..., min_length=3)
    contact_phone: str = Field(..., min_length=5)
    passengers: List[PassengerInput] = Field(..., min_items=1)
    addons: Optional[Union[List[str], Dict[str, Any]]] = None
    promo_code: Optional[str] = None
    expected_price: Optional[int] = None  # To verify against server authoritative price
    idempotency_key: Optional[str] = None
    payment_method: Optional[str] = "upi"
    gstin: Optional[str] = None
    company_name: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: str
    booking_reference: str
    booking_status: str  # PENDING_PAYMENT, PAYMENT_PROCESSING, CONFIRMED, CANCELLED, EXPIRED
    payment_status: str  # PAYMENT_PENDING, PAYMENT_VERIFIED, PAYMENT_FAILED
    payment_order_id: Optional[str] = None
    provider: str
    data_source: str
    is_sandbox: bool
    airline: Optional[str] = None
    flight_no: Optional[str] = None
    sector: str
    travel_date: str
    passenger_count: int
    passengers: List[Dict[str, Any]]
    contact: Dict[str, str]
    pricing: PriceBreakdownItem
    pnr: Optional[str] = None
    seat_number: Optional[str] = None
    voucher_id: Optional[str] = None
    expires_at: str
    created_at: str
    development_notice: Optional[str] = None

class CancelBookingResponse(BaseModel):
    status: str
    booking_id: str
    booking_reference: str
    previous_status: str
    current_status: str
    cancellation_fee: int
    refund_amount: int
    refund_arn: Optional[str] = None
    message: str

def generate_booking_reference() -> str:
    """Generates a travel-industry style 8-character unique alphanumeric booking reference e.g. AXI7K29P."""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    suffix = "".join(random.choice(chars) for _ in range(5))
    return f"AXI{suffix}"

# =========================================================
# ENDPOINTS
# =========================================================

@router.post("", response_model=Union[BookingResponse, Dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_booking(
    req: CreateBookingRequest,
    current_user: Optional[AuthUser] = Depends(get_optional_user)
):
    """
    Creates a new authenticated booking with server-side authoritative price verification,
    multi-passenger persistence, idempotency protection, and payment order linkage.
    """
    # 0. Production Database Fail-Safe Check
    env = os.environ.get("ENVIRONMENT", "development").lower()
    if env == "production" and not supabase_client.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Production database (Supabase PostgreSQL) is not configured or unavailable. Local SQLite persistence is blocked in production mode to prevent split data instances."
        )

    # 1. Validate contact info
    if "@" not in req.contact_email:
        raise HTTPException(status_code=400, detail="Invalid contact email address format.")
    clean_phone = "".join(filter(str.isdigit, req.contact_phone))
    if len(clean_phone) < 7:
        raise HTTPException(status_code=400, detail="Invalid contact phone number.")

    # 2. Validate passengers
    if not req.passengers or len(req.passengers) == 0:
        raise HTTPException(status_code=400, detail="At least one passenger is required.")
    for idx, p in enumerate(req.passengers):
        if not p.first_name or not p.first_name.strip():
            raise HTTPException(status_code=400, detail=f"Passenger #{idx+1} first name is required.")
        if not p.last_name or not p.last_name.strip():
            raise HTTPException(status_code=400, detail=f"Passenger #{idx+1} last name is required.")
        if p.age is not None and (p.age < 0 or p.age > 120):
            raise HTTPException(status_code=400, detail=f"Passenger #{idx+1} has an invalid age ({p.age}).")

    auth_uid = current_user.id if current_user else "guest"
    pax_count = len(req.passengers)

    # 3. Idempotency Check: Prevent duplicate bookings with identical key
    conn = get_db_connection()
    cursor = conn.cursor()

    if req.idempotency_key:
        cursor.execute("SELECT * FROM bookings WHERE idempotency_key = ?", (req.idempotency_key,))
        existing_bkg = cursor.fetchone()
        if existing_bkg:
            b_dict = dict(existing_bkg)
            # Fetch passengers
            cursor.execute("SELECT * FROM booking_passengers WHERE booking_id = ?", (b_dict["booking_id"],))
            p_rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            pricing_obj = json.loads(b_dict["pricing_breakdown"]) if b_dict.get("pricing_breakdown") else {}
            return BookingResponse(
                booking_id=b_dict["booking_id"],
                booking_reference=b_dict.get("booking_reference") or b_dict["booking_id"][:10],
                booking_status=b_dict.get("booking_status", "PENDING_PAYMENT"),
                payment_status=b_dict.get("payment_status", "PAYMENT_PENDING"),
                payment_order_id=b_dict.get("payment_order_id"),
                provider=b_dict.get("provider", "MockDevelopmentProvider"),
                data_source=b_dict.get("data_source", "DEVELOPMENT"),
                is_sandbox=not is_razorpay_live(),
                airline=b_dict.get("airline"),
                flight_no=b_dict.get("flight_no"),
                sector=b_dict.get("sector") or f"{req.origin_code} - {req.destination_code}",
                travel_date=b_dict.get("travel_date", req.travel_date),
                passenger_count=b_dict.get("pax_count", pax_count),
                passengers=p_rows,
                contact={"name": b_dict["traveler_name"], "email": b_dict["email"], "phone": b_dict["phone"]},
                pricing=PriceBreakdownItem(**pricing_obj),
                pnr=b_dict.get("pnr"),
                seat_number=b_dict.get("seat_number"),
                voucher_id=b_dict.get("voucher_id"),
                expires_at=str(b_dict.get("expires_at", "")),
                created_at=str(b_dict.get("created_at", "")),
                development_notice="Development booking — airline ticket issuance is not connected in this environment."
            )

    # 4. Server-Authoritative Price Calculation
    order_req = CreatePaymentOrderRequest(
        booking_type=req.booking_type,
        package_id=req.package_id,
        flight_no=req.flight_no,
        origin_code=req.origin_code,
        destination_code=req.destination_code,
        cabin=req.cabin,
        payment_method=req.payment_method,
        traveler_name=req.contact_name,
        email=req.contact_email,
        phone=req.contact_phone,
        travel_date=req.travel_date,
        pax_count=pax_count,
        promo_code=req.promo_code,
        addons=req.addons,
        gstin=req.gstin,
        company_name=req.company_name
    )

    trusted_pricing = compute_trusted_price(order_req)
    authoritative_amount = trusted_pricing.final_payable_amount

    # 5. Price Tampering / Price Changed Detection
    if req.expected_price is not None and req.expected_price != authoritative_amount:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "PRICE_CHANGED",
                "message": f"Flight price updated by carrier from ₹{req.expected_price:,} to ₹{authoritative_amount:,}. Please review updated breakdown before confirming.",
                "old_price": req.expected_price,
                "new_price": authoritative_amount,
                "currency": "INR",
                "pricing": trusted_pricing.dict()
            }
        )

    # 6. Retrieve airline / provider metadata
    flight_num = req.flight_no or "6E-205"
    cursor.execute("SELECT airline, origin_code, destination_code FROM flights WHERE flight_no = ? LIMIT 1", (flight_num,))
    fl_row = cursor.fetchone()
    airline_name = fl_row["airline"] if fl_row else "IndiGo"
    orig_code = req.origin_code or (fl_row["origin_code"] if fl_row else "HYD")
    dest_code = req.destination_code or (fl_row["destination_code"] if fl_row else "DEL")
    sector_str = f"{orig_code} -> {dest_code}"

    # 7. Generate Booking ID, Reference, and Expiration
    booking_id = f"BKG-AIRX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    booking_ref = generate_booking_reference()
    now_dt = datetime.now()
    expires_dt = now_dt + timedelta(minutes=BOOKING_EXPIRATION_MINUTES)
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    expires_str = expires_dt.strftime("%Y-%m-%d %H:%M:%S")

    order_id = f"order_sbx_{uuid.uuid4().hex[:14]}"
    amount_paise = authoritative_amount * 100
    pricing_json = json.dumps(trusted_pricing.model_dump() if hasattr(trusted_pricing, "model_dump") else trusted_pricing.dict())

    # 8. Persist Booking, Passengers, and Payment Order in Atomic Transaction
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("""
            INSERT INTO bookings (
                booking_id, booking_reference, user_id, booking_type, package_id,
                flight_no, airline, sector, origin_code, destination_code,
                provider, data_source, traveler_name, email, phone, travel_date,
                pax_count, base_fare, taxes, fees, amount, currency,
                payment_status, booking_status, payment_order_id, pricing_breakdown,
                idempotency_key, created_at, updated_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'INR', 'PAYMENT_PENDING', 'PENDING_PAYMENT', ?, ?, ?, ?, ?, ?)
        """, (
            booking_id, booking_ref, auth_uid, req.booking_type, req.package_id,
            flight_num, airline_name, sector_str, orig_code, dest_code,
            "MockDevelopmentProvider", "DEVELOPMENT", req.contact_name, req.contact_email,
            req.contact_phone, req.travel_date, pax_count, trusted_pricing.base_price,
            trusted_pricing.taxes_and_fees, trusted_pricing.service_fee, authoritative_amount,
            order_id, pricing_json, req.idempotency_key, now_str, now_str, expires_str
        ))

        # Insert itemized passengers
        inserted_passengers = []
        for idx, p in enumerate(req.passengers):
            p_full = f"{p.first_name.strip()} {p.last_name.strip()}"
            p_email = p.email or req.contact_email
            p_phone = p.phone or req.contact_phone
            seat = p.seat_choice or f"{12 + idx}{random.choice(['A', 'C', 'D', 'F'])}"

            cursor.execute("""
                INSERT INTO booking_passengers (
                    booking_id, title, first_name, last_name, full_name, email, phone,
                    passenger_type, seat_number, gender, age, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_id, p.title or "Mr", p.first_name.strip(), p.last_name.strip(),
                p_full, p_email, p_phone, p.passenger_type or "ADULT", seat, p.gender or "Male",
                p.age or 28, now_str
            ))
            inserted_passengers.append({
                "title": p.title or "Mr",
                "first_name": p.first_name.strip(),
                "last_name": p.last_name.strip(),
                "full_name": p_full,
                "email": p_email,
                "phone": p_phone,
                "passenger_type": p.passenger_type or "ADULT",
                "seat_number": seat,
                "gender": p.gender or "Male",
                "age": p.age or 28
            })

        # Insert payment record
        cursor.execute("""
            INSERT INTO payments (
                order_id, booking_id, amount, currency, status, idempotency_key, created_at, updated_at
            ) VALUES (?, ?, ?, 'INR', 'CREATED', ?, ?, ?)
        """, (order_id, booking_id, amount_paise, req.idempotency_key, now_str, now_str))

        cursor.execute("COMMIT")
    except Exception as exc:
        cursor.execute("ROLLBACK")
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error creating booking: {str(exc)}")

    conn.close()

    # Async mirror to Supabase cloud if enabled
    try:
        await save_booking_to_supabase({
            "booking_id": booking_id,
            "booking_reference": booking_ref,
            "user_id": auth_uid if auth_uid != "guest" else None,
            "flight_no": flight_num,
            "airline": airline_name,
            "sector": sector_str,
            "traveler_name": req.contact_name,
            "email": req.contact_email,
            "phone": req.contact_phone,
            "travel_date": req.travel_date,
            "pax_count": pax_count,
            "amount": authoritative_amount,
            "booking_status": "PENDING_PAYMENT",
            "payment_status": "PAYMENT_PENDING",
            "payment_order_id": order_id,
            "provider": "MockDevelopmentProvider",
            "data_source": "DEVELOPMENT"
        })
    except Exception as e:
        print(f"[Supabase Sync Note] {e}")

    return BookingResponse(
        booking_id=booking_id,
        booking_reference=booking_ref,
        booking_status="PENDING_PAYMENT",
        payment_status="PAYMENT_PENDING",
        payment_order_id=order_id,
        provider="MockDevelopmentProvider",
        data_source="DEVELOPMENT",
        is_sandbox=True,
        airline=airline_name,
        flight_no=flight_num,
        sector=sector_str,
        travel_date=req.travel_date,
        passenger_count=pax_count,
        passengers=inserted_passengers,
        contact={"name": req.contact_name, "email": req.contact_email, "phone": req.contact_phone},
        pricing=trusted_pricing,
        pnr=None,
        seat_number=None,
        voucher_id=None,
        expires_at=expires_str,
        created_at=now_str,
        development_notice="Development booking — airline ticket issuance is not connected in this environment."
    )

@router.get("/{booking_id_or_ref}", response_model=BookingResponse)
async def get_booking_details(
    booking_id_or_ref: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Returns full booking details, itemized passengers, and fare breakdown.
    Enforces strict user ownership: User B cannot access User A's booking (HTTP 403 Forbidden).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    clean_id = booking_id_or_ref.strip()
    cursor.execute("""
        SELECT * FROM bookings 
        WHERE booking_id = ? OR UPPER(booking_reference) = ?
        LIMIT 1
    """, (clean_id, clean_id.upper()))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Booking '{clean_id}' not found.")

    b = dict(row)

    # Strict server ownership enforcement
    if b.get("user_id") != current_user.id:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to access this booking."
        )

    # Check for expiration of pending bookings
    b_status = b.get("booking_status", "PENDING_PAYMENT")
    if b_status in ["PENDING_PAYMENT", "DRAFT"] and b.get("expires_at"):
        try:
            exp_time = datetime.strptime(b["expires_at"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > exp_time:
                cursor.execute("UPDATE bookings SET booking_status = 'EXPIRED' WHERE booking_id = ?", (b["booking_id"],))
                conn.commit()
                b_status = "EXPIRED"
        except Exception:
            pass

    # Fetch itemized passengers
    cursor.execute("SELECT * FROM booking_passengers WHERE booking_id = ?", (b["booking_id"],))
    passengers = [dict(r) for r in cursor.fetchall()]
    conn.close()

    pricing_obj = json.loads(b["pricing_breakdown"]) if b.get("pricing_breakdown") else {
        "item_title": f"Flight {b.get('flight_no', '')}",
        "base_price": b.get("base_fare", 0),
        "hotel_price": 0,
        "transfers_price": 0,
        "taxes_and_fees": b.get("taxes", 0),
        "service_fee": b.get("fees", 0),
        "discount": 0,
        "final_payable_amount": b.get("amount", 0),
        "currency": "INR"
    }

    return BookingResponse(
        booking_id=b["booking_id"],
        booking_reference=b.get("booking_reference") or b["booking_id"][:10],
        booking_status=b_status,
        payment_status=b.get("payment_status", "PAYMENT_PENDING"),
        payment_order_id=b.get("payment_order_id"),
        provider=b.get("provider", "MockDevelopmentProvider"),
        data_source=b.get("data_source", "DEVELOPMENT"),
        is_sandbox=not is_razorpay_live(),
        airline=b.get("airline"),
        flight_no=b.get("flight_no"),
        sector=b.get("sector", ""),
        travel_date=b.get("travel_date", ""),
        passenger_count=b.get("pax_count", len(passengers)),
        passengers=passengers,
        contact={"name": b.get("traveler_name", ""), "email": b.get("email", ""), "phone": b.get("phone", "")},
        pricing=PriceBreakdownItem(**pricing_obj),
        pnr=b.get("pnr"),
        seat_number=b.get("seat_number"),
        voucher_id=b.get("voucher_id"),
        expires_at=str(b.get("expires_at", "")),
        created_at=str(b.get("created_at", "")),
        development_notice="Development booking — airline ticket issuance is not connected in this environment."
    )

@router.post("/{booking_id_or_ref}/cancel", response_model=CancelBookingResponse)
async def cancel_booking(
    booking_id_or_ref: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Cancels an eligible booking and integrates with statutory DGCA refund calculation.
    Enforces strict ownership: User B cannot cancel User A's booking (HTTP 403 Forbidden).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    clean_id = booking_id_or_ref.strip()
    cursor.execute("""
        SELECT * FROM bookings 
        WHERE booking_id = ? OR UPPER(booking_reference) = ?
        LIMIT 1
    """, (clean_id, clean_id.upper()))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Booking '{clean_id}' not found.")

    b = dict(row)

    # Server ownership check
    if b.get("user_id") != current_user.id:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to cancel this booking."
        )

    current_status = b.get("booking_status", "DRAFT")
    if current_status == "CANCELLED":
        conn.close()
        return CancelBookingResponse(
            status="ALREADY_CANCELLED",
            booking_id=b["booking_id"],
            booking_reference=b.get("booking_reference") or b["booking_id"][:10],
            previous_status="CANCELLED",
            current_status="CANCELLED",
            cancellation_fee=0,
            refund_amount=0,
            refund_arn=None,
            message="This booking is already cancelled."
        )

    if current_status in ["FAILED", "EXPIRED"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel a booking in '{current_status}' state."
        )

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now_date = datetime.now().strftime("%Y-%m-%d")
    credit_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    tot_amount = b.get("amount", 0)

    # If confirmed and paid, apply DGCA statutory cancellation and create refund record
    cancellation_fee = 0
    refund_amount = tot_amount
    refund_arn = None

    if current_status in ["CONFIRMED", "BOOKING_CONFIRMED", "TICKET_ISSUED"]:
        cancellation_fee = min(1200, int(tot_amount * 0.15))
        refund_amount = max(0, tot_amount - cancellation_fee)
        pnr_val = b.get("pnr") or f"AIRX{random.randint(1000, 9999)}"
        refund_arn = f"ARN{pnr_val}{datetime.now().strftime('%m%d%H%M')}"

        cursor.execute("""
            INSERT OR REPLACE INTO refunds (
                user_id, pnr, passenger_name, airline, flight_no, sector, total_fare,
                cancellation_fee, refund_amount, payment_method, arn_number,
                status, stage, cancellation_date, expected_credit_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'UPI / Original Method', ?, 'Processing', 2, ?, ?)
        """, (
            current_user.id, pnr_val, b["traveler_name"], b.get("airline", "IndiGo"),
            b.get("flight_no", "6E-205"), b.get("sector", "HYD -> DEL"), tot_amount,
            cancellation_fee, refund_amount, refund_arn, now_date, credit_date
        ))

    cursor.execute("""
        UPDATE bookings SET
            booking_status = 'CANCELLED',
            payment_status = CASE WHEN payment_status = 'PAYMENT_VERIFIED' THEN 'REFUND_PROCESSING' ELSE 'CANCELLED' END,
            updated_at = ?
        WHERE booking_id = ?
    """, (now_str, b["booking_id"]))
    conn.commit()
    conn.close()

    return CancelBookingResponse(
        status="SUCCESS",
        booking_id=b["booking_id"],
        booking_reference=b.get("booking_reference") or b["booking_id"][:10],
        previous_status=current_status,
        current_status="CANCELLED",
        cancellation_fee=cancellation_fee,
        refund_amount=refund_amount,
        refund_arn=refund_arn,
        message="Booking has been cancelled successfully. Refund processing initiated under DGCA guidelines."
    )

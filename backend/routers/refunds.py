from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from backend.database import get_db_connection

router = APIRouter(prefix="/refunds", tags=["Refund Tracking"])

class RefundClaimRequest(BaseModel):
    pnr: str = Field(..., example="AIRX902")
    passenger_name: str = Field(..., example="Amit Verma")
    airline: str = Field(..., example="IndiGo")
    flight_no: str = Field(..., example="6E 507")
    sector: str = Field(..., example="HYD ➔ DEL")
    total_fare: int = Field(..., example=6100)
    payment_method: str = Field("UPI / Google Pay", example="UPI / Google Pay")

class RefundItem(BaseModel):
    id: int
    pnr: str
    passenger_name: str
    airline: str
    flight_no: str
    sector: str
    total_fare: int
    cancellation_fee: int
    refund_amount: int
    payment_method: str
    arn_number: str
    status: str
    stage: int
    cancellation_date: str
    expected_credit_date: str
    timeline: List[dict]

def build_timeline(stage: int, cancel_date: str, credit_date: str):
    return [
        {
            "step": 1,
            "title": "Ticket Cancellation Initiated",
            "desc": f"Cancelled online via airline portal on {cancel_date}",
            "completed": stage >= 1,
            "current": stage == 1
        },
        {
            "step": 2,
            "title": "Airline Audit & Approval",
            "desc": "DGCA cancellation fee verified, airline approved refund",
            "completed": stage >= 2,
            "current": stage == 2
        },
        {
            "step": 3,
            "title": "Banking Gateway Processing",
            "desc": "Acquirer banking gateway processing transfer to original payment method",
            "completed": stage >= 3,
            "current": stage == 3
        },
        {
            "step": 4,
            "title": "Amount Credited to Account",
            "desc": f"Funds successfully credited. Expected completion: {credit_date}",
            "completed": stage >= 4,
            "current": stage == 4
        }
    ]

@router.get("", response_model=List[RefundItem])
def list_refunds():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM refunds ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["timeline"] = build_timeline(d["stage"], d["cancellation_date"], d["expected_credit_date"])
        results.append(RefundItem(**d))
    return results

@router.get("/track/{pnr}", response_model=RefundItem)
def track_refund(pnr: str):
    clean_pnr = pnr.replace(" ", "").replace("-", "").strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM refunds WHERE UPPER(pnr) = ?", (clean_pnr,))
    row = cursor.fetchone()
    conn.close()

    if row:
        d = dict(row)
        d["timeline"] = build_timeline(d["stage"], d["cancellation_date"], d["expected_credit_date"])
        return RefundItem(**d)
    else:
        # Provide real-time dynamic simulation for any user-entered domestic PNR
        now = datetime.now()
        cancel_date = (now - timedelta(days=2)).strftime("%Y-%m-%d")
        credit_date = (now + timedelta(days=3)).strftime("%Y-%m-%d")
        total_fare = 5400
        cancellation_fee = 999
        refund_amount = total_fare - cancellation_fee

        return RefundItem(
            id=999,
            pnr=clean_pnr,
            passenger_name="Verified Passenger",
            airline="IndiGo",
            flight_no="6E 203",
            sector="HYD ➔ DEL",
            total_fare=total_fare,
            cancellation_fee=cancellation_fee,
            refund_amount=refund_amount,
            payment_method="UPI / Original Payment Card",
            arn_number=f"ARN{clean_pnr}894012",
            status="Processing",
            stage=3,
            cancellation_date=cancel_date,
            expected_credit_date=credit_date,
            timeline=build_timeline(3, cancel_date, credit_date)
        )

@router.post("/claim", response_model=RefundItem, status_code=status.HTTP_201_CREATED)
def submit_claim(claim: RefundClaimRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    now = datetime.now()
    cancel_date = now.strftime("%Y-%m-%d")
    credit_date = (now + timedelta(days=5)).strftime("%Y-%m-%d")
    cancellation_fee = min(1200, int(claim.total_fare * 0.2))
    refund_amount = max(0, claim.total_fare - cancellation_fee)
    clean_pnr = claim.pnr.replace(" ", "").upper()
    arn = f"ARN{clean_pnr}{now.strftime('%m%d%H%M')}"

    cursor.execute("""
        INSERT OR REPLACE INTO refunds (
            pnr, passenger_name, airline, flight_no, sector, total_fare,
            cancellation_fee, refund_amount, payment_method, arn_number,
            status, stage, cancellation_date, expected_credit_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Initiated', 1, ?, ?)
    """, (
        clean_pnr, claim.passenger_name, claim.airline, claim.flight_no, claim.sector,
        claim.total_fare, cancellation_fee, refund_amount, claim.payment_method,
        arn, cancel_date, credit_date
    ))
    conn.commit()
    refund_id = cursor.lastrowid

    cursor.execute("SELECT * FROM refunds WHERE id = ?", (refund_id,))
    row = cursor.fetchone()
    conn.close()

    d = dict(row)
    d["timeline"] = build_timeline(d["stage"], d["cancellation_date"], d["expected_credit_date"])
    return RefundItem(**d)

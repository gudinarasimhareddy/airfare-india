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
            "title": "Refund Requested",
            "desc": f"Cancellation request submitted on {cancel_date}",
            "completed": stage >= 1,
            "current": stage == 1
        },
        {
            "step": 2,
            "title": "Under Review",
            "desc": "Airline verifying flight details under DGCA statutory guidelines",
            "completed": stage >= 2,
            "current": stage == 2
        },
        {
            "step": 3,
            "title": "Refund Approved",
            "desc": "Statutory refund amount approved by carrier",
            "completed": stage >= 3,
            "current": stage == 3
        },
        {
            "step": 4,
            "title": "Refund Processing",
            "desc": "Banking payment switch processing transfer to original payment method",
            "completed": stage >= 4,
            "current": stage == 4
        },
        {
            "step": 5,
            "title": "Refund Credited",
            "desc": f"Funds credited to bank account / UPI VPA. Completed: {credit_date}",
            "completed": stage >= 5,
            "current": stage == 5
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active refund record found for PNR '{clean_pnr}'. If you recently cancelled your flight, please submit a claim below."
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

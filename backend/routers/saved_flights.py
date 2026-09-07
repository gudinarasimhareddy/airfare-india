"""
AirfareX India — Saved Flights Watchlist Router
Enforces strict server-side ownership:
- Users can only view, save, and remove their own watched flights
- Rejects cross-user deletion with HTTP 403 Forbidden
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from backend.database import get_db_connection
from backend.auth import AuthUser, get_current_user

router = APIRouter(prefix="/saved-flights", tags=["Saved Flights Watchlist"])

class SavedFlightCreate(BaseModel):
    flight_no: str
    origin_code: str
    destination_code: str
    travel_date: Optional[str] = None
    observed_fare: Optional[int] = None

class SavedFlightItem(BaseModel):
    id: int
    user_id: str
    flight_no: str
    origin_code: str
    destination_code: str
    travel_date: Optional[str] = None
    observed_fare: Optional[int] = None
    created_at: str

@router.get("", response_model=List[SavedFlightItem])
async def list_saved_flights(current_user: AuthUser = Depends(get_current_user)):
    """
    Protected: Returns all saved flights for the authenticated user only.
    Enforces strict ownership: WHERE user_id = current_user.id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM saved_flights
        WHERE user_id = ?
        ORDER BY id DESC
    """, (current_user.id,))
    rows = cursor.fetchall()
    conn.close()

    return [
        SavedFlightItem(
            id=r["id"],
            user_id=r["user_id"],
            flight_no=r["flight_no"],
            origin_code=r["origin_code"],
            destination_code=r["destination_code"],
            travel_date=r["travel_date"],
            observed_fare=r["observed_fare"],
            created_at=str(r["created_at"])
        )
        for r in rows
    ]

@router.post("", response_model=SavedFlightItem, status_code=status.HTTP_201_CREATED)
async def save_flight(
    req: SavedFlightCreate,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Protected: Saves a flight to the authenticated user's watchlist.
    Binds the record strictly to current_user.id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for existing duplicate save for this user
    cursor.execute("""
        SELECT id FROM saved_flights
        WHERE user_id = ? AND flight_no = ? AND origin_code = ? AND destination_code = ?
    """, (current_user.id, req.flight_no.strip().upper(), req.origin_code.strip().upper(), req.destination_code.strip().upper()))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("SELECT * FROM saved_flights WHERE id = ?", (existing["id"],))
        row = cursor.fetchone()
        conn.close()
        return SavedFlightItem(
            id=row["id"],
            user_id=row["user_id"],
            flight_no=row["flight_no"],
            origin_code=row["origin_code"],
            destination_code=row["destination_code"],
            travel_date=row["travel_date"],
            observed_fare=row["observed_fare"],
            created_at=str(row["created_at"])
        )

    cursor.execute("""
        INSERT INTO saved_flights (
            user_id, flight_no, origin_code, destination_code, travel_date, observed_fare
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        current_user.id,
        req.flight_no.strip().upper(),
        req.origin_code.strip().upper(),
        req.destination_code.strip().upper(),
        req.travel_date,
        req.observed_fare
    ))
    conn.commit()
    new_id = cursor.lastrowid

    cursor.execute("SELECT * FROM saved_flights WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()

    return SavedFlightItem(
        id=row["id"],
        user_id=row["user_id"],
        flight_no=row["flight_no"],
        origin_code=row["origin_code"],
        destination_code=row["destination_code"],
        travel_date=row["travel_date"],
        observed_fare=row["observed_fare"],
        created_at=str(row["created_at"])
    )

@router.delete("/{saved_id}", status_code=status.HTTP_200_OK)
async def delete_saved_flight(
    saved_id: int,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Protected: Removes a flight from user's watchlist.
    CRITICAL OWNERSHIP ENFORCEMENT:
    User A cannot delete User B's saved flight. Rejects with 403 Forbidden.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM saved_flights WHERE id = ?", (saved_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Saved flight record not found.")

    if row["user_id"] != current_user.id:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to delete this saved flight."
        )

    cursor.execute("DELETE FROM saved_flights WHERE id = ?", (saved_id,))
    conn.commit()
    conn.close()

    return {"message": "Saved flight removed successfully", "id": saved_id}

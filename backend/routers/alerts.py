from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from backend.database import get_db_connection
from backend.models import AlertCreateRequest, AlertItem
from backend.supabase_client import get_alerts_from_supabase, save_alert_to_supabase
from backend.auth import AuthUser, get_optional_user

router = APIRouter(prefix="/alerts", tags=["Price Alerts"])

@router.get("", response_model=List[AlertItem])
async def get_alerts(current_user: Optional[AuthUser] = Depends(get_optional_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    if current_user:
        cursor.execute("""
            SELECT id, route, current_fare, target_condition, created_at, is_active
            FROM alerts
            WHERE user_id = ?
            ORDER BY id DESC
        """, (current_user.id,))
    else:
        cursor.execute("""
            SELECT id, route, current_fare, target_condition, created_at, is_active
            FROM alerts
            WHERE user_id = 'guest' OR user_id IS NULL
            ORDER BY id DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    if rows:
        return [
            AlertItem(
                id=r["id"],
                route=r["route"],
                current_fare=r["current_fare"],
                target_condition=r["target_condition"],
                created_at=str(r["created_at"]),
                is_active=bool(r["is_active"])
            )
            for r in rows
        ]

    # Fallback to Supabase if local SQLite has no active rows
    supa_alerts = await get_alerts_from_supabase()
    if supa_alerts:
        return [
            AlertItem(
                id=i + 1,
                route=a.get("route", "DEL → BOM"),
                current_fare=a.get("current_fare", "₹5,000"),
                target_condition=a.get("target_condition", "Price drop"),
                created_at=str(a.get("created_at", "")),
                is_active=bool(a.get("is_active", True))
            )
            for i, a in enumerate(supa_alerts)
        ]

    return []

@router.post("", response_model=AlertItem, status_code=status.HTTP_201_CREATED)
async def create_alert(
    payload: AlertCreateRequest,
    current_user: Optional[AuthUser] = Depends(get_optional_user)
):
    uid = current_user.id if current_user else "guest"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (user_id, route, current_fare, target_condition, is_active)
        VALUES (?, ?, ?, ?, 1)
    """, (uid, payload.route, payload.current_fare, payload.target_condition))
    conn.commit()
    alert_id = cursor.lastrowid

    cursor.execute("SELECT id, route, current_fare, target_condition, created_at, is_active FROM alerts WHERE id = ?", (alert_id,))
    row = cursor.fetchone()
    conn.close()

    # Mirror to Supabase if configured (non-blocking)
    try:
        await save_alert_to_supabase({
            "user_id": uid if uid != "guest" else None,
            "route": payload.route,
            "current_fare": payload.current_fare,
            "target_condition": payload.target_condition,
            "is_active": True
        })
    except Exception as e:
        print(f"[Supabase alert sync note] {e}")

    return AlertItem(
        id=row["id"],
        route=row["route"],
        current_fare=row["current_fare"],
        target_condition=row["target_condition"],
        created_at=str(row["created_at"]),
        is_active=bool(row["is_active"])
    )

@router.delete("/{alert_id}", status_code=status.HTTP_200_OK)
def delete_alert(
    alert_id: int,
    current_user: Optional[AuthUser] = Depends(get_optional_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id FROM alerts WHERE id = ?", (alert_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")

    alert_owner = row["user_id"] if "user_id" in row.keys() else "guest"

    # Server-side ownership enforcement
    if alert_owner != "guest":
        if not current_user:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to delete this alert"
            )
        if alert_owner != current_user.id:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You do not have permission to delete another user's alert"
            )

    cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return {"message": "Alert deleted successfully", "id": alert_id}

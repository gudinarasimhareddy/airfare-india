from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.database import get_db_connection
from backend.models import AlertCreateRequest, AlertItem

router = APIRouter(prefix="/alerts", tags=["Price Alerts"])

@router.get("", response_model=List[AlertItem])
def get_alerts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, route, current_fare, target_condition, created_at, is_active FROM alerts ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
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

@router.post("", response_model=AlertItem, status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreateRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (route, current_fare, target_condition, is_active)
        VALUES (?, ?, ?, 1)
    """, (payload.route, payload.current_fare, payload.target_condition))
    conn.commit()
    alert_id = cursor.lastrowid
    
    cursor.execute("SELECT id, route, current_fare, target_condition, created_at, is_active FROM alerts WHERE id = ?", (alert_id,))
    row = cursor.fetchone()
    conn.close()

    return AlertItem(
        id=row["id"],
        route=row["route"],
        current_fare=row["current_fare"],
        target_condition=row["target_condition"],
        created_at=str(row["created_at"]),
        is_active=bool(row["is_active"])
    )

@router.delete("/{alert_id}", status_code=status.HTTP_200_OK)
def delete_alert(alert_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM alerts WHERE id = ?", (alert_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")

    cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return {"message": "Alert deleted successfully", "id": alert_id}

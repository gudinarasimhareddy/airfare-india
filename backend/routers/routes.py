from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from typing import List, Dict, Any
from backend.database import get_db_connection
from backend.models import RouteItem

router = APIRouter(prefix="/routes", tags=["Routes"])

@router.get("", response_model=List[RouteItem])
def get_monitored_routes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes ORDER BY index_value DESC")
    rows = cursor.fetchall()
    conn.close()
    return [RouteItem(**dict(r)) for r in rows]

@router.get("/{origin}/{destination}/elasticity")
def get_route_elasticity(origin: str, destination: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    route_code = f"{origin.upper()}-{destination.upper()}"
    
    cursor.execute("SELECT * FROM elasticity WHERE route_code = ?", (route_code,))
    rows = cursor.fetchall()
    
    # Fallback to DEL-BOM baseline elasticity curve if route isn't explicitly defined
    if not rows:
        cursor.execute("SELECT * FROM elasticity WHERE route_code = 'DEL-BOM'")
        rows = cursor.fetchall()
        
    conn.close()

    points = []
    for r in rows:
        points.append({
            "window": r["advance_window"],
            "fare": r["fare"],
            "formatted_fare": f"₹{r['fare']:,}",
            "sensitivity": r["sensitivity"]
        })

    return {
        "route": f"{origin.upper()} → {destination.upper()}",
        "sensitivity_level": "HIGH sensitivity",
        "description": "Historical lead-time elasticity curve showing progressive fare discounts with advance purchase",
        "points": points
    }

@router.get("/export/csv")
def export_routes_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT route_code, origin, destination, index_value, change_30d, avg_fare, volatility_score, status FROM routes")
    rows = cursor.fetchall()
    conn.close()

    lines = ["route_code,origin,destination,index_value,change_30d_pct,avg_fare_inr,volatility_score,status"]
    for r in rows:
        lines.append(f"{r['route_code']},\"{r['origin']}\",\"{r['destination']}\",{r['index_value']},{r['change_30d']},{r['avg_fare']},{r['volatility_score']},{r['status']}")
    
    csv_content = "\n".join(lines)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=airfarex_route_intelligence.csv"}
    )

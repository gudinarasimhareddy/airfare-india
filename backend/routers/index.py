from fastapi import APIRouter, Query
from typing import Dict, Any, List
from backend.database import get_db_connection

router = APIRouter(prefix="/apix", tags=["APIx Index"])

@router.get("/overview")
def get_apix_overview() -> Dict[str, Any]:
    return {
        "national_apix": 128.6,
        "base_period": "2024 = 100",
        "monthly_change_pct": 2.8,
        "daily_apix": 128.6,
        "daily_change_pct": 0.8,
        "weekly_apix": 126.9,
        "weekly_change_pct": 2.1,
        "monthly_apix": 121.4,
        "monthly_growth_pct": 7.4,
        "average_domestic_fare": 5842,
        "quotes_processed": "1.24M",
        "data_confidence_pct": 94.2,
        "index_coverage_pct": 94.8,
        "status": "Healthy & Calibrated",
        "pipeline_stages": [
            {"stage": "1. Collect fares", "status": "Complete"},
            {"stage": "2. Clean & deduplicate", "status": "Complete"},
            {"stage": "3. Normalize taxes & fees", "status": "Complete"},
            {"stage": "4. Apply route weights", "status": "Complete"},
            {"stage": "5. Calculate APIx", "status": "Live"}
        ],
        "booking_basket": [
            {"window": "T+1", "fare": 8400, "weight_pct": 92},
            {"window": "T+7", "fare": 6900, "weight_pct": 75},
            {"window": "T+15", "fare": 5800, "weight_pct": 61},
            {"window": "T+30", "fare": 4900, "weight_pct": 52},
            {"window": "T+45", "fare": 4600, "weight_pct": 49}
        ],
        "fare_decomposition": [
            {"component": "Base Fare", "share_pct": 73, "example_inr": 4700},
            {"component": "Taxes & GST", "share_pct": 14, "example_inr": 900},
            {"component": "User Development Fee (UDF)", "share_pct": 7, "example_inr": 450},
            {"component": "Convenience & Other", "share_pct": 4, "example_inr": 250}
        ]
    }

@router.get("/trend")
def get_apix_trend(period: str = Query("30D", description="Time window: 30D, 90D, 1Y")) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    normalized_period = period.upper()
    if normalized_period not in ["30D", "90D", "1Y"]:
        normalized_period = "30D"

    cursor.execute("""
        SELECT label, value, is_projected 
        FROM index_history 
        WHERE period = ? 
        ORDER BY id ASC
    """, (normalized_period,))
    rows = cursor.fetchall()
    conn.close()

    points = [{"label": r["label"], "value": r["value"], "projected": bool(r["is_projected"])} for r in rows]

    return {
        "period": normalized_period,
        "base_period": "2024 = 100",
        "points": points
    }

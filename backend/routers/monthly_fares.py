from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import calendar

router = APIRouter(prefix="/monthly-fares", tags=["Monthly Cheapest Fares"])

BASE_FARES = {
    ("DEL", "BOM"): 4150,
    ("BOM", "DEL"): 4190,
    ("BLR", "DEL"): 4950,
    ("DEL", "BLR"): 4900,
    ("HYD", "DEL"): 4250,
    ("DEL", "HYD"): 4200,
    ("DEL", "GOI"): 4750,
    ("GOI", "DEL"): 4800,
    ("BOM", "BLR"): 3300,
    ("BLR", "BOM"): 3350,
    ("CCU", "DEL"): 4550,
    ("DEL", "CCU"): 4500,
    ("MAA", "DEL"): 4700,
    ("DEL", "MAA"): 4650,
    ("PNQ", "DEL"): 3850,
    ("DEL", "PNQ"): 3900,
    ("DEL", "JAI"): 2450,
    ("JAI", "DEL"): 2480,
    ("BOM", "HYD"): 2850,
    ("HYD", "BOM"): 2890,
    ("BLR", "HYD"): 3150,
    ("HYD", "BLR"): 3100,
    ("BLR", "MAA"): 2350,
    ("MAA", "BLR"): 2350,
    ("BOM", "GOI"): 2980,
    ("GOI", "BOM"): 2950
}

AIRLINES_POOL = ["IndiGo", "Akasa Air", "Air India Express", "Air India", "SpiceJet"]

@router.get("/calendar")
def get_monthly_fare_calendar(
    origin: str = Query("DEL", description="Origin airport code"),
    destination: str = Query("BOM", description="Destination airport code"),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format (defaults to current month)")
):
    """Retrieve 30/31-day lowest fare calendar matrix for route."""
    orig = origin.upper().strip()
    dest = destination.upper().strip()

    now = datetime.now()
    if month and len(month.split("-")) == 2:
        try:
            year, m_num = map(int, month.split("-"))
        except ValueError:
            year, m_num = now.year, now.month
    else:
        year, m_num = now.year, now.month

    num_days = calendar.monthrange(year, m_num)[1]
    month_name = calendar.month_name[m_num]

    base = BASE_FARES.get((orig, dest), 4200)

    calendar_days = []
    fares_list = []

    for d in range(1, num_days + 1):
        curr_date = date(year, m_num, d)
        weekday_idx = curr_date.weekday() # 0 = Mon, 6 = Sun
        weekday_abbr = curr_date.strftime("%a")

        # Deterministic variation based on day of week and day number
        # Tue(1), Wed(2) are cheapest. Fri(4), Sun(6) are peak.
        if weekday_idx in [1, 2]: # Tue, Wed
            day_factor = 0.86
        elif weekday_idx in [0, 3]: # Mon, Thu
            day_factor = 0.96
        elif weekday_idx == 4: # Fri
            day_factor = 1.18
        elif weekday_idx == 5: # Sat
            day_factor = 1.12
        else: # Sun
            day_factor = 1.25

        # Slight sinusoidal modulation for realistic curve
        pseudo_noise = (((d * 7 + 13) % 17) - 8) * 25
        daily_fare = int(base * day_factor) + pseudo_noise
        # Round to nearest ₹50 or ₹99 for airline-like pricing
        daily_fare = (daily_fare // 50) * 50 - 1

        # Determine airline for this cheapest quote
        al_idx = (d + (1 if weekday_idx in [1,2] else 0)) % len(AIRLINES_POOL)
        airline = AIRLINES_POOL[al_idx]

        fares_list.append((daily_fare, d, curr_date.isoformat(), weekday_abbr, airline))

    # Calculate statistics & thresholds
    fares_only = [f[0] for f in fares_list]
    avg_fare = int(sum(fares_only) / len(fares_only))
    min_fare = min(fares_only)
    max_fare = max(fares_only)

    deal_threshold = int(min_fare + (avg_fare - min_fare) * 0.45)
    surge_threshold = int(avg_fare + (max_fare - avg_fare) * 0.35)

    cheapest_item = min(fares_list, key=lambda x: x[0])

    for fare, d, d_iso, w_abbr, al in fares_list:
        if fare <= deal_threshold:
            category = "deal"
            badge = "🔥 Best Deal"
        elif fare >= surge_threshold:
            category = "surge"
            badge = "⚡ Surge Peak"
        else:
            category = "standard"
            badge = "Standard"

        calendar_days.append({
            "day": d,
            "date": d_iso,
            "weekday": w_abbr,
            "fare": fare,
            "airline": al,
            "category": category,
            "badge": badge,
            "savings_vs_avg": max(0, avg_fare - fare)
        })

    return {
        "origin": orig,
        "destination": dest,
        "month_label": f"{month_name} {year}",
        "year": year,
        "month": m_num,
        "total_days": num_days,
        "cheapest_fare": cheapest_item[0],
        "cheapest_date": cheapest_item[2],
        "cheapest_day": cheapest_item[1],
        "cheapest_weekday": cheapest_item[3],
        "cheapest_airline": cheapest_item[4],
        "highest_fare": max_fare,
        "average_fare": avg_fare,
        "max_potential_savings": max_fare - min_fare,
        "insight": f"Flying on {cheapest_item[3]}, {cheapest_item[1]} {month_name} on {cheapest_item[4]} saves ₹{max_fare - min_fare:,} compared to peak weekend departure.",
        "days": calendar_days
    }

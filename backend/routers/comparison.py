from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import sqlite3
from backend.database import get_db_connection

router = APIRouter(prefix="/comparison", tags=["Airline Comparison Matrix"])

AIRLINE_DEFAULTS = {
    "IndiGo": {
        "airline": "IndiGo",
        "iata": "6E",
        "color": "#0052cc",
        "logo_text": "6E IndiGo",
        "seat_pitch_inch": 29.5,
        "cabin_baggage": "7 kg (1 pc)",
        "checked_baggage": "15 kg (1 pc)",
        "excess_baggage_rate_per_kg": 550,
        "meals_policy": "Paid In-flight Café (6E Tiffin)",
        "otp_percentage": 88.6,
        "cancellation_fee": 3000,
        "change_fee": 2500,
        "fleet": "Airbus A320neo / A321neo",
        "wifi_onboard": "No",
        "usb_power": "Select A321neo",
        "co2_emissions_kg": 118,
        "rating": 4.5,
        "badge": "⏱️ Highest Punctuality & Frequency"
    },
    "Air India": {
        "airline": "Air India",
        "iata": "AI",
        "color": "#e01a22",
        "logo_text": "Air India",
        "seat_pitch_inch": 32.0,
        "cabin_baggage": "7 kg (1 pc)",
        "checked_baggage": "15–20 kg (Included)",
        "excess_baggage_rate_per_kg": 500,
        "meals_policy": "Free Hot Gourmet Meals & Beverages",
        "otp_percentage": 82.4,
        "cancellation_fee": 3500,
        "change_fee": 2750,
        "fleet": "Airbus A350-900 / A321neo / B777",
        "wifi_onboard": "On select A350 flights",
        "usb_power": "Yes (All Seats)",
        "co2_emissions_kg": 126,
        "rating": 4.6,
        "badge": "💺 Best Comfort & Free Meals"
    },
    "Akasa Air": {
        "airline": "Akasa Air",
        "iata": "QP",
        "color": "#ff6600",
        "logo_text": "Akasa Air",
        "seat_pitch_inch": 30.5,
        "cabin_baggage": "7 kg (1 pc)",
        "checked_baggage": "15 kg (1 pc)",
        "excess_baggage_rate_per_kg": 525,
        "meals_policy": "Café Akasa (Artisanal Warm Meals)",
        "otp_percentage": 89.2,
        "cancellation_fee": 2999,
        "change_fee": 2250,
        "fleet": "Boeing 737 MAX 8",
        "wifi_onboard": "No",
        "usb_power": "Yes (USB-A & C on every seat)",
        "co2_emissions_kg": 112,
        "rating": 4.7,
        "badge": "🌿 Modern Fleet & Eco Efficiency"
    },
    "SpiceJet": {
        "airline": "SpiceJet",
        "iata": "SG",
        "color": "#d91e18",
        "logo_text": "SpiceJet",
        "seat_pitch_inch": 29.0,
        "cabin_baggage": "7 kg (1 pc)",
        "checked_baggage": "15 kg (1 pc)",
        "excess_baggage_rate_per_kg": 550,
        "meals_policy": "SpiceCafe (Pre-book / Onboard)",
        "otp_percentage": 73.8,
        "cancellation_fee": 3250,
        "change_fee": 2750,
        "fleet": "Boeing 737-800 / Q400",
        "wifi_onboard": "SpicEngage (Inflight Streaming)",
        "usb_power": "Select Aircraft",
        "co2_emissions_kg": 124,
        "rating": 3.9,
        "badge": "💸 Budget Friendly Alternatives"
    },
    "Air India Express": {
        "airline": "Air India Express",
        "iata": "IX",
        "color": "#f37021",
        "logo_text": "AI Express",
        "seat_pitch_inch": 30.0,
        "cabin_baggage": "7 kg (1 pc)",
        "checked_baggage": "15 kg (1 pc)",
        "excess_baggage_rate_per_kg": 500,
        "meals_policy": "Gourmair (Pre-book Hot Meals)",
        "otp_percentage": 84.1,
        "cancellation_fee": 2950,
        "change_fee": 2400,
        "fleet": "Boeing 737 MAX 8 / A320",
        "wifi_onboard": "AirFlix (Streaming Entertainment)",
        "usb_power": "Yes (USB & Type-C)",
        "co2_emissions_kg": 114,
        "rating": 4.4,
        "badge": "⚡ Dynamic Value & Fast Boarding"
    }
}

ROUTE_MULTIPLIERS = {
    ("DEL", "BOM"): {"base": 4200, "duration": "2h 15m", "distance_km": 1148},
    ("BOM", "DEL"): {"base": 4250, "duration": "2h 10m", "distance_km": 1148},
    ("BLR", "DEL"): {"base": 5100, "duration": "2h 45m", "distance_km": 1740},
    ("DEL", "BLR"): {"base": 5150, "duration": "2h 40m", "distance_km": 1740},
    ("HYD", "DEL"): {"base": 4350, "duration": "2h 15m", "distance_km": 1253},
    ("DEL", "HYD"): {"base": 4300, "duration": "2h 10m", "distance_km": 1253},
    ("DEL", "GOI"): {"base": 4890, "duration": "2h 35m", "distance_km": 1515},
    ("GOI", "DEL"): {"base": 4920, "duration": "2h 30m", "distance_km": 1515},
    ("BOM", "BLR"): {"base": 3390, "duration": "1h 45m", "distance_km": 842},
    ("BLR", "BOM"): {"base": 3410, "duration": "1h 40m", "distance_km": 842},
    ("CCU", "DEL"): {"base": 4650, "duration": "2h 20m", "distance_km": 1305},
    ("DEL", "CCU"): {"base": 4600, "duration": "2h 15m", "distance_km": 1305},
    ("MAA", "DEL"): {"base": 4800, "duration": "2h 50m", "distance_km": 1760},
    ("DEL", "MAA"): {"base": 4750, "duration": "2h 45m", "distance_km": 1760},
    ("PNQ", "DEL"): {"base": 3950, "duration": "2h 05m", "distance_km": 1173},
    ("DEL", "PNQ"): {"base": 3980, "duration": "2h 00m", "distance_km": 1173},
    ("DEL", "JAI"): {"base": 2499, "duration": "1h 00m", "distance_km": 240},
    ("JAI", "DEL"): {"base": 2520, "duration": "0h 55m", "distance_km": 240}
}

AIRLINE_PRICE_ADJUSTMENTS = {
    "IndiGo": 1.00,
    "Air India": 1.08,
    "Akasa Air": 0.94,
    "SpiceJet": 0.92,
    "Air India Express": 0.96
}

@router.get("/sector")
def compare_sector_airlines(
    origin: str = Query("DEL", description="Origin airport code"),
    destination: str = Query("BOM", description="Destination airport code")
):
    """Generate multi-airline price, perk, and performance comparison matrix."""
    orig = origin.upper().strip()
    dest = destination.upper().strip()

    route_info = ROUTE_MULTIPLIERS.get((orig, dest), {
        "base": 4200,
        "duration": "2h 15m",
        "distance_km": 1200
    })

    conn = get_db_connection()
    cur = conn.cursor()

    # Query live flights from database if matching
    cur.execute("""
        SELECT airline, flight_no, base_fare, total_fare, duration, stops, emissions_kg
        FROM flights
        WHERE origin_code = ? AND destination_code = ?
    """, (orig, dest))
    live_db_flights = cur.fetchall()
    conn.close()

    db_map = {}
    for row in live_db_flights:
        al = row["airline"]
        if al not in db_map or row["total_fare"] < db_map[al]["total_fare"]:
            db_map[al] = dict(row)

    comparison_results = []
    for al_name, defaults in AIRLINE_DEFAULTS.items():
        factor = AIRLINE_PRICE_ADJUSTMENTS.get(al_name, 1.0)
        
        # Prefer live quote if in DB, otherwise generate calibrated estimate
        if al_name in db_map:
            total_fare = db_map[al_name]["total_fare"]
            base_fare = db_map[al_name]["base_fare"]
            duration = db_map[al_name]["duration"]
            co2 = db_map[al_name]["emissions_kg"]
        else:
            base_fare = int(route_info["base"] * factor)
            taxes = int(base_fare * 0.18) + 380  # GST + UDF
            total_fare = base_fare + taxes
            duration = route_info["duration"]
            co2 = int(defaults["co2_emissions_kg"] * (route_info["distance_km"] / 1148.0))

        item = {
            **defaults,
            "origin": orig,
            "destination": dest,
            "base_fare": base_fare,
            "taxes_fees": total_fare - base_fare,
            "total_fare": total_fare,
            "duration": duration,
            "co2_emissions_kg": co2
        }
        comparison_results.append(item)

    # Sort by total fare
    comparison_results.sort(key=lambda x: x["total_fare"])

    # Determine Winners
    cheapest = comparison_results[0]
    best_otp = max(comparison_results, key=lambda x: x["otp_percentage"])
    best_comfort = max(comparison_results, key=lambda x: x["seat_pitch_inch"])
    lowest_emissions = min(comparison_results, key=lambda x: x["co2_emissions_kg"])

    highlights = {
        "cheapest": {
            "airline": cheapest["airline"],
            "fare": cheapest["total_fare"],
            "tag": "💸 Lowest Fare"
        },
        "most_punctual": {
            "airline": best_otp["airline"],
            "otp": f"{best_otp['otp_percentage']}%",
            "tag": "⏱️ Highest On-Time Performance"
        },
        "most_comfortable": {
            "airline": best_comfort["airline"],
            "pitch": f"{best_comfort['seat_pitch_inch']}\" legroom + {best_comfort['meals_policy']}",
            "tag": "💺 Best Comfort & Free Meals"
        },
        "most_eco_friendly": {
            "airline": lowest_emissions["airline"],
            "emissions": f"{lowest_emissions['co2_emissions_kg']} kg CO₂e",
            "tag": "🌿 Lowest Carbon Footprint"
        }
    }

    return {
        "origin": orig,
        "destination": dest,
        "route_name": f"{orig} ➔ {dest}",
        "distance_km": route_info["distance_km"],
        "duration": route_info["duration"],
        "highlights": highlights,
        "airlines": comparison_results
    }

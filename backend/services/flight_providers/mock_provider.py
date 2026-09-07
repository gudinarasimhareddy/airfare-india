"""
AirfareX India — Mock / Development Flight Provider
Provides realistic deterministic flight schedules, multi-segment connections,
and MoCA/DGCA domestic airfare decomposition for Indian routes.
Always labels results as DEVELOPMENT. Never claims to be LIVE.
"""

import random
from typing import List, Optional, Dict, Any
from backend.database import get_db_connection
from backend.services.flight_providers.base import (
    BaseFlightProvider,
    FlightSearchParams,
    NormalizedFlight,
    NormalizedSearchResponse,
    FlightSegment
)

# Major Indian domestic carriers catalog
AIRLINE_METADATA = [
    {"name": "IndiGo", "code": "6E", "aircraft": "Airbus A321neo", "base_multiplier": 1.00},
    {"name": "Air India", "code": "AI", "aircraft": "Airbus A320neo", "base_multiplier": 1.10},
    {"name": "Akasa Air", "code": "QP", "aircraft": "Boeing 737 MAX 8", "base_multiplier": 0.95},
    {"name": "SpiceJet", "code": "SG", "aircraft": "Boeing 737-800", "base_multiplier": 0.96},
    {"name": "Air India Express", "code": "IX", "aircraft": "Boeing 737 MAX 8", "base_multiplier": 0.92},
    {"name": "Star Air", "code": "S5", "aircraft": "Embraer E175", "base_multiplier": 1.05}
]

# Sector baseline distance & benchmark fares (INR)
KNOWN_SECTORS = {
    ("DEL", "BOM"): {"dist": 1148, "base": 3600, "dur": 135},
    ("BOM", "DEL"): {"dist": 1148, "base": 3600, "dur": 135},
    ("DEL", "BLR"): {"dist": 1740, "base": 4200, "dur": 160},
    ("BLR", "DEL"): {"dist": 1740, "base": 4200, "dur": 160},
    ("BOM", "BLR"): {"dist": 842, "base": 3100, "dur": 105},
    ("BLR", "BOM"): {"dist": 842, "base": 3100, "dur": 105},
    ("HYD", "DEL"): {"dist": 1253, "base": 3700, "dur": 135},
    ("DEL", "HYD"): {"dist": 1253, "base": 3700, "dur": 135},
    ("HYD", "BOM"): {"dist": 620, "base": 2800, "dur": 85},
    ("BOM", "HYD"): {"dist": 620, "base": 2800, "dur": 85},
    ("MAA", "DEL"): {"dist": 1757, "base": 4300, "dur": 165},
    ("DEL", "MAA"): {"dist": 1757, "base": 4300, "dur": 165},
    ("CCU", "DEL"): {"dist": 1305, "base": 3900, "dur": 140},
    ("DEL", "CCU"): {"dist": 1305, "base": 3900, "dur": 140},
    ("BOM", "GOI"): {"dist": 435, "base": 2400, "dur": 70},
    ("GOI", "BOM"): {"dist": 435, "base": 2400, "dur": 70},
}

class MockDevelopmentProvider(BaseFlightProvider):
    """Deterministic Mock / Development Flight Provider for local workflows."""

    def get_name(self) -> str:
        return "MockDevelopmentProvider"

    def is_configured(self) -> bool:
        # Development provider is always ready and operational
        return True

    def _extract_airport_code(self, val: str) -> str:
        """Extracts 3-letter IATA code from string like 'Hyderabad (HYD)' or 'HYD'."""
        clean = (val or "").strip().upper()
        if "(" in clean and ")" in clean:
            start = clean.find("(") + 1
            end = clean.find(")")
            code = clean[start:end].strip()
            if len(code) == 3:
                return code
        parts = clean.split()
        for p in parts:
            p_clean = p.replace("(", "").replace(")", "")
            if len(p_clean) == 3 and p_clean.isalpha():
                return p_clean
        return clean[:3] if len(clean) >= 3 else "DEL"

    def _get_city_name(self, code: str) -> str:
        city_map = {
            "DEL": "Delhi", "BOM": "Mumbai", "BLR": "Bengaluru",
            "HYD": "Hyderabad", "MAA": "Chennai", "CCU": "Kolkata",
            "GOI": "Goa", "PNQ": "Pune", "JAI": "Jaipur",
            "COK": "Kochi", "AMD": "Ahmedabad", "IXC": "Chandigarh",
            "LKO": "Lucknow", "PAT": "Patna", "GAU": "Guwahati"
        }
        return city_map.get(code.upper(), code.upper())

    async def search_flights(self, params: FlightSearchParams) -> NormalizedSearchResponse:
        orig_code = self._extract_airport_code(params.origin)
        dest_code = self._extract_airport_code(params.destination)
        orig_city = self._get_city_name(orig_code)
        dest_city = self._get_city_name(dest_code)

        # 1. Query database for seeded matching flights
        db_flights = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM flights 
                WHERE (UPPER(origin_code) = ? OR UPPER(origin) LIKE ?)
                  AND (UPPER(destination_code) = ? OR UPPER(destination) LIKE ?)
            """, (orig_code, f"%{orig_city}%", dest_code, f"%{dest_city}%"))
            rows = cursor.fetchall()
            db_flights = [dict(r) for r in rows]
            conn.close()
        except Exception:
            db_flights = []

        raw_flight_items: List[Dict[str, Any]] = []

        if db_flights:
            raw_flight_items = db_flights
        else:
            # Dynamically synthesize realistic schedule for this route
            sector_info = KNOWN_SECTORS.get((orig_code, dest_code), {
                "dist": 1200, "base": 3800, "dur": 130
            })
            
            # Deterministic seed based on route and date
            seed_key = f"{orig_code}-{dest_code}-{params.date or '2026-09-06'}"
            rng = random.Random(seed_key)

            times_nonstop = [
                ("06:00", "08:15", "T2", "G4"),
                ("08:45", "11:00", "T3", "G12"),
                ("11:30", "13:45", "T1", "G7"),
                ("14:15", "16:30", "T2", "G18"),
                ("17:40", "19:55", "T3", "G2"),
                ("20:30", "22:45", "T2", "G15"),
            ]

            flight_id_counter = 1000

            # Generate 5-6 nonstop flights
            for i, (dep, arr, term, gate) in enumerate(times_nonstop):
                airline = AIRLINE_METADATA[i % len(AIRLINE_METADATA)]
                base_calc = round(sector_info["base"] * airline["base_multiplier"] / 50) * 50
                tax_calc = round(base_calc * 0.18) + 236 + 380  # GST + ASF + UDF
                tot_calc = base_calc + tax_calc
                flight_no = f"{airline['code']} {rng.randint(200, 2899)}"
                dur_m = sector_info["dur"]
                dur_str = f"{dur_m // 60}h {dur_m % 60}m"

                raw_flight_items.append({
                    "id": flight_id_counter + i,
                    "airline": airline["name"],
                    "airline_code": airline["code"],
                    "flight_no": flight_no,
                    "origin": orig_city,
                    "origin_code": orig_code,
                    "destination": dest_city,
                    "destination_code": dest_code,
                    "dep_time": dep,
                    "arr_time": arr,
                    "duration": dur_str,
                    "duration_mins": dur_m,
                    "stops": "Nonstop",
                    "stop_count": 0,
                    "base_fare": base_calc,
                    "taxes": tax_calc,
                    "total_fare": tot_calc,
                    "bag_fee": 0 if i % 2 == 0 else 450,
                    "emissions_kg": rng.randint(110, 155),
                    "fare_score": rng.randint(82, 98),
                    "tag": "CHEAPEST" if i == 0 else ("FASTEST" if i == 1 else "POPULAR"),
                    "status": "On time",
                    "terminal": term,
                    "gate": gate,
                    "aircraft": airline["aircraft"]
                })

            # Generate 2 one-stop flights (multi-segment)
            intermediate_hub = "HYD" if orig_code != "HYD" and dest_code != "HYD" else "BOM"
            intermediate_city = self._get_city_name(intermediate_hub)

            for j in range(2):
                airline = AIRLINE_METADATA[(j + 2) % len(AIRLINE_METADATA)]
                base_calc = round(sector_info["base"] * 0.90 / 50) * 50
                tax_calc = round(base_calc * 0.18) + 236 + 450
                tot_calc = base_calc + tax_calc
                f_leg1 = f"{airline['code']} {rng.randint(300, 999)}"
                f_leg2 = f"{airline['code']} {rng.randint(1100, 1999)}"
                
                leg1_dur = 65
                layover = 55
                leg2_dur = 75
                total_dur_m = leg1_dur + layover + leg2_dur

                dep_h = 7 + j * 6
                dep_t = f"{dep_h:02d}:15"
                arr_h = (dep_h + total_dur_m // 60) % 24
                arr_m = (15 + total_dur_m % 60) % 60
                arr_t = f"{arr_h:02d}:{arr_m:02d}"

                raw_flight_items.append({
                    "id": flight_id_counter + 10 + j,
                    "airline": airline["name"],
                    "airline_code": airline["code"],
                    "flight_no": f"{f_leg1} / {f_leg2}",
                    "origin": orig_city,
                    "origin_code": orig_code,
                    "destination": dest_city,
                    "destination_code": dest_code,
                    "dep_time": dep_t,
                    "arr_time": arr_t,
                    "duration": f"{total_dur_m // 60}h {total_dur_m % 60}m",
                    "duration_mins": total_dur_m,
                    "stops": "1 stop",
                    "stop_count": 1,
                    "base_fare": base_calc,
                    "taxes": tax_calc,
                    "total_fare": tot_calc,
                    "bag_fee": 0,
                    "emissions_kg": rng.randint(160, 205),
                    "fare_score": rng.randint(75, 88),
                    "tag": "1 STOP SAVER",
                    "status": "On time",
                    "terminal": "T2",
                    "gate": f"G{rng.randint(3, 19)}",
                    "aircraft": airline["aircraft"],
                    "custom_segments": [
                        {
                            "segment_id": f"SEG-{j}-1",
                            "flight_no": f_leg1,
                            "airline": airline["name"],
                            "airline_code": airline["code"],
                            "origin": orig_city,
                            "origin_code": orig_code,
                            "destination": intermediate_city,
                            "destination_code": intermediate_hub,
                            "dep_time": dep_t,
                            "arr_time": f"{(dep_h + 1):02d}:20",
                            "duration": f"{leg1_dur // 60}h {leg1_dur % 60}m",
                            "duration_mins": leg1_dur,
                            "layover_mins": layover,
                            "terminal_dep": "T2",
                            "terminal_arr": "T1",
                            "aircraft": airline["aircraft"]
                        },
                        {
                            "segment_id": f"SEG-{j}-2",
                            "flight_no": f_leg2,
                            "airline": airline["name"],
                            "airline_code": airline["code"],
                            "origin": intermediate_city,
                            "origin_code": intermediate_hub,
                            "destination": dest_city,
                            "destination_code": dest_code,
                            "dep_time": f"{(dep_h + 2):02d}:15",
                            "arr_time": arr_t,
                            "duration": f"{leg2_dur // 60}h {leg2_dur % 60}m",
                            "duration_mins": leg2_dur,
                            "layover_mins": 0,
                            "terminal_dep": "T1",
                            "terminal_arr": "T2",
                            "aircraft": airline["aircraft"]
                        }
                    ]
                })

        # Process and normalize all raw flight records into NormalizedFlight items
        normalized_list: List[NormalizedFlight] = []

        for idx, item in enumerate(raw_flight_items):
            # Apply Filters
            if params.direct_only and str(item.get("stops", "")).lower() != "nonstop":
                continue
            if params.stops != "Any":
                stops_val = str(item.get("stops", "")).lower()
                req_stop = params.stops.lower()
                if req_stop == "nonstop" and stops_val != "nonstop":
                    continue
                elif req_stop in ["1 stop", "1-stop"] and "1" not in stops_val:
                    continue
            if params.airline != "All airlines" and item.get("airline", "").lower() != params.airline.lower():
                continue
            if params.max_price is not None and item.get("total_fare", 0) > params.max_price:
                continue
            if params.baggage == "Include checked bag" and item.get("bag_fee", 0) > 0:
                continue

            # Time of day filter
            dep_hour = int(item.get("dep_time", "06:00").split(":")[0])
            if params.time_of_day == "Morning" and not (5 <= dep_hour < 12):
                continue
            elif params.time_of_day == "Afternoon" and not (12 <= dep_hour < 17):
                continue
            elif params.time_of_day == "Evening" and not (dep_hour >= 17 or dep_hour < 5):
                continue

            # Airline code normalization
            airline_name = item.get("airline", "IndiGo")
            code_map = {
                "IndiGo": "6E", "Air India": "AI", "Akasa Air": "QP",
                "SpiceJet": "SG", "Air India Express": "IX", "Star Air": "S5",
                "Vistara": "UK"
            }
            airline_code = item.get("airline_code") or code_map.get(airline_name, "6E")

            # Segments generation
            stops_str = item.get("stops", "Nonstop")
            stop_cnt = 0 if stops_str.lower() == "nonstop" else (1 if "1" in stops_str else 2)

            f_origin = item.get("origin", orig_city)
            f_origin_code = item.get("origin_code", orig_code)
            f_dest = item.get("destination", dest_city)
            f_dest_code = item.get("destination_code", dest_code)
            f_no = item.get("flight_no", f"{airline_code} 101")
            f_dur = item.get("duration", "2h 15m")
            f_dur_m = item.get("duration_mins", 135)
            f_dep = item.get("dep_time", "06:00")
            f_arr = item.get("arr_time", "08:15")

            segments: List[FlightSegment] = []
            if "custom_segments" in item:
                for s in item["custom_segments"]:
                    segments.append(FlightSegment(**s))
            elif stop_cnt == 1:
                hub_code = "HYD" if f_origin_code != "HYD" and f_dest_code != "HYD" else "BOM"
                hub_city = self._get_city_name(hub_code)
                f_no1 = f_no.split("/")[0].strip() if "/" in f_no else f"{airline_code} 201"
                f_no2 = f_no.split("/")[1].strip() if "/" in f_no else f"{airline_code} 408"
                total_m = int(f_dur_m)
                leg1_m = int(total_m * 0.4)
                layover_m = 50
                leg2_m = max(30, total_m - leg1_m - layover_m)

                segments.append(FlightSegment(
                    segment_id=f"SEG-{idx + 1}-1",
                    flight_no=f_no1,
                    airline=airline_name,
                    airline_code=airline_code,
                    origin=f_origin,
                    origin_code=f_origin_code,
                    destination=hub_city,
                    destination_code=hub_code,
                    dep_time=f_dep,
                    arr_time="--:--",
                    duration=f"{leg1_m // 60}h {leg1_m % 60}m",
                    duration_mins=leg1_m,
                    layover_mins=layover_m,
                    terminal_dep=item.get("terminal") or "T2",
                    terminal_arr="T1",
                    aircraft=item.get("aircraft") or "Airbus A320neo"
                ))
                segments.append(FlightSegment(
                    segment_id=f"SEG-{idx + 1}-2",
                    flight_no=f_no2,
                    airline=airline_name,
                    airline_code=airline_code,
                    origin=hub_city,
                    origin_code=hub_code,
                    destination=f_dest,
                    destination_code=f_dest_code,
                    dep_time="--:--",
                    arr_time=f_arr,
                    duration=f"{leg2_m // 60}h {leg2_m % 60}m",
                    duration_mins=leg2_m,
                    layover_mins=0,
                    terminal_dep="T1",
                    terminal_arr="T2",
                    aircraft=item.get("aircraft") or "Airbus A320neo"
                ))
            else:
                # Default 1 segment for direct flight
                segments.append(FlightSegment(
                    segment_id=f"SEG-{idx + 1}-1",
                    flight_no=f_no,
                    airline=airline_name,
                    airline_code=airline_code,
                    origin=f_origin,
                    origin_code=f_origin_code,
                    destination=f_dest,
                    destination_code=f_dest_code,
                    dep_time=f_dep,
                    arr_time=f_arr,
                    duration=f_dur,
                    duration_mins=f_dur_m,
                    layover_mins=0,
                    terminal_dep=item.get("terminal") or "T2",
                    terminal_arr="T1",
                    aircraft=item.get("aircraft") or "Airbus A320neo"
                ))

            norm_f = NormalizedFlight(
                id=int(item.get("id", idx + 1)),
                airline=airline_name,
                airline_code=airline_code,
                flight_no=item.get("flight_no", f"{airline_code} 101"),
                origin=item.get("origin", orig_city),
                origin_code=item.get("origin_code", orig_code),
                destination=item.get("destination", dest_city),
                destination_code=item.get("destination_code", dest_code),
                dep_time=item.get("dep_time", "06:00"),
                arr_time=item.get("arr_time", "08:15"),
                duration=item.get("duration", "2h 15m"),
                duration_mins=int(item.get("duration_mins", 135)),
                stops=stops_str,
                stop_count=stop_cnt,
                segments=segments,
                base_fare=int(item.get("base_fare", 3800)),
                taxes=int(item.get("taxes", 850)),
                total_fare=int(item.get("total_fare", 4650)),
                currency="INR",
                bag_fee=int(item.get("bag_fee", 0)),
                emissions_kg=int(item.get("emissions_kg", 135)),
                fare_score=int(item.get("fare_score", 90)),
                tag=item.get("tag", "BEST VALUE"),
                status=item.get("status", "On time"),
                terminal=item.get("terminal") or "T2",
                gate=item.get("gate") or "G4",
                aircraft=item.get("aircraft") or "Airbus A320neo",
                provider=self.get_name(),
                data_source="DEVELOPMENT",  # Explicitly DEVELOPMENT
                deeplink=None
            )
            normalized_list.append(norm_f)

        # Sorting
        if params.sort_by == "price":
            normalized_list.sort(key=lambda x: x.total_fare)
        elif params.sort_by == "duration":
            normalized_list.sort(key=lambda x: x.duration_mins)
        elif params.sort_by == "emissions":
            normalized_list.sort(key=lambda x: x.emissions_kg)
        else:  # default 'score'
            normalized_list.sort(key=lambda x: x.fare_score, reverse=True)

        best_fare = min([f.total_fare for f in normalized_list]) if normalized_list else None

        return NormalizedSearchResponse(
            total=len(normalized_list),
            origin=orig_city,
            destination=dest_city,
            date=params.date,
            cabin=params.cabin,
            best_fare=best_fare,
            provider=self.get_name(),
            data_source="DEVELOPMENT",
            cached=False,
            cache_ttl_remaining_secs=None,
            flights=normalized_list
        )

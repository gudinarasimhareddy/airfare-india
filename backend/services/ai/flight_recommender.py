"""
AirfareX India — Transparent Flight Scoring & Recommendation Engine
Calculates deterministic 0-100 scores and assigns CHEAPEST, FASTEST, BEST VALUE, and AIRFAREX PICK badges.
"""

from typing import List, Dict, Any, Optional, Tuple
import re

from backend.services.ai.base import (
    FlightScoringBreakdown,
    FlightRecommendationItem
)

def parse_duration_to_mins(duration_str: str) -> int:
    """Converts duration strings like '2h 15m', '1h 50m', '8h 20m' into total minutes."""
    if not duration_str:
        return 120
    hours = 0
    mins = 0
    h_match = re.search(r'(\d+)\s*h', duration_str, re.IGNORECASE)
    m_match = re.search(r'(\d+)\s*m', duration_str, re.IGNORECASE)
    if h_match:
        hours = int(h_match.group(1))
    if m_match:
        mins = int(m_match.group(1))
    if not h_match and not m_match:
        digits = re.findall(r'\d+', duration_str)
        if digits:
            hours = int(digits[0])
    return (hours * 60) + mins

def format_mins_to_duration(mins: int) -> str:
    """Converts minutes into 'Xh Ym' string."""
    h = mins // 60
    m = mins % 60
    if h > 0 and m > 0:
        return f"{h}h {m}m"
    elif h > 0:
        return f"{h}h"
    return f"{m}m"

class FlightRecommender:
    """Core ranking, scoring, and recommendation engine for AirfareX."""

    @staticmethod
    def calculate_flight_score(
        flight: Dict[str, Any],
        min_fare: int,
        max_fare: int,
        min_dur_mins: int,
        max_dur_mins: int,
        cheapest_flight: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Tuple[FlightScoringBreakdown, List[str]]:
        """
        Calculates deterministic category scores (0-100) and extracts factual reasons.
        """
        fare = flight.get("total_fare", 0)
        dur_str = flight.get("duration", "2h 0m")
        dur_mins = flight.get("duration_mins") or parse_duration_to_mins(dur_str)
        stops_str = str(flight.get("stops", "Nonstop")).strip()
        dep_time = flight.get("dep_time", "08:00")
        arr_time = flight.get("arr_time", "10:00")
        airline = flight.get("airline", "")

        prefs = user_preferences or {}
        priority = prefs.get("priority", "best_value").lower()
        time_pref = prefs.get("time_preference", "any").lower()
        pref_airline = prefs.get("preferred_airline", "").lower()

        # 1. Price Score (0-100)
        if max_fare == min_fare:
            price_score = 100
        else:
            ratio = (fare - min_fare) / max(1, (max_fare - min_fare))
            if priority == "lowest_price":
                # Stricter penalty on any fare above absolute minimum
                extra_fare = fare - min_fare
                price_score = max(20, min(100, int(100 - (ratio * 50) - (extra_fare / 15))))
            else:
                price_score = max(40, min(100, int(100 - (ratio * 50))))

        # 2. Duration Score (0-100)
        if max_dur_mins == min_dur_mins:
            duration_score = 100
        else:
            ratio = (dur_mins - min_dur_mins) / max(1, (max_dur_mins - min_dur_mins))
            if priority == "fastest":
                # Stricter penalty on any duration slower than absolute fastest
                extra_mins = dur_mins - min_dur_mins
                duration_score = max(20, min(100, int(100 - (ratio * 50) - (extra_mins * 2.5))))
            else:
                duration_score = max(35, min(100, int(100 - (ratio * 55))))

        # 3. Stops Score (0-100)
        is_nonstop = stops_str.lower() in ("0", "0 stops", "nonstop", "non-stop", "direct")
        if is_nonstop:
            stops_score = 100
        elif "1" in stops_str:
            stops_score = 70
        else:
            stops_score = 40

        # 4. Convenience Score (0-100)
        try:
            dep_hour = int(dep_time.split(":")[0])
        except Exception:
            dep_hour = 8

        convenience_score = 85
        if 6 <= dep_hour <= 21:
            convenience_score = 95
        elif 22 <= dep_hour <= 23:
            convenience_score = 75
        else: # Red-eye / late night (00:00 - 05:59)
            convenience_score = 60

        # Time preference adjustment
        if time_pref == "morning" and 5 <= dep_hour <= 12:
            convenience_score = min(100, convenience_score + 10)
        elif time_pref == "evening" and 17 <= dep_hour <= 22:
            convenience_score = min(100, convenience_score + 10)

        # 5. Value Score (0-100)
        # Assesses whether paying extra over the cheapest flight saves substantial time
        if cheapest_flight and fare == min_fare:
            value_score = 90
        elif cheapest_flight:
            cheapest_dur = cheapest_flight.get("duration_mins") or parse_duration_to_mins(cheapest_flight.get("duration", "2h 0m"))
            time_saved_mins = cheapest_dur - dur_mins
            price_delta = fare - min_fare

            if time_saved_mins > 0:
                # Value of time: in Indian aviation, saving 1 hour is worth ~₹450
                value_gain = (time_saved_mins / 60.0) * 450
                net_value_diff = value_gain - price_delta
                if net_value_diff >= 0:
                    # Excellent trade-off
                    value_score = min(98, 90 + int(net_value_diff / 100))
                else:
                    value_score = max(50, 90 - int(abs(net_value_diff) / 100))
            else:
                # Costs more without saving time
                value_score = max(40, 85 - int(price_delta / 80))
        else:
            value_score = int((price_score * 0.5) + (duration_score * 0.5))

        # Preferred airline bonus
        airline_bonus = 0
        if pref_airline and pref_airline in airline.lower():
            airline_bonus = 5

        # 6. Weighted Overall Score (0-100)
        if priority == "lowest_price":
            w_price, w_dur, w_stops, w_conv, w_val = 0.80, 0.05, 0.08, 0.04, 0.03
        elif priority == "fastest":
            w_price, w_dur, w_stops, w_conv, w_val = 0.05, 0.75, 0.10, 0.05, 0.05
        elif priority in ("nonstop", "fewest_stops"):
            w_price, w_dur, w_stops, w_conv, w_val = 0.15, 0.15, 0.60, 0.05, 0.05
        elif priority == "best_value":
            w_price, w_dur, w_stops, w_conv, w_val = 0.25, 0.25, 0.15, 0.10, 0.25
        else:
            w_price, w_dur, w_stops, w_conv, w_val = 0.35, 0.25, 0.20, 0.10, 0.10

        overall = (
            (price_score * w_price) +
            (duration_score * w_dur) +
            (stops_score * w_stops) +
            (convenience_score * w_conv) +
            (value_score * w_val) +
            airline_bonus
        )
        overall_score = max(30, min(99, int(round(overall))))

        # Factual reasons extraction (2-4 concise bullets)
        reasons: List[str] = []
        if fare == min_fare:
            reasons.append("Lowest available fare in this search")
        else:
            diff = fare - min_fare
            reasons.append(f"₹{diff:,} above cheapest fare")

        if is_nonstop:
            reasons.append("Non-stop direct flight")
        else:
            reasons.append(f"{stops_str}")

        if dur_mins == min_dur_mins:
            reasons.append("Fastest travel time on this sector")
        elif cheapest_flight:
            cheapest_dur = cheapest_flight.get("duration_mins") or parse_duration_to_mins(cheapest_flight.get("duration", "2h 0m"))
            time_saved = cheapest_dur - dur_mins
            if time_saved > 0:
                reasons.append(f"Saves {format_mins_to_duration(time_saved)} vs cheapest flight")

        if 6 <= dep_hour <= 11:
            reasons.append(f"Convenient morning departure ({dep_time})")
        elif 17 <= dep_hour <= 21:
            reasons.append(f"Convenient evening departure ({dep_time})")

        if overall_score >= 90:
            reasons.append("High overall value score")

        breakdown = FlightScoringBreakdown(
            price_score=price_score,
            duration_score=duration_score,
            stops_score=stops_score,
            convenience_score=convenience_score,
            value_score=value_score,
            overall_score=overall_score
        )

        return breakdown, reasons[:4]

    @classmethod
    def evaluate_and_rank_flights(
        cls,
        flights: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates an entire flight list and selects:
        - CHEAPEST
        - FASTEST
        - BEST VALUE
        - AIRFAREX PICK
        """
        if not flights:
            return {
                "cheapest": None,
                "fastest": None,
                "best_value": None,
                "airfarex_pick": None,
                "scored_flights": [],
                "market_summary": "No flight schedules available."
            }

        # Normalize durations
        parsed_flights = []
        fares = []
        dur_mins_list = []

        for f in flights:
            item = dict(f)
            if "duration_mins" not in item or not item["duration_mins"]:
                item["duration_mins"] = parse_duration_to_mins(item.get("duration", "2h 0m"))
            fares.append(item.get("total_fare", 0))
            dur_mins_list.append(item["duration_mins"])
            parsed_flights.append(item)

        min_fare = min(fares)
        max_fare = max(fares)
        min_dur = min(dur_mins_list)
        max_dur = max(dur_mins_list)

        # Identify cheapest flight object
        cheapest_obj = min(parsed_flights, key=lambda x: x.get("total_fare", 0))
        # Identify fastest flight object
        fastest_obj = min(parsed_flights, key=lambda x: x.get("duration_mins", 0))

        scored_items: List[FlightRecommendationItem] = []

        for f in parsed_flights:
            scores, reasons = cls.calculate_flight_score(
                f,
                min_fare=min_fare,
                max_fare=max_fare,
                min_dur_mins=min_dur,
                max_dur_mins=max_dur,
                cheapest_flight=cheapest_obj,
                user_preferences=user_preferences
            )

            # Generate concise 'why_recommended' narrative
            if f["flight_no"] == cheapest_obj["flight_no"]:
                why = "Lowest total fare available across all airlines on this route."
            else:
                extra = f.get("total_fare", 0) - min_fare
                cheapest_dur = cheapest_obj.get("duration_mins", 0)
                saved_mins = cheapest_dur - f.get("duration_mins", 0)
                if saved_mins > 0:
                    why = f"₹{extra:,} more than cheapest, but saves {format_mins_to_duration(saved_mins)} and offers superior scheduling."
                else:
                    why = f"Standard scheduled flight with {scores.overall_score}/100 quality score."

            scored_items.append(FlightRecommendationItem(
                flight_no=f.get("flight_no", ""),
                airline=f.get("airline", ""),
                total_fare=f.get("total_fare", 0),
                duration=f.get("duration", ""),
                stops=f.get("stops", "Nonstop"),
                scores=scores,
                reasons=reasons,
                why_recommended=why
            ))

        # Find best value (highest value score, with preference to non-stop/fast if small price delta)
        best_val_item = max(scored_items, key=lambda x: (x.scores.value_score, x.scores.overall_score))

        # Find AirfareX pick (highest overall score)
        pick_item = max(scored_items, key=lambda x: x.scores.overall_score)

        # Assign badges
        for item in scored_items:
            if item.flight_no == pick_item.flight_no:
                item.badge = "AIRFAREX PICK"
            elif item.flight_no == best_val_item.flight_no and best_val_item.flight_no != cheapest_obj.get("flight_no"):
                item.badge = "BEST VALUE"
            elif item.flight_no == cheapest_obj.get("flight_no"):
                item.badge = "CHEAPEST"
            elif item.flight_no == fastest_obj.get("flight_no"):
                item.badge = "FASTEST"

        # Market summary
        savings = max_fare - min_fare
        summary = (
            f"Analyzed {len(flights)} flights. Fares range from ₹{min_fare:,} to ₹{max_fare:,} "
            f"(saving up to ₹{savings:,}). Fastest flight is {fastest_obj.get('airline')} at {fastest_obj.get('duration')}."
        )

        return {
            "cheapest": next((i for i in scored_items if i.flight_no == cheapest_obj.get("flight_no")), None),
            "fastest": next((i for i in scored_items if i.flight_no == fastest_obj.get("flight_no")), None),
            "best_value": best_val_item,
            "airfarex_pick": pick_item,
            "scored_flights": scored_items,
            "market_summary": summary
        }

"""
AirfareX India — Flight Explainer & Comparison Engine
Produces explainable multi-flight comparisons and detailed "Why this flight?" breakdowns.
"""

from typing import Dict, Any, List, Optional
from backend.services.ai.base import FlightComparisonResult
from backend.services.ai.flight_recommender import (
    FlightRecommender,
    parse_duration_to_mins,
    format_mins_to_duration
)

class FlightExplainer:
    """Provides transparent, factual flight explainability and side-by-side comparisons."""

    @staticmethod
    def compare_two_flights(
        flight_a: Dict[str, Any],
        flight_b: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None,
        provider: str = "RULE_BASED"
    ) -> FlightComparisonResult:
        """
        Calculates side-by-side differences between Flight A and Flight B and forms an explainable narrative.
        """
        fare_a = int(flight_a.get("total_fare", 0))
        fare_b = int(flight_b.get("total_fare", 0))
        price_diff = fare_b - fare_a # positive means B is more expensive

        dur_a_str = flight_a.get("duration", "2h 0m")
        dur_b_str = flight_b.get("duration", "2h 0m")
        dur_a_mins = flight_a.get("duration_mins") or parse_duration_to_mins(dur_a_str)
        dur_b_mins = flight_b.get("duration_mins") or parse_duration_to_mins(dur_b_str)
        dur_diff_mins = dur_b_mins - dur_a_mins # positive means B is longer

        stops_a = str(flight_a.get("stops", "Nonstop"))
        stops_b = str(flight_b.get("stops", "Nonstop"))

        # Compute scoring for both
        min_f = min(fare_a, fare_b)
        max_f = max(fare_a, fare_b)
        min_d = min(dur_a_mins, dur_b_mins)
        max_d = max(dur_a_mins, dur_b_mins)

        scores_a, _ = FlightRecommender.calculate_flight_score(
            flight_a, min_f, max_f, min_d, max_d, flight_a if fare_a <= fare_b else flight_b, user_preferences
        )
        scores_b, _ = FlightRecommender.calculate_flight_score(
            flight_b, min_f, max_f, min_d, max_d, flight_a if fare_a <= fare_b else flight_b, user_preferences
        )

        flight_a_no = flight_a.get("flight_no", "Flight A")
        flight_b_no = flight_b.get("flight_no", "Flight B")
        airline_a = flight_a.get("airline", "Airline A")
        airline_b = flight_b.get("airline", "Airline B")

        comparison_points: List[str] = []

        # Price comparison point
        if price_diff > 0:
            comparison_points.append(f"{flight_b_no} ({airline_b}) costs ₹{price_diff:,} more than {flight_a_no}")
        elif price_diff < 0:
            comparison_points.append(f"{flight_b_no} ({airline_b}) is ₹{abs(price_diff):,} cheaper than {flight_a_no}")
        else:
            comparison_points.append(f"Both flights have identical total fare of ₹{fare_a:,}")

        # Duration comparison point
        if dur_diff_mins < 0:
            saved = abs(dur_diff_mins)
            comparison_points.append(f"{flight_b_no} is {format_mins_to_duration(saved)} faster ({dur_b_str} vs {dur_a_str})")
        elif dur_diff_mins > 0:
            comparison_points.append(f"{flight_a_no} is {format_mins_to_duration(dur_diff_mins)} faster ({dur_a_str} vs {dur_b_str})")
        else:
            comparison_points.append(f"Both flights have the same duration ({dur_a_str})")

        # Stops comparison point
        if stops_a.lower() != stops_b.lower():
            comparison_points.append(f"{flight_a_no} has {stops_a}, while {flight_b_no} has {stops_b}")

        # Departure/arrival convenience
        dep_a = flight_a.get("dep_time", "")
        dep_b = flight_b.get("dep_time", "")
        if dep_a and dep_b:
            comparison_points.append(f"Departure times: {flight_a_no} at {dep_a} vs {flight_b_no} at {dep_b}")

        # Verdict & narrative generation
        if scores_b.overall_score > scores_a.overall_score:
            rec_flight = flight_b_no
            if price_diff > 0 and dur_diff_mins < 0:
                saved = abs(dur_diff_mins)
                narrative = f"{flight_b_no} costs ₹{price_diff:,} more but is {format_mins_to_duration(saved)} faster and offers higher overall comfort ({scores_b.overall_score}/100 vs {scores_a.overall_score}/100)."
                verdict = f"Choose {flight_b_no} for superior value and significant time savings."
            elif price_diff <= 0:
                narrative = f"{flight_b_no} offers a lower or equal fare with equal or better travel time and convenience score."
                verdict = f"Choose {flight_b_no} — it is the clear winner on both price and scheduling."
            else:
                narrative = f"{flight_b_no} achieves a higher overall score ({scores_b.overall_score}/100) due to scheduling and airline service quality."
                verdict = f"{flight_b_no} is recommended based on overall value."
        else:
            rec_flight = flight_a_no
            if price_diff < 0 and dur_diff_mins > 0:
                saved = dur_diff_mins
                narrative = f"{flight_a_no} is ₹{abs(price_diff):,} more expensive but saves {format_mins_to_duration(saved)} over {flight_b_no}."
                verdict = f"Choose {flight_a_no} if saving {format_mins_to_duration(saved)} is worth the ₹{abs(price_diff):,} difference."
            elif price_diff >= 0:
                narrative = f"{flight_a_no} offers a lower or equal fare of ₹{fare_a:,} with an overall score of {scores_a.overall_score}/100."
                verdict = f"Choose {flight_a_no} for optimal budget efficiency."
            else:
                narrative = f"{flight_a_no} scores higher overall ({scores_a.overall_score}/100 vs {scores_b.overall_score}/100)."
                verdict = f"{flight_a_no} is recommended based on your preferences."

        return FlightComparisonResult(
            flight_a_no=flight_a_no,
            flight_b_no=flight_b_no,
            airline_a=airline_a,
            airline_b=airline_b,
            price_a=fare_a,
            price_b=fare_b,
            price_diff=price_diff,
            duration_a=dur_a_str,
            duration_b=dur_b_str,
            duration_diff_mins=dur_diff_mins,
            stops_a=stops_a,
            stops_b=stops_b,
            score_a=scores_a.overall_score,
            score_b=scores_b.overall_score,
            recommended_flight=rec_flight,
            verdict=verdict,
            narrative=narrative,
            comparison_points=comparison_points,
            provider=provider
        )

    @staticmethod
    def explain_single_flight(
        flight: Dict[str, Any],
        cheapest_flight: Optional[Dict[str, Any]] = None,
        fastest_flight: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Builds the detailed 'Why AirfareX recommends this flight' modal payload.
        """
        fare = flight.get("total_fare", 0)
        dur_str = flight.get("duration", "2h 0m")
        dur_mins = flight.get("duration_mins") or parse_duration_to_mins(dur_str)
        stops_str = str(flight.get("stops", "Nonstop"))

        c_fare = cheapest_flight.get("total_fare", fare) if cheapest_flight else fare
        c_dur = cheapest_flight.get("duration_mins", dur_mins) if cheapest_flight else dur_mins

        price_delta = fare - c_fare
        time_saved_mins = c_dur - dur_mins

        min_f = min(fare, c_fare)
        max_f = max(fare, c_fare)
        min_d = min(dur_mins, c_dur)
        max_d = max(dur_mins, c_dur)

        scores, reasons = FlightRecommender.calculate_flight_score(
            flight, min_f, max_f, min_d, max_d, cheapest_flight, user_preferences
        )

        comparison_vs_cheapest = {
            "price_delta": price_delta,
            "price_delta_formatted": f"+₹{price_delta:,}" if price_delta > 0 else ("₹0 (Cheapest)" if price_delta == 0 else f"-₹{abs(price_delta):,}"),
            "time_saved_mins": time_saved_mins,
            "time_saved_formatted": f"{format_mins_to_duration(time_saved_mins)} faster" if time_saved_mins > 0 else ("Same duration" if time_saved_mins == 0 else f"{format_mins_to_duration(abs(time_saved_mins))} slower"),
            "stops_benefit": "Direct non-stop flight" if stops_str.lower() in ("nonstop", "0", "0 stops") else stops_str
        }

        return {
            "flight_no": flight.get("flight_no"),
            "airline": flight.get("airline"),
            "sector": f"{flight.get('origin_code', '')} ➔ {flight.get('destination_code', '')}",
            "dep_time": flight.get("dep_time"),
            "arr_time": flight.get("arr_time"),
            "duration": dur_str,
            "stops": stops_str,
            "total_fare": fare,
            "scores": scores.model_dump() if hasattr(scores, "model_dump") else scores.dict(),
            "comparison_vs_cheapest": comparison_vs_cheapest,
            "reasons": reasons,
            "dgca_protection": "Covered by DGCA Civil Aviation Requirements (CAR Section 3) for statutory refunds and cancellation protections.",
            "baggage_info": f"Cabin: 7kg Included · Checked: {'15kg Included' if flight.get('bag_fee', 0) == 0 else '+₹' + str(flight.get('bag_fee', 550))}"
        }

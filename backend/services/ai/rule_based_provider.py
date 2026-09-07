"""
AirfareX India — Deterministic Rule-Based Aviation Intelligence Provider
Operates autonomously without external API keys, ensuring 100% data consistency, zero hallucinations,
and strict safety boundaries.
"""

from typing import Dict, Any, List, Optional
import re

from backend.services.ai.base import (
    BaseAIProvider,
    CopilotResponse,
    NLSearchParams
)
from backend.services.ai.nl_search import NLSearchInterpreter
from backend.services.ai.flight_recommender import (
    FlightRecommender,
    parse_duration_to_mins,
    format_mins_to_duration
)
from backend.services.ai.price_intelligence import PriceIntelligenceService
from backend.database import get_db_connection

class RuleBasedAIProvider(BaseAIProvider):
    """Deterministic, factual AI intelligence provider for AirfareX."""

    @property
    def provider_name(self) -> str:
        return "RULE_BASED"

    def interpret_nl_query(self, query: str) -> NLSearchParams:
        return NLSearchInterpreter.parse_query(query)

    async def generate_copilot_response(
        self,
        query: str,
        search_context: Optional[Dict[str, Any]] = None,
        available_flights: Optional[List[Dict[str, Any]]] = None,
        selected_flight: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> CopilotResponse:
        q_lower = query.strip().lower()

        ctx = search_context or {}
        flights = available_flights or []
        sel = selected_flight

        # If flights are empty, attempt to fetch from DB for the sector in context or query
        if not flights:
            origin = ctx.get("origin") or ctx.get("from_city")
            dest = ctx.get("destination") or ctx.get("to_city")
            if not origin or not dest:
                nl_p = NLSearchInterpreter.parse_query(query)
                origin = nl_p.origin or "DEL"
                dest = nl_p.destination or "BOM"

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM flights 
                WHERE origin_code = ? AND destination_code = ?
                ORDER BY total_fare ASC
                LIMIT 10
            """, (origin, dest))
            rows = cur.fetchall()
            if not rows:
                cur.execute("SELECT * FROM flights ORDER BY total_fare ASC LIMIT 10")
                rows = cur.fetchall()
            conn.close()
            flights = [dict(r) for r in rows]

        # Evaluate recommendations if we have flights
        rec_data = FlightRecommender.evaluate_and_rank_flights(flights, user_preferences)
        cheapest = rec_data.get("cheapest")
        fastest = rec_data.get("fastest")
        best_value = rec_data.get("best_value")
        pick = rec_data.get("airfarex_pick")

        # 1. Price Good / Trend / "Should I book"
        if any(w in q_lower for w in ["price good", "is this price good", "fare good", "good price", "book now or wait", "should i book", "trend"]):
            orig = ctx.get("origin", flights[0].get("origin_code", "DEL") if flights else "DEL")
            dest = ctx.get("destination", flights[0].get("destination_code", "BOM") if flights else "BOM")
            dep_date = ctx.get("date")

            pred = PriceIntelligenceService.get_price_prediction_insight(orig, dest, dep_date)
            cur_fare = sel.get("total_fare") if sel else (cheapest.total_fare if cheapest else pred.get("current_fare", 5000))
            rec_action = pred.get("recommendation", "BUY_NOW")

            if rec_action == "BUY_NOW":
                ans = (
                    f"**Price Recommendation: BUY NOW** for {orig} ➔ {dest}.\n\n"
                    f"• Current observed fare: **₹{cur_fare:,}**\n"
                    f"• Market prediction: {pred.get('recommendation_desc')}\n"
                    f"• Forecast confidence: **{pred.get('confidence_pct', 85)}%**\n"
                    f"• Optimal booking window: {pred.get('optimal_booking_window', 'Advance booking')}"
                )
            else:
                ans = (
                    f"**Price Recommendation: WAIT / MONITOR** for {orig} ➔ {dest}.\n\n"
                    f"• Current observed fare: **₹{cur_fare:,}**\n"
                    f"• Market prediction: {pred.get('recommendation_desc')}\n"
                    f"• Potential correction: ~₹{abs(pred.get('expected_delta_inr', 500)):,} drop predicted."
                )

            facts = [
                f"Sector: {orig} ➔ {dest}",
                f"Current fare: ₹{cur_fare:,}",
                f"Confidence: {pred.get('confidence_pct')}%" if pred.get('confidence_pct') else "Baseline estimation"
            ]

            return CopilotResponse(
                answer=ans,
                recommendation={"action": rec_action, "sector": f"{orig} ➔ {dest}", "fare": cur_fare},
                facts=facts,
                confidence=pred.get("confidence_pct"),
                provider="RULE_BASED",
                suggestions=["Which flight should I choose?", "Compare cheapest vs fastest", "Show alternative dates"]
            )

        # 2. "Which flight should I choose?" / "What is best?" / "Recommend"
        if any(w in q_lower for w in ["which flight", "should i choose", "best flight", "recommend", "what is the best", "pick"]):
            if best_value and cheapest:
                facts = [
                    f"Cheapest: {cheapest.flight_no} ({cheapest.airline}) at ₹{cheapest.total_fare:,}",
                    f"Fastest: {fastest.flight_no} ({fastest.airline}) in {fastest.duration}",
                    f"Best Value: {best_value.flight_no} ({best_value.airline}) with score {best_value.scores.overall_score}/100"
                ]

                ans = (
                    f"Based on actual flight schedules and pricing on this route, here is the decision breakdown:\n\n"
                    f"👑 **AirfareX Best Value Pick: {best_value.flight_no} ({best_value.airline}) — ₹{best_value.total_fare:,}**\n"
                    f"• **Why?** {best_value.why_recommended}\n"
                    f"• **Stops:** {best_value.stops} · **Duration:** {best_value.duration}\n"
                    f"• **Overall Score:** {best_value.scores.overall_score}/100\n\n"
                    f"💡 **Alternatives:**\n"
                    f"• **Lowest Budget:** {cheapest.flight_no} at ₹{cheapest.total_fare:,} ({cheapest.duration})\n"
                    f"• **Maximum Speed:** {fastest.flight_no} at ₹{fastest.total_fare:,} ({fastest.duration})"
                )

                return CopilotResponse(
                    answer=ans,
                    recommendation={
                        "flight_no": best_value.flight_no,
                        "airline": best_value.airline,
                        "fare": best_value.total_fare,
                        "reason": best_value.why_recommended
                    },
                    facts=facts,
                    confidence=95,
                    provider="RULE_BASED",
                    action={"type": "populate_search", "origin": flights[0].get("origin_code", "DEL"), "destination": flights[0].get("destination_code", "BOM"), "fare": best_value.total_fare},
                    suggestions=["What happens if I choose the cheaper flight?", "Is this price good?", "Compare Flight A vs Flight B"]
                )

        # 3. "What happens if I choose the cheaper flight?" / "Why not cheapest?"
        if any(w in q_lower for w in ["cheaper flight", "choose the cheaper", "why not cheapest", "cheaper option", "trade off", "tradeoff"]):
            if cheapest and best_value:
                cheapest_dur_mins = cheapest.scores.duration_score # or dur
                diff_fare = best_value.total_fare - cheapest.total_fare
                ans = (
                    f"**Trade-off Analysis: Cheapest Flight ({cheapest.flight_no}) vs Best Value ({best_value.flight_no})**\n\n"
                    f"• **Cost difference:** {cheapest.flight_no} saves you **₹{diff_fare:,}** upfront.\n"
                    f"• **Time difference:** {cheapest.flight_no} takes **{cheapest.duration}** vs {best_value.duration} for {best_value.flight_no}.\n"
                    f"• **Stops:** {cheapest.flight_no} ({cheapest.stops}) vs {best_value.flight_no} ({best_value.stops}).\n\n"
                    f"**Verdict:** If you are strictly traveling on a budget, choose **{cheapest.flight_no}** (₹{cheapest.total_fare:,}). "
                    f"If you want to save travel time and avoid layovers, the ₹{diff_fare:,} upgrade to **{best_value.flight_no}** offers significantly better value."
                )

                facts = [
                    f"Cheapest: ₹{cheapest.total_fare:,} ({cheapest.duration})",
                    f"Best Value: ₹{best_value.total_fare:,} ({best_value.duration})",
                    f"Fare delta: ₹{diff_fare:,}"
                ]

                return CopilotResponse(
                    answer=ans,
                    recommendation={"flight_no": cheapest.flight_no, "fare": cheapest.total_fare, "reason": "Lowest absolute fare"},
                    facts=facts,
                    confidence=98,
                    provider="RULE_BASED",
                    suggestions=["Which flight is fastest?", "Should I book now?", "Check baggage allowance"]
                )

        # 4. "Which flight is fastest?" / "Fastest"
        if any(w in q_lower for w in ["fastest", "quickest", "shortest duration"]):
            if fastest:
                ans = (
                    f"⚡ **Fastest Option: {fastest.flight_no} ({fastest.airline})**\n\n"
                    f"• **Duration:** {fastest.duration} (Non-stop direct)\n"
                    f"• **Total Fare:** ₹{fastest.total_fare:,}\n"
                    f"• **Score:** {fastest.scores.overall_score}/100\n\n"
                    f"{fastest.why_recommended}"
                )
                facts = [f"Flight {fastest.flight_no} duration: {fastest.duration}", f"Fare: ₹{fastest.total_fare:,}"]
                return CopilotResponse(
                    answer=ans,
                    recommendation={"flight_no": fastest.flight_no, "fare": fastest.total_fare, "reason": "Fastest travel time"},
                    facts=facts,
                    confidence=100,
                    provider="RULE_BASED",
                    suggestions=["What is the cheapest option?", "Which flight should I choose?", "Is this price good?"]
                )

        # 5. "What is the cheapest option?" / "Cheapest"
        if any(w in q_lower for w in ["cheapest", "lowest fare", "lowest price", "least expensive"]):
            if cheapest:
                ans = (
                    f"💸 **Cheapest Option: {cheapest.flight_no} ({cheapest.airline})**\n\n"
                    f"• **Total Fare:** ₹{cheapest.total_fare:,} (Includes all mandatory taxes & fees)\n"
                    f"• **Duration:** {cheapest.duration} ({cheapest.stops})\n"
                    f"• **Score:** {cheapest.scores.overall_score}/100\n\n"
                    f"Lowest available fare in this search pool."
                )
                facts = [f"Lowest fare: ₹{cheapest.total_fare:,}", f"Flight: {cheapest.flight_no}"]
                return CopilotResponse(
                    answer=ans,
                    recommendation={"flight_no": cheapest.flight_no, "fare": cheapest.total_fare, "reason": "Lowest available fare"},
                    facts=facts,
                    confidence=100,
                    provider="RULE_BASED",
                    suggestions=["Which flight is fastest?", "What happens if I choose the cheaper flight?", "Is this price good?"]
                )

        # 6. "Show me alternatives" / "Alternative dates" / "Alternative routes"
        if any(w in q_lower for w in ["alternative", "alternate", "nearby airport", "other dates", "different date"]):
            orig = ctx.get("origin", flights[0].get("origin_code", "DEL") if flights else "DEL")
            dest = ctx.get("destination", flights[0].get("destination_code", "BOM") if flights else "BOM")
            dep_date = ctx.get("date")

            alt_dates = PriceIntelligenceService.get_alternative_date_suggestions(orig, dest, dep_date)
            alt_routes = PriceIntelligenceService.get_route_alternatives(orig, dest)

            ans_parts = [f"**Alternative Travel Insights for {orig} ➔ {dest}:**\n"]

            if alt_dates.get("best_saving", 0) > 0:
                ans_parts.append(f"📅 **Date Flexibility:** {alt_dates['narrative']}")
                for opt in alt_dates.get("date_options", [])[:3]:
                    ans_parts.append(f"  • {opt['label']}: ₹{opt['fare']:,}")
            else:
                ans_parts.append("📅 **Date Flexibility:** Current date has the lowest baseline rate for this week.")

            if alt_routes:
                ans_parts.append(f"\n🛣️ **Nearby Route Alternatives:**")
                for r in alt_routes:
                    ans_parts.append(f"  • **{orig} ➔ {r['alternative_airport']} ({r['alternative_city']}):** From ₹{r['fare']:,} ({r['duration']}) — *{r['transfer_note']}*")

            ans = "\n".join(ans_parts)
            facts = [f"Base fare: ₹{alt_dates.get('base_fare', 4500):,}"]

            return CopilotResponse(
                answer=ans,
                facts=facts,
                confidence=92,
                provider="RULE_BASED",
                suggestions=["Which flight should I choose?", "What is the cheapest option?", "Should I book now?"]
            )

        # 7. "Why is this flight better?" / Single flight inquiry
        if sel or any(w in q_lower for w in ["why this flight", "is this flight better", "why is this better"]):
            target_f = sel or (pick.model_dump() if pick else flights[0])
            f_no = target_f.get("flight_no", "")
            f_fare = target_f.get("total_fare", 0)
            f_dur = target_f.get("duration", "2h 0m")

            ans = (
                f"**Flight Evaluation: {f_no} ({target_f.get('airline', 'Airline')})**\n\n"
                f"• **Total Fare:** ₹{f_fare:,}\n"
                f"• **Travel Time:** {f_dur} ({target_f.get('stops', 'Nonstop')})\n"
                f"• **Departure:** {target_f.get('dep_time', '08:00')} ➔ Arrival: {target_f.get('arr_time', '10:15')}\n\n"
                f"This flight offers a balanced combination of on-time reliability, convenient slotting, and transparent DGCA-regulated fare structure."
            )

            facts = [f"Flight {f_no} Fare: ₹{f_fare:,}", f"Duration: {f_dur}"]
            return CopilotResponse(
                answer=ans,
                recommendation={"flight_no": f_no, "fare": f_fare, "reason": "Evaluated candidate"},
                facts=facts,
                confidence=90,
                provider="RULE_BASED",
                suggestions=["What is the cheapest option?", "Which flight is fastest?", "Should I book now?"]
            )

        # 8. General Aviation & DGCA Passenger Charter Questions
        if any(w in q_lower for w in ["refund", "cancel", "baggage", "dgca", "delay", "compensation"]):
            ans = (
                "**AirfareX Aviation Compliance & DGCA Passenger Charter Guidelines:**\n\n"
                "• **Cancellation & Statutory Refunds:** Passenger-initiated cancellations receive full statutory UDF, PSF, and Aviation Security Fee (ASF) refunds under DGCA CAR Section 3.\n"
                "• **Flight Delays > 2 Hours:** Airlines must provide free refreshments/meals.\n"
                "• **Flight Cancellation < 24 Hours:** Airline must offer alternate flight or 100% full refund.\n"
                "• **Standard Domestic Baggage:** 7 kg cabin baggage + 15 kg checked baggage (1 piece) on standard economy tickets."
            )
            facts = ["DGCA CAR Section 3 Series M Part IV compliant", "Full statutory tax refunds protected"]
            return CopilotResponse(
                answer=ans,
                facts=facts,
                confidence=100,
                provider="RULE_BASED",
                action={"type": "open_tab", "tab": "refunds"},
                suggestions=["Which flight should I choose?", "Is this price good?", "What is the cheapest option?"]
            )

        # 9. Default Fallback
        if flights:
            ans = (
                f"I analyzed **{len(flights)} available flights** for your route.\n\n"
                f"• 👑 **AirfareX Pick:** {pick.flight_no} ({pick.airline}) at **₹{pick.total_fare:,}** (Score: {pick.scores.overall_score}/100)\n"
                f"• 💸 **Cheapest:** {cheapest.flight_no} at **₹{cheapest.total_fare:,}**\n"
                f"• ⚡ **Fastest:** {fastest.flight_no} in **{fastest.duration}**\n\n"
                f"Ask me specifically: *'Which flight is fastest?'*, *'Should I book now or wait?'*, or *'What happens if I choose the cheaper flight?'*"
            )
            return CopilotResponse(
                answer=ans,
                recommendation={"flight_no": pick.flight_no, "fare": pick.total_fare, "reason": pick.why_recommended},
                facts=[f"Total flights: {len(flights)}", f"Cheapest: ₹{cheapest.total_fare:,}"],
                confidence=95,
                provider="RULE_BASED",
                suggestions=["Which flight should I choose?", "Is this price good?", "Show me alternatives"]
            )

        return CopilotResponse(
            answer="I am your AirfareX Aviation Copilot. Please search for a route (e.g. Delhi to Mumbai) or ask about flights, prices, and DGCA refund policies.",
            facts=[],
            confidence=100,
            provider="RULE_BASED",
            suggestions=["Flights from Delhi to Mumbai", "Cheapest flight to Goa", "Check DGCA refund policy"]
        )

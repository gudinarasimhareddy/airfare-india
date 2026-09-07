"""
AirfareX India — LLM Provider Interface (Gemini & OpenAI)
Integrates external LLMs when credentials are provided, with strict grounding, token limits,
and automatic fallback to RuleBasedAIProvider.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

from backend.services.ai.base import (
    BaseAIProvider,
    CopilotResponse,
    NLSearchParams
)
from backend.services.ai.rule_based_provider import RuleBasedAIProvider
from backend.services.ai.nl_search import NLSearchInterpreter

logger = logging.getLogger("airfarex.ai")

class LLMAviationProvider(BaseAIProvider):
    """
    Pluggable LLM provider for Gemini / OpenAI.
    Enforces strict grounding against backend flight data.
    """

    def __init__(self, provider_type: str = "GEMINI"):
        self._provider_type = provider_type.upper()
        self.fallback = RuleBasedAIProvider()

    @property
    def provider_name(self) -> str:
        return self._provider_type

    def is_configured(self) -> bool:
        """Checks whether the requisite API key is present in environment."""
        if self._provider_type == "GEMINI":
            return bool(os.environ.get("GEMINI_API_KEY", "").strip())
        elif self._provider_type == "OPENAI":
            return bool(os.environ.get("OPENAI_API_KEY", "").strip())
        return False

    def interpret_nl_query(self, query: str) -> NLSearchParams:
        # We always use the deterministic validated parser for maximum safety and speed
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
        """
        Calls external LLM if configured, otherwise falls back to deterministic RuleBasedAIProvider.
        """
        if not self.is_configured():
            # Graceful, transparent fallback
            return await self.fallback.generate_copilot_response(
                query=query,
                search_context=search_context,
                available_flights=available_flights,
                selected_flight=selected_flight,
                user_preferences=user_preferences,
                language=language
            )

        # Truncate top 5 candidates to save tokens and avoid leakage
        top_candidates = []
        for f in (available_flights or [])[:5]:
            top_candidates.append({
                "flight_no": f.get("flight_no"),
                "airline": f.get("airline"),
                "total_fare": f.get("total_fare"),
                "duration": f.get("duration"),
                "stops": f.get("stops"),
                "dep_time": f.get("dep_time"),
                "arr_time": f.get("arr_time")
            })

        # Structured grounding prompt
        system_instruction = (
            "You are the AirfareX India Aviation Copilot. You assist travelers in choosing the best flight.\n"
            "CRITICAL RULES:\n"
            "1. ONLY use the flight numbers, airlines, and prices provided in the verified flight data.\n"
            "2. NEVER invent fake flight numbers, fares, or airline refund guarantees.\n"
            "3. You CANNOT create bookings, confirm payments, or issue tickets.\n"
            "4. Be concise, objective, and highlight the trade-offs between price, travel time, and stops.\n"
            "5. If information is missing, say: 'I don't have verified data for that.'\n"
        )

        user_prompt = f"""
Traveler Query: {query}
Search Context: {json.dumps(search_context or {})}
Verified Top Flights: {json.dumps(top_candidates)}
Selected Flight: {json.dumps(selected_flight) if selected_flight else "None"}
User Preferences: {json.dumps(user_preferences or {})}
Language: {language}

Provide a concise, helpful response comparing the verified options and explaining which flight best meets their goal.
"""

        try:
            if self._provider_type == "GEMINI":
                # Simulated / real Gemini integration via google-generativeai / REST if installed
                # In standard sandbox without external internet or key, this safely falls back
                api_key = os.environ.get("GEMINI_API_KEY", "")
                if not api_key:
                    raise ValueError("No Gemini API key")
                
                # If genuine key exists, try calling REST or library
                import httpx
                headers = {"Content-Type": "application/json"}
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                payload = {
                    "contents": [{
                        "parts": [{"text": f"{system_instruction}\n\n{user_prompt}"}]
                    }],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 400}
                }
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return CopilotResponse(
                            answer=text,
                            provider="GEMINI",
                            suggestions=["Which flight is fastest?", "What is the cheapest option?", "Check baggage rules"]
                        )
                    else:
                        logger.warning(f"Gemini API returned status {resp.status_code}, falling back.")
            elif self._provider_type == "OPENAI":
                api_key = os.environ.get("OPENAI_API_KEY", "")
                if not api_key:
                    raise ValueError("No OpenAI API key")

                import httpx
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 400
                }
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["choices"][0]["message"]["content"]
                        return CopilotResponse(
                            answer=text,
                            provider="OPENAI",
                            suggestions=["Which flight is fastest?", "What is the cheapest option?", "Check baggage rules"]
                        )
                    else:
                        logger.warning(f"OpenAI API returned status {resp.status_code}, falling back.")
        except Exception as e:
            logger.info(f"External LLM invocation failed or timed out ({e}); using deterministic fallback.")

        # Deterministic fallback
        return await self.fallback.generate_copilot_response(
            query=query,
            search_context=search_context,
            available_flights=available_flights,
            selected_flight=selected_flight,
            user_preferences=user_preferences,
            language=language
        )

"""
AirfareX India — Travel Copilot Coordinator
Manages AI provider selection, context dispatch, and unified aviation intelligence operations.
"""

import os
import logging
from typing import Dict, Any, List, Optional

from backend.services.ai.base import (
    BaseAIProvider,
    CopilotResponse,
    NLSearchParams,
    FlightComparisonResult
)
from backend.services.ai.rule_based_provider import RuleBasedAIProvider
from backend.services.ai.llm_provider import LLMAviationProvider
from backend.services.ai.flight_recommender import FlightRecommender
from backend.services.ai.flight_explainer import FlightExplainer
from backend.services.ai.price_intelligence import PriceIntelligenceService

logger = logging.getLogger("airfarex.ai")

class TravelCopilotCoordinator:
    """Central manager for AirfareX AI intelligence."""

    def __init__(self):
        self.rule_provider = RuleBasedAIProvider()
        self._custom_provider: Optional[BaseAIProvider] = None

    def get_provider(self) -> BaseAIProvider:
        """Determines active provider based on environment configuration."""
        prov_env = os.environ.get("AI_PROVIDER", "rule_based").strip().lower()

        if prov_env == "gemini":
            if not self._custom_provider or self._custom_provider.provider_name != "GEMINI":
                self._custom_provider = LLMAviationProvider("GEMINI")
            return self._custom_provider
        elif prov_env in ("openai", "gpt"):
            if not self._custom_provider or self._custom_provider.provider_name != "OPENAI":
                self._custom_provider = LLMAviationProvider("OPENAI")
            return self._custom_provider
        else:
            return self.rule_provider

    def get_status(self) -> Dict[str, Any]:
        """Returns active AI engine status without leaking credentials."""
        provider = self.get_provider()
        has_gemini = bool(os.environ.get("GEMINI_API_KEY", "").strip())
        has_openai = bool(os.environ.get("OPENAI_API_KEY", "").strip())

        return {
            "active_provider": provider.provider_name,
            "mode": "LIVE_LLM" if (provider.provider_name in ("GEMINI", "OPENAI") and (has_gemini or has_openai)) else "DETERMINISTIC_RULE_BASED",
            "capabilities": [
                "Smart Flight Scoring (0-100)",
                "Best Value & Fastest Optimization",
                "Natural Language Flight Queries",
                "Explainable Side-by-Side Comparison",
                "Price Prediction & Drop Alert Intelligence",
                "Alternative Date & Route Suggestions",
                "Context-Aware Travel Copilot"
            ],
            "attribution": "Powered by AirfareX Intelligence" if provider.provider_name == "RULE_BASED" else f"AirfareX AI ({provider.provider_name})",
            "external_credentials_configured": has_gemini or has_openai
        }

    async def chat(
        self,
        query: str,
        search_context: Optional[Dict[str, Any]] = None,
        available_flights: Optional[List[Dict[str, Any]]] = None,
        selected_flight: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> CopilotResponse:
        """Dispatches chat query to the active provider with complete context."""
        provider = self.get_provider()
        return await provider.generate_copilot_response(
            query=query,
            search_context=search_context,
            available_flights=available_flights,
            selected_flight=selected_flight,
            user_preferences=user_preferences,
            language=language
        )

    def interpret_search(self, query: str) -> NLSearchParams:
        """Parses natural language query into validated parameters."""
        provider = self.get_provider()
        return provider.interpret_nl_query(query)

    def recommend_flights(
        self,
        flights: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculates scores and picks for a flight list."""
        return FlightRecommender.evaluate_and_rank_flights(flights, user_preferences)

    def compare_flights(
        self,
        flight_a: Dict[str, Any],
        flight_b: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> FlightComparisonResult:
        """Generates explainable side-by-side comparison between two flights."""
        provider = self.get_provider()
        return FlightExplainer.compare_two_flights(
            flight_a,
            flight_b,
            user_preferences,
            provider=provider.provider_name
        )

    def explain_flight(
        self,
        flight: Dict[str, Any],
        cheapest_flight: Optional[Dict[str, Any]] = None,
        fastest_flight: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Produces explainability breakdown for a single flight."""
        return FlightExplainer.explain_single_flight(
            flight,
            cheapest_flight,
            fastest_flight,
            user_preferences
        )

# Global singleton
travel_copilot_service = TravelCopilotCoordinator()

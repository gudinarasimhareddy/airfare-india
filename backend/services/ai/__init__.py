"""
AirfareX India — AI Aviation Intelligence Package
"""

from backend.services.ai.base import (
    BaseAIProvider,
    AIProviderType,
    CopilotResponse,
    NLSearchParams,
    FlightComparisonResult,
    FlightScoringBreakdown,
    FlightRecommendationItem
)
from backend.services.ai.rule_based_provider import RuleBasedAIProvider
from backend.services.ai.llm_provider import LLMAviationProvider
from backend.services.ai.flight_recommender import FlightRecommender
from backend.services.ai.flight_explainer import FlightExplainer
from backend.services.ai.price_intelligence import PriceIntelligenceService
from backend.services.ai.nl_search import NLSearchInterpreter
from backend.services.ai.travel_copilot import travel_copilot_service

__all__ = [
    "BaseAIProvider",
    "AIProviderType",
    "CopilotResponse",
    "NLSearchParams",
    "FlightComparisonResult",
    "FlightScoringBreakdown",
    "FlightRecommendationItem",
    "RuleBasedAIProvider",
    "LLMAviationProvider",
    "FlightRecommender",
    "FlightExplainer",
    "PriceIntelligenceService",
    "NLSearchInterpreter",
    "travel_copilot_service"
]
